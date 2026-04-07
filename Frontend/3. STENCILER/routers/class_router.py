"""
Class & Student Router — Missions 214, 215, 216, 217
Classes, roster parsing, student login, milestone detection, teacher dashboard, DNMADE evaluation.
"""

import os
import re
import json
import uuid
import logging
import unicodedata
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger("AetherFlowV3")

router = APIRouter(prefix="/api/classes")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
CLASSES_DIR = ROOT_DIR / "classes"
CLASSES_DIR.mkdir(parents=True, exist_ok=True)

# --- DB ---
from bkd_service import bkd_db_con

# --- MODELS ---
class ClassCreateRequest(BaseModel):
    name: str
    subject: str = ""

class RosterRequest(BaseModel):
    raw: str

class MilestoneUpdate(BaseModel):
    level: int

class StudentStartResponse(BaseModel):
    project_id: str
    student_id: str
    display: str

# --- HELPERS ---

def slugify(text: str) -> str:
    """NOM_Prenom → nom-prenom (lowercase, accents normalisés, espaces → tirets)."""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    text = text.lower().strip()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text.strip('-')

def parse_roster(raw: str) -> List[Dict[str, str]]:
    """
    Parse liste brute :
    BLART Samuel

    BLIN Zoé

    CALAIS Jeanne
    → [{id, display, nom, prenom}]
    """
    students = []
    # Split on lignes vides multiples
    blocks = re.split(r'\n\s*\n', raw.strip())
    for block in blocks:
        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
        if not lines:
            continue
        # Prendre la première ligne non-vide
        full_name = lines[0]
        parts = full_name.split(None, 1)
        if len(parts) == 2:
            nom, prenom = parts[0], parts[1]
        elif len(parts) == 1:
            nom, prenom = parts[0], ""
        else:
            continue

        display = full_name
        student_id = slugify(f"{nom}_{prenom}")

        students.append({
            "id": student_id,
            "display": display,
            "nom": nom,
            "prenom": prenom,
        })
    return students

def create_student_project(student: Dict[str, str], class_id: str) -> str:
    """Crée un projet HoméOS pour l'étudiant."""
    project_id = f"{class_id}-{student['id']}"
    project_path = PROJECTS_DIR / project_id
    project_path.mkdir(parents=True, exist_ok=True)

    # Créer manifest.json minimal
    manifest = {
        "name": f"Projet {student['display']}",
        "author": student['display'],
        "description": f"Projet HoméOS de {student['display']}",
        "class_id": class_id,
        "student_id": student['id'],
        "version": "0.1.0",
        "elements": [],
        "intents": []
    }
    (project_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8'
    )

    # Créer dossiers standards
    (project_path / "imports").mkdir(exist_ok=True)
    (project_path / "exports").mkdir(exist_ok=True)

    return project_id

def detect_milestone(project_id: str) -> Dict[str, Any]:
    """
    Détecte le milestone N0→N5 en inspectant le projet.
    N0: Projet créé
    N1: Manifest rédigé + maquette importée
    N2: Wire validé
    N3: Forge réussie
    N4: Sullivan interactions (logic/)
    N5: Déployé
    """
    project_path = PROJECTS_DIR / project_id
    if not project_path.exists():
        return {"level": 0, "label": "Projet inexistant"}

    manifest_path = project_path / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except Exception:
            pass

    imports_dir = project_path / "imports"
    exports_dir = project_path / "exports"
    logic_dir = project_path / "logic"

    # N1: Manifest avec titre + imports non vide
    has_manifest_title = bool(manifest.get("name") and manifest["name"] != f"Projet {manifest.get('author', '')}")
    has_imports = imports_dir.exists() and len(list(imports_dir.iterdir())) > 0
    if has_manifest_title or has_imports:
        level = 1
        label = "Maquette importée"
    else:
        level = 0
        label = "Démarré"

    # N2: Wire validé
    index_path = exports_dir / "index.json"
    if index_path.exists():
        try:
            index_data = json.loads(index_path.read_text(encoding='utf-8'))
            for imp in index_data.get("imports", []):
                if imp.get("wire_validated"):
                    level = 2
                    label = "Wire validé"
                    break
        except Exception:
            pass

    # N3: Forge réussie (HTML export avec archetype != stitch_import)
    if exports_dir.exists():
        for f in exports_dir.iterdir():
            if f.suffix == ".html":
                level = 3
                label = "Forge réussie"
                break

    # N4: Sullivan interactions (logic/ non vide)
    if logic_dir.exists() and len(list(logic_dir.iterdir())) > 0:
        level = 4
        label = "Interactions Sullivan"

    # N5: Déployé
    if manifest.get("deployed_url"):
        level = 5
        label = "Déployé"

    return {"level": level, "label": label}


