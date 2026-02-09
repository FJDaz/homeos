# PLAN INTEGRATION FIGMA EDITOR - Genome FRD

**Date** : 2026-02-08  
**Status** : ✅ **RESTRUCTURATION + DIMENSIONS RÉELLES COMPLÉTÉES**  
**Fichier cible** : `server_9999_v2.py`  
**Port** : 9999  
**URL** : http://localhost:9999/studio

---

## 🏗️ ARCHITECTURE RESTRUCTURÉE N0-N3 + DIMENSIONS RÉELLES

### Vue d'ensemble

```
┌──────────────────────────────────────────────────────────┐
│  ROW CORPS (N0) - 9 phases du genome                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ [Aperçu│ │ [Aperçu│ │ [Aperçu│ │ [Aperçu│       │
│  │  wiref] │ │  wiref] │ │  wiref] │ │  wiref] │       │
│  │ Intent  │ │ Arbitra │ │ Session │ │ Navigat │       │
│  │   ✓     │ │         │ │         │ │         │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│  [Cliquer = changer contexte sidebar]                   │
├──────────────────────────────────────────────────────────┤
│  CANVAS - Corps en DIMENSIONS RÉELLES                   │
│  ┌─────────────────────────────────────────┐            │
│  │ ┌─────────────────────────────────────┐ │            │
│  │ │ Intent Refactoring    1440×900    │ │ ← Header    │
│  │ ├─────────────────────────────────────┤ │            │
│  │ │ ┌────────┐  ┌───────────────────┐ │ │            │
│  │ │ │sidebar │  │                   │ │ │ ← Zones    │
│  │ │ │  280px │  │    content        │ │ │   Sullivan │
│  │ │ │        │  │    1160px         │ │ │            │
│  │ │ └────────┘  └───────────────────┘ │ │            │
│  │ └─────────────────────────────────────┘ │            │
│  │          [25% échelle affichage]        │            │
│  └─────────────────────────────────────────┘            │
│  [Drop Corps = rendu 1440×900 avec layout]              │
├──────────────────────────────────────────────────────────┤
│  SIDEBAR - Organes du Corps actif uniquement            │
│  ┌─────────────────────────────────────────┐             │
│  │ ▼ Corps Actif: Intent Refactoring       │             │
│  │   ├─ Rapport IR (N1)                   │             │
│  │   │   ├─ Tableau IR (N2)               │             │
│  │   │   └─ Détail Organe (N2)            │             │
│  └─────────────────────────────────────────┘             │
├──────────────────────────────────────────────────────────┤
│  [Delete/Suppr/Backspace] = Supprimer objet sélectionné │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ RESTRUCTURATION N0-N3 COMPLÉTÉE

### 1. Row Corps - 9 N0 avec wireframes persistés

**9 Corps extraits de `n0_phases`** :
1. `phase_1_ir` → Intent Refactoring (table)
2. `phase_2_arbiter` → Arbitrage (card)
3. `phase_3_session` → Session (status)
4. `phase_4_navigation` → Navigation (breadcrumb)
5. `phase_5_layout` → Layout (grid)
6. `phase_6_upload` → Upload (upload)
7. `phase_7_chat` → Dialogue (chat)
8. `phase_8_validation` → Validation (dashboard)
9. `phase_9_zoom` → Adaptation (preview)

**Aperçus visuels** :
- SVG wireframe unique par type
- Persisté dans `localStorage` (cache)
- Généré une seule fois, réutilisé ensuite

### 2. Sidebar - Filtrage strict par Corps actif

```javascript
function activateCorps(corpsId) {
  // Highlight dans le Row
  // Filtrer sidebar : uniquement N1 de ce N0
  // Reset N2/N3
}
```

### 3. Canvas - Dimensions réelles 1440×900

**Avant** : Petit rectangle 300×200px
**Après** : Desktop réel 1440×900px (affiché à 25% = 360×225px)

```javascript
function renderCorpsOnCanvas(canvas, corpsId, dropX, dropY) {
  const REAL_WIDTH = 1440;
  const REAL_HEIGHT = 900;
  const scale = 0.25; // 25% pour tenir dans la vue
  
  // Rendu avec :
  // - Cadre principal (blanc + bordure verte)
  // - Header (80px réel = 20px affiché)
  // - Titre du Corps
  // - Badge "1440×900"
  // - Zones selon structure Sullivan
}
```

### 4. Structure Sullivan appliquée

Selon `CORP_STRUCTURES` :

| Type | Layout | Zones visibles |
|------|--------|----------------|
| `dashboard` | header-grid-footer | header + stats + content |
| `table` | header-content | header + table |
| `editor` | sidebar-content | sidebar (280px) + content (1160px) |
| `grid` | masonry | grille de cartes |
| `preview` | single | zone preview unique |

### 5. Suppression (Delete/Suppr/Backspace)

```javascript
document.addEventListener('keydown', (e) => {
  if ((e.key === 'Delete' || e.key === 'Backspace') && canvas.getActiveObject()) {
    canvas.remove(canvas.getActiveObject());
    saveCanvasState();
  }
});
```

---

## 🎯 WORKFLOW UTILISATEUR

1. **Sélectionner** dans Browser → "Valider"
2. **Row** s'affiche avec les 9 Corps + aperçus
3. **Premier Corps** actif par défaut
4. **Sidebar** affiche ses organes uniquement
5. **Drag Corps** sur canvas → Apparaît en 1440×900
6. **Zones visibles** selon type (header/sidebar/content...)
7. **Cliquer autre Corps** dans Row → Sidebar change
8. **Delete** pour supprimer
9. **Zoom** pour voir les détails

---

## 📊 COMPARAISON AVANT/APRÈS

| Aspect | Avant | Après |
|--------|-------|-------|
| **Row** | 29 éléments mélangés | 9 Corps N0 structurés |
| **Aperçus** | Rectangle gris générique | Wireframe SVG typé |
| **Sidebar** | Tout mélangé | Filtré par Corps actif |
| **Canvas** | 300×200px | 1440×900px (échelle 25%) |
| **Layout** | Simple rectangle | Structure Sullivan complète |
| **Suppression** | Non implémentée | Delete/Suppr/Backspace |

---

## 🔧 DÉTAILS TECHNIQUES

### Rendu Canvas (1440×900)

```
Dimensions réelles:     1440 × 900 px
Échelle affichage:      25%
Dimensions affichées:   360 × 225 px

