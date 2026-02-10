# 📋 Intent Revue (IR) - AetherFlow Studio

**Généré le:** 2026-02-05T08:41:29.028020+00:00  
**Version:** 0.1.0  
**Intent:** PaaS_Studio

---

## 🗺️ Topologie

```
Brainstorm → Back → Front → Deploy
```

---

## 🔌 Endpoints (44)

| Méthode | Path | UI Hint | 🎨 Visuel | Composant DaisyUI |
|---------|------|---------|-----------|-------------------|
| 🟢 GET | `/studio/reports/ir` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio/reports/arbitrage` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio/arbitrage/forms` | generic | 📄 list | `daisy_list` |
| 🟡 POST | `/studio/validate` | generic | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/studio/distillation/entries` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio/genome/summary` | generic | 📄 list | `daisy_list` |
| 🟡 POST | `/studio/next/{current_step}` | generic | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/studio/step/{step}` | detail | 📋 card | `daisy_card` |
| 🟢 GET | `/studio/step/5/layouts` | generic | 📋 card | `daisy_card` |
| 🟡 POST | `/studio/step/5/select-layout/{layout_id}` | generic | 📝 form | `daisy_fieldset` |
| 🟡 POST | `/studio/designer/upload` | form | 📤 upload | `daisy_file_input` |
| 🟢 GET | `/studio/zoom/{level}/{target_id}` | detail | 📋 card | `daisy_card` |
| 🟡 POST | `/studio/finalize` | generic | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/studio/zoom/out` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio/session` | generic | 📄 list | `daisy_list` |
| 🟡 POST | `/studio/session/reset` | generic | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/studio/typologies/arbiter` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio/typologies/daisy` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio/inference/{typology}` | detail | 📋 card | `daisy_card` |
| 🟡 POST | `/sullivan/agent/chat` | generic | 📝 form | `daisy_fieldset` |
| 🟡 POST | `/sullivan/agent/chat/stream` | generic | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/sullivan/agent/session/{session_id}` | detail | 📋 card | `daisy_card` |
| 🟡 POST | `/sullivan/agent/session/{session_id}/clear` | generic | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/sullivan/agent/tools` | generic | 📄 list | `daisy_list` |
| 🟡 POST | `/execute` | form | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/health` | status | 📈 stat | `daisy_stat` |
| 🟢 GET | `/studio/genome` | generic | 📄 list | `daisy_list` |
| 🟡 POST | `/sullivan/search` | dashboard | 📝 form | `daisy_fieldset` |
| 🟢 GET | `/sullivan/components` | dashboard | 📄 list | `daisy_list` |
| 🟢 GET | `/` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio/` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/studio` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/homeos/` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/homeos` | generic | 📄 list | `daisy_list` |
| 🟢 GET | `/components/` | dashboard | 📄 list | `daisy_list` |
| 🟢 GET | `/components` | dashboard | 📄 list | `daisy_list` |
| 🟢 GET | `/arbiter-showcase` | generic | 📋 card | `daisy_card` |
| 🟢 GET | `/daisy-showcase` | generic | 📋 card | `daisy_card` |
| 🟡 POST | `/sullivan/dev/analyze` | form | 📝 form | `daisy_fieldset` |
| 🟡 POST | `/sullivan/designer/analyze` | form | 📝 form | `daisy_fieldset` |
| 🟡 POST | `/sullivan/designer/upload` | form | 📤 upload | `daisy_file_input` |
| 🟢 GET | `/sullivan/preview/{component_id}` | dashboard | 📋 card | `daisy_card` |
| 🟢 GET | `/sullivan/preview` | generic | 📋 card | `daisy_card` |
| 🟢 GET | `/sullivan/preview/{component_id}/render` | dashboard | 📋 card | `daisy_card` |


---

## 🎨 Détail par Catégorie Visuelle

### 👁️ Data Display (30 endpoints)

**GET** `/studio/reports/ir`
- **Summary:** Get Ir Report
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/reports/arbitrage`
- **Summary:** Get Arbitrage Report
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/arbitrage/forms`
- **Summary:** Get Arbitrage Forms
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/distillation/entries`
- **Summary:** Get Distillation Entries
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/genome/summary`
- **Summary:** Get Genome Summary
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/step/{step}`
- **Summary:** Get Step Fragment
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/studio/step/5/layouts`
- **Summary:** Get Step 5 Layouts
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/studio/zoom/{level}/{target_id}`
- **Summary:** Handle Zoom
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/studio/zoom/out`
- **Summary:** Handle Zoom Out
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/session`
- **Summary:** Get Session
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/typologies/arbiter`
- **Summary:** Get Arbiter Typologies
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/typologies/daisy`
- **Summary:** Get Daisy Typologies
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/inference/{typology}`
- **Summary:** Get Inference Results
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/sullivan/agent/session/{session_id}`
- **Summary:** Get Session
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/sullivan/agent/tools`
- **Summary:** List Tools
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/health`
- **Summary:** Health
- **Visual Hint:** stat
- **DaisyUI Component:** `daisy_stat`
- **Wireframe:** Grid of stat cards with large numbers + trend indicators + sparklines

