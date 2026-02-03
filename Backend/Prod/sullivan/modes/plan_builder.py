"""
PlanBuilder - Sullivan comme architecte.

Transforme un brief en plan structuré (backend + frontend).
Avec monitoring en temps réel et dialogue interactif.
"""

import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from ...models.gemini_client import GeminiClient
from ...models.groq_client import GroqClient
from ...models.plan_reader import Plan, Step
from ...models.execution_monitor import ExecutionMonitor, StepStatus
from ...config.settings import settings


@dataclass
class PlanStep:
    """Étape de plan enrichie pour Sullivan."""
    id: str
    description: str
    type: str  # "backend", "frontend", "api", "component", "integration"
    complexity: float
    estimated_tokens: int
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    validation_prompt: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "complexity": self.complexity,
            "estimated_tokens": self.estimated_tokens,
            "dependencies": self.dependencies,
            "context": self.context,
            "validation_criteria": [self.validation_prompt] if self.validation_prompt else []
        }


@dataclass
class SullivanPlan:
    """Plan généré par Sullivan."""
    task_id: str
    description: str
    brief: str
    steps: List[PlanStep]
    metadata: Dict[str, Any]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "metadata": {
                **self.metadata,
                "brief": self.brief,
                "generated_at": self.generated_at,
            }
        }
    
    def to_plan_reader_format(self) -> Dict[str, Any]:
        """Convertit au format attendu par PlanReader."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "metadata": self.metadata
        }


class PlanBuilder:
    """
    Sullivan PlanBuilder - De l'intention au plan structuré.
    
    Usage:
        builder = PlanBuilder()
        plan = await builder.create_plan_from_brief(
            "Crée un dashboard avec graphiques et authentification",
            interactive=True  # Mode dialogue
        )
    """
    
    def __init__(self):
        # Gemini en priorité (rate limit quasi illimité)
        # Fallback: DeepSeek, puis Groq si nécessaire
        self.gemini = GeminiClient(execution_mode="BUILD")
        self.groq = GroqClient()
        self.console = Console()
        self.output_dir = Path(settings.output_dir) / "plans"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_plan_from_brief(
        self,
        brief: str,
        interactive: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> SullivanPlan:
        """
        Transforme un brief utilisateur en plan structuré.
        
        Args:
            brief: Description en langage naturel
            interactive: Si True, dialogue avec l'utilisateur pour valider/ajuster
            context: Contexte additionnel (genome, préférences, etc.)
            
        Returns:
            Plan Sullivan complet
        """
        self.console.print(f"\n[bold cyan]🎯 PlanBuilder - Analyse du brief[/]")
        self.console.print(f"[dim]{brief}[/]\n")
        
        # 1. Analyse intelligente du brief
        analysis = await self._analyze_brief(brief, context)
        
        self.console.print(f"[green]✓ Analyse complète[/]")
        self.console.print(f"  Type: {analysis.get('project_type', 'mixed')}")
        self.console.print(f"  Backend: {'✓' if analysis.get('needs_backend') else '✗'}")
        self.console.print(f"  Frontend: {'✓' if analysis.get('needs_frontend') else '✗'}")
        self.console.print(f"  Complexité: {analysis.get('complexity', 'medium')}\n")
        
        # 2. Mode interactif - Affiner avec l'utilisateur
        if interactive:
            analysis = await self._interactive_refinement(brief, analysis)
        
        # 3. Générer les étapes
        steps = await self._generate_steps(analysis, context)
        
        # 4. Créer le plan
        plan = SullivanPlan(
            task_id=f"sullivan_plan_{int(time.time())}",
            description=analysis.get('project_description', brief[:100]),
            brief=brief,
            steps=steps,
            metadata={
                "planner": "sullivan_plan_builder",
                "project_type": analysis.get('project_type', 'mixed'),
                "complexity": analysis.get('complexity', 'medium'),
                "features": analysis.get('features', []),
                "tech_stack": analysis.get('tech_stack', {}),
            }
        )
        
        # 5. Afficher le résumé
        self._display_plan_summary(plan)
        
        # 6. Sauvegarder
        plan_path = self._save_plan(plan)
        self.console.print(f"\n[green]✓ Plan sauvegardé:[/] [cyan]{plan_path}[/]")
        
        return plan
    
    async def _analyze_brief(self, brief: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyse le brief avec Gemini pour comprendre les besoins."""
        
        context_str = ""
        if context and context.get('genome'):
            genome = context['genome']
            endpoints = genome.get('endpoints', [])
            context_str = f"\nContexte - API existante: {len(endpoints)} endpoints disponibles"
        
        prompt = f"""Tu es Sullivan, architecte logiciel senior. Analyse ce brief et extrait la structure technique.

BRIEF: "{brief}"{context_str}

Réponds UNIQUEMENT en JSON:
```json
{{
  "project_type": "backend|frontend|fullstack|api|component",
  "project_description": "Description technique 20 mots",
  "needs_backend": true|false,
  "needs_frontend": true|false,
  "needs_api": true|false,
  "needs_auth": true|false,
  "needs_database": true|false,
  "complexity": "low|medium|high",
  "features": ["feature1", "feature2"],
  "tech_stack": {{
    "backend": "FastAPI|Flask|Django|None",
    "frontend": "HTML/Tailwind|React|Vue|None", 
    "database": "SQLite|PostgreSQL|None"
  }},
  "components": ["header", "form", "dashboard", "chart"],
  "pages": ["login", "home", "dashboard"],
  "entities": ["User", "Project", "Task"],
  "estimated_steps": 5
}}
```

RÈGLES:
- Si mention de "page", "bouton", "interface" → needs_frontend = true
- Si mention de "API", "endpoint", "base de données" → needs_backend = true
- Si les deux → project_type = "fullstack"
"""
        
        result = await self.gemini.generate(prompt=prompt, max_tokens=2048)
        
        if not result.success or not result.code:
            # Fallback Groq
            result = await self.groq.generate(prompt=prompt, max_tokens=2048)
        
        try:
            code = result.code or "{}"
            if "```json" in code:
                code = code.split("```json")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            return json.loads(code.strip())
        except Exception as e:
            logger.warning(f"Failed to parse analysis: {e}")
            return {
                "project_type": "mixed",
                "needs_backend": True,
                "needs_frontend": True,
                "complexity": "medium",
                "features": [],
                "tech_stack": {"backend": "FastAPI", "frontend": "HTML/Tailwind"},
            }
    
    async def _interactive_refinement(
        self,
        brief: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dialogue avec l'utilisateur pour affiner le plan.
        """
        self.console.print("[bold cyan]💬 Affinage interactif[/]\n")
        
        # Question 1: Validation du type
        self.console.print(f"[dim]Je détecte un projet [cyan]{analysis['project_type']}[/].[/]")
        response = input("Correct ? [Y/n/modify]: ").strip().lower()
        
        if response == 'n':
            self.console.print("  Types: backend, frontend, fullstack, api, component")
            new_type = input("Type correct: ").strip()
            if new_type:
                analysis['project_type'] = new_type
        elif response == 'modify':
            # Mode modification détaillée
            self.console.print("\n[dim]Modification des paramètres:[/]")
            
            backend = input(f"  Backend nécessaire ? [Y/n] (actuel: {'Oui' if analysis.get('needs_backend') else 'Non'}): ").strip()
            if backend.lower() == 'n':
                analysis['needs_backend'] = False
            elif backend.lower() == 'y':
                analysis['needs_backend'] = True
            
            frontend = input(f"  Frontend nécessaire ? [Y/n] (actuel: {'Oui' if analysis.get('needs_frontend') else 'Non'}): ").strip()
            if frontend.lower() == 'n':
                analysis['needs_frontend'] = False
            elif frontend.lower() == 'y':
                analysis['needs_frontend'] = True
        
        # Question 2: Features prioritaires
        if analysis.get('features'):
            self.console.print(f"\n[dim]Features détectées: {', '.join(analysis['features'])}[/]")
            add_features = input("Features supplémentaires ? (séparées par virgule, ou Enter): ").strip()
            if add_features:
                analysis['features'].extend([f.strip() for f in add_features.split(',')])
        
        # Question 3: Complexité
        self.console.print(f"\n[dim]Complexité estimée: [cyan]{analysis.get('complexity', 'medium')}[/][/]")
        complexity = input("Modifier ? [low/medium/high/Enter]: ").strip()
        if complexity in ['low', 'medium', 'high']:
            analysis['complexity'] = complexity
        
        self.console.print("[green]✓ Configuration validée[/]\n")
        return analysis
    
    async def _generate_steps(
        self,
        analysis: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> List[PlanStep]:
        """Génère les étapes détaillées du plan."""
        
        steps = []
        step_counter = 1
        
        # Étape 0: Setup/Config (si nécessaire)
        if analysis.get('needs_backend') and analysis.get('needs_frontend'):
            steps.append(PlanStep(
                id=f"step_{step_counter:02d}",
                description="Configuration projet - structure dossiers et dépendances",
                type="setup",
                complexity=0.3,
                estimated_tokens=500,
                dependencies=[],
                validation_prompt="Structure de projet propre avec séparation backend/frontend"
            ))
            step_counter += 1
        
        # Étape 1: Backend - Modèles/Schemas
        if analysis.get('needs_backend'):
            entities = analysis.get('entities', ['Entity'])
            for entity in entities:
                steps.append(PlanStep(
                    id=f"step_{step_counter:02d}",
                    description=f"Backend - Modèle et schema {entity}",
                    type="backend",
                    complexity=0.5,
                    estimated_tokens=800,
                    dependencies=[s.id for s in steps if s.type == "setup"],
                    context={"entity": entity, "language": "python"},
                    validation_prompt=f"Modèle {entity} avec Pydantic, validation et types"
                ))
                step_counter += 1
            
            # Étape 2: Backend - Endpoints API
            steps.append(PlanStep(
                id=f"step_{step_counter:02d}",
                description="Backend - Endpoints API CRUD",
                type="api",
                complexity=0.7,
                estimated_tokens=1200,
                dependencies=[s.id for s in steps if s.type == "backend"],
                context={"framework": analysis.get('tech_stack', {}).get('backend', 'FastAPI')},
                validation_prompt="Endpoints RESTful avec documentation OpenAPI"
            ))
            step_counter += 1
            
            # Étape 3: Backend - Auth (si nécessaire)
            if analysis.get('needs_auth'):
                steps.append(PlanStep(
                    id=f"step_{step_counter:02d}",
                    description="Backend - Système d'authentification JWT",
                    type="backend",
                    complexity=0.8,
                    estimated_tokens=1500,
                    dependencies=[f"step_{step_counter-1:02d}"],
                    validation_prompt="Auth sécurisée avec JWT, hash passwords, protection routes"
                ))
                step_counter += 1
        
        # Étape 4: Frontend - Layout/Structure
        if analysis.get('needs_frontend'):
            steps.append(PlanStep(
                id=f"step_{step_counter:02d}",
                description="Frontend - Layout de base et navigation",
                type="frontend",
                complexity=0.4,
                estimated_tokens=600,
                dependencies=[s.id for s in steps if s.type == "setup"],
                context={"tech": analysis.get('tech_stack', {}).get('frontend', 'HTML/Tailwind')},
                validation_prompt="Layout responsive avec navigation fonctionnelle"
            ))
            step_counter += 1
            
            # Étape 5: Frontend - Pages
            pages = analysis.get('pages', ['index'])
            for i, page in enumerate(pages):
                deps = [f"step_{step_counter-1:02d}"]
                # Si auth nécessaire et ce n'est pas la page de login
                if analysis.get('needs_auth') and page != 'login':
                    # Trouver l'étape auth ou utiliser step_01
                    auth_steps = [s.id for s in steps if 'auth' in s.description.lower()]
                    auth_dep = auth_steps[0] if auth_steps else "step_01"
                    deps.append(auth_dep)
                
                steps.append(PlanStep(
                    id=f"step_{step_counter:02d}",
                    description=f"Frontend - Page {page}",
                    type="frontend",
                    complexity=0.6,
                    estimated_tokens=1000,
                    dependencies=deps,
                    context={"page": page, "requires_auth": analysis.get('needs_auth') and page != 'login'},
                    validation_prompt=f"Page {page} fonctionnelle avec appels API si nécessaire"
                ))
                step_counter += 1
            
            # Étape 6: Frontend - Composants
            components = analysis.get('components', [])
            for component in components:
                if component not in ['page', 'layout']:  # Éviter doublons
                    steps.append(PlanStep(
                        id=f"step_{step_counter:02d}",
                        description=f"Frontend - Composant {component}",
                        type="component",
                        complexity=0.5,
                        estimated_tokens=800,
                        dependencies=[f"step_{step_counter-len(pages)-1:02d}"],
                        context={"component_type": component},
                        validation_prompt=f"Composant {component} réutilisable et accessible"
                    ))
                    step_counter += 1
        
        # Étape finale: Intégration
        if analysis.get('needs_backend') and analysis.get('needs_frontend'):
            steps.append(PlanStep(
                id=f"step_{step_counter:02d}",
                description="Intégration - Câblage Frontend ↔ Backend",
                type="integration",
                complexity=0.7,
                estimated_tokens=1000,
                dependencies=[s.id for s in steps if s.type in ['api', 'frontend']],
                validation_prompt="Frontend communique correctement avec l'API"
            ))
            step_counter += 1
        
        return steps
    
    def _display_plan_summary(self, plan: SullivanPlan) -> None:
        """Affiche un résumé du plan généré."""
        self.console.print("\n" + "="*80)
        self.console.print(f"[bold cyan]📋 PLAN GÉNÉRÉ: {plan.description}[/]")
        self.console.print("="*80)
        
        table = Table(box=box.ROUNDED, show_header=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Type", style="yellow", width=12)
        table.add_column("Description", style="white", width=50)
        table.add_column("Complexity", width=10)
        table.add_column("Deps", style="dim", width=8)
        
        for i, step in enumerate(plan.steps, 1):
            type_color = {
                "setup": "dim",
                "backend": "blue",
                "api": "magenta",
                "frontend": "green",
                "component": "cyan",
                "integration": "yellow"
            }.get(step.type, "white")
            
            deps_str = ",".join([d.replace("step_", "") for d in step.dependencies[:2]])
            if len(step.dependencies) > 2:
                deps_str += "..."
            
            table.add_row(
                str(i),
                f"[{type_color}]{step.type}[/{type_color}]",
                step.description,
                f"{step.complexity:.1f}",
                deps_str or "-"
            )
        
        self.console.print(table)
        
        # Stats
        backend_steps = len([s for s in plan.steps if s.type == "backend"])
        frontend_steps = len([s for s in plan.steps if s.type in ["frontend", "component"]])
        
        self.console.print(f"\n[dim]Total: {len(plan.steps)} étapes[/]")
        self.console.print(f"  [blue]Backend: {backend_steps}[/] | [green]Frontend: {frontend_steps}[/]")
        self.console.print("="*80 + "\n")
    
    def _save_plan(self, plan: SullivanPlan) -> Path:
        """Sauvegarde le plan sur disque."""
        plan_path = self.output_dir / f"{plan.task_id}.json"
        plan_path.write_text(
            json.dumps(plan.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return plan_path
    
    async def execute_plan_step_by_step(
        self,
        plan: SullivanPlan,
        interactive: bool = True
    ) -> Dict[str, Any]:
        """
        Exécute un plan étape par étape avec monitoring.
        
        Args:
            plan: Plan à exécuter
            interactive: Si True, demande validation à chaque étape
            
        Returns:
            Résultat de l'exécution
        """
        self.console.print(f"\n[bold cyan]🚀 Exécution du plan[/] [dim]{plan.task_id}[/]")
        self.console.print(f"[dim]{len(plan.steps)} étapes à exécuter[/]\n")
        
        # Initialiser le monitoring
        monitor = ExecutionMonitor(plan.description, len(plan.steps))
        for step in plan.steps:
            monitor.add_step(step.id, step.description, step.type, step.complexity)
        
        monitor.start_monitoring()
        
        results = {}
        
        try:
            # Grouper par niveau de dépendances
            execution_order = self._get_execution_order(plan.steps)
            
            for batch_idx, batch in enumerate(execution_order):
                for step in batch:
                    # Mode interactif - Demander validation
                    if interactive:
                        self.console.print(f"\n[bold]Étape:[/] {step.description}")
                        self.console.print(f"[dim]Type: {step.type} | Complexité: {step.complexity}[/]")
                        
                        response = input("Exécuter ? [Y/n/skip/quit]: ").strip().lower()
                        
                        if response == 'n':
                            self.console.print("  [yellow]Étape ignorée[/]")
                            monitor.complete_step(step.id, False, 0, 0, 0, "Skipped by user")
                            continue
                        elif response == 'skip':
                            self.console.print("  [yellow]Étape sautée[/]")
                            monitor.complete_step(step.id, False, 0, 0, 0, "Skipped")
                            continue
                        elif response == 'quit':
                            self.console.print("  [red]Exécution arrêtée[/]")
                            break
                    
                    # Exécuter l'étape
                    start_time = time.time()
                    monitor.start_step(step.id, "groq")
                    
                    try:
                        result = await self._execute_step(step, plan)
                        elapsed = (time.time() - start_time) * 1000
                        
                        monitor.complete_step(
                            step.id,
                            success=result.get('success', False),
                            execution_time_ms=elapsed,
                            tokens_used=result.get('tokens', 0),
                            cost_usd=result.get('cost', 0.0)
                        )
                        
                        results[step.id] = result
                        
                    except Exception as e:
                        elapsed = (time.time() - start_time) * 1000
                        monitor.complete_step(
                            step.id,
                            success=False,
                            execution_time_ms=elapsed,
                            tokens_used=0,
                            cost_usd=0.0,
                            error=str(e)
                        )
                        results[step.id] = {"success": False, "error": str(e)}
                        
                        if interactive:
                            cont = input("Continuer malgré l'erreur ? [Y/n]: ").strip().lower()
                            if cont == 'n':
                                break
            
            monitor.stop_monitoring()
            monitor.print_final_summary()
            
            return {
                "success": all(r.get('success') for r in results.values()),
                "plan_id": plan.task_id,
                "results": results,
                "total_steps": len(plan.steps),
                "completed_steps": len([r for r in results.values() if r.get('success')])
            }
            
        except Exception as e:
            monitor.stop_monitoring()
            self.console.print(f"[red]❌ Erreur: {e}[/]")
            return {"success": False, "error": str(e)}
    
    def _get_execution_order(self, steps: List[PlanStep]) -> List[List[PlanStep]]:
        """Organise les étapes par ordre d'exécution (respect des dépendances)."""
        step_map = {s.id: s for s in steps}
        in_degree = {s.id: len(s.dependencies) for s in steps}
        
        order = []
        remaining = set(s.id for s in steps)
        
        while remaining:
            ready = [step_map[sid] for sid in remaining if in_degree[sid] == 0]
            if not ready:
                raise ValueError("Dépendances circulaires détectées")
            
            order.append(ready)
            for step in ready:
                remaining.remove(step.id)
                for other in remaining:
                    if step.id in step_map[other].dependencies:
                        in_degree[other] -= 1
        
        return order
    
    async def _execute_step(self, step: PlanStep, plan: SullivanPlan) -> Dict[str, Any]:
        """Exécute une étape individuelle."""
        # Selon le type d'étape
        if step.type == "frontend" or step.type == "component":
            return await self._execute_frontend_step(step)
        elif step.type == "backend":
            return await self._execute_backend_step(step)
        else:
            # Par défaut, génération via LLM
            return await self._execute_llm_step(step)
    
    async def _execute_frontend_step(self, step: PlanStep) -> Dict[str, Any]:
        """Exécute une étape frontend (génération composant)."""
        from ...models.agent_router import AgentRouter
        from ...cache import PromptCache, SemanticCache
        
        description = step.description
        component_type = step.context.get('component_type', 'component')
        
        prompt = f"""Génère un composant {component_type} en HTML avec Tailwind CSS.

Description: {description}
Règles:
- Utilise UNIQUEMENT Tailwind CSS
- Responsive mobile-first
- Code propre et sémantique
- Retourne UNIQUEMENT le HTML
"""
        
        router = AgentRouter(
            prompt_cache=PromptCache(),
            semantic_cache=SemanticCache(),
            execution_mode="BUILD"
        )
        
        result = await router.route_and_generate(
            prompt=prompt,
            context_size=len(prompt),
            validation_level="fast"
        )
        
        return {
            "success": result.get('success', False),
            "code": result.get('code'),
            "tokens": result.get('tokens', {}).get('total', 0),
            "cost": result.get('cost_usd', 0)
        }
    
    async def _execute_backend_step(self, step: PlanStep) -> Dict[str, Any]:
        """Exécute une étape backend (génération Python)."""
        entity = step.context.get('entity', 'Model')
        
        prompt = f"""Génère un modèle Pydantic pour {entity}.

Inclut:
- Champs avec types Python
- Validations Pydantic
- Docstrings
- Méthodes utilitaires si pertinent

Retourne UNIQUEMENT le code Python.
"""
        
        result = await self.groq.generate(prompt=prompt, max_tokens=2048)
        
        return {
            "success": result.success,
            "code": result.code,
            "tokens": 2048,  # Estimation
            "cost": 0.0001
        }
    
    async def _execute_llm_step(self, step: PlanStep) -> Dict[str, Any]:
        """Exécute une étape générique via LLM."""
        result = await self.groq.generate(
            prompt=f"Exécute cette tâche: {step.description}",
            max_tokens=step.estimated_tokens
        )
        
        return {
            "success": result.success,
            "output": result.code,
            "tokens": step.estimated_tokens,
            "cost": 0.0001
        }


__all__ = ["PlanBuilder", "SullivanPlan", "PlanStep"]
