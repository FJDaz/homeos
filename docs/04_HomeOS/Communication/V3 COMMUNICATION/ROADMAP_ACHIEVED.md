# ROADMAP V3 — ACHIEVED (append-only)

---

### [2026-03-02] Mission 19B — SurgicalEditor JS

**ACTOR: GEMINI | MODE: CODE DIRECT / HYBRID**

- ✅ Sous-projet Node.js créé avec `acorn` (`js_parser/`).
- ✅ `ast_parser.js` développé pour extraire char-ranges (AST JS).
- ✅ Wrapper Python `SurgicalEditorJS` développé sur le modèle strict de `SurgicalEditor`.
- ✅ Remplacement astucieux par char-ranges (start_char, end_char) fonctionnel.
- ✅ `ApplyEngine` mis à jour pour router automatiquement les `.js` via le nouveau parser.
- ✅ E2E Tests validés (add_import, add_method, modify_function).

---

### [2026-03-02] Mission V3-A — Dead Code Cleanup (PARTIEL)

**ACTOR: GEMINI | MODE: CODE DIRECT**

- ✅ 20 fichiers `.generated.py` supprimés dans `Backend/Prod/sullivan/`
- ✅ `astunparse` déjà présent dans `requirements.txt` (L46)
- ⏸ `apply_generated_code()` non supprimée — appelée par proto.py / frd.py / verify_fix.py → reporté en V3-B1
- ℹ️ Régression `surgical_editor.py` détectée et corrigée (évasion \n trop agressive)
- Tests : 21/21 PASS

---

### [2026-03-02] Restructuration Architecture V3

**ACTOR: CLAUDE (git direct)**

- ✅ Branche `v3` créée depuis `idx-setup`
- ✅ `Backend/Prod/sullivan/` → `Backend/_archive/sullivan/` (git mv)
- ✅ `Backend/Prod/homeos_v2/` → `Backend/_archive/homeos_v2/` (git mv)
- ✅ `Backend/Prod/workflows/frd.py` → `Backend/_archive/`
- ✅ `Backend/Prod/workflows/verify_fix.py` → `Backend/_archive/`
- ✅ `Backend/Prod/core/apply_engine.py` commité (ApplyEngine validé)
- ✅ Tests E2E + fuzzy parser + merge fix commités
- Commit : `ae36270` — 192 fichiers bougés

---

### [2026-03-02] Repair Apply Pipeline

**ACTOR: CLAUDE + GEMINI**

- ✅ `SurgicalInstructionParser.parse_instructions()` réécrit (fuzzy parser)
  - Brace-counting, trailing commas, nested JSON, multiple blocks
- ✅ `ApplyEngine` créé — hiérarchie Surgical → Smart Overwrite → Review Fallback
- ✅ `orchestrator.py` : ancien VETO block remplacé par `ApplyEngine`
- ✅ `get_step_output()` : préfère `_code.txt` (propre) sur `.txt` (pollué)
- ✅ `merge_step_outputs_to_file()` implémentée (était un import fantôme)
- ✅ `PostApplyValidator` branché (plus dead code)
- ✅ Phase 2.5 stubbed (no-op)
- Tests : 4 fuzzy + 12 unit + 3 E2E + 2 merge = **21/21 PASS**
