"""
Tools - Système d'outils pour que Sullivan puisse AGIR, pas juste parler.

Exemples d'outils:
- generate_component: Générer un composant HTML
- analyze_design: Analyser une image de design
- modify_code: Modifier du code existant
- search_components: Chercher dans la librairie
- validate_structure: Valider la cohérence
"""

import json
import asyncio
import time
import re
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass
from pathlib import Path
from loguru import logger


# ===== HELPERS REGISTRY =====

REGISTRY_FILE = Path("/Users/francois-jeandazin/AETHERFLOW/output/components/registry.json")

def _load_registry() -> List[Dict[str, Any]]:
    """Charge le registre des composants."""
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return []
    return []

def _save_registry(registry: List[Dict[str, Any]]) -> None:
    """Sauvegarde le registre des composants."""
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


@dataclass
class ToolResult:
    """Résultat d'un appel d'outil."""
    success: bool
    content: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class Tool:
    """Définition d'un outil."""
    name: str
    description: str
    parameters: Dict[str, Any]  # Schema JSON des paramètres
    handler: Callable[..., Awaitable[ToolResult]]
    requires_confirmation: bool = False  # Pour actions destructives
    
    async def execute(self, **kwargs) -> ToolResult:
        """Exécute l'outil avec les paramètres donnés."""
        try:
            return await self.handler(**kwargs)
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {e}")
            return ToolResult(
                success=False,
                content=f"Erreur lors de l'exécution de {self.name}",
                error=str(e),
            )
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convertit en schema OpenAI Function Calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """
    Registre des outils disponibles pour Sullivan.
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._register_default_tools()
    
    def register(self, tool: Tool) -> None:
        """Enregistre un nouvel outil."""
        self._tools[tool.name] = tool
        logger.info(f"Tool registered: {tool.name}")
    
    def get(self, name: str) -> Optional[Tool]:
        """Récupère un outil par son nom."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """Liste tous les outils disponibles."""
        return list(self._tools.values())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Retourne les schemas pour le LLM."""
        return [tool.to_openai_schema() for tool in self._tools.values()]
    
    def _register_default_tools(self) -> None:
        """Enregistre les outils par défaut de Sullivan."""
        
        # Tool: analyze_design
        self.register(Tool(
            name="analyze_design",
            description="Analyse une image de design (PNG, JPG) et extrait sa structure",
            parameters={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Chemin vers l'image à analyser",
                    },
                    "extract_principles": {
                        "type": "boolean",
                        "description": "Extraire aussi les principes graphiques (couleurs, typo)",
                        "default": False,
                    },
                },
                "required": ["image_path"],
                "additionalProperties": True,
            },
            handler=self._analyze_design,
        ))
        
        # Tool: generate_component
        self.register(Tool(
            name="generate_component",
            description="Génère un composant HTML/CSS à partir d'une description",
            parameters={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Description du composant souhaité",
                    },
                    "component_type": {
                        "type": "string",
                        "enum": ["button", "card", "form", "modal", "navbar", "input", "list", "table"],
                        "description": "Type de composant",
                    },
                    "style": {
                        "type": "string",
                        "description": "Style visuel (minimal, brutalist, glassmorphism, etc.)",
                        "default": "minimal",
                    },
                },
                "required": ["description", "component_type"],
                "additionalProperties": True,
            },
            handler=self._generate_component,
        ))
        
        # Tool: search_components
        self.register(Tool(
            name="search_components",
            description="Cherche des composants dans la librairie Elite ou le cache local",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Recherche par mot-clé ou description",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["monitoring", "orchestrator", "gallery", "designer", "preview"],
                        "description": "Catégorie de composant",
                    },
                },
                "required": ["query"],
                "additionalProperties": True,
            },
            handler=self._search_components,
        ))
        
        # Tool: validate_genome
        self.register(Tool(
            name="validate_genome",
            description="Valide la cohérence du genome (homéostasie)",
            parameters={
                "type": "object",
                "properties": {
                    "genome_json": {
                        "type": "string",
                        "description": "JSON du genome à valider",
                    },
                },
                "required": ["genome_json"],
                "additionalProperties": True,
            },
            handler=self._validate_genome,
        ))
        
        # Tool: read_documentation
        self.register(Tool(
            name="read_documentation",
            description="Lit et analyse un fichier de documentation (MD, TXT, JSON). Paramètres: path (ou doc_path, file, file_path), section (optionnel)",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Chemin vers le fichier doc (ex: docs/02-sullivan/PRD_SULLIVAN.md)",
                    },
                    "doc_path": {
                        "type": "string",
                        "description": "Alternative à path",
                    },
                    "file": {
                        "type": "string",
                        "description": "Alternative à path",
                    },
                    "section": {
                        "type": "string",
                        "description": "Section spécifique à lire (optionnel, ex: '## Architecture')",
                        "default": None,
                    },
                },
                "additionalProperties": True,
            },
            handler=self._read_documentation,
        ))
        
        # Tool: analyze_codebase
        self.register(Tool(
            name="analyze_codebase",
            description="Analyse la structure de la codebase. Paramètres: path (ou target_path), analysis_type (structure, endpoints), depth (optionnel)",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Chemin à analyser (défaut: Backend/Prod)",
                    },
                    "target_path": {
                        "type": "string",
                        "description": "Alternative à path",
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["structure", "endpoints"],
                        "description": "Type d'analyse",
                        "default": "structure",
                    },
                    "depth": {
                        "type": "string",
                        "description": "Niveau d'analyse (basic, full)",
                    },
                },
                "additionalProperties": True,
            },
            handler=self._analyze_codebase,
        ))
        
        # Tool: search_in_code
        self.register(Tool(
            name="search_in_code",
            description="Recherche du texte ou patterns dans le codebase",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Texte ou pattern à rechercher",
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Pattern de fichiers (ex: '*.py', '*.md')",
                        "default": "*.py",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Nombre max de résultats",
                        "default": 10,
                    },
                },
                "required": ["query"],
                "additionalProperties": True,
            },
            handler=self._search_in_code,
        ))
        
        # Tool: get_step_guidance
        self.register(Tool(
            name="get_step_guidance",
            description="Donne des conseils pour l'étape actuelle du parcours UX (1-9)",
            parameters={
                "type": "object",
                "properties": {
                    "step": {
                        "type": "integer",
                        "description": "Numéro de l'étape (1-9)",
                        "minimum": 1,
                        "maximum": 9,
                    },
                },
                "required": ["step"],
                "additionalProperties": True,
            },
            handler=self._get_step_guidance,
        ))
        
        # Tool: refine_style
        self.register(Tool(
            name="refine_style",
            description="Affine le style d'un composant HTML existant",
            parameters={
                "type": "object",
                "properties": {
                    "html": {
                        "type": "string",
                        "description": "Code HTML à modifier",
                    },
                    "instruction": {
                        "type": "string",
                        "description": "Instruction de modification (ex: 'rendre plus arrondi')",
                    },
                },
                "required": ["html", "instruction"],
                "additionalProperties": True,
            },
            handler=self._refine_style,
        ))

        # ===== OUTILS CTO AGENT =====

        # Tool: create_plan
        self.register(Tool(
            name="create_plan",
            description="Crée un plan JSON structuré à partir d'un brief ou document. Utilise le PlanBuilder pour analyser et structurer les étapes.",
            parameters={
                "type": "object",
                "properties": {
                    "brief": {
                        "type": "string",
                        "description": "Description textuelle du projet/tâche à planifier",
                    },
                    "document_path": {
                        "type": "string",
                        "description": "Chemin vers un document à analyser pour créer le plan (MD, TXT, JSON)",
                    },
                },
                "additionalProperties": True,
            },
            handler=self._create_plan,
        ))

        # Tool: execute_plan
        self.register(Tool(
            name="execute_plan",
            description="Exécute un plan JSON via workflow AetherFlow (proto=rapide, prod=qualité).",
            parameters={
                "type": "object",
                "properties": {
                    "plan_path": {
                        "type": "string",
                        "description": "Chemin vers le fichier plan JSON à exécuter",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["proto", "prod"],
                        "description": "Mode d'exécution: proto (rapide) ou prod (qualité)",
                        "default": "proto",
                    },
                },
                "required": ["plan_path"],
                "additionalProperties": True,
            },
            handler=self._execute_plan,
        ))

        # Tool: get_project_context
        self.register(Tool(
            name="get_project_context",
            description="Récupère le contexte du projet (genome, plans récents, fichiers générés, sessions).",
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": True,
            },
            handler=self._get_project_context,
        ))

        # Tool: write_file
        self.register(Tool(
            name="write_file",
            description="Écrit un fichier sur le disque (plan, code, config, etc.).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Chemin du fichier à créer/écrire",
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenu à écrire dans le fichier",
                    },
                    "create_dirs": {
                        "type": "boolean",
                        "description": "Créer les dossiers parents si nécessaire",
                        "default": True,
                    },
                },
                "required": ["path", "content"],
                "additionalProperties": True,
            },
            handler=self._write_file,
        ))

        # Tool: extract_components
        self.register(Tool(
            name="extract_components",
            description="Extrait les composants HTML d'un document et les sauvegarde en fichiers séparés. Utile pour créer une bibliothèque de composants depuis une documentation.",
            parameters={
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "Chemin vers le document contenant les composants (MD, TXT)",
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Dossier de sortie pour les composants",
                        "default": "output/components",
                    },
                },
                "required": ["document_path"],
                "additionalProperties": True,
            },
            handler=self._extract_components,
        ))

        # Tool: select_component (SULLIVAN SELECTEUR)
        self.register(Tool(
            name="select_component",
            description="Sélectionne un composant dans la library selon l'intention utilisateur. Cherche d'abord dans la Core Library, adapte les paramètres, et place au bon endroit. Utilise cette fonction PREFERENTIELLEMENT à generate_component.",
            parameters={
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "description": "Description de ce que l'utilisateur veut (ex: 'bouton rouge', 'formulaire login')",
                    },
                    "target_zone": {
                        "type": "string",
                        "description": "Selecteur CSS de la zone cible (défaut: auto-détecté)",
                        "default": "auto",
                    },
                    "params": {
                        "type": "object",
                        "description": "Paramètres d'adaptation (couleur, texte, endpoint, etc.)",
                        "default": {},
                    },
                    "force_generate": {
                        "type": "boolean",
                        "description": "Forcer la génération même si un composant existe (défaut: false)",
                        "default": False,
                    },
                },
                "required": ["intent"],
                "additionalProperties": True,
            },
            handler=self._select_component,
        ))
        
        # Tool: select_component_set (SULLIVAN SELECTEUR SET)
        self.register(Tool(
            name="select_component_set",
            description="Sélectionne un SET de composants pour une typologie entière basé sur les endpoints. Utilise l'inférence pour choisir automatiquement les composants appropriés.",
            parameters={
                "type": "object",
                "properties": {
                    "typography": {
                        "type": "string",
                        "enum": ["Brainstorm", "Backend", "Frontend", "Deploy"],
                        "description": "La typologie cible",
                    },
                    "endpoints": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                            },
                        },
                        "description": "Liste des endpoints à couvrir",
                    },
                },
                "required": ["typography"],
            },
            handler=self._select_component_set,
        ))

    # ===== HANDLERS DES OUTILS =====
    
    async def _analyze_design(
        self,
        image_path: str,
        extract_principles: bool = False,
        **kwargs,
    ) -> ToolResult:
        """Analyse une image de design."""
        try:
            from ..analyzer.design_analyzer_fast import analyze_image_fast
            
            structure = await analyze_image_fast(Path(image_path))
            
            return ToolResult(
                success=True,
                content=f"Design analysé : {len(structure.sections)} sections détectées.",
                data={
                    "sections": structure.sections,
                    "layout": structure.layout,
                    "components_count": len(structure.components),
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="L'analyse du design a échoué.",
                error=str(e),
            )
    
    async def _generate_component(
        self,
        description: str,
        component_type: str,
        style: str = "minimal",
        **kwargs,
    ) -> ToolResult:
        """Génère un composant HTML avec Tailwind CSS."""
        try:
            from ...models.groq_client import GroqClient
            from ...models.gemini_client import GeminiClient

            # Prompt de génération spécialisé
            prompt = f"""Tu es un expert en développement frontend. Génère un composant {component_type} en HTML avec Tailwind CSS.

DESCRIPTION: {description}
STYLE: {style}

RÈGLES:
1. Utilise UNIQUEMENT Tailwind CSS (pas de CSS custom)
2. Le composant doit être responsive (mobile-first)
3. Inclure les états hover/focus appropriés
4. Code propre et sémantique
5. Pas de JavaScript sauf si absolument nécessaire

STYLES DISPONIBLES:
- minimal: épuré, beaucoup d'espace blanc, bordures fines
- brutalist: contrastes forts, typographie bold, angles droits
- glassmorphism: effets de verre, blur, transparence
- neumorphism: ombres douces, effet 3D subtil
- modern: gradients subtils, coins arrondis, ombres légères

Retourne UNIQUEMENT le code HTML, sans explications ni markdown.
"""

            # Utiliser Groq pour une génération rapide
            groq = GroqClient()
            result = await groq.generate(
                prompt=prompt,
                max_tokens=2048,
            )

            if result.success and result.code:
                # Nettoyer le HTML (enlever les balises markdown si présentes)
                html = result.code.strip()
                if html.startswith("```"):
                    # Extraire le contenu entre les balises
                    lines = html.split("\n")
                    html_lines = []
                    in_code = False
                    for line in lines:
                        if line.startswith("```"):
                            in_code = not in_code
                            continue
                        if in_code or not line.startswith("```"):
                            html_lines.append(line)
                    html = "\n".join(html_lines).strip()

                # Générer un ID unique pour le composant
                component_id = f"{component_type}_{int(time.time())}"

                # Sauvegarder dans le registre
                registry = _load_registry()
                registry_entry = {
                    "id": component_id,
                    "type": component_type,
                    "description": description,
                    "style": style,
                    "html": html,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                registry.append(registry_entry)
                _save_registry(registry)

                # Sauvegarder aussi le HTML dans un fichier séparé
                component_file = REGISTRY_FILE.parent / f"{component_id}.html"
                component_file.write_text(html, encoding="utf-8")

                return ToolResult(
                    success=True,
                    content=f"✓ Composant '{component_id}' généré et ajouté à la sidebar.",
                    data={
                        "html": html,
                        "component_type": component_type,
                        "style": style,
                        "component_id": component_id,
                        # Action DOM pour injecter dans la sidebar
                        "dom_action": {
                            "type": "insertHTML",
                            "selector": "#sullivan-components",
                            "position": "beforeend",
                            "html": f'<div class="component-card" data-id="{component_id}"><h4>{component_type}</h4><div class="preview">{html}</div></div>'
                        },
                    },
                )
            else:
                # Fallback sur Gemini si Groq échoue
                gemini = GeminiClient(execution_mode="BUILD")
                result = await gemini.generate(
                    prompt=prompt,
                    max_tokens=2048,
                )

                if result.success and result.code:
                    html = result.code.strip()
                    if html.startswith("```"):
                        lines = html.split("\n")
                        html_lines = []
                        in_code = False
                        for line in lines:
                            if line.startswith("```"):
                                in_code = not in_code
                                continue
                            if in_code or not line.startswith("```"):
                                html_lines.append(line)
                        html = "\n".join(html_lines).strip()

                    # Générer un ID unique pour le composant
                    component_id = f"{component_type}_{int(time.time())}"

                    # Sauvegarder dans le registre
                    registry = _load_registry()
                    registry_entry = {
                        "id": component_id,
                        "type": component_type,
                        "description": description,
                        "style": style,
                        "html": html,
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    }
                    registry.append(registry_entry)
                    _save_registry(registry)

                    # Sauvegarder aussi le HTML dans un fichier séparé
                    component_file = REGISTRY_FILE.parent / f"{component_id}.html"
                    component_file.write_text(html, encoding="utf-8")

                    return ToolResult(
                        success=True,
                        content=f"✓ Composant '{component_id}' généré (via Gemini) et ajouté à la sidebar.",
                        data={
                            "html": html,
                            "component_type": component_type,
                            "style": style,
                            "component_id": component_id,
                            # Action DOM pour injecter dans la sidebar
                            "dom_action": {
                                "type": "insertHTML",
                                "selector": "#sullivan-components",
                                "position": "beforeend",
                                "html": f'<div class="component-card" data-id="{component_id}"><h4>{component_type}</h4><div class="preview">{html}</div></div>'
                            },
                        },
                    )

                return ToolResult(
                    success=False,
                    content="La génération a échoué avec les deux providers.",
                    error=result.error or "Unknown error",
                )

        except Exception as e:
            logger.error(f"generate_component error: {e}")
            return ToolResult(
                success=False,
                content="La génération du composant a échoué.",
                error=str(e),
            )
    
    async def _search_components(
        self,
        query: str,
        category: Optional[str] = None,
        **kwargs,
    ) -> ToolResult:
        """Cherche des composants."""
        try:
            from ..registry import ComponentRegistry
            
            registry = ComponentRegistry()
            
            # Recherche simple par intent
            component = await registry.get_or_generate(
                intent=query,
                user_id="chatbot",
            )
            
            return ToolResult(
                success=True,
                content=f"Composant trouvé: {component.name} (score: {component.sullivan_score})",
                data={
                    "component_name": component.name,
                    "score": component.sullivan_score,
                    "category": category,
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="La recherche a échoué.",
                error=str(e),
            )
    
    async def _validate_genome(self, genome_json: str, **kwargs) -> ToolResult:
        """Valide un genome."""
        try:
            from ..identity import auditor
            
            genome = json.loads(genome_json)
            current_design = {"active_functions": []}  # Simplifié
            
            alerts = auditor.check_homeostasis(current_design, genome)
            
            if alerts:
                return ToolResult(
                    success=True,
                    content=f"{len(alerts)} alertes d'homéostasie détectées.",
                    data={"alerts": alerts, "valid": False},
                )
            else:
                return ToolResult(
                    success=True,
                    content="Genome valide. Pas d'alertes.",
                    data={"alerts": [], "valid": True},
                )
        except Exception as e:
            return ToolResult(
                success=False,
                content="La validation a échoué.",
                error=str(e),
            )
    
    async def _get_step_guidance(self, step: int, **kwargs) -> ToolResult:
        """Donne des conseils pour une étape."""
        guidance = {
            1: "Étape 1 - IR: Définissez l'intention de votre application. Quel problème résolvez-vous ?",
            2: "Étape 2 - Arbitrage: Validez les capacités de votre application. Gardez l'essentiel.",
            3: "Étape 3 - Genome: La topologie est figée. Vérifiez que tous les endpoints sont présents.",
            4: "Étape 4 - Composants: Voici les composants par défaut. Prêts à personnaliser ?",
            5: "Étape 5 - Carrefour: Importez votre design ou choisissez parmi nos propositions.",
            6: "Étape 6 - Analyse: J'ai analysé votre image. Validez les zones détectées.",
            7: "Étape 7 - Dialogue: Affinons ensemble les détails avant de finaliser.",
            8: "Étape 8 - Validation: Dernier check. Tout est bon pour vous ?",
            9: "Étape 9 - Adaptation: Navigation top-bottom. Zoom sur les zones à ajuster.",
        }
        
        return ToolResult(
            success=True,
            content=guidance.get(step, "Étape inconnue"),
            data={"step": step, "next_steps": [step + 1] if step < 9 else []},
        )
    
    async def _refine_style(
        self,
        html: str,
        instruction: str,
        **kwargs,
    ) -> ToolResult:
        """Affine le style d'un composant."""
        try:
            from ..modes.frontend_mode import FrontendMode
            
            frontend = FrontendMode()
            refined = await frontend.refine_style(html, instruction)
            
            return ToolResult(
                success=True,
                content="Style affiné selon vos instructions.",
                data={"html": refined},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="Le raffinement a échoué.",
                error=str(e),
            )
    
    async def _read_documentation(
        self,
        path: str = None,
        doc_path: str = None,
        doc: str = None,
        file: str = None,
        file_path: str = None,
        section: Optional[str] = None,
        **kwargs,
    ) -> ToolResult:
        """Lit un fichier de documentation."""
        try:
            # Accepter path, doc_path, doc, file, ou file_path
            actual_path = path or doc_path or doc or file or file_path
            if not actual_path:
                return ToolResult(
                    success=False,
                    content="Aucun chemin de fichier fourni",
                    error="Missing path parameter",
                )
            file_path = Path(actual_path)
            
            # Chercher dans différents chemins possibles
            search_paths = [
                file_path,
                Path("/Users/francois-jeandazin/AETHERFLOW") / file_path,
                Path("/Users/francois-jeandazin/AETHERFLOW/docs") / file_path,
            ]
            
            found_path = None
            for sp in search_paths:
                if sp.exists():
                    found_path = sp
                    break
            
            if not found_path:
                # Chercher récursivement
                root = Path("/Users/francois-jeandazin/AETHERFLOW")
                for p in root.rglob(file_path.name if file_path.name else "*"):
                    if p.name == file_path.name:
                        found_path = p
                        break
            
            if not found_path or not found_path.exists():
                return ToolResult(
                    success=False,
                    content=f"Fichier non trouvé: {actual_path}",
                    error="File not found",
                )
            
            # Lire le contenu
            content = found_path.read_text(encoding="utf-8")
            
            # Extraire une section si demandée
            if section:
                lines = content.split("\n")
                section_content = []
                in_section = False
                section_level = None
                
                # Nettoyer le nom de section (enlever ## si présent)
                clean_section = section.replace("#", "").strip().lower()
                
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.startswith("#"):
                        # Extraire le titre sans les #
                        header_text = line_stripped.lstrip("#").strip().lower()
                        # Vérifier si c'est la section cherchée
                        if clean_section in header_text or header_text in clean_section:
                            in_section = True
                            section_level = line_stripped.count("#")
                            section_content.append(line)
                        elif in_section and line_stripped.count("#") <= section_level:
                            # Nouvelle section de même niveau ou supérieur = fin
                            break
                    elif in_section:
                        section_content.append(line)
                
                content = "\n".join(section_content) if section_content else content
            
            # Limiter la taille
            max_chars = 8000
            truncated = len(content) > max_chars
            display_content = content[:max_chars] + ("\n... (tronqué)" if truncated else "")
            
            return ToolResult(
                success=True,
                content=f"Document lu: {found_path.name} ({len(content)} caractères)",
                data={
                    "file_path": str(found_path),
                    "content": display_content,
                    "truncated": truncated,
                    "total_chars": len(content),
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content=f"Erreur de lecture: {str(e)}",
                error=str(e),
            )
    
    async def _analyze_codebase(
        self,
        path: str = None,
        target_path: str = None,
        analysis_type: str = "structure",
        depth: str = None,
        **kwargs,
    ) -> ToolResult:
        """Analyse la structure de la codebase."""
        try:
            # Accepter path ou target_path
            actual_path = path or target_path or "Backend/Prod"
            root = Path("/Users/francois-jeandazin/AETHERFLOW") / actual_path
            
            if not root.exists():
                return ToolResult(
                    success=False,
                    content=f"Chemin non trouvé: {target_path}",
                    error="Path not found",
                )
            
            if analysis_type == "structure":
                # Analyse de structure des dossiers
                structure = {}
                python_files = list(root.rglob("*.py"))
                
                for py_file in python_files[:50]:  # Limiter à 50 fichiers
                    rel_path = py_file.relative_to(root)
                    parts = rel_path.parts
                    
                    current = structure
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    
                    file_key = parts[-1] if parts else str(rel_path)
                    current[file_key] = "file"
                
                stats = {
                    "total_py_files": len(python_files),
                    "directories": len(set(f.parent for f in python_files)),
                }
                
                return ToolResult(
                    success=True,
                    content=f"Structure analysée: {stats['total_py_files']} fichiers Python dans {stats['directories']} dossiers",
                    data={
                        "structure": structure,
                        "stats": stats,
                        "root": str(root),
                    },
                )
            
            elif analysis_type == "endpoints":
                # Extraire les endpoints FastAPI
                endpoints = []
                
                for py_file in root.rglob("*.py"):
                    try:
                        content = py_file.read_text(encoding="utf-8")
                        lines = content.split("\n")
                        
                        for i, line in enumerate(lines):
                            if "@router" in line or "@app." in line:
                                # Chercher la route
                                route_match = None
                                method = "GET"
                                
                                if "get(" in line:
                                    method = "GET"
                                elif "post(" in line:
                                    method = "POST"
                                elif "put(" in line:
                                    method = "PUT"
                                elif "delete(" in line:
                                    method = "DELETE"
                                
                                # Chercher la fonction suivante
                                for j in range(i+1, min(i+5, len(lines))):
                                    func_line = lines[j]
                                    if "async def " in func_line or "def " in func_line:
                                        func_name = func_line.split("def ")[1].split("(")[0].strip()
                                        endpoints.append({
                                            "file": str(py_file.relative_to(root)),
                                            "method": method,
                                            "function": func_name,
                                            "line": i+1,
                                        })
                                        break
                    except:
                        continue
                
                return ToolResult(
                    success=True,
                    content=f"{len(endpoints)} endpoints trouvés",
                    data={
                        "endpoints": endpoints[:20],  # Limiter
                        "total": len(endpoints),
                    },
                )
            
            else:
                return ToolResult(
                    success=True,
                    content=f"Analyse '{analysis_type}' non implémentée. Utilisez: structure, endpoints",
                    data={"available_types": ["structure", "endpoints"]},
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                content=f"Erreur d'analyse: {str(e)}",
                error=str(e),
            )
    
    async def _search_in_code(
        self,
        query: str,
        file_pattern: str = "*.py",
        max_results: int = 10,
        **kwargs,
    ) -> ToolResult:
        """Recherche dans le code."""
        try:
            root = Path("/Users/francois-jeandazin/AETHERFLOW")
            results = []
            
            for file_path in root.rglob(file_pattern):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.split("\n")
                    
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            results.append({
                                "file": str(file_path.relative_to(root)),
                                "line": i + 1,
                                "content": line.strip()[:100],
                            })
                            
                            if len(results) >= max_results:
                                break
                    
                    if len(results) >= max_results:
                        break
                        
                except Exception:
                    continue
            
            return ToolResult(
                success=True,
                content=f"{len(results)} résultats trouvés pour '{query}'",
                data={
                    "query": query,
                    "results": results,
                    "file_pattern": file_pattern,
                },
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content=f"Erreur de recherche: {str(e)}",
                error=str(e),
            )

    # ===== NOUVEAUX OUTILS CTO AGENT =====

    async def _create_plan(
        self,
        brief: str = None,
        document_path: str = None,
        doc_path: str = None,
        path: str = None,
        **kwargs,
    ) -> ToolResult:
        """Crée un plan JSON structuré à partir d'un brief ou document."""
        try:
            from ..modes.plan_builder import PlanBuilder
            import time

            # Accepter plusieurs noms de paramètres
            actual_path = document_path or doc_path or path

            # Si un document est fourni, le lire pour enrichir le brief
            actual_brief = brief or ""
            if actual_path:
                doc_file = Path(actual_path)
                if not doc_file.exists():
                    # Chercher dans AETHERFLOW
                    doc_file = Path("/Users/francois-jeandazin/AETHERFLOW") / actual_path
                if doc_file.exists():
                    content = doc_file.read_text(encoding="utf-8")
                    actual_brief = f"""Document: {doc_file.name}

Contenu:
{content[:8000]}

Brief: {brief or 'Crée un plan d implémentation basé sur ce document.'}"""
                else:
                    return ToolResult(
                        success=False,
                        content=f"Document non trouvé: {actual_path}",
                        error="File not found",
                    )

            if not actual_brief:
                return ToolResult(
                    success=False,
                    content="Brief ou document requis pour créer un plan.",
                    error="Missing brief or document_path",
                )

            # Créer le plan via PlanBuilder (mode non-interactif)
            builder = PlanBuilder()
            plan = await builder.create_plan_from_brief(
                brief=actual_brief,
                interactive=False,
            )

            # Sauvegarder le plan
            output_dir = Path("/Users/francois-jeandazin/AETHERFLOW/output/plans")
            output_dir.mkdir(parents=True, exist_ok=True)
            plan_file = output_dir / f"sullivan_plan_{int(time.time())}.json"
            plan_dict = plan.to_dict()
            plan_file.write_text(json.dumps(plan_dict, indent=2, ensure_ascii=False), encoding="utf-8")

            # Résumé pour l'affichage
            steps_summary = [f"- {s.type}: {s.description[:60]}..." for s in plan.steps[:5]]
            if len(plan.steps) > 5:
                steps_summary.append(f"... et {len(plan.steps) - 5} autres étapes")

            return ToolResult(
                success=True,
                content=f"Plan créé: {plan_file.name} ({len(plan.steps)} étapes)",
                data={
                    "plan_file": str(plan_file),
                    "task_id": plan.task_id,
                    "steps_count": len(plan.steps),
                    "complexity": plan.metadata.get("complexity", "unknown"),
                    "steps_preview": steps_summary,
                    "plan": plan_dict,
                },
            )
        except Exception as e:
            logger.error(f"create_plan error: {e}")
            return ToolResult(
                success=False,
                content=f"Erreur création plan: {str(e)}",
                error=str(e),
            )

    async def _execute_plan(
        self,
        plan_path: str = None,
        plan_file: str = None,
        mode: str = "proto",
        **kwargs,
    ) -> ToolResult:
        """Exécute un plan via workflow AetherFlow."""
        try:
            actual_path = plan_path or plan_file
            if not actual_path:
                return ToolResult(
                    success=False,
                    content="Chemin du plan requis (plan_path ou plan_file).",
                    error="Missing plan_path",
                )

            plan_file = Path(actual_path)
            if not plan_file.exists():
                plan_file = Path("/Users/francois-jeandazin/AETHERFLOW") / actual_path
            if not plan_file.exists():
                return ToolResult(
                    success=False,
                    content=f"Plan non trouvé: {actual_path}",
                    error="Plan file not found",
                )

            # Charger le plan
            plan_data = json.loads(plan_file.read_text(encoding="utf-8"))

            # Exécuter via le workflow approprié
            if mode == "proto":
                from ...workflows.proto import ProtoWorkflow
                workflow = ProtoWorkflow()
            else:
                from ...workflows.prod import ProdWorkflow
                workflow = ProdWorkflow()

            result = await workflow.execute(
                plan=plan_data,
                output_dir=Path("/Users/francois-jeandazin/AETHERFLOW/output/cto"),
            )

            return ToolResult(
                success=result.get("success", False),
                content=f"Plan exécuté ({mode}): {result.get('steps_completed', 0)} étapes",
                data={
                    "mode": mode,
                    "steps_completed": result.get("steps_completed", 0),
                    "files_generated": result.get("files_generated", []),
                    "time_ms": result.get("time_ms", 0),
                    "errors": result.get("errors", []),
                },
            )
        except Exception as e:
            logger.error(f"execute_plan error: {e}")
            return ToolResult(
                success=False,
                content=f"Erreur exécution plan: {str(e)}",
                error=str(e),
            )

    async def _get_project_context(self, **kwargs) -> ToolResult:
        """Récupère le contexte du projet (genome, structure, état)."""
        try:
            context_parts = []
            data = {}

            # 1. Lire le genome si présent
            genome_path = Path("/Users/francois-jeandazin/AETHERFLOW/output/studio/homeos_genome.json")
            if genome_path.exists():
                genome = json.loads(genome_path.read_text(encoding="utf-8"))
                data["genome"] = {
                    "endpoints_count": len(genome.get("topology", {}).get("endpoints", [])),
                    "name": genome.get("metadata", {}).get("project_name", "unknown"),
                }
                context_parts.append(f"Genome: {data['genome']['name']} ({data['genome']['endpoints_count']} endpoints)")

            # 2. Lire les plans récents
            plans_dir = Path("/Users/francois-jeandazin/AETHERFLOW/output/plans")
            if plans_dir.exists():
                plans = sorted(plans_dir.glob("sullivan_plan_*.json"), reverse=True)[:3]
                data["recent_plans"] = [p.name for p in plans]
                if plans:
                    context_parts.append(f"Plans récents: {len(plans)}")

            # 3. Fichiers générés récents
            cto_dir = Path("/Users/francois-jeandazin/AETHERFLOW/output/cto")
            if cto_dir.exists():
                recent_files = sorted(cto_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                data["recent_files"] = [f.name for f in recent_files]
                if recent_files:
                    context_parts.append(f"Fichiers récents: {len(recent_files)}")

            # 4. Sessions actives
            sessions_dir = Path.home() / ".aetherflow" / "sessions"
            if sessions_dir.exists():
                sessions = list(sessions_dir.glob("*.json"))
                data["sessions_count"] = len(sessions)
                context_parts.append(f"Sessions: {len(sessions)}")

            summary = " | ".join(context_parts) if context_parts else "Aucun contexte projet trouvé"

            return ToolResult(
                success=True,
                content=summary,
                data=data,
            )
        except Exception as e:
            logger.error(f"get_project_context error: {e}")
            return ToolResult(
                success=False,
                content=f"Erreur récupération contexte: {str(e)}",
                error=str(e),
            )

    async def _write_file(
        self,
        path: str,
        file_path: str = None,
        content: str = "",
        create_dirs: bool = True,
        **kwargs,
    ) -> ToolResult:
        """Écrit un fichier sur le disque."""
        try:
            actual_path = path or file_path
            if not actual_path:
                return ToolResult(
                    success=False,
                    content="Chemin de fichier requis (path).",
                    error="Missing path",
                )

            file = Path(actual_path)
            if not file.is_absolute():
                file = Path("/Users/francois-jeandazin/AETHERFLOW") / actual_path

            if create_dirs:
                file.parent.mkdir(parents=True, exist_ok=True)

            file.write_text(content, encoding="utf-8")

            return ToolResult(
                success=True,
                content=f"Fichier écrit: {file.name} ({len(content)} caractères)",
                data={
                    "file_path": str(file),
                    "size_chars": len(content),
                },
            )
        except Exception as e:
            logger.error(f"write_file error: {e}")
            return ToolResult(
                success=False,
                content=f"Erreur écriture fichier: {str(e)}",
                error=str(e),
            )

    async def _extract_components(
        self,
        document_path: str,
        output_dir: str = "output/components",
        **kwargs,
    ) -> ToolResult:
        """Extrait les composants HTML d'un document et les sauvegarde."""
        import re

        try:
            # Trouver le fichier
            doc_file = Path(document_path)
            if not doc_file.exists():
                doc_file = Path("/Users/francois-jeandazin/AETHERFLOW") / document_path
            if not doc_file.exists():
                return ToolResult(
                    success=False,
                    content=f"Document non trouvé: {document_path}",
                    error="File not found",
                )

            content = doc_file.read_text(encoding="utf-8")

            # Créer le dossier de sortie
            out_path = Path("/Users/francois-jeandazin/AETHERFLOW") / output_dir
            out_path.mkdir(parents=True, exist_ok=True)

            # Pattern pour extraire les blocs HTML avec leur chemin
            # Cherche: <!-- atoms/button.html --> ou commentaire similaire, puis le code HTML
            pattern = r'```html\s*\n(?:<!--\s*([a-zA-Z0-9_/.-]+\.html)\s*-->\s*\n)?(.*?)```'
            matches = re.findall(pattern, content, re.DOTALL)

            # Pattern alternatif: ### **N. Name - Description** puis ```html
            section_pattern = r'###\s*\*\*\d+\.\s*([^-*]+)\s*[-–]\s*([^*]+)\*\*\s*\n```html\s*\n(.*?)```'
            section_matches = re.findall(section_pattern, content, re.DOTALL)

            created_files = []
            components_data = []

            # Traiter les blocs avec chemin explicite
            for file_path, html_content in matches:
                if file_path and html_content.strip():
                    # Nettoyer le chemin
                    clean_path = file_path.strip()
                    # Créer sous-dossiers si nécessaire
                    full_path = out_path / clean_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    # Écrire le fichier
                    full_path.write_text(html_content.strip(), encoding="utf-8")
                    created_files.append(clean_path)
                    components_data.append({
                        "path": clean_path,
                        "size": len(html_content.strip()),
                    })

            # Traiter les sections sans chemin explicite
            for name, desc, html_content in section_matches:
                if html_content.strip():
                    # Générer un nom de fichier à partir du nom
                    clean_name = name.strip().lower().replace(" ", "_")
                    clean_name = re.sub(r'[^a-z0-9_]', '', clean_name)

                    # Déterminer le sous-dossier selon le contexte
                    if "atom" in content[:content.find(name)].lower().split('\n')[-10:]:
                        subdir = "atoms"
                    elif "molecule" in content[:content.find(name)].lower().split('\n')[-10:]:
                        subdir = "molecules"
                    elif "organism" in content[:content.find(name)].lower().split('\n')[-10:]:
                        subdir = "organisms"
                    else:
                        subdir = "components"

                    file_path = f"{subdir}/{clean_name}.html"
                    full_path = out_path / file_path

                    # Ne pas écraser si déjà créé
                    if file_path not in created_files:
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(html_content.strip(), encoding="utf-8")
                        created_files.append(file_path)
                        components_data.append({
                            "path": file_path,
                            "name": name.strip(),
                            "description": desc.strip(),
                            "size": len(html_content.strip()),
                        })

            if not created_files:
                return ToolResult(
                    success=False,
                    content="Aucun composant HTML trouvé dans le document.",
                    error="No components found",
                )

            # Créer un index.json
            index_path = out_path / "index.json"
            index_path.write_text(json.dumps({
                "source": str(doc_file.name),
                "output_dir": output_dir,
                "components_count": len(created_files),
                "components": components_data,
            }, indent=2, ensure_ascii=False), encoding="utf-8")

            return ToolResult(
                success=True,
                content=f"{len(created_files)} composants extraits dans {output_dir}/",
                data={
                    "output_dir": output_dir,
                    "components_count": len(created_files),
                    "files": created_files[:10],  # Limiter l'affichage
                    "index_file": str(index_path),
                },
            )

        except Exception as e:
            logger.error(f"extract_components error: {e}")
            return ToolResult(
                success=False,
                content=f"Erreur extraction composants: {str(e)}",
                error=str(e),
            )

    # ===== SULLIVAN SELECTEUR =====
    # Nouvelle architecture: Tier 1 (Core Library) → Tier 2 (Adaptation) → Tier 3 (Generation)

    # Mapping intent → zone cible (logique Top-Bottom)
    INTENT_TO_ZONE = {
        # Brainstorm (étapes 1-3)
        "wireframe|sketch|idea|concept|brainstorm|maquette": "#tab-brainstorm",
        
        # Backend (étapes 4-5)
        "api|endpoint|schema|model|database|backend": "#tab-backend",
        
        # Frontend (étapes 6-8) - DÉFAUT
        "button|form|card|table|input|modal|navbar|alert|badge|list|nav|header|footer": "#sullivan-components",
        
        # Deploy (étape 9)
        "deploy|config|build|preview|pipeline": "#tab-deploy",
    }

    def _detect_target_zone(self, intent: str) -> str:
        """Détecte la zone cible selon l'intention."""
        intent_lower = intent.lower()
        for pattern, zone in self.INTENT_TO_ZONE.items():
            keywords = pattern.split("|")
            if any(kw in intent_lower for kw in keywords):
                return zone
        return "#sullivan-components"  # Défaut: sidebar components

    def _load_component_library(self) -> Dict[str, Any]:
        """
        Charge la Core Library depuis output/components/library.json
        
        Returns:
            Dict avec les composants organisés par catégorie
        """
        library_path = Path("/Users/francois-jeandazin/AETHERFLOW/output/components/library.json")
        
        if not library_path.exists():
            logger.warning(f"Library non trouvée: {library_path}")
            return {"categories": {}, "stats": {}}
        
        try:
            data = json.loads(library_path.read_text(encoding="utf-8"))
            logger.debug(f"Library chargée: {data.get('stats', {}).get('total', 0)} composants")
            return data
        except Exception as e:
            logger.error(f"Erreur chargement library: {e}")
            return {"categories": {}, "stats": {}}

    def _find_best_component(self, library: Dict, intent: str) -> Optional[Dict]:
        """
        Cherche le meilleur composant correspondant à l'intention.
        
        Algorithme:
        1. Matching exact sur les tags
        2. Matching partiel (score de similarité)
        3. Retourne le meilleur match ou None
        
        Supporte le français via mapping FR→EN.
        """
        if not library or "categories" not in library:
            return None
        
        # Mapping français → anglais pour matching
        FR_TO_EN = {
            "bouton": "button",
            "formulaire": "form",
            "tableau": "table",
            "carte": "card",
            "champ": "input",
            "icône": "icon",
            "icone": "icon",
            "entête": "header",
            "entete": "header",
            "pied": "footer",
            "barre": "bar",
            "recherche": "search",
            "nav": "nav",
            "navigation": "nav",
            "login": "login",
            "connexion": "login",
            "modal": "modal",
            "boîte": "modal",
            "boite": "modal",
            "liste": "list",
            "texte": "text",
            "couleur": "color",
        }
        
        intent_lower = intent.lower()
        intent_words = set(intent_lower.split())
        
        # Ajouter traductions FR→EN aux mots de l'intent
        for fr_word, en_word in FR_TO_EN.items():
            if fr_word in intent_lower:
                intent_words.add(en_word)
        
        best_match = None
        best_score = 0
        
        # Parcourir toutes les catégories
        for category, components in library["categories"].items():
            for name, comp in components.items():
                score = 0
                tags = [t.lower() for t in comp.get("tags", [])]
                
                # 1. Matching exact sur les tags (prioritaire)
                for tag in tags:
                    if tag in intent_words:
                        score += 15  # Score très élevé pour match tag exact
                    elif tag in intent_lower:
                        score += 10  # Match partiel
                
                # 2. Matching sur le nom du composant (nom simple ou traduit)
                name_clean = name.lower().split("___")[0]  # Enlever suffixe ___description
                if name_clean in intent_words:
                    score += 12  # Nom exact match
                elif name_clean in intent_lower:
                    score += 8   # Nom partiel match
                
                # 3. Matching mots-clés prioritaires (button, card, form, etc.)
                priority_keywords = ["button", "card", "form", "input", "modal", "search", "nav"]
                for keyword in priority_keywords:
                    if keyword in intent_words and keyword in tags:
                        score += 8  # Bonus priorité
                
                # 4. Matching partiel général
                comp_words = set(name_clean.split("_") + tags)
                common_words = intent_words & comp_words
                score += len(common_words) * 2
                
                # 5. Bonus catégorie
                if category == "atoms" and any(w in intent_words for w in ["button", "input", "icon"]):
                    score += 3
                elif category == "molecules" and any(w in intent_words for w in ["form", "search", "card"]):
                    score += 3
                
                # 5. Malus complexité si demande simple
                complexity = comp.get("complexity", "medium")
                if complexity == "high" and len(intent_words) < 3:
                    score -= 3
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        **comp,
                        "match_score": score,
                        "matched_category": category,
                    }
        
        # Seuil minimum pour considérer un match valide
        if best_score >= 5:
            logger.info(f"Meilleur match: {best_match['id']} (score: {best_score})")
            return best_match
        
        logger.debug(f"Aucun match valide trouvé (meilleur score: {best_score})")
        return None

    def _adapt_component(self, component: Dict, params: Dict) -> str:
        """
        Adapte un composant avec les paramètres fournis.
        
        Remplace:
        - Variables CSS (--xxx) par les valeurs fournies
        - Data attributes (data-xxx) par les valeurs fournies
        - Classes dynamiques si spécifiées
        """
        html = component.get("html", "")
        css = component.get("css", "")
        
        # Fusionner avec les defaults
        defaults = component.get("defaults", {})
        effective_params = {**defaults, **params}
        
        # 1. Remplacer les variables CSS dans le style
        for param_key, value in effective_params.items():
            if param_key.startswith("css:"):
                var_name = param_key[4:]  # Enlever le prefix
                # Remplacer var(--xxx) par la valeur
                css_var_pattern = rf'var\(--{re.escape(var_name)}\)'
                css = re.sub(css_var_pattern, value, css)
                # Remplacer aussi --xxx: default; par --xxx: value;
                css_default_pattern = rf'(--{re.escape(var_name)}):\s*[^;]+;'
                css = re.sub(css_default_pattern, f'\\1: {value};', css)
        
        # 2. Remplacer les data attributes
        for param_key, value in effective_params.items():
            if param_key.startswith("data:"):
                attr_name = param_key[5:]
                # Pattern: data-attr="value" ou data-attr='value'
                pattern = f'data-{attr_name}="[^"]*"'
                replacement = f'data-{attr_name}="{value}"'
                html = re.sub(pattern, replacement, html)
                # Pattern simple quote
                pattern2 = f"data-{attr_name}='[^']*'"
                replacement2 = f"data-{attr_name}='{value}'"
                html = re.sub(pattern2, replacement2, html)
        
        # 3. Remplacer le contenu texte pour les boutons
        if "text" in effective_params and "<button" in html:
            # Chercher le span.btn-content ou le texte direct
            if '<span class="btn-content">' in html:
                html = re.sub(
                    r'(<span class="btn-content">)[^<]*(</span>)',
                    f'\\1{effective_params["text"]}\\2',
                    html
                )
        
        # 4. Remplacer le placeholder pour les inputs
        if "placeholder" in effective_params and "<input" in html:
            html = re.sub(
                r'placeholder="[^"]*"',
                f'placeholder="{effective_params["placeholder"]}"',
                html
            )
        
        # Combiner HTML et CSS
        if css.strip():
            return f"{html}\n<style>{css}</style>"
        return html

    async def _select_component(
        self,
        intent: str,
        target_zone: str = "auto",
        params: Dict = None,
        force_generate: bool = False,
        **kwargs,
    ) -> ToolResult:
        """
        Sélectionne un composant de la library selon l'intent.
        
        Architecture 3 Tiers:
        1. Tier 1: Core Library (0ms) - Match exact
        2. Tier 2: Adaptation (<100ms) - Paramétrage
        3. Tier 3: Generation (1-5s) - Dernier recours
        """
        start_time = time.time()
        params = params or {}
        
        try:
            # Détecter la zone cible si auto
            if target_zone == "auto":
                target_zone = self._detect_target_zone(intent)
            
            # === TIER 3 (Dernier recours): Generation forcée ===
            if force_generate:
                logger.info("Tier 3: Generation forcée")
                return await self._generate_component(
                    description=intent,
                    component_type="custom",
                )
            
            # === TIER 1: Core Library ===
            library = self._load_component_library()
            best_match = self._find_best_component(library, intent)
            
            if not best_match:
                # === TIER 3: Aucun match → Generation ===
                logger.info(f"Tier 3: Aucun match pour '{intent}', génération...")
                gen_result = await self._generate_component(
                    description=intent,
                    component_type="custom",
                )
                
                if gen_result.success:
                    # Injecter dans la bonne zone
                    if gen_result.data and "dom_action" in gen_result.data:
                        gen_result.data["dom_action"]["selector"] = target_zone
                    # Ajouter les métadonnées manquantes
                    if gen_result.data:
                        gen_result.data["target_zone"] = target_zone
                        gen_result.data["tier"] = 3  # Generation tier
                
                return gen_result
            
            # === TIER 2: Adaptation ===
            adapted_html = self._adapt_component(best_match, params)
            exec_time = (time.time() - start_time) * 1000  # ms
            
            # Construire la dom_action
            dom_action = {
                "type": "insertHTML",
                "selector": target_zone,
                "position": "beforeend",
                "html": adapted_html,
            }
            
            # Générer un ID unique pour cette instance
            instance_id = f"{best_match['id']}_{int(time.time())}"
            
            return ToolResult(
                success=True,
                content=f"✓ Composant '{best_match['name']}' sélectionné (score: {best_match.get('match_score', 0)}) et adapté en {exec_time:.0f}ms",
                data={
                    "component_id": best_match["id"],
                    "instance_id": instance_id,
                    "category": best_match.get("matched_category"),
                    "match_score": best_match.get("match_score", 0),
                    "adaptation_time_ms": exec_time,
                    "target_zone": target_zone,
                    "html": adapted_html,
                    "dom_action": dom_action,
                    "tier": 2,  # Adaptation tier
                },
            )
            
        except Exception as e:
            logger.error(f"select_component error: {e}")
            return ToolResult(
                success=False,
                content=f"Erreur sélection composant: {str(e)}",
                error=str(e),
            )
    
    async def _select_component_set(
        self,
        typography: str,
        endpoints: List[Dict] = None,
        **kwargs,
    ) -> ToolResult:
        """
        Sélectionne un set de composants pour une typologie.

        Args:
            typography: Backend, Frontend, Deploy
            endpoints: Liste d'endpoints [{path, method}, ...]

        Returns:
            ToolResult avec les composants par endpoint
        """
        from Backend.Prod.sullivan.agent.component_inference import (
            infer_components_for_typography,
            infer_components_for_endpoint,
        )
        
        try:
            if endpoints:
                results = infer_components_for_typography(typography, endpoints)
            else:
                # Pas d'endpoints fournis, utiliser des defaults selon typography
                default_endpoints = {
                    "Backend": [
                        {"path": "/api/health", "method": "GET"},
                        {"path": "/api/config", "method": "GET"},
                    ],
                    "Frontend": [
                        {"path": "/api/users", "method": "GET"},
                        {"path": "/api/users", "method": "POST"},
                    ],
                    "Deploy": [
                        {"path": "/api/status", "method": "GET"},
                    ],
                }
                results = infer_components_for_typography(
                    typography,
                    default_endpoints.get(typography, []),
                )

            # Formater la réponse
            output = []
            all_components = []

            for result in results:
                endpoint_info = {
                    "endpoint": result.endpoint,
                    "method": result.method,
                    "components": [],
                }

                for comp in result.components:
                    comp_info = {
                        "id": comp.component_id,
                        "category": comp.category,
                        "reason": comp.reason,
                        "selected": comp.selected,
                    }
                    endpoint_info["components"].append(comp_info)
                    all_components.append(comp_info)

                output.append(endpoint_info)

            # Dédupliquer les composants
            seen = set()
            unique_components = []
            for c in all_components:
                if c["id"] not in seen:
                    seen.add(c["id"])
                    unique_components.append(c)

            return ToolResult(
                success=True,
                content=f"✅ {len(unique_components)} composants sélectionnés pour {typography}",
                data={
                    "typography": typography,
                    "total_components": len(unique_components),
                    "by_endpoint": output,
                    "unique_components": unique_components,
                },
            )

        except Exception as e:
            logger.error(f"Erreur select_component_set: {e}")
            return ToolResult(
                success=False,
                content=f"❌ Erreur: {str(e)}",
                data={"error": str(e)},
            )


# Instance globale
tool_registry = ToolRegistry()


__all__ = [
    "Tool",
    "ToolResult",
    "ToolRegistry",
    "tool_registry",
]
