"""
ManifestReader — Retro-Genome Pipeline (Mission 35)
Lit un manifeste texte libre (intention d'un étudiant) et extrait un JSON sémantique structuré.
"""
import json
import re
from pathlib import Path
from typing import Dict
from loguru import logger
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

MANIFEST_PROMPT = """Tu es un expert en Ingénierie Pédagogique et Analyse HCI.
Ta mission est d'extraire les INTENTIONS DÉCLARÉES d'un manifeste étudiant décrivant un projet d'interface.

Le manifeste peut décrire aussi bien une UI classique (dashboard, e-commerce, app mobile) qu'un système HCI
expérimental (carré magique, triangle de Pascal, diagramme de Venn, contrainte péréquienne...).
Ne projette aucun pré-supposé. Lis ce qui est écrit.

EXTRAIS :
1. Le concept central de l'interface (en une phrase).
2. Les règles logiques ou contraintes formelles déclarées.
3. Les zones ou composants mentionnés et leur rôle déclaré.
4. Les interactions ou flux déclarés.
5. Les éléments que l'étudiant dit explicitement ne PAS avoir encore réalisés (absent_elements).
6. Les références théoriques, artistiques ou techniques citées.

Réponds UNIQUEMENT avec un objet JSON valide. Pas de markdown, pas de commentaires.

JSON SCHEMA :
{
  "project_title": "string ou null",
  "concept": "description synthétique du paradigme ou de l'intention principale",
  "rules": ["règle logique 1", "règle logique 2"],
  "declared_zones": [
    {
      "id": "slug",
      "name": "nom",
      "role": "ce que fait cette zone selon le manifeste"
    }
  ],
  "declared_interactions": ["interaction 1", "interaction 2"],
  "absent_elements": ["élément non encore réalisé 1"],
  "references": ["référence théorique ou formelle"]
}"""

from Backend.Prod.models.gemini_client import GeminiClient


class ManifestReader:
    def __init__(self):
        self.client = GeminiClient(execution_mode="FAST")

    async def read_manifest(self, text: str) -> Dict:
        """Lit un manifeste texte libre et retourne un JSON structuré."""
        if not text or not text.strip():
            logger.warning("📄 Empty manifeste received — returning empty intent structure.")
            return self._empty_manifest()

        logger.info("📄 Reading Student Manifeste (Retro-Genome)...")

        try:
            result = await self.client.generate(
                prompt=f"{MANIFEST_PROMPT}\n\nMANIFESTE :\n{text}",
                output_constraint="JSON only",
                max_tokens=2048
            )

            if not result.success:
                raise ValueError(result.error)

            content = result.code
            match = re.search(r'(\{.*\})', content, re.DOTALL)
            if match:
                content = match.group(1)

            return json.loads(content)
        except Exception as e:
            logger.error(f"[ManifestReader] Failed: {e}")
            return {"error": str(e)}
        finally:
            await self.client.close()

    @staticmethod
    def _empty_manifest() -> Dict:
        return {
            "project_title": None,
            "concept": None,
            "rules": [],
            "declared_zones": [],
            "declared_interactions": [],
            "absent_elements": [],
            "references": []
        }
