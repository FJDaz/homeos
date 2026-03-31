# ROADMAP — HomeOS V3 (AetherFlow Backend)

**Vision V3 :** DevOps pipeline uniquement. Standalone. Containerisable. Multi-LLM.
**Branche active :** `v3`
**Principe :** maximum de runs via AetherFlow. CODE DIRECT réservé aux hotfixes < 10L.

---

## État branche v3 (2026-03-02)

```
Backend/Prod/
  core/          → surgical_editor.py + apply_engine.py (validés 21 tests ✅)
  workflows/     → prod.py (actif) + proto.py (à nettoyer)
  tests/         → 21 tests PASS
Backend/_archive/ → sullivan/ + homeos_v2/ + frd.py + verify_fix.py
```

---

## ✅ Phases Complètes → [ROADMAP_ACHIEVED.md](ROADMAP_ACHIEVED.md)

---

## 🚀 PHASE ACTIVE : V3-B — Kill Zombies + UnifiedExecutor

---

### Mission V3-B1 — Nettoyer proto.py + supprimer apply_generated_code()

**ACTOR: AETHERFLOW -f | MODE: BUILD | STATUS: EN ATTENTE**
**PLAN:** `V3 COMMUNICATION/plans/plan_v3b1_kill_zombies.json`
**RUN:** `cd /Users/francois-jeandazin/AETHERFLOW && source .venv/bin/activate && aetherflow --plan "V3 COMMUNICATION/plans/plan_v3b1_kill_zombies.json" --output output/v3b1/`

#### Contexte
`apply_generated_code()` dans `claude_helper.py` est du dead code depuis ApplyEngine.
Encore appelée par `proto.py` (L180, L229). `frd.py` et `verify_fix.py` = déjà archivés.
`test_new_file_creation.py` l'appelle aussi.

#### Fichiers à lire AVANT de coder
1. `Backend/Prod/workflows/proto.py` — identifier les appels à `apply_generated_code`
2. `Backend/Prod/claude_helper.py` — la fonction (L~315-393)
3. `Backend/Prod/tests/test_new_file_creation.py` — voir ce qui est testé

#### Tâches
- [ ] Dans `proto.py` : remplacer les appels `apply_generated_code()` par `ApplyEngine`
  ```python
  # AVANT
  apply_generated_code(output, target_file, step)
  # APRÈS
  from .core.apply_engine import ApplyEngine
  engine = ApplyEngine(project_root)
  engine.apply(step_id, output, [str(target_file)], step_type=step.get('type','code_generation'))
  ```
- [ ] Dans `claude_helper.py` : supprimer le bloc `apply_generated_code()` entier
- [ ] `test_new_file_creation.py` : supprimer si couvert par `test_apply_engine_e2e.py`, sinon migrer

#### Critères d'acceptation
- [ ] `grep -rn "apply_generated_code" Backend/` = zéro résultat
- [ ] `PYTHONPATH=. pytest Backend/Prod/tests/ -v` = tous PASS

---

### Mission V3-B2 — UnifiedExecutor

**ACTOR: AETHERFLOW -f | MODE: BUILD | STATUS: EN ATTENTE (après B1)**

#### Contexte
`prod.py` + `proto.py` partagent ~80% de logique. PRD V3 demande un seul exécuteur.

#### Cible : `Backend/Prod/core/unified_executor.py`
```python
class UnifiedExecutor:
    def __init__(self, mode: str = "build", project_root: Path = None):
        # mode: "fast" | "build"
    async def execute(self, plan: dict) -> dict: ...
```

#### Critères d'acceptation
- [ ] `prod.py` et `proto.py` supprimés (ou réduits à 1 ligne d'import)
- [ ] `orchestrator.py` branché sur `UnifiedExecutor`
- [ ] 21 tests PASS + nouveaux tests UnifiedExecutor

---

## 📅 Prochaines Phases

| Phase | Contenu | Dépend de |
|-------|---------|-----------|
| **V3-C** | Docker + docker-compose | V3-B |
| **V3-D** | LLMProvider ABC + adapters (hexagonale) | V3-C |
| **V3-E** | SQLite Storage (Génome + traces) | V3-D |
| **V3-F** | IDE 4 panneaux (CodeMirror + xterm.js) | V3-E |
| **V3-G** | Traces BRS (intégrer /TRACES) | V3-F |

Détails dans [ROADMAP_BACKLOG.md](ROADMAP_BACKLOG.md).
