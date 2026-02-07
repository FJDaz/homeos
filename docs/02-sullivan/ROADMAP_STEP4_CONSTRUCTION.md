# ROADMAP Step 4 → Mode Construction

**Date** : 6 février 2026
**Objectif** : Pipeline complet IR → Genome → Canvas → UI HomeOS

---

## ARCHITECTURE STEP 4

```
┌──────────────────────────────────────────────────────────────────────────┐
│ SIDEBAR GAUCHE (250px)   │ ZONE PRINCIPALE (100% - 250px)                │
│                          │                                                │
│ [Drilldown Genome]       │ ┌─────────────────────────────────────────┐   │
│ ├── Corps 1 [✓]          │ │  ANCHOR FRD/STEP1 : IR + GENOME         │   │
│ │   ├── Organe A         │ │  ┌──────────────┬──────────────┐        │   │
│ │   └── Organe B         │ │  │ IR + Visuel  │ Genome JSON  │        │   │
│ ├── Corps 2 [WIP]        │ │  │ (50%)        │ (50%)        │        │   │
│ │   └── ...              │ │  └──────────────┴──────────────┘        │   │
│ └── Corps 3 [TODO]       │ │                                          │   │
│                          │ │  [VALIDER IR/GENOME ▼]                   │   │
│                          │ │  (transition CSS vers anchor step2)      │   │
│ ──────────────────────── │ └─────────────────────────────────────────┘   │
│                          │                                                │
│ [Outils Figma]           │ ┌─────────────────────────────────────────┐   │
│ ├── Sélection (V)        │ │  ANCHOR FRD/STEP2 : DESIGN INPUT        │   │
│ ├── Rectangle (R)        │ │                                          │   │
│ ├── Cercle (O)           │ │  [UPLOAD FICHIER]  ou  [DESIGN PROPOSÉ] │   │
│ ├── Texte (T)            │ │  (KIMI K2.5 génère template Figma)      │   │
│ └── Ligne (L)            │ │                                          │   │
│                          │ │  [VALIDER DESIGN ▼]                      │   │
│ [Propriétés]             │ │  (transition CSS vers anchor step3)      │   │
│ ├── Position X, Y        │ └─────────────────────────────────────────┘   │
│ ├── Dimensions W, H      │                                                │
│ ├── Fill                 │ ┌─────────────────────────────────────────┐   │
│ ├── Stroke               │ │  ANCHOR FRD/STEP3 : CANVAS FIGMA        │   │
│ └── Corner Radius        │ │  (100% zone principale)                  │   │
│                          │ │                                          │   │
│ ──────────────────────── │ │  [CANVAS INTERACTIF]                    │   │
│                          │ │  - Drag & drop composants                │   │
│ [Composants DaisyUI]     │ │  - Édition visuelle                     │   │
│ ├── Buttons              │ │  - Grille + snap                        │   │
│ ├── Cards                │ │                                          │   │
│ ├── Forms                │ │  [VALIDER CORPS ▼] → Corps suivant      │   │
│ └── ...                  │ │                                          │   │
│                          │ └─────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## FLOW DE VALIDATION (2 NIVEAUX)

### Niveau 1 : Validation par Corps

```
Pour chaque Corps dans Genome:
    1. Afficher IR + Genome du Corps
    2. [VALIDER IR/GENOME] → passe à step2
    3. Upload design OU Design proposé par KIMI
    4. [VALIDER DESIGN] → passe à step3
    5. Éditer dans Canvas Figma
    6. [VALIDER CORPS] → sauvegarde, passe au Corps suivant
```

### Niveau 2 : Validation UI Globale

```
Après STEPS.length Corps validés:
    1. [VALIDER UI] → aperçu réel du rendu
    2. Si pas bon:
       - [ANNULER] → retour au step KIMI
       - Choix du/des Corps problématiques
       - Recommencer le flow pour ces Corps
    3. Si bon:
       - [VALIDER MODE CONSTRUCTION]
       - Remplace l'UI existant de HomeOS