# --- ROUTES ---

@router.post("")
async def create_class(req: ClassCreateRequest):
    """Créer une classe."""
    class_id = slugify(req.name)
    with bkd_db_con() as con:
        con.execute(
            "INSERT OR IGNORE INTO classes (id, name, subject) VALUES (?, ?, ?)",
            (class_id, req.name, req.subject)
        )
    return {"id": class_id, "name": req.name, "subject": req.subject}


@router.get("")
async def list_classes():
    """Liste toutes les classes."""
    with bkd_db_con() as con:
        rows = con.execute(
            "SELECT id, name, subject, created_at FROM classes ORDER BY created_at DESC"
        ).fetchall()
    return {"classes": [{"id": r[0], "name": r[1], "subject": r[2], "created_at": r[3]} for r in rows]}


@router.get("/{class_id}/students")
async def list_students(class_id: str):
    """Liste étudiants d'une classe avec milestone et project_id."""
    with bkd_db_con() as con:
        rows = con.execute(
            "SELECT id, display, nom, prenom, project_id, milestone FROM students WHERE class_id=?",
            (class_id,)
        ).fetchall()
    students = []
    for r in rows:
        milestone_info = {"level": r[5], "label": _milestone_label(r[5])}
        students.append({
            "id": r[0],
            "display": r[1],
            "nom": r[2],
            "prenom": r[3],
            "project_id": r[4],
            "milestone": milestone_info,
        })
    return {"students": students}


@router.post("/{class_id}/roster")
async def import_roster(class_id: str, req: RosterRequest):
    """Parser + importer liste brute d'étudiants."""
    students = parse_roster(req.raw)
    if not students:
        return {"imported": 0, "students": []}

    with bkd_db_con() as con:
        imported = 0
        for s in students:
            con.execute(
                "INSERT OR IGNORE INTO students (id, class_id, display, nom, prenom) VALUES (?, ?, ?, ?, ?)",
                (s["id"], class_id, s["display"], s["nom"], s["prenom"])
            )
            imported += 1

    return {"imported": imported, "students": students}


