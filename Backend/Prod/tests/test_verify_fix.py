"""Tests unitaires pour le workflow VerifyFix (-vfx).

Mode -vfx : exécution BUILD → validation DOUBLE-CHECK → corrections si erreurs.

Couverture :
- VerifyFixWorkflow._build_fix_plan : construction du plan de correction
- VerifyFixWorkflow._fix_context : contexte pour les corrections
- API genome : _get_minimal_genome, get_studio_genome (fallback sans 500)
- API serve : _serve_svelte_route (studio.html | studio/index.html)
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

from Backend.Prod.workflows.verify_fix import VerifyFixWorkflow
from Backend.Prod.models.plan_reader import Plan


# --- _build_fix_plan ---


def test_build_fix_plan_empty_invalid_details():
    """_build_fix_plan avec invalid_details vide retourne {}."""
    workflow = VerifyFixWorkflow()
    plan = Plan({"task_id": "test", "description": "", "steps": [], "metadata": {}})
    assert workflow._build_fix_plan(plan, []) == {}


def test_build_fix_plan_no_matching_step():
    """_build_fix_plan ignore les invalid_details sans plan_step correspondant."""
    workflow = VerifyFixWorkflow()
    plan = Plan({
        "task_id": "test",
        "description": "",
        "steps": [{"id": "step_1", "description": "", "type": "code_generation", "complexity": 0.5, "estimated_tokens": 500}],
        "metadata": {},
    })
    invalid_details = [{"step_id": "step_99", "output": "error"}]
    result = workflow._build_fix_plan(plan, invalid_details)
    assert result == {}
    assert result.get("steps", []) == []


def test_build_fix_plan_creates_fix_steps():
    """_build_fix_plan crée des steps de correction avec le bon format."""
    workflow = VerifyFixWorkflow()
    plan = Plan({
        "task_id": "test",
        "description": "",
        "steps": [{
            "id": "step_1",
            "description": "Fix X",
            "type": "refactoring",
            "complexity": 0.3,
            "estimated_tokens": 400,
            "context": {"files": ["foo.py"]},
        }],
        "metadata": {},
    })
    invalid_details = [
        {
            "step_id": "step_1",
            "output": "Code has issues",
            "pedagogical_feedback": {
                "violations": [
                    {"suggestion": "Add type hint", "issue": "Missing type"},
                ],
                "overall_feedback": "Fix types",
            },
        }
    ]
    result = workflow._build_fix_plan(plan, invalid_details)
    assert "task_id" in result
    assert "steps" in result
    assert len(result["steps"]) == 1
    step = result["steps"][0]
    assert step["id"] == "step_1_fix"
    assert step["type"] == "refactoring"
    assert "Add type hint" in step["description"]
    assert step["context"]["files"] == ["foo.py"]


def test_build_fix_plan_fallback_without_pedagogical_feedback():
    """_build_fix_plan utilise output si pas de pedagogical_feedback."""
    workflow = VerifyFixWorkflow()
    plan = Plan({
        "task_id": "test",
        "description": "",
        "steps": [{"id": "step_1", "description": "", "type": "code_generation", "complexity": 0.5, "estimated_tokens": 500}],
        "metadata": {},
    })
    invalid_details = [{"step_id": "step_1", "output": "Fix the bugs"}]
    result = workflow._build_fix_plan(plan, invalid_details)
    assert len(result["steps"]) == 1
    assert "Fix the bugs" in result["steps"][0]["description"]


# --- _fix_context ---


def test_fix_context_formats_details():
    """_fix_context formate les invalid_details pour le contexte."""
    workflow = VerifyFixWorkflow()
    details = [
        {"step_id": "step_1", "output": "Error A" * 50},
        {"step_id": "step_2", "output": "Error B"},
    ]
    ctx = workflow._fix_context(details)
    assert "step_1" in ctx
    assert "step_2" in ctx
    assert "Error A" in ctx
    assert "Error B" in ctx
    assert "Validation reported" in ctx


# --- API genome (effets efficaces) ---


def test_get_minimal_genome_structure():
    """_get_minimal_genome retourne un genome avec metadata, topology, endpoints."""
    from Backend.Prod.api import _get_minimal_genome

    genome = _get_minimal_genome()
    assert "metadata" in genome
    assert genome["metadata"].get("source") == "minimal_fallback"
    assert "topology" in genome
    assert "endpoints" in genome
    assert len(genome["endpoints"]) >= 3
    paths = [e["path"] for e in genome["endpoints"]]
    assert "/health" in paths
    assert "/studio/genome" in paths


def test_get_studio_genome_returns_json_with_endpoints():
    """get_studio_genome retourne du JSON valide avec endpoints (minimal ou fichier)."""
    from Backend.Prod.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/studio/genome")
    assert resp.status_code == 200
    data = resp.json()
    assert "endpoints" in data
    assert isinstance(data["endpoints"], list)
    assert len(data["endpoints"]) >= 1


def test_get_studio_genome_never_500():
    """get_studio_genome ne doit jamais retourner 500 (fallback minimal)."""
    from Backend.Prod.api import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    resp = client.get("/studio/genome")
    assert resp.status_code != 500


# --- API _serve_svelte_route (effets efficaces) ---


def test_serve_svelte_route_returns_none_if_build_missing(tmp_path):
    """_serve_svelte_route retourne None si svelte_build_path n'existe pas."""
    import Backend.Prod.api as api_module

    orig_path = api_module.svelte_build_path
    try:
        api_module.svelte_build_path = tmp_path / "nonexistent"
        assert api_module._serve_svelte_route("studio") is None
    finally:
        api_module.svelte_build_path = orig_path


