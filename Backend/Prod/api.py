"""AetherFlow API - Interface simple pour Claude Code."""
import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Literal, Tuple, List
from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from loguru import logger

try:
    # Imports relatifs (package mode)
    from .orchestrator import Orchestrator, ExecutionError
    from .models.plan_reader import PlanReader, PlanValidationError, Plan
    from .workflows.proto import ProtoWorkflow
    from .workflows.prod import ProdWorkflow
    from .sullivan.registry import ComponentRegistry
    from .sullivan.models.component import Component
    from .config.settings import settings
    from .sullivan.studio_routes import router as studio_router
    from .sullivan.agent.api import router as agent_router
except ImportError:
    # Imports absolus (module mode - Python 3.14 compatible)
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from orchestrator import Orchestrator, ExecutionError
    from models.plan_reader import PlanReader, PlanValidationError, Plan
    from workflows.proto import ProtoWorkflow
    from workflows.prod import ProdWorkflow
    from sullivan.registry import ComponentRegistry
    from sullivan.models.component import Component
    from config.settings import settings
    from sullivan.studio_routes import router as studio_router
    from sullivan.agent.api import router as agent_router


app = FastAPI(title="AetherFlow API", version="0.1.0")


# Middleware pour injecter le widget Sullivan sur toutes les pages HTML
class SullivanWidgetMiddleware(BaseHTTPMiddleware):
    """Injecte automatiquement le script Sullivan dans toutes les réponses HTML."""

    WIDGET_SCRIPT = b'\n    <!-- Sullivan Agent Widget -->\n    <script src="/js/sullivan-super-widget.js"></script>\n</body>'

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Ne traiter que les réponses HTML
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return response

        # Collecter le body
        body_parts = []
        async for chunk in response.body_iterator:
            body_parts.append(chunk)
        body = b"".join(body_parts)

        # Injecter le script avant </body>
        if b"</body>" in body and b"sullivan-super-widget.js" not in body:
            body = body.replace(b"</body>", self.WIDGET_SCRIPT)

        # Mettre à jour Content-Length
        headers = dict(response.headers)
        headers["content-length"] = str(len(body))

        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )


app.add_middleware(SullivanWidgetMiddleware)

# Include studio routes (Parcours UX Sullivan)
app.include_router(studio_router)

# Include agent routes (Chatbot Sullivan)
app.include_router(agent_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For beta: allow all origins (restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecutePlanRequest(BaseModel):
    """Request to execute a plan."""
    plan_path: Optional[str] = None
    plan_json: Optional[Dict[str, Any]] = None
    workflow: Optional[Literal["PROTO", "PROD"]] = "PROTO"
    output_dir: Optional[str] = None
    context: Optional[str] = None


class ExecutePlanResponse(BaseModel):
    """Response from plan execution."""
    success: bool
    task_id: str
    results: Dict[str, Any]
    metrics: Dict[str, Any]
    output_dir: str
    message: str


def _validate_request(request: ExecutePlanRequest) -> None:
    """
    Validate that request has at least plan_path or plan_json.
    
    Args:
        request: ExecutePlanRequest to validate
        
    Raises:
        HTTPException: If neither plan_path nor plan_json is provided
    """
    if not request.plan_path and not request.plan_json:
        raise HTTPException(
            status_code=400,
            detail="Either 'plan_path' or 'plan_json' must be provided"
        )


def _create_temp_plan_file(plan_json: Dict[str, Any]) -> Tuple[Path, Optional[Any]]:
    """
    Validate plan_json and create temporary file.
    
    Args:
        plan_json: Plan JSON dictionary
        
    Returns:
        Tuple of (plan_path, temp_file) where temp_file is None if validation fails
        
    Raises:
        HTTPException: If plan_json is invalid
    """
    plan_reader = PlanReader()
    try:
        plan_str = json.dumps(plan_json)
        plan = plan_reader.read_from_string(plan_str)
        logger.info(f"API: Validated plan_json with task_id: {plan.task_id}")
    except PlanValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan_json: {e}"
        )
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        delete=False,
        dir=settings.output_dir
    )
    json.dump(plan_json, temp_file)
    temp_file.close()
    plan_path = Path(temp_file.name)
    logger.info(f"API: Created temporary plan file: {plan_path}")
    
    return plan_path, temp_file


