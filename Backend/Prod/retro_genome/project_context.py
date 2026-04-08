"""
ProjectContext — M226
Contexte projet canonique injecté dans tous les appels LLM.
Agrège manifest, genome, PRD, design system, sujet DNMADE, référentiel.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("AetherFlow.ProjectContext")

# --- PATHS ---
PROJECTS_DIR = Path(__file__).parent.parent.parent.parent / "projects"
CLASSES_DIR = Path(__file__).parent.parent.parent.parent / "classes"
ROOT_DIR = Path(__file__).parent.parent.parent.parent
CONSTITUTION_DIR = ROOT_DIR / "Frontend" / "1. CONSTITUTION"


class ProjectContext:
    def __init__(self, project_id: str = None, class_id: str = None, student_id: str = None):
        self.project_id = project_id
        self.class_id = class_id
        self.student_id = student_id
        self._cache = None

    def load(self) -> str:
        """Charge et formate toutes les sources en un bloc texte pour le prompt."""
        if self._cache:
            return self._cache

        sections = []

        # 1. Manifest
        if self.project_id:
            manifest_path = PROJECTS_DIR / self.project_id / "manifest.json"
            manifest = self._read_json(manifest_path)
            if manifest:
                sections.append(self._format_manifest(manifest))

            # 2. Genome
            genome = self._read_json(PROJECTS_DIR / self.project_id / "genome.json")
            if genome:
                sections.append(f"GÉNOME PROJET:\n{json.dumps(genome, ensure_ascii=False, indent=2)[:2000]}")

            # 3. Dernier PRD
            prd = self._latest_prd()
            if prd:
                sections.append(f"PRD VALIDÉ:\n{prd[:3000]}")

            # 4. Design system projet ou HoméOS global
            design = self._read_file(PROJECTS_DIR / self.project_id / "design.md") \
                     or self._read_file(CONSTITUTION_DIR / "DESIGN.md")
            if design:
                sections.append(f"DESIGN SYSTEM:\n{design[:1500]}")

        # 5. Sujet DNMADE si class_id
        if self.class_id:
            sujet = self._latest_subject()
            if sujet:
                sections.append(f"SUJET DNMADE:\n{sujet}")
            ref = self._load_dnmade_referentiel()
            if ref:
                sections.append(f"RÉFÉRENTIEL DNMADE:\n{ref}")

        self._cache = "\n\n---\n\n".join(sections) if sections else ""
        return self._cache

    def as_system_prefix(self) -> str:
        """Retourne le préfixe système à injecter avant tout prompt LLM."""
        ctx = self.load()
        if not ctx:
            return ""
        return (
            "CONTEXTE PROJET — respecte ces règles IMPÉRATIVEMENT avant de répondre.\n"
            "Ne propose rien qui contredise le manifest, le design system ou le PRD validé.\n\n"
            + ctx + "\n\n---\n\n"
        )

    def to_dict(self) -> dict:
        """Retourne le contexte structuré (pour API)."""
        return {
            "project_id": self.project_id,
            "class_id": self.class_id,
            "student_id": self.student_id,
            "context_text": self.load(),
            "has_context": bool(self.load())
        }

    # --- HELPERS ---

    def _read_json(self, path: Path) -> Optional[dict]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            logger.warning(f"ProjectContext: failed to read {path}: {e}")
        return None

    def _read_file(self, path: Path) -> Optional[str]:
        try:
            if path.exists():
                return path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"ProjectContext: failed to read {path}: {e}")
        return None

    def _format_manifest(self, manifest: dict) -> str:
        lines = ["MANIFEST PROJET:"]
        if manifest.get("name"):
            lines.append(f"Nom: {manifest['name']}")
        if manifest.get("description"):
            lines.append(f"Description: {manifest['description']}")
        if manifest.get("stitch_project_id"):
            lines.append(f"Stitch Project ID: {manifest['stitch_project_id']}")
        screens = manifest.get("screens", [])
        if screens:
            lines.append(f"Écrans ({len(screens)}):")
            for s in screens[:10]:
                lines.append(f"  - {s.get('name', 'unknown')} ({s.get('archetype', '')})")
        intents = manifest.get("intents", [])
        if intents:
            lines.append(f"Intentions ({len(intents)}):")
            for i in intents[:5]:
                lines.append(f"  - {i.get('label', i.get('id', 'unknown'))}")
        return "\n".join(lines)

    def _latest_prd(self) -> Optional[str]:
        """Trouve le PRD le plus récent dans exports/."""
        if not self.project_id:
            return None
        exports_dir = PROJECTS_DIR / self.project_id / "exports"
        if not exports_dir.exists():
            return None
        prd_files = sorted(exports_dir.glob("PRD_*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not prd_files:
            return None
        try:
            return prd_files[0].read_text(encoding='utf-8')
        except Exception:
            return None

    def _latest_subject(self) -> Optional[str]:
        """Trouve le dernier sujet DNMADE de la classe."""
        if not self.class_id:
            return None
        subjects_dir = CLASSES_DIR / self.class_id / "subjects"
        if not subjects_dir.exists():
            return None
        subject_files = sorted(subjects_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not subject_files:
            return None
        try:
            data = json.loads(subject_files[0].read_text(encoding='utf-8'))
            parts = []
            if data.get("title"):
                parts.append(f"Titre: {data['title']}")
            if data.get("problematique"):
                parts.append(f"Problématique: {data['problematique']}")
            if data.get("contexte"):
                parts.append(f"Contexte: {data['contexte']}")
            if data.get("parties"):
                parts.append(f"Parties ({len(data['parties'])}):")
                for p in data['parties']:
                    parts.append(f"  - {p.get('titre', '')}: {p.get('description', '')}")
            if data.get("livrables"):
                parts.append(f"Livrables: {', '.join(data['livrables'])}")
            if data.get("evaluation", {}).get("modalite"):
                parts.append(f"Évaluation: {data['evaluation']['modalite']}")
            return "\n".join(parts)
        except Exception:
            return None

    def _load_dnmade_referentiel(self) -> str:
        """Charge le référentiel DNMADE."""
        ref_path = ROOT_DIR / "Frontend" / "3. STENCILER" / "core" / "dnmade_referentiel.json"
        if not ref_path.exists():
            return ""
        try:
            data = json.loads(ref_path.read_text(encoding='utf-8'))
            lines = []
            for domain_id, domain in data.get("domains", {}).items():
                lines.append(f"Domaine {domain_id} -- {domain.get('label', '')}:")
                for comp_id, comp in domain.get("competences", {}).items():
                    lines.append(f"  {comp_id} : {comp.get('label', '')}")
            return "\n".join(lines)
        except Exception:
            return ""
