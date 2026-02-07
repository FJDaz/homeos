# 🧬 Genome Enrichi - AetherFlow Studio

**Version:** 1.0-enriched  
**Généré:** 2026-02-05T09:59:12.733381  
**Source:** ir_visuel_edite.md

---

## 📊 Stats

| Niveau | Count |
|--------|-------|
| N0 Genome | 1 |
| N1 Corps | 9 |
| N2 Organes | 20 |
| N3 Atomes | 44 |
| Coverage | 44/44 endpoints mappes |

---

## 🗺️ Structure N0-N3

### 📦 Studio `status: todo` `FRAME`

#### 📁 Reports `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `studio_reports_get__studio_reports_ir...` | 🟢 GET | `/studio/reports/ir` | `daisy_list` | 📄 list |
| `studio_reports_get__studio_reports_arbit...` | 🟢 GET | `/studio/reports/arbitrage` | `daisy_list` | 📄 list |

#### 📁 Arbitrage `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `studio_arbitrage_get__studio_arbitrage_f...` | 🟢 GET | `/studio/arbitrage/forms` | `daisy_list` | 📄 list |
| `studio_arbitrage_post__studio_validate...` | 🟡 POST | `/studio/validate` | `daisy_fieldset` | 📝 form |
| `studio_arbitrage_get__studio_typologies_...` | 🟢 GET | `/studio/typologies/arbiter` | `daisy_list` | 📄 list |
| `studio_arbitrage_get__studio_typologies_...` | 🟢 GET | `/studio/typologies/daisy` | `daisy_list` | 📄 list |

#### 📁 Genome `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `studio_genome_get__studio_distillation_e...` | 🟢 GET | `/studio/distillation/entries` | `daisy_list` | 📄 list |
| `studio_genome_get__studio_genome_summary...` | 🟢 GET | `/studio/genome/summary` | `daisy_list` | 📄 list |
| `studio_genome_post__studio_finalize...` | 🟡 POST | `/studio/finalize` | `daisy_fieldset` | 📝 form |
| `studio_genome_get__studio_genome...` | 🟢 GET | `/studio/genome` | `daisy_list` | 📄 list |

#### 📁 Navigation `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `studio_navigation_post__studio_next_curr...` | 🟡 POST | `/studio/next/{current_step}` | `daisy_fieldset` | 📝 form |
| `studio_navigation_get__studio_step_step...` | 🟢 GET | `/studio/step/{step}` | `daisy_card` | 📋 card |
| `studio_navigation_get__studio_step_5_lay...` | 🟢 GET | `/studio/step/5/layouts` | `daisy_card` | 📋 card |
| `studio_navigation_post__studio_step_5_se...` | 🟡 POST | `/studio/step/5/select-layout/{layout_id}` | `daisy_fieldset` | 📝 form |
| `studio_navigation_get__studio_zoom_level...` | 🟢 GET | `/studio/zoom/{level}/{target_id}` | `daisy_card` | 📋 card |
| `studio_navigation_get__studio_zoom_out...` | 🟢 GET | `/studio/zoom/out` | `daisy_list` | 📄 list |

#### 📁 Designer `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `studio_designer_post__studio_designer_up...` | 🟡 POST | `/studio/designer/upload` | `daisy_file_input` | 📤 upload |

#### 📁 Session `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `studio_session_get__studio_session...` | 🟢 GET | `/studio/session` | `daisy_list` | 📄 list |
| `studio_session_post__studio_session_rese...` | 🟡 POST | `/studio/session/reset` | `daisy_fieldset` | 📝 form |

#### 📁 Divers `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `studio_misc_get__studio_inference_typolo...` | 🟢 GET | `/studio/inference/{typology}` | `daisy_card` | 📋 card |
| `studio_misc_get__studio_...` | 🟢 GET | `/studio/` | `daisy_list` | 📄 list |

### 📦 Sullivan Agent `status: todo` `FRAME`

#### 📁 Chat `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `sullivan_agent_chat_post__sullivan_agent...` | 🟡 POST | `/sullivan/agent/chat` | `daisy_fieldset` | 📝 form |
| `sullivan_agent_chat_post__sullivan_agent...` | 🟡 POST | `/sullivan/agent/chat/stream` | `daisy_fieldset` | 📝 form |

#### 📁 Session `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `sullivan_agent_session_get__sullivan_age...` | 🟢 GET | `/sullivan/agent/session/{session_id}` | `daisy_card` | 📋 card |
| `sullivan_agent_session_post__sullivan_ag...` | 🟡 POST | `/sullivan/agent/session/{session_id}/clear` | `daisy_fieldset` | 📝 form |