def _resolve_plan_path(request: ExecutePlanRequest) -> Tuple[Path, Optional[Any]]:
    """
    Resolve plan path from request (either plan_path or plan_json).
    
    Args:
        request: ExecutePlanRequest
        
    Returns:
        Tuple of (plan_path, temp_file) where temp_file is None if using plan_path
        
    Raises:
        HTTPException: If plan file not found or plan_json invalid
    """
    if request.plan_json:
        return _create_temp_plan_file(request.plan_json)
    else:
        plan_path = Path(request.plan_path)
        if not plan_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Plan file not found: {plan_path}"
            )
        return plan_path, None


async def _execute_with_workflow(
    plan_path: Path,
    workflow_type: str,
    output_dir: Path,
    context: Optional[str]
) -> Tuple[Dict[str, Any], str]:
    """
    Execute plan using specified workflow.
    
    Args:
        plan_path: Path to plan JSON file
        workflow_type: Workflow type ("PROTO", "PROD", or "DIRECT")
        output_dir: Output directory
        context: Optional context
        
    Returns:
        Tuple of (main_result, workflow_used)
        
    Raises:
        HTTPException: If execution fails
    """
    if workflow_type == "PROTO":
        workflow = ProtoWorkflow()
        workflow_result = await workflow.execute(
            plan_path=plan_path,
            output_dir=output_dir,
            context=context
        )
        # Extract main execution result from fast_execution
        main_result = workflow_result.get("fast_execution", workflow_result)
        return main_result, "PROTO"
        
    elif workflow_type == "PROD":
        workflow = ProdWorkflow()
        workflow_result = await workflow.execute(
            plan_path=plan_path,
            output_dir=output_dir,
            context=context
        )
        # Extract main execution result from build_refactored (final refactored code)
        main_result = workflow_result.get("build_refactored", workflow_result)
        return main_result, "PROD"
        
    else:
        # Direct orchestrator execution (backward compatibility)
        orchestrator = Orchestrator()
        try:
            main_result = await orchestrator.execute_plan(
                plan_path=plan_path,
                output_dir=output_dir,
                context=context
            )
            await orchestrator.close()
            return main_result, "DIRECT"
        except ExecutionError as e:
            await orchestrator.close()
            raise HTTPException(status_code=400, detail=str(e))


def _extract_execution_result(main_result: Dict[str, Any]) -> Tuple[Plan, Dict[str, Any], Dict[str, Any], bool]:
    """
    Extract plan, metrics, results, and success from execution result.
    
    Args:
        main_result: Result dictionary from workflow/orchestrator
        
    Returns:
        Tuple of (plan, metrics, results_dict, success)
        
    Raises:
        HTTPException: If result format is invalid
    """
    if not isinstance(main_result, dict):
        raise HTTPException(
            status_code=500,
            detail="Unexpected result format from workflow/orchestrator"
        )
    
    plan = main_result.get("plan")
    metrics = main_result.get("metrics")
    results_dict = main_result.get("results", {})
    success = main_result.get("success", True)
    
    if not plan:
        raise HTTPException(
            status_code=500,
            detail="Plan not found in execution result"
        )
    
    return plan, metrics, results_dict, success


