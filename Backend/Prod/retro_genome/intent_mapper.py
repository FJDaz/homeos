"""
SemanticMatcher (intent_mapper.py) — Retro-Genome Pipeline (Mission 35)
Mise en tension du JSON visuel (VisualDecomposer) contre le JSON manifeste (ManifestReader).
Fonctionne avec ou sans manifeste.
"""
import json
import re
from pathlib import Path
from typing import Dict, Optional
from loguru import logger
from dotenv import load_dotenv
from Backend.Prod.retro_genome.analyzer import extract_json_robust

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

SEMANTIC_MATCHER_PROMPT = """Tu es un expert en Audit HCI et Ingénierie Pédagogique.

Ta mission est de COMPARER ce que l'étudiant a déclaré vouloir faire (MANIFESTE)
avec ce qui est RÉELLEMENT OBSERVABLE dans sa maquette (ANALYSE VISUELLE).

⚠️ LE MANIFESTE PEUT ÊTRE ABSENT : si le champ "concept" du manifeste est null ou vide,
tu dois INFÉRER les intentions probables à partir de l'analyse visuelle seule,
en t'appuyant sur les patterns UI courants ET en restant ouvert aux structures atypiques.

IDENTIFIE :
1. CORRESPONDANCES : éléments visuels qui réalisent bien une intention du manifeste.
2. GAPS : intentions déclarées dans le manifeste mais absentes ou insuffisantes visuellement.
   (Ne pas signaler les "absent_elements" : l'étudiant les a explicitement exclus.)
3. SURPLUS : éléments visuels non justifiés par le manifeste (peut être intentionnel ou un oubli).
4. SCORE DE FIDÉLITÉ : 0-100 mesurant l'alignement global entre l'intention et la réalisation.
5. SUGGESTIONS : améliorations concrètes et pédagogiquement pertinentes.

Réponds UNIQUEMENT avec un objet JSON valide. Pas de markdown, pas de commentaires.

JSON SCHEMA :
{
  "fidelity_score": 85,
  "concept_inferred": "description du concept tel qu'on peut le déduire",
  "matches": [
    {
      "visual_element_id": "id_from_visual",
      "declared_intent": "intention du manifeste correspondante ou intention inférée",
      "confidence": 0.9,
      "note": "explication courte"
    }
  ],
  "gaps": [
    {
      "intent_id": "id_or_description",
      "description": "ce qui manque",
      "severity": "critical|major|minor",
      "suggestion": "comment le corriger"
    }
  ],
  "surplus": [
    {
      "visual_element_id": "id_from_visual",
      "description": "élément non justifié par le manifeste",
      "evaluation": "positif|neutre|problématique"
    }
  ],
  "pedagogical_summary": "synthèse pédagogique en 2-3 phrases pour l'étudiant"
}"""


from Backend.Prod.models.gemini_client import GeminiClient


class IntentMapper:
    """SemanticMatcher — Mise en tension Visuel ↔ Manifeste."""

    def __init__(self):
        self.client = GeminiClient(execution_mode="FAST")

    async def map_intents(self, visual_analysis: Dict, manifest: Optional[str] = None) -> Dict:
        """
        Compare l'analyse visuelle au manifeste.
        Si manifest est None ou vide, l'inférence se fait depuis le visuel seul.
        """
        logger.info("🧠 SemanticMatcher: Matching visual ↔ manifeste...")

        # Le manifeste est du texte brut (saisi par l'étudiant)
        manifest_text = (manifest or '').strip()
        manifest_section = manifest_text if manifest_text else "(aucun manifeste fourni — inférence depuis le visuel seul)"

        # Détecter si l'analyse visuelle a échoué
        if visual_analysis.get('error'):
            logger.warning(f"[SemanticMatcher] Analyse visuelle corrompue: {visual_analysis['error']}")

        visual_json = json.dumps(visual_analysis, indent=2, ensure_ascii=False)

        prompt = (
            f"{SEMANTIC_MATCHER_PROMPT}\n\n"
            f"MANIFESTE (peut être vide si non fourni) :\n{manifest_section}\n\n"
            f"ANALYSE VISUELLE :\n{visual_json}"
        )

        try:
            result = await self.client.generate(
                prompt=prompt,
                output_constraint="JSON only",
                max_tokens=4096
            )

            if not result.success:
                raise ValueError(result.error)

            raw = result.code if result.code and result.code.strip() else getattr(result, 'text', '') or ''
            if not raw:
                raise ValueError("Réponse vide de Gemini")

            logger.debug(f"[SemanticMatcher] Raw response (first 300): {raw[:300]}")
            return extract_json_robust(raw)
        except Exception as e:
            logger.error(f"[SemanticMatcher] Failed: {e}")
            return {
                "fidelity_score": 0,
                "concept_inferred": f"Erreur d'analyse : {str(e)[:100]}",
                "matches": [],
                "gaps": [{"intent_id": "system_error", "description": str(e), "severity": "critical", "suggestion": "Vérifier les logs serveur."}],
                "surplus": [],
                "pedagogical_summary": f"Une erreur technique s'est produite : {str(e)[:150]}"
            }
        finally:
            await self.client.close()
