"""ComponentGenerator - Génération réelle de composants HTML/CSS/JS via AETHERFLOW."""
import json
import uuid
import tempfile
from typing import Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re
from loguru import logger

from ...models.agent_router import AgentRouter
from ...workflows.proto import ProtoWorkflow
from ...workflows.prod import ProdWorkflow
from ...claude_helper import get_step_output
from ..knowledge.knowledge_base import KnowledgeBase
from ..models.component import Component


class ComponentGenerator:
    """
    Générateur de composants frontend via AETHERFLOW.
    
    Crée un plan JSON pour génération composant (HTML, CSS, JS),
    exécute via AETHERFLOW workflows (PROTO pour rapidité, PROD pour qualité),
    parse le code généré et structure le composant avec métadonnées.
    """
    
    def __init__(
        self,
        agent_router: Optional[AgentRouter] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        workflow: str = "PROTO"
    ):
        """
        Initialise le générateur de composants.

        Args:
            agent_router: Router pour sélection modèle LLM (optionnel)
            knowledge_base: Base de connaissances pour enrichir contexte (optionnel)
            workflow: Workflow AETHERFLOW ("PROTO" pour rapidité, "PROD" pour qualité)
        """
        self.agent_router = agent_router or AgentRouter(execution_mode="BUILD")
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.workflow = workflow.upper()
        
        logger.info(f"ComponentGenerator initialized with workflow: {self.workflow}")
    
    async def generate_component(
        self,
        intent: str,
        context: str,
        user_id: str
    ) -> Component:
        """
        Génère un composant frontend complet (HTML/CSS/JS) via AETHERFLOW.

        Args:
            intent: Description de l'intention du composant
            context: Contexte additionnel pour la génération
            user_id: Identifiant de l'utilisateur

        Returns:
            Component: Composant généré avec métadonnées
        """
        logger.info(f"Generating component for intent: '{intent}' (user: {user_id})")
        
        # Enrichir contexte depuis KnowledgeBase et STAR
        enriched_context = self._enrich_context(intent, context)
        
        # Créer plan JSON pour génération
        plan_path = self._create_generation_plan(intent, enriched_context, user_id)
        
        # Exécuter plan via AETHERFLOW workflow
        output_dir = await self._execute_plan(plan_path)
        
        # Parser code généré depuis outputs
        html, css, js = self._parse_generated_code(output_dir)
        
        # Structurer composant avec métadonnées
        component = self._structure_component(intent, html, css, js, user_id)
        
        # Sauvegarder systématiquement le composant généré
        await self._save_component_systematically(component, intent, html, css, js, user_id)
        
        logger.info(f"Generated component: {component.name} ({component.size_kb} KB)")
        return component
    
    def _enrich_context(self, intent: str, context: str) -> str:
        """
        Enrichit le contexte depuis KnowledgeBase et IntentTranslator/STAR.

        Args:
            intent: Intention du composant
            context: Contexte initial

        Returns:
            Contexte enrichi avec patterns, principes HCI et patterns STAR
        """
        # Rechercher patterns similaires dans KnowledgeBase
        patterns = self.knowledge_base.search_patterns(intent)
        
        # Récupérer principes HCI
        hci_principles = self.knowledge_base.get_hci_principles()
        
        # Construire contexte enrichi
        enriched = f"{context}\n\n"
        
        if patterns:
            enriched += f"Patterns similaires trouvés: {len(patterns)}\n"
            for pattern_name, pattern_data in list(patterns.items())[:3]:  # Top 3
                enriched += f"- {pattern_name}: {pattern_data}\n"
        
        if hci_principles:
            enriched += f"\nPrincipes HCI à respecter: {len(hci_principles)} principes\n"
        
        # Enrichir avec IntentTranslator/STAR si disponible
        star_enrichment = self._enrich_with_star(intent)
        if star_enrichment:
            enriched += f"\n{star_enrichment}\n"
        
        return enriched
    
    def _enrich_with_star(self, intent: str) -> Optional[str]:
        """
        Enrichit le contexte avec patterns STAR via IntentTranslator.

        Args:
            intent: Intention du composant

        Returns:
            Chaîne d'enrichissement STAR ou None si non disponible
        """
        try:
            # Lazy import d'IntentTranslator pour éviter dépendances circulaires
            from ..intent_translator import IntentTranslator
            
            # Créer instance IntentTranslator
            intent_translator = IntentTranslator()
            
            # Rechercher situations similaires avec embeddings
            situations = intent_translator.search_situation(intent, limit=3)
            
            if not situations:
                return None
            
            # Propager STAR pour obtenir réalisations
            star_info = []
            for situation in situations:
                realisation = intent_translator.propagate_star(situation)
                if realisation:
                    star_info.append(
                        f"STAR Pattern: {situation.pattern_name or 'Unknown'}\n"
                        f"  Situation: {situation.description}\n"
                        f"  Realisation: {realisation.description}\n"
                        f"  Template: {realisation.template or 'N/A'}"
                    )
            
            if star_info:
                logger.debug(f"Enriched context with {len(star_info)} STAR patterns for intent: {intent}")
                return f"\n=== Patterns STAR ===\n" + "\n\n".join(star_info)
            
        except ImportError as e:
            logger.debug(f"IntentTranslator not available: {e}. Skipping STAR enrichment.")
        except Exception as e:
            logger.warning(f"Error enriching with STAR for intent '{intent}': {e}. Skipping STAR enrichment.")
        
        return None
    
    def _create_generation_plan(
        self,
        intent: str,
        context: str,
        user_id: str
    ) -> Path:
        """
        Crée un plan JSON pour génération de composant via AETHERFLOW.

        Args:
            intent: Intention du composant
            context: Contexte enrichi
            user_id: Identifiant utilisateur

        Returns:
            Chemin vers le plan JSON créé
        """
        task_id = str(uuid.uuid4())
        
        plan = {
            "task_id": task_id,
            "description": f"Générer composant frontend pour: {intent}",
            "steps": [
                {
                    "id": "step_html",
                    "description": f"Générer code HTML pour composant: {intent}. Contexte: {context}. Respecter principes HCI, accessibilité WCAG, performance. Générer HTML sémantique et accessible.",
                    "type": "code_generation",
                    "complexity": 0.5,
                    "estimated_tokens": 2000,
                    "dependencies": [],
                    "validation_criteria": [
                        "HTML sémantique et valide",
                        "Accessibilité WCAG respectée",
                        "Structure claire et maintenable"
                    ],
                    "context": {
                        "language": "html",
                        "framework": "vanilla",
                        "files": ["component.html"]
                    }
                },
                {
                    "id": "step_css",
                    "description": f"Générer code CSS pour composant: {intent}. Contexte: {context}. CSS moderne (Grid/Flexbox), responsive, performant, écologique (taille minimale).",
                    "type": "code_generation",
                    "complexity": 0.5,
                    "estimated_tokens": 2000,
                    "dependencies": ["step_html"],
                    "validation_criteria": [
                        "CSS moderne et performant",
                        "Responsive design",
                        "Taille minimale (écologie)"
                    ],
                    "context": {
                        "language": "css",
                        "framework": "vanilla",
                        "files": ["component.css"]
                    }
                },
                {
                    "id": "step_js",
                    "description": f"Générer code JavaScript pour composant: {intent}. Contexte: {context}. JS vanilla (pas de framework), performant, accessible (ARIA), écologique.",
                    "type": "code_generation",
                    "complexity": 0.6,
                    "estimated_tokens": 2500,
                    "dependencies": ["step_html", "step_css"],
                    "validation_criteria": [
                        "JavaScript vanilla (pas de framework)",
                        "Performance optimale",
                        "Accessibilité ARIA respectée",
                        "Code maintenable"
                    ],
                    "context": {
                        "language": "javascript",
                        "framework": "vanilla",
                        "files": ["component.js"]
                    }
                }
            ],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "claude_version": "claude-code",
                "project_context": f"Génération composant Sullivan: {intent}",
                "user_id": user_id
            }
        }
        
        # Sauvegarder plan dans fichier temporaire
        temp_dir = Path(tempfile.gettempdir()) / "sullivan_plans"
        temp_dir.mkdir(parents=True, exist_ok=True)
        plan_path = temp_dir / f"component_{task_id}.json"
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2)
        
        logger.info(f"Created generation plan: {plan_path}")
        return plan_path
    
    async def _execute_plan(self, plan_path: Path) -> Path:
        """
        Exécute le plan via AETHERFLOW workflow.

        Args:
            plan_path: Chemin vers le plan JSON

        Returns:
            Chemin vers le répertoire de sortie
        """
        logger.info(f"Executing plan via AETHERFLOW workflow: {self.workflow}")
        
        # Créer répertoire de sortie
        output_dir = Path(tempfile.gettempdir()) / "sullivan_outputs" / plan_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Exécuter workflow approprié
        if self.workflow == "PROTO":
            workflow = ProtoWorkflow()
        else:
            workflow = ProdWorkflow()
        
        try:
            result = await workflow.execute(
                plan_path=plan_path,
                output_dir=output_dir,
                context=None
            )
            
            if not result.get("success", False):
                raise Exception(f"Workflow execution failed: {result.get('error', 'Unknown error')}")
            
            logger.info(f"Plan executed successfully, outputs in: {output_dir}")
            return output_dir
            
        except Exception as e:
            logger.error(f"Error executing plan: {e}", exc_info=True)
            raise
    
    def _parse_generated_code(self, output_dir: Path) -> Tuple[str, str, str]:
        """
        Parse le code généré depuis les outputs AETHERFLOW.

        Args:
            output_dir: Répertoire de sortie AETHERFLOW

        Returns:
            Tuple (HTML, CSS, JS) extrait depuis les outputs
        """
        logger.info("Parsing generated code from AETHERFLOW outputs")
        
        html = ""
        css = ""
        js = ""
        
        # Déterminer les répertoires à chercher selon le workflow
        # PROD utilise fast_draft/ et build_refactored/
        # PROTO utilise fast/ et build/
        # validation/ est commun aux deux workflows
        if self.workflow == "PROD":
            # Workflow PROD : chercher dans fast_draft/, build_refactored/, validation/
            fast_draft_outputs_dir = output_dir / "fast_draft" / "step_outputs"
            build_refactored_outputs_dir = output_dir / "build_refactored" / "step_outputs"
            validation_outputs_dir = output_dir / "validation" / "step_outputs"
            
            # Essayer fast_draft d'abord, puis build_refactored, puis validation
            step_outputs_dir = None
            if fast_draft_outputs_dir.exists():
                step_outputs_dir = fast_draft_outputs_dir
                logger.info(f"Found PROD outputs in fast_draft/step_outputs")
            elif build_refactored_outputs_dir.exists():
                step_outputs_dir = build_refactored_outputs_dir
                logger.info(f"Found PROD outputs in build_refactored/step_outputs")
            elif validation_outputs_dir.exists():
                step_outputs_dir = validation_outputs_dir
                logger.info(f"Found PROD outputs in validation/step_outputs")
        else:
            # Workflow PROTO : chercher dans fast/, build/, validation/
            fast_outputs_dir = output_dir / "fast" / "step_outputs"
            build_outputs_dir = output_dir / "build" / "step_outputs"
            validation_outputs_dir = output_dir / "validation" / "step_outputs"
            
            # Essayer fast d'abord, puis build, puis validation
            step_outputs_dir = None
            if fast_outputs_dir.exists():
                step_outputs_dir = fast_outputs_dir
                logger.info(f"Found PROTO outputs in fast/step_outputs")
            elif build_outputs_dir.exists():
                step_outputs_dir = build_outputs_dir
                logger.info(f"Found PROTO outputs in build/step_outputs")
            elif validation_outputs_dir.exists():
                step_outputs_dir = validation_outputs_dir
                logger.info(f"Found PROTO outputs in validation/step_outputs")
        
        if not step_outputs_dir:
            logger.warning(f"No step outputs directory found in {output_dir} for workflow {self.workflow}")
            return "", "", ""
        
        # Lire directement les fichiers step_outputs
        html_file = step_outputs_dir / "step_html.txt"
        css_file = step_outputs_dir / "step_css.txt"
        js_file = step_outputs_dir / "step_js.txt"
        
        # Extraire HTML depuis step_html
        if html_file.exists():
            html_output = html_file.read_text(encoding='utf-8')
            html = self._extract_code_from_output(html_output, "html")
        else:
            logger.warning(f"HTML output file not found: {html_file}")
        
        # Extraire CSS depuis step_css
        if css_file.exists():
            css_output = css_file.read_text(encoding='utf-8')
            css = self._extract_code_from_output(css_output, "css")
        else:
            logger.warning(f"CSS output file not found: {css_file}")
        
        # Extraire JS depuis step_js
        if js_file.exists():
            js_output = js_file.read_text(encoding='utf-8')
            js = self._extract_code_from_output(js_output, "javascript")
        else:
            logger.warning(f"JS output file not found: {js_file}")
        
        logger.info(f"Parsed code: HTML={len(html)} chars, CSS={len(css)} chars, JS={len(js)} chars")
        return html, css, js
    
    def _extract_code_from_output(self, output: str, language: str) -> str:
        """
        Extrait le code depuis un output de step.

        Args:
            output: Output brut du step
            language: Langage du code (html, css, javascript)

        Returns:
            Code extrait
        """
        # Pattern pour blocs de code markdown
        patterns = {
            "html": [
                r'```html\n(.*?)```',
                r'```\n(.*?)```',  # Bloc générique
                r'<html[^>]*>(.*?)</html>',
                r'<[^>]+>.*?</[^>]+>',  # Tags HTML
            ],
            "css": [
                r'```css\n(.*?)```',
                r'```\n(.*?)```',
                r'<style[^>]*>(.*?)</style>',
            ],
            "javascript": [
                r'```javascript\n(.*?)```',
                r'```js\n(.*?)```',
                r'```\n(.*?)```',
                r'<script[^>]*>(.*?)</script>',
            ]
        }
        
        code_patterns = patterns.get(language, [r'```\n(.*?)```'])
        
        for pattern in code_patterns:
            matches = re.finditer(pattern, output, re.DOTALL)
            for match in matches:
                code = match.group(1).strip()
                if code and len(code) > 50:  # Minimum raisonnable
                    return code
        
        # Si aucun bloc trouvé, retourner output brut (peut contenir du code)
        return output.strip()
    
    def _structure_component(
        self,
        intent: str,
        html: str,
        css: str,
        js: str,
        user_id: str
    ) -> Component:
        """
        Structure un composant avec métadonnées.

        Args:
            intent: Intention du composant
            context: Contexte enrichi
            html: Code HTML généré
            css: Code CSS généré
            js: Code JavaScript généré
            user_id: Identifiant utilisateur

        Returns:
            Component structuré avec métadonnées
        """
        # Calculer taille totale en KB
        total_size_bytes = len(html.encode('utf-8')) + len(css.encode('utf-8')) + len(js.encode('utf-8'))
        size_kb = total_size_bytes / 1024
        
        # Générer nom de composant depuis intent
        component_name = self._generate_component_name(intent)
        
        # Créer composant avec scores par défaut (seront évalués en Phase 4)
        # Note: Component nécessite created_at comme datetime, pas Optional
        component = Component(
            name=component_name,
            sullivan_score=75.0,  # Score par défaut, sera recalculé en Phase 4
            performance_score=80,
            accessibility_score=70,
            ecology_score=75,
            popularity_score=0,  # Nouveau composant
            validation_score=80,
            size_kb=int(size_kb),
            created_at=datetime.now(),
            user_id=user_id
        )
        
        logger.info(f"Structured component: {component.name} ({component.size_kb} KB)")
        return component
    
    def _generate_component_name(self, intent: str) -> str:
        """
        Génère un nom de composant depuis l'intent.

        Args:
            intent: Intention du composant

        Returns:
            Nom de composant normalisé
        """
        # Normaliser intent en nom de composant
        name = intent.lower()
        name = re.sub(r'[^a-z0-9\s]', '', name)  # Supprimer caractères spéciaux
        name = re.sub(r'\s+', '_', name)  # Remplacer espaces par underscores
        name = name[:50]  # Limiter longueur
        
        # Ajouter préfixe si nécessaire
        if not name.startswith('component_'):
            name = f"component_{name}"
        
        return name
    
    async def _save_component_systematically(
        self,
        component: Component,
        intent: str,
        html: str,
        css: str,
        js: str,
        user_id: str
    ) -> None:
        """
        Sauvegarde systématiquement le composant généré dans LocalCache et EliteLibrary si nécessaire.

        Args:
            component: Composant structuré
            intent: Intention du composant
            html: Code HTML généré
            css: Code CSS généré
            js: Code JavaScript généré
            user_id: Identifiant utilisateur
        """
        try:
            from ..cache.local_cache import LocalCache
            from ..library.elite_library import EliteLibrary
            from ..models.sullivan_score import ELITE_THRESHOLD
            
            # Créer instances LocalCache et EliteLibrary
            local_cache = LocalCache()
            elite_library = EliteLibrary()
            
            # Sauvegarder dans LocalCache (même si score < 70)
            component_id = component.name
            cache_path = local_cache.save_component(
                component_id=component_id,
                intent=intent,
                html=html,
                css=css,
                js=js,
                component=component
            )
            
            logger.info(f"Component saved to LocalCache: {cache_path}")
            
            # Sauvegarder fichiers HTML/CSS/JS dans format exploitable
            if cache_path:
                component_dir = cache_path.parent / component_id
                component_dir.mkdir(parents=True, exist_ok=True)
                
                # Sauvegarder fichiers séparés
                (component_dir / "component.html").write_text(html, encoding='utf-8')
                (component_dir / "component.css").write_text(css, encoding='utf-8')
                (component_dir / "component.js").write_text(js, encoding='utf-8')
                
                # Créer metadata JSON avec informations complètes
                metadata = {
                    "component_id": component_id,
                    "intent": intent,
                    "scores": {
                        "sullivan_score": component.sullivan_score,
                        "performance_score": component.performance_score,
                        "accessibility_score": component.accessibility_score,
                        "ecology_score": component.ecology_score,
                        "popularity_score": component.popularity_score,
                        "validation_score": component.validation_score
                    },
                    "size_kb": component.size_kb,
                    "created_at": component.created_at.isoformat() if component.created_at else None,
                    "user_id": user_id,
                    "category": component.category,
                    "workflow": self.workflow
                }
                
                # Ajouter patterns STAR si disponibles
                try:
                    from ..intent_translator import IntentTranslator
                    intent_translator = IntentTranslator()
                    situations = intent_translator.search_situation(intent, limit=1)
                    if situations:
                        realisation = intent_translator.propagate_star(situations[0])
                        if realisation:
                            metadata["star_patterns"] = {
                                "pattern_name": situations[0].pattern_name,
                                "situation": situations[0].description,
                                "realisation": realisation.description
                            }
                except Exception as e:
                    logger.debug(f"Could not add STAR patterns to metadata: {e}")
                
                # Sauvegarder metadata
                import json
                (component_dir / "metadata.json").write_text(
                    json.dumps(metadata, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                
                logger.info(f"Component files saved to: {component_dir}")
            
            # Intégrer avec Elite Library si score >= 85
            if component.sullivan_score >= ELITE_THRESHOLD:
                try:
                    if elite_library.add(component):
                        logger.info(f"Component added to Elite Library (score: {component.sullivan_score})")
                    else:
                        logger.debug(f"Component not added to Elite Library (validation failed)")
                except Exception as e:
                    logger.warning(f"Failed to add component to Elite Library: {e}")
            
        except ImportError as e:
            logger.warning(f"LocalCache or EliteLibrary not available: {e}. Skipping systematic save.")
        except Exception as e:
            logger.error(f"Error saving component systematically: {e}", exc_info=True)


# Exemple d'utilisation
if __name__ == "__main__":
    import asyncio
    
    async def main():
        generator = ComponentGenerator(workflow="PROTO")
        
        component = await generator.generate_component(
            intent="Bouton d'appel à l'action",
            context="Bouton pour landing page SaaS",
            user_id="user_123"
        )
        
        print(f"Generated component: {component.name}")
        print(f"Size: {component.size_kb} KB")
        print(f"Sullivan score: {component.sullivan_score}")
    
    asyncio.run(main())