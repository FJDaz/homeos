# Mocks JSON — Stenciler

**Rôle** : Données de test pour le développement Frontend  
**Conformité** : CONSTITUTION_AETHERFLOW v1.0.0

## Fichiers

| Fichier | Description | API Endpoint simulé |
|---------|-------------|---------------------|
| `corps_previews.json` | 4 Corps à 20% pour bande preview | `GET /api/corps` |

## Attributs Sémantiques (Pas de CSS)

Chaque Corps contient :
- `id`, `path`, `name` — Identification
- `semantic_role` — discovery | infrastructure | interface | delivery
- `importance` — primary | secondary | tertiary
- `visual_hint` — brainstorm | backend | frontend | deploy
- `accent_color` — Hex (interprété librement par KIMI)
- `density` — airy | normal | compact
- `layout_type` — flex | grid | stack (sémantique, pas CSS)

## Usage

```javascript
// Chargement mock (développement)
const response = await fetch('/mocks/corps_previews.json');
const data = await response.json();

// Rendu (KIMI interprète librement)
const corpsCards = data.corps.map(c => `
  <div class="corps-preview" data-id="${c.id}">
    <h3 style="color: ${c.accent_color}">${c.name}</h3>
    <p>${c.description}</p>
  </div>
`);
```

## Règle d'Or

> **KIMI reçoit du JSON sémantique. KIMI rend du HTML/CSS. Claude ne touche pas au rendu.**
