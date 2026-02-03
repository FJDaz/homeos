"""
CTO Mode - Sullivan comme Chief Technology Officer.

Transforme les demandes en langage naturel en exécutions AetherFlow.
Pas de conversation inutile - que des actions.
"""

import json
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger

from ...models.groq_client import GroqClient
from ...models.gemini_client import GeminiClient
from ...config.settings import settings


@dataclass
class CTODecision:
    """Décision du CTO Sullivan."""
    mode: str  # "proto", "prod", "designer", "frontend", "direct"
    intent: str  # Description de ce que veut l'utilisateur
    plan_required: bool
    plan_path: Optional[Path] = None
    parameters: Dict[str, Any] = None
    reasoning: str = ""  # Pourquoi ce mode


class CTOMode:
    """
    Sullivan en mode CTO - Décide et Exécute.
    
    Usage:
        cto = CTOMode()
        result = await cto.execute("Crée une page de login avec Tailwind")
        # result contient: fichiers créés, coût, temps, statut
    """
    
    def __init__(self):
        self.groq = GroqClient()
        self.gemini = GeminiClient(execution_mode="BUILD")
        self.output_dir = Path(settings.output_dir) / "cto"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, user_request: str) -> Dict[str, Any]:
        """
        Point d'entrée principal. Transforme une demande en résultat.
        
        Args:
            user_request: Demande en langage naturel
            
        Returns:
            Rapport d'exécution complet
        """
        start_time = time.time()
        
        # 1. Analyse CTO - Comprendre ce qu'il faut faire
        decision = await self._analyze_request(user_request)
        
        # 2. Exécuter selon le mode décidé
        if decision.mode == "designer":
            result = await self._run_designer_mode(decision)
        elif decision.mode == "frontend":
            result = await self._run_frontend_mode(decision)
        elif decision.mode == "proto":
            result = await self._run_proto_mode(decision)
        elif decision.mode == "prod":
            result = await self._run_prod_mode(decision)
        else:
            # Mode direct - exécution simple
            result = await self._run_direct_mode(decision)
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            "success": result.get("success", False),
            "mode": decision.mode,
            "intent": decision.intent,
            "reasoning": decision.reasoning,
            "total_time_ms": total_time,
            "result": result,
            "user_request": user_request,
        }
    
    async def _analyze_request(self, request: str) -> CTODecision:
        """
        Analyse la demande et décide quel mode utiliser.
        Comme un CTO qui reçoit une spec et choisit l'approche.
        """
        prompt = f"""Tu es le CTO d'AetherFlow. Analyse cette demande et choisis la stratégie technique.

DEMANDE: "{request}"

RÈGLES DE DÉCISION:

1. **DESIGNER** (`designer`)
   - Si l'utilisateur parle d'analyser une image, maquette, screenshot
   - Si mentionne "design", "maquette", "image", "template", "Figma"
   - → Génère: {{"mode": "designer", "image_path": "..."}}

2. **FRONTEND** (`frontend`)
   - Si demande de générer du HTML, CSS, composant UI
   - Si mentionne "page", "composant", "bouton", "formulaire", "interface"
   - Sans image à analyser (création from scratch)
   - → Génère: {{"mode": "frontend", "component_type": "...", "description": "..."}}

3. **PROTO** (`proto`)
   - Si c'est du POC, test, experimentation rapide
   - Si mentionne "test", "poc", "prototyper", "voir si ça marche"
   - Code Python/utilitaire rapide
   - → Génère: {{"mode": "proto", "plan_description": "..."}}

4. **PROD** (`prod`)
   - Si c'est du code de production, qualité enterprise
   - Si mentionne "production", "propre", "robuste", "refactor"
   - → Génère: {{"mode": "prod", "plan_description": "..."}}

5. **DIRECT** (`direct`)
   - Si c'est une question, analyse, ou tâche simple
   - Si demande d'expliquer, analyser, chercher
   - → Génère: {{"mode": "direct", "action": "..."}}

RÉPONDS UNIQUEMENT EN JSON:
```json
{{
  "mode": "designer|frontend|proto|prod|direct",
  "intent": "résumé 10 mots de la demande",
  "reasoning": "pourquoi ce mode (1 phrase)",
  "parameters": {{
    // selon le mode
  }}
}}
```

Exemples:
- "Analyse cette image docs/mockup.png" → {{"mode": "designer", "intent": "analyse maquette", "parameters": {{"image_path": "docs/mockup.png"}}}}
- "Crée une page de login" → {{"mode": "frontend", "intent": "page login", "parameters": {{"component_type": "page", "description": "login form"}}}}
- "Teste si cette API fonctionne" → {{"mode": "proto", "intent": "test API", "parameters": {{"plan_description": "Créer script de test API"}}}}
"""
        
        # Utiliser Gemini pour l'analyse (plus fiable pour la classification)
        result = await self.gemini.generate(prompt=prompt, max_tokens=1024)
        
        if not result.success or not result.code:
            # Fallback sur Groq
            result = await self.groq.generate(prompt=prompt, max_tokens=1024)
        
        try:
            # Extraire le JSON
            code = result.code or "{}"
            # Chercher le bloc JSON
            if "```json" in code:
                code = code.split("```json")[1].split("```")[0]
            elif "```" in code:
                code = code.split("```")[1].split("```")[0]
            
            data = json.loads(code.strip())
            
            return CTODecision(
                mode=data.get("mode", "direct"),
                intent=data.get("intent", request[:50]),
                plan_required=data.get("mode") in ["proto", "prod"],
                parameters=data.get("parameters", {}),
                reasoning=data.get("reasoning", "Décision par défaut"),
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse CTO decision: {e}")
            # Fallback: mode direct
            return CTODecision(
                mode="direct",
                intent=request[:50],
                plan_required=False,
                parameters={"request": request},
                reasoning="Erreur parsing, fallback mode direct",
            )
    
    async def _run_designer_mode(self, decision: CTODecision) -> Dict[str, Any]:
        """Exécute le mode DESIGNER (analyse d'image)."""
        from ..analyzer.design_analyzer_fast import analyze_image_fast
        
        params = decision.parameters
        image_path = params.get("image_path") or params.get("design")
        
        if not image_path:
            return {"success": False, "error": "Aucune image spécifiée"}
        
        image_path = Path(image_path)
        if not image_path.exists():
            # Chercher dans le projet
            base = Path("/Users/francois-jeandazin/AETHERFLOW")
            for p in [image_path, base / image_path, base / "docs" / image_path.name]:
                if p.exists():
                    image_path = p
                    break
            else:
                return {"success": False, "error": f"Image non trouvée: {image_path}"}
        
        start = time.time()
        structure = await analyze_image_fast(image_path)
        elapsed = (time.time() - start) * 1000
        
        return {
            "success": True,
            "mode": "designer",
            "image": str(image_path),
            "sections_found": len(structure.sections),
            "components_found": len(structure.components),
            "time_ms": elapsed,
            "structure": {
                "sections": structure.sections,
                "layout": structure.layout,
            }
        }
    
    async def _run_frontend_mode(self, decision: CTODecision) -> Dict[str, Any]:
        """Exécute le mode FRONTEND (génération HTML)."""
        from ...models.groq_client import GroqClient
        from ...models.gemini_client import GeminiClient

        params = decision.parameters
        description = params.get("description", params.get("intent", "composant"))
        component_type = params.get("component_type", "component")
        style = params.get("style", "minimal")

        prompt = f"""Génère un composant {component_type} en HTML avec Tailwind CSS.

Description: {description}
Style: {style}

RÈGLES:
- Utilise UNIQUEMENT Tailwind CSS
- Responsive mobile-first
- Code propre et sémantique
- Retourne UNIQUEMENT le HTML, sans markdown ni ```
"""

        start = time.time()
        provider = "groq"

        # Essayer Groq d'abord (rapide)
        groq = GroqClient()
        result = await groq.generate(prompt=prompt, max_tokens=2048)

        # Fallback sur Gemini si Groq échoue
        if not result.success:
            provider = "gemini"
            gemini = GeminiClient(execution_mode="BUILD")
            result = await gemini.generate(prompt=prompt, max_tokens=2048)

        elapsed = (time.time() - start) * 1000

        # Nettoyer le code (enlever markdown si présent)
        code = result.code if result.success else None
        if code:
            if code.startswith("```"):
                lines = code.split("\n")
                code = "\n".join(l for l in lines if not l.startswith("```"))

        # Sauvegarder le résultat
        output_file = self.output_dir / f"{component_type}_{int(time.time())}.html"
        if code:
            output_file.write_text(code, encoding="utf-8")

        return {
            "success": result.success,
            "mode": "frontend",
            "component_type": component_type,
            "output_file": str(output_file) if code else None,
            "time_ms": elapsed,
            "tokens": {"total": result.tokens_used if hasattr(result, 'tokens_used') else 0},
            "cost_usd": result.cost_usd if hasattr(result, 'cost_usd') else 0,
            "provider": provider,
            "code": code,
        }
    
    async def _run_proto_mode(self, decision: CTODecision) -> Dict[str, Any]:
        """Exécute le mode PROTO (POC rapide)."""
        # Pour l'instant, générer un plan simple et l'exécuter
        params = decision.parameters
        description = params.get("plan_description", params.get("description", "tâche"))
        
        # Créer un plan minimal
        plan = self._create_simple_plan(description, mode="proto")
        plan_path = self.output_dir / f"proto_plan_{int(time.time())}.json"
        plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        
        # Exécuter via ProtoWorkflow
        from ...workflows.proto import ProtoWorkflow
        
        workflow = ProtoWorkflow()
        result = await workflow.execute(
            plan_path=plan_path,
            output_dir=self.output_dir / f"proto_{int(time.time())}",
        )
        
        return {
            "success": result.get("success", False),
            "mode": "proto",
            "plan": str(plan_path),
            "total_time_ms": result.get("total_time_ms", 0),
            "total_cost_usd": result.get("total_cost_usd", 0),
        }
    
    async def _run_prod_mode(self, decision: CTODecision) -> Dict[str, Any]:
        """Exécute le mode PROD (qualité entreprise)."""
        params = decision.parameters
        description = params.get("plan_description", params.get("description", "tâche"))
        
        # Créer un plan
        plan = self._create_simple_plan(description, mode="prod")
        plan_path = self.output_dir / f"prod_plan_{int(time.time())}.json"
        plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        
        # Exécuter via ProdWorkflow
        from ...workflows.prod import ProdWorkflow
        
        workflow = ProdWorkflow()
        result = await workflow.execute(
            plan_path=plan_path,
            output_dir=self.output_dir / f"prod_{int(time.time())}",
        )
        
        return {
            "success": result.get("success", False),
            "mode": "prod",
            "plan": str(plan_path),
            "total_time_ms": result.get("total_time_ms", 0),
            "total_cost_usd": result.get("total_cost_usd", 0),
        }
    
    async def _run_direct_mode(self, decision: CTODecision) -> Dict[str, Any]:
        """Exécute le mode DIRECT (réponse simple via LLM)."""
        params = decision.parameters
        request = params.get("request", decision.intent)
        
        prompt = f"""Tu es Sullivan, assistant technique expert.

Demande: {request}

Réponds de manière concise et pratique. Maximum 3-4 phrases.
Si c'est une question technique, donne un exemple concret.
"""
        
        start = time.time()
        result = await self.groq.generate(prompt=prompt, max_tokens=1024)
        elapsed = (time.time() - start) * 1000
        
        return {
            "success": result.success,
            "mode": "direct",
            "response": result.code if result.success else result.error,
            "time_ms": elapsed,
        }
    
    def _create_simple_plan(self, description: str, mode: str = "proto") -> Dict[str, Any]:
        """Crée un plan minimal pour exécution."""
        return {
            "task_id": f"{mode}_{int(time.time())}",
            "description": description,
            "steps": [
                {
                    "id": "step_1",
                    "type": "code",
                    "description": description,
                    "complexity": 0.5,
                    "validation_rules": ["syntax", "style"],
                }
            ],
            "metadata": {
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "planner": "cto_mode",
                "mode": mode,
            }
        }


# Instance globale
cto_mode = CTOMode()


async def run_cto(request: str) -> Dict[str, Any]:
    """Fonction utilitaire pour exécuter le mode CTO."""
    cto = CTOMode()
    return await cto.execute(request)


__all__ = ["CTOMode", "CTODecision", "run_cto", "cto_mode"]
