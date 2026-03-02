# Backend/Prod/sullivan/modes/frontend_mode.py
"""
FrontendMode - Mode FRONTEND de Sullivan.

Orchestre intelligemment les modèles IA selon le type de tâche :
- Gemini : vision, grand contexte
- DeepSeek : génération de code
- Groq : micro-ajustements, dialogue, validation (fallback Gemini)
"""
import json
from typing import Dict, Optional, Any, List
from pathlib import Path
from loguru import logger

from ...models.frontend_router import FrontendRouter
from ...models.gemini_client import GeminiClient
from ...models.groq_client import GroqClient
from ...models.deepseek_client import DeepSeekClient
from ...models.base_client import GenerationResult
from ..analyzer.design_analyzer import DesignAnalyzer, DesignStructure
from ..knowledge.knowledge_base import KnowledgeBase
from ..analyzer.design_principles_extractor import DesignPrinciplesExtractor
from ...models.agent_router import AgentRouter


class FrontendMode:
    """
    Mode FRONTEND de Sullivan - Gère les workflows liés à l'interface utilisateur,
    incluant l'analyse de design, la génération de composants, le raffinement
    de styles, le dialogue et la validation d'homéostasie.
    """

    def __init__(
        self,
        frontend_router: Optional[FrontendRouter] = None,
        gemini_client: Optional[GeminiClient] = None,
        groq_client: Optional[GroqClient] = None,
        deepseek_client: Optional[DeepSeekClient] = None,
    ):
        """
        Initialise FrontendMode avec les clients IA.

        Args:
            frontend_router: Router pour sélection du provider (optionnel)
            gemini_client: Client Gemini (optionnel)
            groq_client: Client Groq (optionnel)
            deepseek_client: Client DeepSeek (optionnel)
        """
        self.router = frontend_router or FrontendRouter()
        self.gemini = gemini_client or GeminiClient(execution_mode="BUILD")
        self.groq = groq_client or GroqClient()
        self.deepseek = deepseek_client or DeepSeekClient()

        agent_router = AgentRouter(execution_mode="BUILD")
        self.knowledge_base = KnowledgeBase()
        self.design_analyzer = DesignAnalyzer(
            agent_router=agent_router,
            knowledge_base=self.knowledge_base,
        )
        self.design_principles_extractor = DesignPrinciplesExtractor(
            agent_router=agent_router,
            gemini_client=self.gemini,
        )

        logger.info("FrontendMode initialized")

    async def analyze_design(self, image_path: Path) -> Dict[str, Any]:
        """
        Analyse un design avec Gemini (via DesignAnalyzer).

        Args:
            image_path: Chemin vers l'image (PNG/JPG/SVG)

        Returns:
            Structure de design en dictionnaire (sections, components, layout, hierarchy)
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Analyzing design: {image_path}")
        structure = await self.design_analyzer.analyze_image(image_path)
        return structure.to_dict()

    async def generate_components(
        self,
        design_structure: Dict[str, Any],
        genome: Optional[Dict[str, Any]],
        webography: str,
        context_size: Optional[int] = None,
    ) -> str:
        """
        Génère les composants HTML selon design_structure, genome et webographie.
        Utilise Gemini si context_size > 50000, sinon DeepSeek (via FrontendRouter).

        Args:
            design_structure: Structure de design (sections, components, layout)
            genome: Structure frontend optionnelle (Miroir)
            webography: Références webdesign
            context_size: Taille du contexte en tokens (optionnel)

        Returns:
            HTML généré (string)
        """
        if context_size is None:
            payload = json.dumps({"design_structure": design_structure, "genome": genome})
            context_size = len(payload) + len(webography)

        provider = self.router.get_provider_for_task(
            task_type="generate_components/generate_html",
            context_size=context_size,
        )

        prompt = (
            "Contexte: "
            + json.dumps({"design_structure": design_structure, "genome": genome or {}})
            + ". Webographie: "
            + webography
            + ". Instruction: Générez un document HTML/CSS/JS complet single-file brutalist."
        )
        if len(prompt) > 50000:
            prompt = prompt[:50000] + "..."

        client = self.gemini if provider == "gemini" else self.deepseek
        result = await client.generate(
            prompt,
            context=None,
            output_constraint="Code only",
            max_tokens=16384,
        )

        if not result.success or not result.code:
            raise RuntimeError(result.error or f"{provider} generation failed")

        return self._extract_html(result.code)

    async def refine_style(self, html_fragment: str, instruction: str) -> str:
        """
        Raffine le style d'un fragment HTML selon l'instruction.
        Utilise Groq (fallback Gemini).

        Args:
            html_fragment: Fragment HTML à modifier
            instruction: Instruction de raffinement

        Returns:
            HTML raffiné
        """
        provider = self.router.get_provider_for_task(
            task_type="refine_style/micro_adjustment"
        )
        client = self.groq if provider == "groq" else self.gemini

        prompt = f"Fragment HTML:\n{html_fragment}\n\nInstruction: {instruction}\n\nRetourne uniquement le HTML modifié."
        result = await client.generate(
            prompt,
            output_constraint="Code only",
            max_tokens=8192,
        )

        if not result.success or not result.code:
            raise RuntimeError(result.error or f"{provider} refine failed")

        return self._extract_html(result.code)

    async def dialogue(
        self,
        message: str,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Dialogue conversationnel. Utilise Groq (fallback Gemini).

        Args:
            message: Message utilisateur
            session_context: Contexte de session optionnel

        Returns:
            Réponse du modèle
        """
        provider = self.router.get_provider_for_task(task_type="dialogue/chat")
        client = self.groq if provider == "groq" else self.gemini

        context_str = ""
        if session_context:
            context_str = f"\nContexte: {json.dumps(session_context)}"

        prompt = f"{message}{context_str}"
        result = await client.generate(prompt, max_tokens=2048)

        if not result.success:
            raise RuntimeError(result.error or f"{provider} dialogue failed")

        return result.code or ""

    async def validate_homeostasis(self, json_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide l'homéostasie d'un payload JSON.
        Utilise Groq (fallback Gemini).

        Args:
            json_payload: Payload à valider

        Returns:
            Résultat de validation (valid: bool, issues: list, etc.)
        """
        provider = self.router.get_provider_for_task(
            task_type="validate_homeostasis/validation"
        )
        client = self.groq if provider == "groq" else self.gemini

        prompt = (
            "Valide ce payload JSON pour l'homéostasie (cohérence, complétude). "
            f"Payload: {json.dumps(json_payload)}\n\n"
            "Retourne un JSON avec: {\"valid\": bool, \"issues\": [...], \"suggestions\": [...]}"
        )
        result = await client.generate(
            prompt,
            output_constraint="JSON only",
            max_tokens=1024,
        )

        if not result.success or not result.code:
            raise RuntimeError(result.error or f"{provider} validation failed")

        try:
            return json.loads(self._extract_json(result.code))
        except json.JSONDecodeError as e:
            logger.warning(f"Validation response not valid JSON: {e}")
            return {"valid": False, "issues": [str(e)], "suggestions": []}

    @staticmethod
    def _extract_html(raw: str) -> str:
        """Extrait le HTML du output modèle (strip ```html ... ``` si présent)."""
        import re

        s = raw.strip()
        m = re.search(r"```(?:html)?\s*([\s\S]*?)\s*```", s)
        if m:
            return m.group(1).strip()
        return s

    @staticmethod
    def _extract_json(raw: str) -> str:
        """Extrait le JSON du output modèle (strip ```json ... ``` si présent)."""
        import re

        s = raw.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s)
        if m:
            return m.group(1).strip()
        return s
