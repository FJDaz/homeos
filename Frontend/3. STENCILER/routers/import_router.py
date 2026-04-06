from pathlib import Path
import json
import logging
import unicodedata
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from bs4 import BeautifulSoup

logger = logging.getLogger("ImportRouter")

CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
STATIC_DIR_PATH = CWD / "static"

router = APIRouter()

_NEW_IMPORTS_COUNT = 0


def get_project_imports_dir():
    from bkd_service import get_active_project_path
    d = get_active_project_path() / "imports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_active_project_path():
    from bkd_service import get_active_project_path
    return get_active_project_path()


def ensure_ids(html: str) -> str:
    """Mission 187: Injecte ou renomme les IDs pour qu'ils soient exploitables."""
    import re
    import unicodedata

    def slugify(text: str, max_len: int = 30) -> str:
        text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode()
        text = re.sub(r"[^\w\s-]", "", text).strip().lower()
        text = re.sub(r"[\s_]+", "-", text)
        return text[:max_len].rstrip("-")

    TAG_PREFIXES = {
        "button": "btn", "a": "lnk", "input": "inp", "form": "frm",
        "select": "sel", "summary": "tog", "textarea": "inp",
        "header": "hdr", "footer": "ftr", "nav": "nav", "section": "sec"
    }

    soup = BeautifulSoup(html, "html.parser")
    counters = {}

    targets = soup.find_all(["button", "a", "input", "form", "select", "summary", "textarea", "header", "footer", "nav", "section", "h1", "h2", "h3"])

    for el in targets:
        current_id = el.get("id", "")
        is_generic = not current_id or re.match(r"^(el|div|section|block|id|tmp|gen)-\d+$", current_id) or len(current_id) < 3

        if is_generic:
            prefix = TAG_PREFIXES.get(el.name, "el")
            raw_text = el.get_text(strip=True)[:40] or el.get("placeholder", "") or el.get("aria-label", "") or el.get("name", "")

            if raw_text:
                slug = slugify(raw_text)
                new_id = f"{prefix}-{slug}" if slug else f"{prefix}-{counters.get(prefix, 0)+1}"
            else:
                counters[prefix] = counters.get(prefix, 0) + 1
                new_id = f"{prefix}-{counters[prefix]}"

            base_id = new_id
            c = 1
            while soup.find(id=new_id):
                new_id = f"{base_id}-{c}"
                c += 1

            el["id"] = new_id
            logger.info(f"Ensured ID: {current_id} -> {new_id}")

    return str(soup)