def _build_response_metrics(metrics: Any, workflow_used: str) -> Dict[str, Any]:
    """
    Build response metrics dictionary.
    
    Args:
        metrics: PlanMetrics object or None
        workflow_used: Workflow used for execution
        
    Returns:
        Dictionary with metrics for response
    """
    return {
        "total_steps": metrics.total_steps if metrics else 0,
        "successful_steps": metrics.successful_steps if metrics else 0,
        "failed_steps": metrics.failed_steps if metrics else 0,
        "total_cost": metrics.total_cost_usd if metrics else 0.0,
        "total_tokens": metrics.total_tokens_used if metrics else 0,
        "success_rate": metrics.success_rate if metrics else 0.0,
        "workflow": workflow_used
    }


def _format_step_result(res: Any) -> Dict[str, Any]:
    """
    Format a single step result for API response.
    
    Args:
        res: StepResult object or dict
        
    Returns:
        Formatted dictionary with step result data
    """
    return {
        "success": res.success if hasattr(res, 'success') else True,
        "output": (
            (res.output[:500] + "..." if len(res.output) > 500 else res.output)
            if hasattr(res, 'output') else str(res)
        ),
        "tokens": res.tokens_used if hasattr(res, 'tokens_used') else 0,
        "cost": res.cost_usd if hasattr(res, 'cost_usd') else 0.0
    }


