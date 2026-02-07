# MISSION: Intégration Outils Figma dans Studio Step 4

**Date**: 6 février 2026  
**Référence**: http://localhost:8000/studio?step=4 (layout actuel)  
**Statut**: À implémenter

---

## 🎯 OBJECTIF

Intégrer les outils Figma (actuellement dans `aside.sidebar-right`) dans le layout Step 4 du Studio, tout en préservant la structure existante.

---

## 📐 LAYOUT CIBLE

```
┌─────────────────────────────────────────────────────────────────┐
│ Header / Tabs (Brainstorm | Back | Frontend | Déployer)        │
├─────────────────────────┬───────────────────────────────────────┤
│ SIDEBAR GAUCHE          │ ZONE PRINCIPALE                       │
│                         │                                       │
│ ┌─────────────────────┐ │ ┌─────────────────┬─────────────────┐ │
│ │ OUTILS FIGMA        │ │ │   IR + Visuel   │     Genome      │ │
│ │ (from sidebar-right)│ │ │    (50%)        │     (50%)       │ │
│ │                     │ │ └─────────────────┴─────────────────┘ │
│ │ - Fill              │ │         [VALIDER ↓]                   │
│ │ - Stroke            │ │            ↓                          │
│ │ - Radius            │ │    [Anchor FRD/step2]                 │
│ │ - Opacity           │ │    UPLOAD Fil ou Design               │
│ └─────────────────────┘ │         [VALIDER ↓]                   │
│                         │            ↓                          │
│ ┌─────────────────────┐ │    [Anchor FRD/step2]                 │
│ │ DRILLDOWN GENOME    │ │    CANVAS FIGMA (100% width)          │
│ │                     │ │                                       │
│ │ ▼ Corps             │ │    ┌─────────────────────────────┐    │
│ │   ▼ Organes         │ │    │                             │    │
│ │     ▶ Atomes        │ │    │    Zone de dessin Figma     │    │
│ │                     │ │    │                             │    │
│ └─────────────────────┘ │    └─────────────────────────────┘    │
│                         │                                       │
└─────────────────────────┴───────────────────────────────────────┘
```

---

## 🔧 SPÉCIFICATIONS TECHNIQUES

### 1. Sidebar Gauche (fusion)

**Section 1: Outils Figma** (haut)
- Récupérer depuis `<aside class="sidebar sidebar-right">` du template actuel
- Propriétés: Position (X,Y), Dimensions (W,H), Fill, Stroke, Radius, Opacity
- Collapsible

**Section 2: Drilldown Genome** (bas)
- Arborescence N0 (Genome) > N1 (Corps) > N2 (Organes) > N3 (Atomes)
- Navigation drill-down avec breadcrumbs
- Thumbnails visuels des composants

### 2. Zone Principale (50/50)

**Colonne Gauche (50%)**: IR + Visuel
- Visual Intent Report
- Wireframe esquissé
- Infos endpoints (method, path, hint)

**Colonne Droite (50%)**: Genome
- Structure JSON du genome enrichi
- Mapping N0-N1-N2-N3
- Composants DaisyUI associés

### 3. Workflow Validation (2 niveaux)

**Niveau 1: Valider Corps**
- Bouton "VALIDER ↓" avec transition CSS
- Passe au corps suivant
- Sauvegarde le corps actuel
- Scroll vers anchor FRD/step2

**Niveau 2: Valider UI**
- Après STEPS.length corps validés
- Remplace actual design
- Aperçu réel du rendu
- Si OK → Valider Mode Construction
- Si KO → Annuler → Retour stepSortie KIMI

### 4. Canvas Figma
- Prend 100% de la zone principale
- Sous les sections IR/Genome
- Outils: select, rectangle, circle, text, line
- Grid + snap
- Zoom/Pan

---

## 📁 FICHIERS CONCERNÉS

| Fichier | Action |
|---------|--------|
| `Backend/Prod/templates/studio_homeos.html` | Modifier layout step=4 |
| `Frontend/canvas-figma/` | Réutiliser pour le canvas |
| `Frontend/drilldown-sidebar.html` | Adapter pour sidebar gauche |
| `output/studio/genome_enrichi.json` | Source données |

---

## 🎨 CONSERVATION DESIGN

- **Couleurs**: Conserver palette actuelle (vert #8cc63f, gris #f8f8f8)
- **Typography**: System fonts
- **Spacing**: 12px, 16px, 24px (comme actuel)
- **Transitions**: CSS ease 0.2s-0.3s
- **Z-index**: sidebar (100), modals (200), tooltips (300)

---

## ⚡ COMPORTEMENTS

1. **Drilldown**: Click N0 → affiche N1 → Click N1 → affiche N2, etc.
2. **Outils Figma**: Modifient la preview en temps réel
3. **Validation**: Animation slide-down vers anchor suivant
4. **Canvas**: Interactif, sauvegarde localStorage

---

## 🔍 RÉFÉRENCE EXACTE

URL de travail: `http://localhost:8000/studio?step=4`
Template: `Backend/Prod/templates/studio_homeos.html`
Section cible: Frontend tab (step 4)

---

**Note**: Ne PAS modifier la structure HTML existante, uniquement réorganiser et injecter les nouveaux éléments dans les containers prévus.
