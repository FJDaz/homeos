# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Phase Active (2026-04-03)

### Thème 0 — Hotfixes
> M121 ✅, M116 ✅, M122 ✅, M123 ✅, M124 ✅, M125 ✅, M126 ✅, M127 ✅ — archivées dans ROADMAP_ACHIEVED.md (2026-04-01)

---

### Thème 7 — Drill : Manifeste → Wire → Cadrage

### Mission 147 — Wire : overlay Z-index + fond blur + validation
**STATUS: 🔵 EN COURS**
**DATE: 2026-04-02**
- [ ] Overlay `#ws-wire-overlay` dans workspace.html (Gemini)
- [ ] Logic JS + Route Python (Claude)

---

### Mission 157 — Nettoyage ROADMAP.md : collapse des missions archivées
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-03**
- [ ] Collapse missions ✅ LIVRÉ
- [ ] Archive complète dans ROADMAP_ACHIEVED.md
- [ ] Cible < 600 lignes

---

### Mission 155 — Bouton Stop Sullivan : annulation de requête en cours
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-03**
- [ ] WsChat.js : AbortController + bouton Stop UI

---

### Mission 153 — Undo Sullivan : rebrancher la stack d'historique
**STATUS: 🔵 EN COURS — GEMINI**
**DATE: 2026-04-03**
- [ ] WsCanvas.js : snapshot avant update
- [ ] Bouton Undo dans le header workspace

---

### Mission 150 — Retour Cadrage : session pré-alimentée par le manifeste Wire
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-02**
- [ ] Route `POST /api/cadrage/init-context`
- [ ] Badge "contexte wire chargé" dans Cadrage UI

---

### Mission 149 — Canvas N0 : États de sélection + toolbar opérationnelle
**STATUS: 🟠 PRÊTE**
**DATE: 2026-04-02**
- [ ] États CSS (hover, selected, dragging)
- [ ] WsCanvas.js logic (notifyToolbar, cursor)

---

## Backlog des Thèmes

### Thème 1 — Sullivan Typography Engine (suite)

### Mission 110 — Templates FRD : liste vide après manifest minimal
**STATUS: 🔴 HOTFIX**
**DATE: 2026-03-31**
- [ ] Diagnostic endpoint `#template-select` vide.

---

### Thème 2 — Architecture User / Project

### Mission 111-A — Multi-project : backend isolation
**STATUS: 🔵 BACKLOG**
- Objectif : Isolation des dossiers `projects/{uuid}/` (manifests/imports/exports).

### Mission 111-B — Multi-project : UI landing + header
**STATUS: 🔵 BACKLOG**
- Objectif : Switcher de projet sur la landing.

---

### Thème 3 — UX Cléa

### Mission 112 — Sullivan Welcome Screen
**STATUS: 🔵 BACKLOG**
- Objectif : Accueil sémantique par Sullivan sur la landing.

### Mission 113 — Sullivan Tips + Smart Nudges
**STATUS: 🔵 BACKLOG**
- Objectif : Micro-apprentissages typographiques pendant les chargements.

---

### Thème 4 — FRD Canvas v2 : features Stenciler portées

### Mission 114 — FRD Canvas v2 : snap grid + zoom + resize
**STATUS: 🔵 BACKLOG**
- Objectif : Porter le moteur SVG du Stenciler dans le mode Wire FRD.

---

### Thème 5 — Pipeline landing → FRD : fluidité de base

### Mission 115 — Bouton "éditer" global + template courant dans FRD
**STATUS: 🔴 HOTFIX**

### Mission 118 — Pont SVG Illustrator → Tailwind Direct
**STATUS: 🔵 BACKLOG**

### Mission 120 — Rebranchement Plugin Figma → FRD Editor
**STATUS: 🔵 BACKLOG**

---

## Features prioritaires
### Mission 135 — Système d'Authentification
### Mission 136 — Gestion Multi-tenancy
### Mission 137 — Système BYOK (Bring Your Own Key)
### Mission 138 — Bouton Upload Universel
### Mission 139 — Révision du mode Wired (FrdWire v2)
