"""Survey agent: log all system anomalies (errors, corrections, build/deploy/API, etc.).

Scope: toutes les anomalies du système — pas seulement Aetherflow. Entries are
written to a dedicated directory (settings.error_log_dir) with:
- Title, date, nature, proposed solution
- Optional: raw error, step_id, file path, source (aetherflow | cursor | claude | system)

Natures (examples): step_failed, step_exception, apply_failed, validation_failed,
build_error, deploy_error, api_error, timeout, key_missing, balance_low, cli_error,
workflow_failed, correction_applied, other.

Independence: automatic logging does NOT depend on report-correction. Reading
(aetherflow survey) shows all entries regardless of origin.
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from ..config.settings import settings


def _slug(s: str, max_len: int = 50) -> str:
    s = re.sub(r"[^\w\-]+", "_", s.strip().lower())
    return s[:max_len].rstrip("_") or "entry"


def _ensure_dir() -> Path:
    d = Path(settings.error_log_dir)
    d.mkdir(parents=True, exist_ok=True)
    readme = d / "README.md"
    if not readme.exists():
        readme.write_text(
            "# AETHERFLOW Survey — Anomalies du système\n\n"
            "**Scope** : toutes les anomalies du système (pas seulement Aetherflow).\n\n"
            "Ce répertoire compile :\n"
            "- **Erreurs Aetherflow** : step failed, apply failed, validation failed\n"
            "- **Corrections** : Cursor/Claude (`aetherflow report-correction`)\n"
            "- **Anomalies système** : build_error, deploy_error, api_error, timeout, key_missing, balance_low, cli_error, workflow_failed, etc.\n\n"
            "Chaque entrée = un fichier `.md` (titre, date, nature, proposition de solution) + `.json` (métadonnées).\n"
            "Répertoire configurable : `AETHERFLOW_ERROR_LOG_DIR` (défaut : output/aetherflow_error_log).\n",
            encoding="utf-8",
        )
    return d


def log_entry(
    title: str,
    nature: str,
    proposed_solution: str,
    *,
    source: str = "system",
    raw_error: Optional[str] = None,
    step_id: Optional[str] = None,
    file_path: Optional[str] = None,
    plan_path: Optional[str] = None,
    workflow: Optional[str] = None,
    date: Optional[datetime] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Path:
    """Write one error/correction entry to the survey directory.

    Args:
        title: Short title of the problem/correction.
        nature: Nature of the problem (e.g. step_failed, apply_failed, validation_failed, build_error, correction_applied).
        proposed_solution: Description of the fix or proposed solution.
        source: aetherflow | cursor | claude | system.
        raw_error: Optional raw error message.
        step_id: Optional step id (e.g. step_1).
        file_path: Optional file concerned.
        plan_path: Optional plan path.
        workflow: Optional workflow (PROTO, PROD, VerifyFix, RunAndFix).
        date: Optional datetime (default: now).
        extra: Optional dict for additional fields (stored in JSON sidecar).

    Returns:
        Path to the written .md file.
    """
    now = date or datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S")
    slug = _slug(title)
    base_name = f"{date_str}_{time_str}_{slug}"
    dir_path = _ensure_dir()
    md_path = dir_path / f"{base_name}.md"
    json_path = dir_path / f"{base_name}.json"

    lines = [
        f"# {title}",
        "",
        f"**Date** : {now.isoformat()}",
        f"**Nature** : {nature}",
        f"**Source** : {source}",
        "",
        "## Proposition de solution",
        "",
        proposed_solution.strip(),
        "",
    ]
    if raw_error:
        lines.extend(["## Erreur brute", "", "```", raw_error.strip(), "```", ""])
    if step_id:
        lines.append(f"- **Step** : {step_id}")
    if file_path:
        lines.append(f"- **Fichier** : {file_path}")
    if plan_path:
        lines.append(f"- **Plan** : {plan_path}")
    if workflow:
        lines.append(f"- **Workflow** : {workflow}")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    meta = {
        "title": title,
        "date": now.isoformat(),
        "nature": nature,
        "source": source,
        "step_id": step_id,
        "file_path": file_path,
        "plan_path": plan_path,
        "workflow": workflow,
    }
    if extra:
        meta["extra"] = extra
    import json
    json_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.debug(f"Error survey entry: {md_path}")
    return md_path


def log_aetherflow_error(
    title: str,
    nature: str,
    proposed_solution: str,
    *,
    raw_error: Optional[str] = None,
    step_id: Optional[str] = None,
    file_path: Optional[str] = None,
    plan_path: Optional[str] = None,
    workflow: Optional[str] = None,
) -> Path:
    """Convenience: log an error produced by Aetherflow."""
    return log_entry(
        title=title,
        nature=nature,
        proposed_solution=proposed_solution,
        source="aetherflow",
        raw_error=raw_error,
        step_id=step_id,
        file_path=file_path,
        plan_path=plan_path,
        workflow=workflow,
    )


def log_correction(
    title: str,
    nature: str,
    proposed_solution: str,
    *,
    source: str = "cursor",
    raw_error: Optional[str] = None,
    step_id: Optional[str] = None,
    file_path: Optional[str] = None,
) -> Path:
    """Convenience: log a correction applied by Cursor or Claude."""
    return log_entry(
        title=title,
        nature=nature,
        proposed_solution=proposed_solution,
        source=source,
        raw_error=raw_error,
        step_id=step_id,
        file_path=file_path,
    )


def list_entries(
    *,
    source: Optional[str] = None,
    nature: Optional[str] = None,
    limit: Optional[int] = None,
    sort_desc: bool = True,
) -> list[Dict[str, Any]]:
    """List all survey entries (anomalies, errors, corrections) from the survey directory.

    Entries are read from JSON sidecars; the .md path is inferred (same base name).
    Scope: toutes les anomalies du système (Aetherflow, corrections, build, API, etc.).

    Args:
        source: Filter by source (aetherflow | cursor | claude | system). None = all.
        nature: Filter by nature (e.g. step_failed, build_error, correction_applied). None = all.
        limit: Max number of entries to return. None = no limit.
        sort_desc: If True, newest first; else oldest first.

    Returns:
        List of dicts with keys: title, date, nature, source, step_id, file_path,
        plan_path, workflow, md_path, json_path.
    """
    import json

    dir_path = Path(settings.error_log_dir)
    if not dir_path.exists():
        return []

    result: list[Dict[str, Any]] = []
    for json_path in sorted(dir_path.glob("*.json"), reverse=sort_desc):
        try:
            meta = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if source is not None and meta.get("source") != source:
            continue
        if nature is not None and meta.get("nature") != nature:
            continue
        md_path = json_path.with_suffix(".md")
        meta["md_path"] = str(md_path) if md_path.exists() else None
        meta["json_path"] = str(json_path)
        result.append(meta)
        if limit is not None and len(result) >= limit:
            break
    return result
