import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger

# Load environment
project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

PRD_TEMPLATE_FR = """# PRD : {project_name}
**Date** : {date}
**Source** : Analyse Rétro-Génome AetherFlow

## 1. Vision & Résumé Exécutif
{vision}

## 2. Manifeste FRD (Intention des élèves)
{manifest_content}

## 3. Spécifications Fonctionnelles (Intents)
{functional_requirements}

## 4. Audit Ergonomique & Gaps UX
{ergonomic_audit}

## 5. Spécifications Techniques & Design Tokens
{technical_specs}
"""

ROADMAP_TEMPLATE_FR = """# Feuille de Route (Roadmap) : {project_name}
**Date** : {date}

## Phases d'Exécution

{roadmap}

---
*Généré par AetherFlow Retro-Genome*
"""

GENERATOR_PROMPT_FR = """Tu es un Product Manager Senior et Architecte Solutions spécialisé dans le framework AetherFlow.

Basé sur l'analyse Rétro-Génome et le mapping d'intents fournis, ainsi que sur le Manifeste FRD (vision des élèves), génère un PRD professionnel et une Roadmap détaillée par phases.

MANIFESTE FRD (Vision des élèves) :
{manifest_frd}

DONNÉES D'ANALYSE UI :
{analysis_data}

OBJECTIFS :
1. Synthétiser la vision du projet en français.
2. Détailler les exigences fonctionnelles basées sur les intents mappés.
3. Intégrer les conclusions de l'audit ergonomique.
4. Définir une roadmap en 3 phases (Alpha/MVP, Beta/Affinement, V1/Hardening).

Réponds UNIQUEMENT avec un objet JSON contenant deux champs : 'prd' (markdown) et 'roadmap' (markdown).
Tout le texte doit être en FRANÇAIS.
"""

from Backend.Prod.models.gemini_client import GeminiClient

class PRDGenerator:
    def __init__(self):
        # Utilise le client natif AetherFlow
        self.client = GeminiClient(execution_mode="BUILD")

    def _load_manifest(self) -> str:
        """Charge le Manifeste FRD s'il existe."""
        manifest_path = project_root / "docs" / "02_Sullivan" / "Genome_Enrichi" / "MANIFEST_FRD.md"
        if manifest_path.exists():
            try:
                return manifest_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Impossible de lire le manifeste : {e}")
        return "Aucun manifeste FRD fourni."

    async def generate(self, data: Dict, project_name: str = "Projet Inconnu") -> Dict:
        """Génère le PRD et la Roadmap en français dans des fichiers séparés."""
        logger.info(f"📄 Génération PRD & Roadmap FR pour : {project_name}")
        
        manifest_content = self._load_manifest()
        
        try:
            result = await self.client.generate(
                prompt=GENERATOR_PROMPT_FR.format(
                    manifest_frd=manifest_content,
                    analysis_data=json.dumps(data, indent=2)
                ),
                output_constraint="JSON only (prd, roadmap)",
                max_tokens=4096
            )
            
            if not result.success:
                raise ValueError(result.error)

            content = json.loads(result.code)
        except Exception as e:
            logger.error(f"Échec de la génération avec GeminiClient : {e}")
            content = {"prd": f"Erreur de génération : {e}", "roadmap": "TBD"}
        finally:
            await self.client.close()
        
        # Sauvegarde dans des fichiers séparés
        today = datetime.now().strftime("%Y-%m-%d")
        ts = datetime.now().strftime("%H%M%S")
        safe_name = project_name.lower().replace(" ", "_")
        output_dir = project_root / "docs" / "02_Sullivan" / "Retro_Genome"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Fichier PRD
        prd_md = PRD_TEMPLATE_FR.format(
            project_name=project_name,
            date=today,
            vision="Vision déduite de la hiérarchie visuelle et du manifeste.",
            manifest_content=manifest_content[:1000] + "...", # On tronque pour le PRD si trop long
            functional_requirements=content.get('prd', 'TBD'),
            ergonomic_audit="Voir détails dans l'analyse UI.",
            technical_specs="Tokens standards AetherFlow."
        )
        prd_path = output_dir / f"PRD_{safe_name}_{ts}_FR.md"
        prd_path.write_text(prd_md, encoding="utf-8")
        
        # 2. Fichier Roadmap
        roadmap_md = ROADMAP_TEMPLATE_FR.format(
            project_name=project_name,
            date=today,
            roadmap=content.get('roadmap', 'TBD')
        )
        roadmap_path = output_dir / f"ROADMAP_{safe_name}_{ts}_FR.md"
        roadmap_path.write_text(roadmap_md, encoding="utf-8")
        
        logger.info(f"✅ PRD généré : {prd_path}")
        logger.info(f"✅ Roadmap générée : {roadmap_path}")
        
        return {
            "prd_path": str(prd_path),
            "roadmap_path": str(roadmap_path),
            "status": "ok"
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("data_json", help="Path to the combined analysis/audit JSON")
    args = parser.parse_args()
    
    with open(args.data_json, "r") as f:
        data = json.load(f)
        
    generator = PRDGenerator()
    result = generator.generate(data)
    print(f"PRD generated at: {result['prd_path']}")