@router.post("/api/import/upload")
async def import_upload(file: UploadFile = File(...), filename: str = Form("")):
    """
    Mission 100-bis: Generic upload endpoint for multi-format imports.
    Supports: ZIP (Stitch), TSX/TS (React), HTML/CSS/JS files.
    """
    exports_dir = get_project_imports_dir()
    exports_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    safe_name = (filename or file.filename or "upload").replace(" ", "_").replace("/", "_")[:128]
    timestamp_str = datetime.now().strftime("%H%M%S")
    today_str = datetime.now().strftime("%Y-%m-%d")

    ext = Path(file.filename).suffix.lower() if file.filename else ""
    stored_filename = f"IMPORT_{safe_name}_{timestamp_str}{ext}"

    today_dir = exports_dir / today_str
    today_dir.mkdir(parents=True, exist_ok=True)
    file_path = today_dir / stored_filename

    content = await file.read()

    # MISSION 187 : Nettoyage & IDs semantiques a l'import
    if ext == ".html":
        try:
            html_content = content.decode("utf-8")
            html_content = ensure_ids(html_content)
            content = html_content.encode("utf-8")
        except Exception as e:
            logger.error(f"Failed to ensure IDs during import: {e}")

    file_path.write_bytes(content)

    # Update index.json
    index_path = exports_dir / "index.json"
    try:
        if index_path.exists():
            index_data = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            index_data = {"imports": []}

        # Pour les HTML uploades : copier directement dans templates/ et setter html_template
        html_template_name = None
        if ext == ".html":
            templates_dir = STATIC_DIR_PATH / "templates"
            templates_dir.mkdir(parents=True, exist_ok=True)
            tpl_filename = f"import_{today_str}_{timestamp_str}_{safe_name}.html"
            tpl_path = templates_dir / tpl_filename
            tpl_path.write_bytes(content)
            html_template_name = tpl_filename

            # Mission 151: Auto-generated Wire Manifest (Static DOM parsing)
            try:
                from Backend.Prod.retro_genome.archetype_detector import ArchetypeDetector

                # Inference statique (No browser)
                soup = BeautifulSoup(content, "lxml") or BeautifulSoup(content, "html.parser")

                # Extraction des elements structurants
                elements = []
                items = soup.find_all(["section", "nav", "header", "footer", "div", "button", "h1", "h2", "h3", "p", "input"])

                for idx, el in enumerate(items[:35]):  # Limite 35
                    el_id = el.get("id") or el.get("data-id") or f"el_{idx}"
                    text = el.get_text(strip=True)[:50]
                    role = el.get("data-role") or (el.get("data-af-region") if el.has_attr("data-af-region") else el.name)

                    elements.append({
                        "id": el_id,
                        "name": el.name.upper(),
                        "role": role,
                        "text": text,
                        "visual_hint": el.get("class", [""])[0] if el.get("class") else ""
                    })

                # Archetype Detection
                detector = ArchetypeDetector()
                archetype = detector.detect({"elements": elements})

                # Mapping Components (WsWire.js compatible)
                components = []
                for idx, el in enumerate(elements):
                    components.append({
                        "id": el["id"],
                        "name": el["name"],
                        "role": el["role"],
                        "z_index": idx + 1,
                        "text": el["text"]
                    })

                final_manifest = {
                    "import_id": f"{today_str}_{timestamp_str}_{safe_name}",
                    "archetype": archetype,
                    "components": components,
                    "screens": [{"id": "main", "name": "Main Screen", "components": components}],
                    "generated_at": datetime.now().isoformat(),
                    "source": "M151 Static Inference"
                }

                # Sauvegarde project-specific
                from bkd_service import get_active_project_path
                prj_path = get_active_project_path()
                if prj_path:
                    m_dir = prj_path / "manifests"
                    m_dir.mkdir(parents=True, exist_ok=True)
                    m_file = m_dir / f"manifest_{today_str}_{timestamp_str}_{safe_name}.json"
                    m_file.write_text(json.dumps(final_manifest, indent=2, ensure_ascii=False))
                    logger.info(f"M151: Manifest generated statically for {tpl_filename}")
            except Exception as e:
                logger.error(f"M151: Static inference failed: {e}")

        new_entry = {
            "id": f"{today_str}_{timestamp_str}_{safe_name}",
            "name": Path(safe_name).stem + ext,
            "timestamp": datetime.now().isoformat(),
            "file_path": f"{today_str}/{stored_filename}",
            "date": today_str,
            "type": ext.lstrip(".") if ext else "unknown",
            "archetype_id": "multi_format_import",
            "archetype_label": "import multi-format",
            "html_template": html_template_name,
            "elements_count": 0
        }
        index_data["imports"].insert(0, new_entry)
        index_data["imports"] = index_data["imports"][:50]
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        logger.error(f"[Import] Failed to update index.json: {e}")

    logger.info(f"[Import] File saved: {file_path}")

    global _NEW_IMPORTS_COUNT
    _NEW_IMPORTS_COUNT += 1

    return {"status": "ok", "import": new_entry}


@router.delete("/api/imports/{import_id}")
async def import_delete(import_id: str):
    """
    Mission 125: Suppression d'un import.
    Supprime l'entree de index.json et les fichiers sur disque.
    """
    exports_dir = get_project_imports_dir()
    index_path = exports_dir / "index.json"

    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Index not found")

    try:
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        imports = index_data.get("imports", [])

        # Support NFC normalization for IDs
        req_id_nfc = unicodedata.normalize("NFC", import_id)

        target_index = -1
        target_entry = None

        for i, entry in enumerate(imports):
            if unicodedata.normalize("NFC", entry.get("id", "")) == req_id_nfc:
                target_index = i
                target_entry = entry
                break

        if target_index == -1:
            raise HTTPException(status_code=404, detail=f"Import {import_id} not found")

        # Suppression des fichiers physiques
        paths_to_check = [target_entry.get("svg_path"), target_entry.get("file_path")]
        for rel_p in paths_to_check:
            if rel_p:
                abs_p = exports_dir / rel_p
                if abs_p.exists():
                    try:
                        abs_p.unlink()
                        logger.info(f"[Import] Deleted physical file: {abs_p}")
                    except Exception as e:
                        logger.warning(f"[Import] Failed to unlink {abs_p}: {e}")

        # Retrait de l'index
        imports.pop(target_index)
        index_data["imports"] = imports
        index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info(f"[Import] Successfully deleted import entry: {import_id}")
        return {"status": "deleted", "id": import_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Import] Deletion crash: {e}")
        raise HTTPException(status_code=500, detail=str(e))