@router.post("/{class_id}/students/{student_id}/start")
async def start_student_project(class_id: str, student_id: str):
    """Créer projet HoméOS pour l'étudiant (ou reprendre existant)."""
    with bkd_db_con() as con:
        row = con.execute(
            "SELECT id, display, project_id FROM students WHERE id=? AND class_id=?",
            (student_id, class_id)
        ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    db_student_id, display, existing_project_id = row

    if existing_project_id:
        # Reprendre projet existant
        project_path = PROJECTS_DIR / existing_project_id
        if project_path.exists():
            return StudentStartResponse(
                project_id=existing_project_id,
                student_id=student_id,
                display=display
            )

    # Créer nouveau projet
    student = {"id": student_id, "display": display}
    project_id = create_student_project(student, class_id)

    with bkd_db_con() as con:
        con.execute(
            "UPDATE students SET project_id=? WHERE id=?",
            (project_id, student_id)
        )

    return StudentStartResponse(
        project_id=project_id,
        student_id=student_id,
        display=display
    )


@router.put("/{class_id}/students/{student_id}/milestone")
async def update_milestone(class_id: str, student_id: str, req: MilestoneUpdate):
    """Mettre à jour le milestone d'un étudiant."""
    level = max(0, min(5, req.level))
    with bkd_db_con() as con:
        con.execute(
            "UPDATE students SET milestone=? WHERE id=? AND class_id=?",
            (level, student_id, class_id)
        )
    return {"ok": True, "level": level, "label": _milestone_label(level)}


@router.post("/{class_id}/students/{student_id}/detect-milestone")
async def detect_student_milestone(class_id: str, student_id: str):
    """Détecter automatiquement le milestone en inspectant le projet."""
    with bkd_db_con() as con:
        row = con.execute(
            "SELECT project_id FROM students WHERE id=? AND class_id=?",
            (student_id, class_id)
        ).fetchone()

    if not row or not row[0]:
        return {"level": 0, "label": "Aucun projet"}

    milestone = detect_milestone(row[0])

    with bkd_db_con() as con:
        con.execute(
            "UPDATE students SET milestone=? WHERE id=?",
            (milestone["level"], student_id)
        )

    return milestone


# --- TEACHER DASHBOARD ---

@router.get("/{class_id}/dashboard")
async def class_dashboard(class_id: str):
    """Vue complète de la classe pour le prof."""
    with bkd_db_con() as con:
        class_row = con.execute(
            "SELECT id, name, subject FROM classes WHERE id=?", (class_id,)
        ).fetchone()
        if not class_row:
            raise HTTPException(status_code=404, detail="Classe non trouvée")

        students = con.execute(
            "SELECT id, display, nom, prenom, project_id, milestone FROM students WHERE class_id=? ORDER BY display",
            (class_id,)
        ).fetchall()

    student_list = []
    for s in students:
        milestone = detect_milestone(s[4]) if s[4] else {"level": 0, "label": "Aucun projet"}
        # Update DB if different
        if milestone["level"] != s[5]:
            with bkd_db_con() as con:
                con.execute("UPDATE students SET milestone=? WHERE id=?", (milestone["level"], s[0]))
        student_list.append({
            "id": s[0],
            "display": s[1],
            "project_id": s[4],
            "milestone": milestone,
        })

    return {
        "class": {"id": class_row[0], "name": class_row[1], "subject": class_row[2]},
        "students": student_list,
    }


# --- DNMADE EVALUATION ---

@router.post("/{class_id}/students/{student_id}/pre-eval")
async def student_pre_eval(class_id: str, student_id: str):
    """Pré-évaluation LLM DNMADE pour un étudiant."""
    with bkd_db_con() as con:
        row = con.execute(
            "SELECT project_id FROM students WHERE id=? AND class_id=?",
            (student_id, class_id)
        ).fetchone()

    if not row or not row[0]:
        raise HTTPException(status_code=404, detail="Aucun projet pour cet étudiant")

    project_id = row[0]
    project_path = PROJECTS_DIR / project_id

    # Lire manifest
    manifest = {}
    manifest_path = project_path / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        except Exception:
            pass

    # Lire HOMEO_GENOME.md si existe
    genome = ""
    genome_path = project_path / "HOMEO_GENOME.md"
    if genome_path.exists():
        genome = genome_path.read_text(encoding='utf-8')[:5000]

    # Charger référentiel DNMADE
    ref_path = CWD / "core" / "dnmade_referentiel.json"
    referentiel = {}
    if ref_path.exists():
        referentiel = json.loads(ref_path.read_text(encoding='utf-8'))

    # Pré-éval simulée (en attendant le vrai LLM)
    pre_eval = {
        "project_id": project_id,
        "student_id": student_id,
        "competences": {},
        "generated_at": "now",
    }

    # Pour chaque compétence du référentiel, évaluer basiquement
    for domain_id, domain in referentiel.get("domains", {}).items():
        for comp_id, comp in domain.get("competences", {}).items():
            # Évaluation basique basée sur le contenu du projet
            level = "non_acquis"
            justification = "Projet en cours de développement."

            if manifest.get("name") and manifest["name"] != f"Projet {manifest.get('author', '')}":
                level = "en_cours"
                justification = "Manifest rédigé, projet structuré."

            if (project_path / "imports").exists() and len(list((project_path / "imports").iterdir())) > 0:
                level = "en_cours"
                justification = "Maquette importée, travail en cours."

            if (project_path / "exports").exists() and len(list((project_path / "exports").iterdir())) > 0:
                level = "acquis"
                justification = "Export/forge réalisé."

            pre_eval["competences"][comp_id] = {
                "domain": domain_id,
                "competence": comp.get("label", comp_id),
                "niveau": level,
                "justification": justification,
            }

    return pre_eval


def _milestone_label(level: int) -> str:
    labels = {
        0: "Démarré",
        1: "Maquette importée",
        2: "Wire validé",
        3: "Forge réussie",
        4: "Interactions Sullivan",
        5: "Déployé",
    }
    return labels.get(level, "Inconnu")
