# Sullivan Validation UI

## Purpose

Overlay UI for validation, scoring, and action buttons during construction. Part of the Sullivan Studio UI layer (z-index 10000).

## Z-index

- **sullivan_validation** : 10000 (top layer)
- **studio_admin** : 1000
- **user_application** : 1

Defined in `homeos/config/construction_config.yaml` under `z_index_layers.sullivan_validation`.

## Integration

- Rendered as overlay above the Studio (SvelteKit) and the generated preview.
- Used during Intent Refactoring and construction steps to display validation results and allow user actions (accept, reject, refine).
- Optional Python stub: `homeos/construction/validation_ui.py` with `SullivanValidationUI.render_overlay()` for server-side or contract definition.

## Reference

- docs/04-homeos/PLAN_MODE_MANAGER.md (step 5)
- homeos/config/construction_config.yaml (z_index_layers)