**GET** `/studio/genome`
- **Summary:** Get Studio Genome
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/sullivan/components`
- **Summary:** List Components
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/`
- **Summary:** Serve Index
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio/`
- **Summary:** Serve Studio Page
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/studio`
- **Summary:** Serve Studio Page
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/homeos/`
- **Summary:** Serve Homeos Page
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/homeos`
- **Summary:** Serve Homeos Page
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/components/`
- **Summary:** Serve Components Page
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/components`
- **Summary:** Serve Components Page
- **Visual Hint:** list
- **DaisyUI Component:** `daisy_list`
- **Wireframe:** Vertical list with item titles + descriptions + action icons

**GET** `/arbiter-showcase`
- **Summary:** Serve Arbiter Showcase
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/daisy-showcase`
- **Summary:** Serve Daisy Showcase
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/sullivan/preview/{component_id}`
- **Summary:** Preview Component
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/sullivan/preview`
- **Summary:** Preview List
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

**GET** `/sullivan/preview/{component_id}/render`
- **Summary:** Render Component
- **Visual Hint:** card
- **DaisyUI Component:** `daisy_card`
- **Wireframe:** Header with title + avatar/icon + body content + action buttons footer

### ⌨️ Data Input (14 endpoints)

**POST** `/studio/validate`
- **Summary:** Post Studio Validate
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/studio/next/{current_step}`
- **Summary:** Navigate Next Step
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/studio/step/5/select-layout/{layout_id}`
- **Summary:** Select Layout
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/studio/designer/upload`
- **Summary:** Studio Designer Upload
- **Visual Hint:** upload
- **DaisyUI Component:** `daisy_file_input`
- **Wireframe:** Drop zone with icon + file list + progress bars + upload button

**POST** `/studio/finalize`
- **Summary:** Finalize Generation
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/studio/session/reset`
- **Summary:** Reset Session
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/sullivan/agent/chat`
- **Summary:** Chat
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/sullivan/agent/chat/stream`
- **Summary:** Chat Stream
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/sullivan/agent/session/{session_id}/clear`
- **Summary:** Clear Session
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/execute`
- **Summary:** Execute Plan
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/sullivan/search`
- **Summary:** Search Component
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/sullivan/dev/analyze`
- **Summary:** Sullivan Dev Analyze
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/sullivan/designer/analyze`
- **Summary:** Sullivan Designer Analyze
- **Visual Hint:** form
- **DaisyUI Component:** `daisy_fieldset`
- **Wireframe:** Grouped input fields with labels + submit button + validation messages

**POST** `/sullivan/designer/upload`
- **Summary:** Sullivan Designer Upload
- **Visual Hint:** upload
- **DaisyUI Component:** `daisy_file_input`
- **Wireframe:** Drop zone with icon + file list + progress bars + upload button

---

## 📐 Schémas (16)

- **Body_post_studio_validate_studio_validate_post** (object): `section_id`, `section_title`, `items`, `verdict`
- **Body_studio_designer_upload_studio_designer_upload_post** (object): `design_file`
- **Body_sullivan_designer_upload_sullivan_designer_upload_post** (object): `file`
- **ChatRequest** (object): `message`, `session_id`, `user_id`, `context`, `step`, ...(1 more)
- **ChatResponse** (object): `content`, `session_id`, `tool_calls`, `dom_actions`, `code_actions`, ...(1 more)
- ... et 11 autres schémas


---

## 🌼 Composants DaisyUI Référencés

- `daisy_card` (10×)
- `daisy_fieldset` (12×)
- `daisy_file_input` (2×)
- `daisy_list` (19×)
- `daisy_stat` (1×)


---

*IR généré automatiquement par Sullivan Genome Generator avec couche visuelle (Mission 2)*