```

---

## ÉTAPES D'IMPLÉMENTATION

### Étape 0 : Intégration Canvas dans Step 4

**Fichiers concernés :**
- `Frontend/studio-step4-static.html` ou template step 4
- `Frontend/canvas-figma/` (existant)

**Actions :**
1. Insérer les outils Figma (`<aside class="sidebar sidebar-right">`) dans la sidebar gauche
2. Déplacer le panneau propriétés dans la sidebar gauche
3. Zone principale = 3 anchors scrollables (step1, step2, step3)
4. Composants DaisyUI draggables depuis sidebar vers canvas

### Étape 1 : Optimisation IR → Genome

**Fichiers concernés :**
- `Backend/Prod/core/genome_generator.py`
- `output/studio/genome_enrichi.json`
- `output/studio/ir_visuel_edite.md`

**Actions :**
1. IR avec visual hints (déjà fait)
2. Genome structuré Corps/Organes/Atomes (déjà fait)
3. Affichage côte à côte 50/50 dans step1

### Étape 2 : KIMI K2.5 → Template Figma

**Fichiers concernés :**
- `Backend/Prod/models/kimi_vision_client.py` (existant)
- Nouveau : `Backend/Prod/sullivan/template_generator.py`

**Actions :**
1. KIMI analyse le Genome d'un Corps
2. Génère un template HTML/CSS tagué Figma-compatible
3. Template chargé dans le Canvas

**Format sortie KIMI :**
```json
{
  "corps_id": "dashboard",
  "template": {
    "html": "<div class='frame' data-figma-type='FRAME'>...</div>",
    "css": ".frame { ... }",
    "elements": [
      {"type": "RECTANGLE", "x": 0, "y": 0, "w": 1200, "h": 800, "fill": "#1a1a1a"},
      {"type": "COMPONENT", "ref": "daisy_navbar", "x": 0, "y": 0}
    ]
  }
}
```

### Étape 3 : Canvas interactif

**Fichiers concernés :**
- `Frontend/canvas-figma/canvas.js` (existant)
- Nouveau : `Frontend/canvas-figma/homeos-bridge.js`

**Actions :**
1. Charger le template KIMI dans le canvas
2. Permettre l'édition visuelle
3. Exporter le résultat en JSON Figma-compatible

### Étape 4 : Validation et sauvegarde

**Fichiers concernés :**
- `Backend/Prod/sullivan/studio_routes.py`
- Nouveau : endpoint `/studio/corps/{id}/validate`

**Actions :**
1. [VALIDER CORPS] → POST `/studio/corps/{id}/validate`
2. Sauvegarde le canvas comme écran final
3. Marque le Corps comme [✓] validé
4. Passe au Corps suivant

### Étape 5 : Mode Construction

**Fichiers concernés :**
- `Backend/Prod/sullivan/studio_routes.py`
- Templates HomeOS

**Actions :**
1. [VALIDER UI] → aperçu dans iframe
2. [VALIDER MODE CONSTRUCTION] → remplace les templates existants
3. HomeOS utilise les nouveaux écrans

---

## POINTS DE NON-RETOUR (à confirmer avant chaque étape)

| Étape | Confirmation requise | Rollback possible |
|-------|---------------------|-------------------|
| Valider IR/Genome | "L'IR et le Genome sont corrects ?" | Oui, éditer |
| Valider Design | "Le template KIMI est acceptable ?" | Oui, re-générer |
| Valider Corps | "Ce Corps est finalisé ?" | Oui, revenir |
| Valider UI | "L'UI globale est prête ?" | Oui, choisir Corps à refaire |
| Mode Construction | "Remplacer l'UI existante ?" | ⚠️ Archive créée avant |

---

## ORDRE DES MISSIONS KIMI

1. **MISSION_STEP4_INTEGRATION** : Intégrer canvas + outils dans step 4
2. **MISSION_IR_GENOME_VIEW** : Affichage 50/50 IR + Genome
3. **MISSION_KIMI_TEMPLATE_GEN** : KIMI K2.5 → Template Figma
4. **MISSION_CANVAS_HOMEOS** : Bridge canvas ↔ HomeOS
5. **MISSION_VALIDATION_FLOW** : Flow de validation 2 niveaux
6. **MISSION_MODE_CONSTRUCTION** : Remplacement UI final

---

## FICHIERS CRÉÉS/MODIFIÉS (PRÉVISION)

```
Frontend/
├── canvas-figma/
│   ├── index.html (existant)
│   ├── styles.css (existant)
│   ├── canvas.js (existant)
│   └── homeos-bridge.js (NOUVEAU)
├── studio-step4-integrated.html (NOUVEAU)

Backend/Prod/
├── sullivan/
│   ├── studio_routes.py (MODIFIÉ - routes validation)
│   └── template_generator.py (NOUVEAU - KIMI → template)
├── models/
│   └── kimi_vision_client.py (existant)

output/studio/
├── genome_enrichi.json (existant)
├── corps_validated/ (NOUVEAU - Corps validés)
│   ├── dashboard.json
│   └── ...
```

---

**Cette roadmap est la référence. Toute déviation doit être justifiée.**