Structure rendue:
┌────────────────────────────────────────┐ ← Frame (blanc + ombre)
│ Intent Refactoring        1440×900    │ ← Header (h:20px)
├────────────────────────────────────────┤
│ ┌─────┐ ┌──────────────────────────┐ │ ← Zones selon type
│ │side │ │                          │ │   - sidebar: 70px
│ │70px │ │       content            │ │   - content: 290px
│ │     │ │       290px              │ │
│ └─────┘ └──────────────────────────┘ │
└────────────────────────────────────────┘
```

### Cache Wireframes

```javascript
const WIREFRAME_CACHE_KEY = 'homeos_wireframe_cache';
// Stockage: { 'phase_1_ir': '<svg>...</svg>', ... }
```

---

## CONTRAINTES RESPECTÉES

- ✅ PAS DE SERVEUR (Python = statique)
- ✅ PAS DE BUILD (Fabric.js CDN)
- ✅ PAS DE FRAMEWORK (Vanilla JS)
- ✅ localStorage persistance
- ✅ 9 Corps max N0
- ✅ Dimensions réelles desktop
- ✅ Suppression clavier

---

## COMMANDES

```bash
python3 server_9999_v2.py
# http://localhost:9999/studio
```

---

**Mémo** : "9 Corps, dimensions réelles, structure Sullivan, suppression fluide."
