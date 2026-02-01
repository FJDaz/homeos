"""Tests unitaires pour la phase Apply : split structure/code, get_step_output, _save_step_outputs.

Couverture de la phase « revert heuristiques + séparation structure/code en deux fichiers » :
- split_structure_and_code (claude_helper)
- get_step_output (préférence _code.txt, fallback .txt)
- _save_step_outputs (orchestrator) : écriture step_X_code.txt, step_X_structure.md, step_X.txt
"""
import pytest
import tempfile
from pathlib import Path

from Backend.Prod.claude_helper import split_structure_and_code, get_step_output
from Backend.Prod.orchestrator import Orchestrator
from Backend.Prod.models.plan_reader import Plan
from Backend.Prod.models.deepseek_client import StepResult


# --- split_structure_and_code ---


def test_split_structure_and_code_empty():
    """Input vide ou whitespace : structure_part vide, code_part = raw_output."""
    assert split_structure_and_code("") == ("", "")
    assert split_structure_and_code("   \n  ") == ("", "   \n  ")


def test_split_structure_and_code_no_structure():
    """Pas d'arborescence : tout reste dans code_part."""
    raw = "def hello():\n    print('world')"
    struct, code = split_structure_and_code(raw)
    assert struct == ""
    assert code == raw


def test_split_structure_and_code_file_tree_block():
    """Bloc explicite ```file_tree ... ``` extrait en structure_part."""
    raw = """Intro text
```file_tree
src/
├── main.py
└── lib/
    └── util.py
```
```python
def main(): pass
```"""
    struct, code = split_structure_and_code(raw)
    assert "src/" in struct and "main.py" in struct and "util.py" in struct
    assert "```python" in code and "def main(): pass" in code
    assert "file_tree" not in code
    assert "├──" not in code


def test_split_structure_and_code_structure_block():
    """Bloc explicite ```structure ... ``` extrait en structure_part."""
    raw = """Before
```structure
foo/
│   bar.txt
└── baz/
```
After code"""
    struct, code = split_structure_and_code(raw)
    assert "foo/" in struct and "bar.txt" in struct
    assert "structure" not in code
    assert "After code" in code


def test_split_structure_and_code_tree_lines_unicode():
    """Lignes arborescence (├──, │, └──) sans bloc explicite : extraites en structure_part."""
    raw = """Some intro
├── a
│   ├── b
└── c
Code after
def x(): pass"""
    struct, code = split_structure_and_code(raw)
    assert "├──" in struct and "└──" in struct
    assert "def x(): pass" in code
    assert "├──" not in code


def test_split_structure_and_code_single_tree_line_ignored():
    """Une seule ligne type arborescence ne suffit pas (>= 2 requises)."""
    raw = "├── only_one_line\ncode here"
    struct, code = split_structure_and_code(raw)
    assert struct == ""
    assert "only_one_line" in code
    assert "code here" in code


# --- get_step_output ---


def test_get_step_output_prefers_code_txt(tmp_path):
    """get_step_output préfère step_X_code.txt quand il existe."""
    out = tmp_path / "step_outputs"
    out.mkdir()
    (out / "step_1.txt").write_text("full output with header\nand tree\n├── x")
    (out / "step_1_code.txt").write_text("code only content")
    assert get_step_output("step_1", str(tmp_path)) == "code only content"


def test_get_step_output_fallback_to_txt(tmp_path):
    """get_step_output utilise step_X.txt si step_X_code.txt absent."""
    out = tmp_path / "step_outputs"
    out.mkdir()
    (out / "step_1.txt").write_text("full content")
    assert get_step_output("step_1", str(tmp_path)) == "full content"


def test_get_step_output_missing_returns_none(tmp_path):
    """get_step_output retourne None si aucun fichier."""
    out = tmp_path / "step_outputs"
    out.mkdir()
    assert get_step_output("step_1", str(tmp_path)) is None
    assert get_step_output("step_99", str(tmp_path)) is None


def test_get_step_output_default_output_dir():
    """get_step_output avec output_dir par défaut 'output' (peut ne pas exister)."""
    # Sans créer de répertoire, on attend None pour un step inexistant
    result = get_step_output("step_nonexistent", "output")
    assert result is None


# --- _save_step_outputs (via Orchestrator) ---


def test_save_step_outputs_writes_code_and_structure(tmp_path):
    """_save_step_outputs écrit step_X_code.txt, step_X_structure.md si structure, step_X.txt."""
    plan = Plan({
        "task_id": "test-task",
        "description": "Test",
        "steps": [
            {
                "id": "step_1",
                "description": "Step with tree",
                "type": "code_generation",
                "complexity": 0.5,
                "estimated_tokens": 100,
                "dependencies": [],
                "validation_criteria": [],
                "context": {},
            }
        ],
        "metadata": {},
    })
    result = StepResult(
        step_id="step_1",
        success=True,
        output="""Intro
```file_tree
foo/
└── bar.py
```
```python
def bar(): pass
```""",
        tokens_used=50,
        input_tokens=10,
        output_tokens=40,
        execution_time_ms=100.0,
        error=None,
        cost_usd=0.001,
    )
    orch = Orchestrator()
    orch._save_step_outputs(tmp_path, plan, {"step_1": result})

    out = tmp_path / "step_outputs"
    assert (out / "step_1_code.txt").exists()
    assert (out / "step_1_structure.md").exists()
    assert (out / "step_1.txt").exists()

    code_content = (out / "step_1_code.txt").read_text()
    assert "def bar(): pass" in code_content
    assert "foo/" not in code_content

    struct_content = (out / "step_1_structure.md").read_text()
    assert "foo/" in struct_content and "bar.py" in struct_content

    # get_step_output doit retourner le contenu code
    assert get_step_output("step_1", str(tmp_path)) == code_content


def test_save_step_outputs_no_structure_no_structure_file(tmp_path):
    """Si pas de structure détectée, step_X_structure.md n'est pas créé."""
    plan = Plan({
        "task_id": "t2",
        "description": "No tree",
        "steps": [
            {
                "id": "step_2",
                "description": "Plain code",
                "type": "code_generation",
                "complexity": 0.3,
                "estimated_tokens": 80,
                "dependencies": [],
                "validation_criteria": [],
                "context": {},
            }
        ],
        "metadata": {},
    })
    result = StepResult(
        step_id="step_2",
        success=True,
        output="just code\nprint(1)",
        tokens_used=20,
        input_tokens=5,
        output_tokens=15,
        execution_time_ms=50.0,
        error=None,
        cost_usd=0.0,
    )
    orch = Orchestrator()
    orch._save_step_outputs(tmp_path, plan, {"step_2": result})

    out = tmp_path / "step_outputs"
    assert (out / "step_2_code.txt").exists()
    assert not (out / "step_2_structure.md").exists()
    assert (out / "step_2.txt").exists()
    assert get_step_output("step_2", str(tmp_path)) == "just code\nprint(1)"