@app.post("/execute", response_model=ExecutePlanResponse)
async def execute_plan(request: ExecutePlanRequest):
    """
    Execute a plan and return results.
    
    Supports both plan_path (file path) and plan_json (direct JSON object).
    Can use PROTO or PROD workflow, or direct orchestrator execution.
    
    Args:
        request: ExecutePlanRequest with plan_path or plan_json, workflow, etc.
        
    Returns:
        ExecutePlanResponse with execution results and metrics
        
    Raises:
        HTTPException: If validation fails or execution errors occur
    """
    temp_file = None
    
    try:
        # Validate request
        _validate_request(request)
        
        # Resolve plan path (from plan_path or plan_json)
        plan_path, temp_file = _resolve_plan_path(request)
        
        # Prepare output directory
        output_dir = Path(request.output_dir) if request.output_dir else settings.output_dir
        logger.info(f"API: Executing plan {plan_path} with workflow: {request.workflow}")
        
        # Execute using workflow or orchestrator
        main_result, workflow_used = await _execute_with_workflow(
            plan_path=plan_path,
            workflow_type=request.workflow or "DIRECT",
            output_dir=output_dir,
            context=request.context
        )
        
        # Extract execution results
        plan, metrics, results_dict, success = _extract_execution_result(main_result)
        
        # Build response
        response_metrics = _build_response_metrics(metrics, workflow_used)
        
        return ExecutePlanResponse(
            success=success,
            task_id=plan.task_id,
            results={
                step_id: _format_step_result(res)
                for step_id, res in results_dict.items()
            },
            metrics=response_metrics,
            output_dir=str(output_dir),
            message=f"Plan executed successfully using {workflow_used} workflow"
        )
        
    except HTTPException:
        raise
    except PlanValidationError as e:
        raise HTTPException(status_code=400, detail=f"Plan validation failed: {e}")
    except ExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("API error")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file if created
        if temp_file and Path(temp_file.name).exists():
            try:
                Path(temp_file.name).unlink()
                logger.info(f"API: Cleaned up temporary file: {temp_file.name}")
            except Exception as e:
                logger.warning(f"API: Failed to clean up temporary file {temp_file.name}: {e}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "AetherFlow"}


def _get_minimal_genome() -> Dict[str, Any]:
    """
    Genome minimal en mode construction : pas de fichier, pas de génération OpenAPI.
    Permet au Studio d'afficher au moins /health et /studio/genome.
    """
    from datetime import datetime, timezone
    return {
        "metadata": {
            "intent": "construction",
            "version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "minimal_fallback",
        },
        "topology": ["Brainstorm", "Back", "Front", "Deploy"],
        "endpoints": [
            {"method": "GET", "path": "/health", "x_ui_hint": "status", "summary": "Health"},
            {"method": "GET", "path": "/studio/genome", "x_ui_hint": "generic", "summary": "Get Genome"},
            {"method": "POST", "path": "/execute", "x_ui_hint": "form", "summary": "Execute Plan"},
            {"method": "GET", "path": "/", "x_ui_hint": "generic", "summary": "Index"},
        ],
        "schema_definitions": {},
    }


@app.get("/studio/genome")
async def get_studio_genome(path: Optional[str] = None):
    """
    Return the Studio genome JSON (homeos_genome.json).
    Query param path (optional): path to genome JSON file.
    Default: settings.output_dir / "studio" / "homeos_genome.json".
    If file is missing: try generate_genome(); if that fails, return minimal genome (mode construction).
    Never returns 500: falls back to minimal genome on any error.
    """
    try:
        output_dir = getattr(settings, "output_dir", None)
        if not output_dir:
            return JSONResponse(content=_get_minimal_genome(), media_type="application/json")
        if path:
            genome_path = Path(path)
        else:
            genome_path = Path(output_dir) / "studio" / "homeos_genome.json"
        if not genome_path.exists():
            try:
                from .core.genome_generator import generate_genome
                generate_genome(output_path=genome_path)
            except Exception as e:
                logger.warning(f"Genome generation failed: {e}, serving minimal genome (construction mode)")
                return JSONResponse(content=_get_minimal_genome(), media_type="application/json")
        if not genome_path.exists():
            return JSONResponse(content=_get_minimal_genome(), media_type="application/json")
        data = json.loads(genome_path.read_text(encoding="utf-8"))
        return JSONResponse(content=data, media_type="application/json")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Genome serve failed: {e}, returning minimal genome")
        return JSONResponse(content=_get_minimal_genome(), media_type="application/json")


# Sullivan Kernel API endpoints
class SearchComponentRequest(BaseModel):
    """Request to search for a component."""
    intent: str
    user_id: str = "default_user"


class SearchComponentResponse(BaseModel):
    """Response from component search."""
    success: bool
    component: Optional[Dict[str, Any]] = None
    found_in: Optional[str] = None  # "local_cache", "elite_library", or "generated"
    message: str


@app.post("/sullivan/search", response_model=SearchComponentResponse)
async def search_component(request: SearchComponentRequest):
    """
    Search for a component using Sullivan Kernel.
    
    Args:
        request: SearchComponentRequest with intent and user_id
        
    Returns:
        SearchComponentResponse with component details
    """
    try:
        registry = ComponentRegistry()
        component = await registry.get_or_generate(
            intent=request.intent,
            user_id=request.user_id
        )
        
        # Determine where component was found
        found_in = "generated"  # Default
        local_component = registry.local_cache.find_similar(request.intent, request.user_id)
        if local_component and local_component.sullivan_score > 70:
            found_in = "local_cache"
        else:
            elite_component = registry.elite_library.find_similar(request.intent)
            if elite_component:
                found_in = "elite_library"
        
        return SearchComponentResponse(
            success=True,
            component={
                "name": component.name,
                "sullivan_score": component.sullivan_score,
                "performance_score": component.performance_score,
                "accessibility_score": component.accessibility_score,
                "ecology_score": component.ecology_score,
                "popularity_score": component.popularity_score,
                "validation_score": component.validation_score,
                "size_kb": component.size_kb,
                "created_at": component.created_at.isoformat(),
                "user_id": component.user_id
            },
            found_in=found_in,
            message=f"Component found in {found_in}"
        )
    except Exception as e:
        logger.error(f"Sullivan search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sullivan/components")
async def list_components(user_id: Optional[str] = None):
    """
    List available components from LocalCache and EliteLibrary.
    
    Args:
        user_id: Optional user ID to filter local cache
        
    Returns:
        Dictionary with components from both sources
    """
    try:
        registry = ComponentRegistry()
        
        result = {
            "local_cache": [],
            "elite_library": []
        }
        
        # List local cache components
        if user_id:
            cache_dir = registry.local_cache.cache_dir / user_id
            if cache_dir.exists():
                for file in cache_dir.glob("*.json"):
                    try:
                        import json
                        with open(file, 'r') as f:
                            component_data = json.load(f)
                            result["local_cache"].append(component_data)
                    except Exception as e:
                        logger.warning(f"Failed to load component from {file}: {e}")
        
        # List elite library components
        elite_dir = registry.elite_library.path
        if elite_dir.exists():
            for file in elite_dir.glob("*.json"):
                try:
                    import json
                    with open(file, 'r') as f:
                        component_data = json.load(f)
                        result["elite_library"].append(component_data)
                except Exception as e:
                    logger.warning(f"Failed to load component from {file}: {e}")
        
        return result
    except Exception as e:
        logger.error(f"Sullivan list components failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files for frontend
_root = Path(__file__).resolve().parent.parent.parent
frontend_path = _root / "Frontend"
svelte_build_path = _root / "frontend-svelte" / "build"
studio_index_path = _root / "output" / "studio" / "studio_index.html"

# Route "/" : Studio > Svelte build > Frontend > page d'accueil API (jamais 404)
@app.get("/")
async def serve_index():
    """Serve la page d'accueil (Studio, Svelte, Frontend) ou une landing API."""
    from fastapi.responses import HTMLResponse
    if studio_index_path.exists():
        return FileResponse(studio_index_path)
    if (svelte_build_path / "index.html").exists():
        return FileResponse(svelte_build_path / "index.html")
    if (frontend_path / "index.html").exists():
        return FileResponse(frontend_path / "index.html")
    # Aucun index trouvé : page d'accueil API (200, pas 404)
    return HTMLResponse(
        """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AetherFlow API</title></head>
<body>
<h1>AetherFlow API</h1>
<ul>
<li><a href="/health">/health</a></li>
<li><a href="/studio/genome">/studio/genome</a></li>
<li><a href="/studio">/studio</a> (HTMX - Parcours UX Sullivan)</li>
</ul>
<p>Frontend Svelte : <code>cd frontend-svelte && npm run dev</code> puis <a href="http://localhost:5173/studio">http://localhost:5173/studio</a>.</p>
</body></html>""",
        status_code=200,
    )

# Montages Svelte si présent
_app_dir = svelte_build_path / "_app"
if _app_dir.exists():
    app.mount("/_app", StaticFiles(directory=str(_app_dir)), name="svelte_app")

# Routes SvelteKit (build/studio/, build/components/) — évite 404 sur accès direct
def _serve_svelte_route(path: str) -> Optional[FileResponse]:
    """Serve la page Svelte si elle existe (studio, components)."""
    if not svelte_build_path.exists():
        return None
    base = path.lstrip("/").split("/")[0]
    # trailingSlash: ignore → studio.html, components.html | always → studio/index.html
    for candidate in [svelte_build_path / f"{base}.html", svelte_build_path / base / "index.html"]:
        if candidate.exists():
            return FileResponse(candidate)
    return None


@app.get("/studio")
@app.get("/studio/")
async def serve_studio_page(
    request: Request,
    step: int = 1,
    layout: Optional[str] = None
):
    """
    Studio Sullivan — Layout HomeOS unifié (4 tabs + sidebar).
    
    Args:
        step: Étape du parcours (1-9). Défaut: 1
        layout: Layout optionnel (non utilisé actuellement)
    """
    from fastapi.templating import Jinja2Templates
    templates_dir = Path(__file__).resolve().parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # Validation step 1-9 avec fallback
    if step < 1 or step > 9:
        step = 1
    
    # TOUJOURS studio_homeos.html (layout unifié)
    return templates.TemplateResponse(
        "studio_homeos.html", 
        {"request": request, "step": step, "layout": layout}
    )


@app.get("/homeos")
@app.get("/homeos/")
async def serve_homeos_page(request: Request):
    """Redirige vers /studio (layout unifié)."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/studio", status_code=302)


@app.get("/components")
@app.get("/components/")
async def serve_components_page():
    """Sert la page Components (galerie Svelte)."""
    if res := _serve_svelte_route("components"):
        return res
    raise HTTPException(
        status_code=404,
        detail="Components: run 'cd frontend-svelte && npm run build' then ./start_api.sh",
    )

# Frontend assets (css, js) when Frontend exists
# NOTE: /studio.html supprimé - utiliser /studio (HTMX) à la place
if frontend_path.exists():

    if (frontend_path / "css").exists():
        app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
    if (frontend_path / "js").exists():
        app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")


# Route ARBITER Component Gallery
@app.get("/arbiter-showcase", response_class=HTMLResponse)
async def serve_arbiter_showcase():
    """Sert la page galerie des composants ARBITER."""
    showcase_path = frontend_path / "arbiter-showcase.html"
    if showcase_path.exists():
        return HTMLResponse(content=showcase_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="arbiter-showcase.html not found")


# Route DaisyUI Component Gallery
@app.get("/daisy-showcase", response_class=HTMLResponse)
async def serve_daisy_showcase():
    """Sert la page galerie des composants DaisyUI."""
    showcase_path = frontend_path / "daisy-showcase.html"
    if showcase_path.exists():
        return HTMLResponse(content=showcase_path.read_text(encoding='utf-8'))
    raise HTTPException(status_code=404, detail="daisy-showcase.html not found")


# Sullivan DevMode endpoint
class DevAnalyzeRequest(BaseModel):
    """Request for Sullivan DevMode analysis."""
    backend_path: str
    output_path: Optional[str] = None
    analyze_only: bool = False
    non_interactive: bool = False


class DevAnalyzeResponse(BaseModel):
    """Response from Sullivan DevMode analysis."""
    success: bool
    global_function: Optional[Dict[str, Any]] = None
    ui_intent: Optional[Dict[str, Any]] = None
    frontend_structure: Optional[Dict[str, Any]] = None
    message: str


@app.post("/sullivan/dev/analyze", response_model=DevAnalyzeResponse)
async def sullivan_dev_analyze(request: DevAnalyzeRequest):
    """
    Analyze backend and generate frontend using Sullivan DevMode.
    
    Args:
        request: DevAnalyzeRequest with backend_path and options
        
    Returns:
        DevAnalyzeResponse with analysis results
    """
    try:
        from .sullivan.modes.dev_mode import DevMode
        
        dev_mode = DevMode(
            backend_path=Path(request.backend_path),
            output_path=Path(request.output_path) if request.output_path else None,
            analyze_only=request.analyze_only,
            non_interactive=request.non_interactive
        )
        
        result = await dev_mode.run()
        
        return DevAnalyzeResponse(
            success=result["success"],
            global_function=result.get("global_function"),
            ui_intent=result.get("ui_intent"),
            frontend_structure=result.get("frontend_structure"),
            message=result.get("message", "Analysis completed")
        )
        
    except Exception as e:
        logger.error(f"Sullivan DevMode API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Sullivan DevMode failed: {str(e)}"
        )


# Sullivan DesignerMode endpoint
class DesignerAnalyzeRequest(BaseModel):
    """Request for Sullivan DesignerMode analysis."""
    design_path: str
    output_path: Optional[str] = None
    non_interactive: bool = False


class DesignerAnalyzeResponse(BaseModel):
    """Response from Sullivan DesignerMode analysis."""
    success: bool
    design_structure: Optional[Dict[str, Any]] = None
    matched_patterns: Optional[List[Dict[str, Any]]] = None
    frontend_structure: Optional[Dict[str, Any]] = None
    message: str


@app.post("/sullivan/designer/analyze", response_model=DesignerAnalyzeResponse)
async def sullivan_designer_analyze(request: DesignerAnalyzeRequest):
    """
    Analyze design and generate frontend using Sullivan DesignerMode.
    
    Args:
        request: DesignerAnalyzeRequest with design_path and options
        
    Returns:
        DesignerAnalyzeResponse with analysis results
    """
    try:
        from .sullivan.modes.designer_mode import DesignerMode
        
        designer_mode = DesignerMode(
            design_path=Path(request.design_path),
            output_path=Path(request.output_path) if request.output_path else None,
            non_interactive=request.non_interactive
        )
        
        result = await designer_mode.run()
        
        return DesignerAnalyzeResponse(
            success=result["success"],
            design_structure=result.get("design_structure"),
            matched_patterns=result.get("matched_patterns"),
            frontend_structure=result.get("frontend_structure"),
            message=result.get("message", "Analysis completed")
        )
        
    except Exception as e:
        logger.error(f"Sullivan DesignerMode API error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Sullivan DesignerMode failed: {str(e)}"
        )


# Sullivan DesignerMode: upload template (image) for analysis
@app.post("/sullivan/designer/upload", response_model=DesignerAnalyzeResponse)
async def sullivan_designer_upload(file: UploadFile = File(...)):
    """
    Upload a design template (PNG, JPG, JPEG, SVG) for Sullivan DesignerMode analysis.
    Saves file temporarily, runs DesignerMode (Gemini), returns analysis result.
    """
    allowed = {".png", ".jpg", ".jpeg", ".svg"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed)}"
        )
    try:
        import tempfile
        from .sullivan.modes.designer_mode import DesignerMode

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            designer_mode = DesignerMode(
                design_path=tmp_path,
                output_path=None,
                non_interactive=True
            )
            result = await designer_mode.run()
            return DesignerAnalyzeResponse(
                success=result["success"],
                design_structure=result.get("design_structure"),
                matched_patterns=result.get("matched_patterns"),
                frontend_structure=result.get("frontend_structure"),
                message=result.get("message", "Analysis completed")
            )
        finally:
            tmp_path.unlink(missing_ok=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sullivan DesignerMode upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Sullivan DesignerMode upload failed: {str(e)}"
        )


# Sullivan Preview endpoints
from fastapi.responses import HTMLResponse


@app.get("/sullivan/preview/{component_id}", response_class=HTMLResponse)
async def preview_component(component_id: str, user_id: str = "default_user"):
    """
    Prévisualise un composant spécifique.
    
    Args:
        component_id: Identifiant du composant (nom sans préfixe component_)
        user_id: Identifiant utilisateur (query param, défaut: default_user)
        
    Returns:
        HTMLResponse avec prévisualisation du composant
    """
    try:
        from .sullivan.registry import ComponentRegistry
        from .sullivan.preview.preview_generator import generate_preview_html
        
        registry = ComponentRegistry()
        
        # Chercher composant dans LocalCache puis EliteLibrary
        component = None
        
        # Essayer LocalCache
        component = registry.local_cache.load(component_id, user_id)
        if not component:
            # Essayer EliteLibrary
            component = registry.elite_library.find_similar(component_id)
        
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"Component '{component_id}' not found in LocalCache or EliteLibrary"
            )
        
        # Générer HTML de prévisualisation
        base_url = "http://localhost:8000"  # TODO: Récupérer depuis request
        preview_html = generate_preview_html(component, base_url)
        
        return HTMLResponse(content=preview_html, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview for component '{component_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate preview: {str(e)}"
        )


@app.get("/sullivan/preview", response_class=HTMLResponse)
async def preview_list(user_id: str = "default_user"):
    """
    Liste tous les composants avec liens vers leurs prévisualisations.
    
    Args:
        user_id: Identifiant utilisateur (query param, défaut: default_user)
        
    Returns:
        HTMLResponse avec liste de composants
    """
    try:
        from .sullivan.registry import ComponentRegistry
        from .sullivan.preview.preview_generator import generate_preview_page
        
        registry = ComponentRegistry()
        
        # Récupérer tous les composants depuis LocalCache et EliteLibrary
        components = []
        
        # Charger depuis LocalCache
        user_cache_dir = registry.local_cache.cache_dir / user_id
        if user_cache_dir.exists():
            for file in user_cache_dir.glob("*.json"):
                try:
                    component = registry.local_cache.load(file.stem, user_id)
                    if component:
                        components.append(component)
                except Exception as e:
                    logger.debug(f"Error loading component from {file}: {e}")
        
        # Charger depuis EliteLibrary
        elite_components = registry.elite_library.list_all()
        components.extend(elite_components)
        
        # Dédupliquer par nom
        seen_names = set()
        unique_components = []
        for comp in components:
            if comp.name not in seen_names:
                seen_names.add(comp.name)
                unique_components.append(comp)
        
        # Générer page de liste (vide ou avec composants)
        base_url = "http://localhost:8000"  # TODO: Récupérer depuis request
        try:
            list_html = generate_preview_page(unique_components, base_url)
        except Exception as gen_e:
            logger.warning(f"generate_preview_page failed: {gen_e}, returning fallback")
            list_html = "<html><body><p>No components yet.</p></body></html>"
        return HTMLResponse(content=list_html, status_code=200)
        
    except Exception as e:
        logger.error(f"Error generating preview list: {e}", exc_info=True)
        return HTMLResponse(
            content="<html><body><p>No components yet.</p></body></html>",
            status_code=200
        )


@app.get("/sullivan/preview/{component_id}/render", response_class=HTMLResponse)
async def render_component(component_id: str, user_id: str = "default_user"):
    """
    Rend le composant lui-même (HTML/CSS/JS) pour affichage dans iframe.
    
    Args:
        component_id: Identifiant du composant
        user_id: Identifiant utilisateur (query param, défaut: default_user)
        
    Returns:
        HTMLResponse avec HTML/CSS/JS du composant
    """
    try:
        from .sullivan.registry import ComponentRegistry
        
        registry = ComponentRegistry()
        
        # Chercher composant
        component = registry.local_cache.load(component_id, user_id)
        if not component:
            component = registry.elite_library.find_similar(component_id)
        
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"Component '{component_id}' not found"
            )
        
        # Charger fichiers HTML/CSS/JS depuis cache
        user_cache_dir = registry.local_cache.cache_dir / user_id
        component_dir = user_cache_dir / component_id
        
        html_content = ""
        css_content = ""
        js_content = ""
        
        if component_dir.exists():
            html_file = component_dir / "component.html"
            css_file = component_dir / "component.css"
            js_file = component_dir / "component.js"
            
            if html_file.exists():
                html_content = html_file.read_text(encoding='utf-8')
            if css_file.exists():
                css_content = css_file.read_text(encoding='utf-8')
            if js_file.exists():
                js_content = js_file.read_text(encoding='utf-8')
        
        # Générer HTML complet du composant
        component_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component.name}</title>
    <style>
        {css_content}
    </style>
</head>
<body>
    {html_content}
    <script>
        {js_content}
    </script>
</body>
</html>'''
        
        return HTMLResponse(content=component_html, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering component '{component_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to render component: {str(e)}"
        )


def run_api(host: str = "127.0.0.1", port: int = 8000):
    """Run the API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api()


# Route pour servir le genome_inferred_complete.json
@app.get("/studio/genome/inferred")
async def get_genome_inferred():
    """Sert le genome_inferred_complete.json depuis la racine du projet."""
    genome_path = Path("/Users/francois-jeandazin/AETHERFLOW/genome_inferred_complete.json")
    if genome_path.exists():
        with open(genome_path, 'r') as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Genome file not found")