def test_serve_svelte_route_prefers_html_over_index(tmp_path):
    """_serve_svelte_route préfère {base}.html puis {base}/index.html."""
    build = tmp_path / "build"
    build.mkdir()
    studio_html = build / "studio.html"
    studio_html.write_text("<!DOCTYPE html>")
    studio_index = build / "studio"
    studio_index.mkdir()
    (studio_index / "index.html").write_text("<!DOCTYPE html>")

    import Backend.Prod.api as api_module
    orig_path = api_module.svelte_build_path
    try:
        api_module.svelte_build_path = build
        res = api_module._serve_svelte_route("studio")
        assert res is not None
        assert "studio.html" in str(res.path) or "studio" in str(res.path)
    finally:
        api_module.svelte_build_path = orig_path


def test_serve_svelte_route_finds_index_html(tmp_path):
    """_serve_svelte_route trouve studio/index.html si studio.html absent."""
    build = tmp_path / "build"
    build.mkdir()
    studio_dir = build / "studio"
    studio_dir.mkdir()
    (studio_dir / "index.html").write_text("<!DOCTYPE html>")

    import Backend.Prod.api as api_module
    orig_path = api_module.svelte_build_path
    try:
        api_module.svelte_build_path = build
        res = api_module._serve_svelte_route("studio")
        assert res is not None
        assert (studio_dir / "index.html").exists()
    finally:
        api_module.svelte_build_path = orig_path


# --- Plan fix studio 404 (validation) ---


def test_plan_fix_studio_404_exists_and_valid():
    """Le plan plan_fix_studio_404.json existe et est valide."""
    # Backend/Prod/tests -> Backend -> Backend/Notebooks/benchmark_tasks
    plan_path = Path(__file__).resolve().parent.parent.parent / "Notebooks" / "benchmark_tasks" / "plan_fix_studio_404.json"
    if not plan_path.exists():
        pytest.skip("plan_fix_studio_404.json not found")
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    assert "task_id" in plan
    assert "steps" in plan
    assert len(plan["steps"]) >= 2
    step1 = next(s for s in plan["steps"] if s["id"] == "step_1")
    step2 = next(s for s in plan["steps"] if s["id"] == "step_2")
    assert "trailingslash" in step1["description"].lower() or "layout" in step1["description"].lower()
    assert "_serve_svelte_route" in step2["description"] or "studio" in step2["description"].lower()