#### 📁 Outils `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `sullivan_agent_tools_get__sullivan_agent...` | 🟢 GET | `/sullivan/agent/tools` | `daisy_list` | 📄 list |

### 📦 Execute `status: todo` `FRAME`

#### 📁 Exécution `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `execute_execution_post__execute...` | 🟡 POST | `/execute` | `daisy_fieldset` | 📝 form |

#### 📁 Recherche `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `execute_search_post__sullivan_search...` | 🟡 POST | `/sullivan/search` | `daisy_fieldset` | 📝 form |

#### 📁 Dev `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `execute_dev_post__sullivan_dev_analyze...` | 🟡 POST | `/sullivan/dev/analyze` | `daisy_fieldset` | 📝 form |

### 📦 System `status: todo` `FRAME`

#### 📁 Santé `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `system_health_get__health...` | 🟢 GET | `/health` | `daisy_stat` | 📈 stat |

### 📦 Components `status: todo` `FRAME`

#### 📁 Liste `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `components_list_get__sullivan_components...` | 🟢 GET | `/sullivan/components` | `daisy_list` | 📄 list |
| `components_list_get__components_...` | 🟢 GET | `/components/` | `daisy_list` | 📄 list |
| `components_list_get__components...` | 🟢 GET | `/components` | `daisy_list` | 📄 list |

### 📦 Divers `status: todo` `FRAME`

#### 📁 Divers `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `misc_misc_get__...` | 🟢 GET | `/` | `daisy_list` | 📄 list |
| `misc_misc_get__studio...` | 🟢 GET | `/studio` | `daisy_list` | 📄 list |
| `misc_misc_get__arbiter_showcase...` | 🟢 GET | `/arbiter-showcase` | `daisy_card` | 📋 card |
| `misc_misc_get__daisy_showcase...` | 🟢 GET | `/daisy-showcase` | `daisy_card` | 📋 card |

### 📦 HomeOS `status: todo` `FRAME`

#### 📁 Pages `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `homeos_pages_get__homeos_...` | 🟢 GET | `/homeos/` | `daisy_list` | 📄 list |
| `homeos_pages_get__homeos...` | 🟢 GET | `/homeos` | `daisy_list` | 📄 list |

### 📦 Designer `status: todo` `FRAME`

#### 📁 Analyse `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `designer_analyze_post__sullivan_designer...` | 🟡 POST | `/sullivan/designer/analyze` | `daisy_fieldset` | 📝 form |

#### 📁 Upload `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `designer_upload_post__sullivan_designer_...` | 🟡 POST | `/sullivan/designer/upload` | `daisy_file_input` | 📤 upload |

### 📦 Preview `status: todo` `FRAME`

#### 📁 Prévisualisation `COMPONENT_SET`

| Atome | Method | Endpoint | Component | Visual |
|-------|--------|----------|-----------|--------|
| `preview_preview_get__sullivan_preview_co...` | 🟢 GET | `/sullivan/preview/{component_id}` | `daisy_card` | 📋 card |
| `preview_preview_get__sullivan_preview...` | 🟢 GET | `/sullivan/preview` | `daisy_card` | 📋 card |
| `preview_preview_get__sullivan_preview_co...` | 🟢 GET | `/sullivan/preview/{component_id}/render` | `daisy_card` | 📋 card |

---

## 🌼 Mapping Composants DaisyUI

### `daisy_card` (10 utilisations)

- `GET /studio/step/{step}`
- `GET /studio/step/5/layouts`
- `GET /studio/zoom/{level}/{target_id}`
- `GET /studio/inference/{typology}`
- `GET /sullivan/agent/session/{session_id}`
- ... et 5 autres

### `daisy_fieldset` (12 utilisations)

- `POST /studio/validate`
- `POST /studio/finalize`
- `POST /studio/next/{current_step}`
- `POST /studio/step/5/select-layout/{layout_id}`
- `POST /studio/session/reset`
- ... et 7 autres

### `daisy_file_input` (2 utilisations)

- `POST /studio/designer/upload`
- `POST /sullivan/designer/upload`

### `daisy_list` (19 utilisations)

- `GET /studio/reports/ir`
- `GET /studio/reports/arbitrage`
- `GET /studio/arbitrage/forms`
- `GET /studio/typologies/arbiter`
- `GET /studio/typologies/daisy`
- ... et 14 autres

### `daisy_stat` (1 utilisations)

- `GET /health`

---

*Généré automatiquement par le système N0-N3 de Sullivan*
