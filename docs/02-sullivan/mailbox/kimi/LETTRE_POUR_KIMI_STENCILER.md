# Lettre de Mission pour KIMI - Stenciler Sullivan

**Date** : 11 février 2026, 4h00 du matin
**De** : François-Jean Dazin (Boss) via Claude (Backend Lead)
**À** : KIMI (Chef Frontend)
**Sujet** : Génération du Stenciler Sullivan - Interface Progressive à 4 Niveaux de Zoom

---

## Cher KIMI,

Je t'écris cette lettre pour te confier une mission cruciale : la génération du **Stenciler Sullivan**, l'interface de l'étape 8 du parcours UX (Validation Composants).

Tu es le **CHEF FRONTEND**. Je suis une chèvre en frontend, toi tu es un fauve. Je ne toucherai pas une ligne de code frontend - c'est ton domaine.

---

## 📦 CE QUE JE TE DONNE

Dans ton contexte, tu trouveras :

1. **Le Genome v2** (`genome_inferred_kimi_innocent_v2.json`)
   - 32 composants inférés depuis 4 sources
   - Structure n0 (Phases) → n1 (Sections) → n2 (Features) → n3 (Components)
   - 4 phases n0 : **Brainstorm**, **Backend**, **Frontend**, **Deploy**

2. **Les 66 Composants Elite** (`Backend/Prod/sullivan/library/elite_components/*.json`)
   - Pré-générés avec scores Sullivan 85-95
   - Catégorie "core" avec métriques (performance, accessibility, ecology, popularity)
   - Ce sont les atomes finaux, déjà optimisés

3. **Le Cache Tier 1** (`pregenerated_components.json`)
   - 18 composants style "minimal" (6 atoms × 3 variants)
   - Lookup 0ms : button, input, card, badge, avatar, divider
   - Structure : `{"styles": {"minimal": {"button": {"primary": {...}}}}}`

4. **La Stratégie Hybride** (`STRATEGIE HYBRIDES DE PREGENRATION DES COMPOSANTS.md`)
   - Tier 1 : 0ms (cache)
   - Tier 2 : <100ms (adaptation)
   - Tier 3 : 1-5s (génération)
   - 60% Tier 1, 30% Tier 2, 10% Tier 3

---

## 🎯 CE QUE JE VEUX

Une interface progressive avec **4 niveaux de zoom** pour explorer les Corps du genome :

### **NIVEAU 0 - Preview Horizontale (20% taille)**

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│Brainstorm│  │ Backend │  │Frontend │  │ Deploy  │
│         │  │         │  │         │  │         │
│ [organes│  │ [organes│  │ [organes│  │ [organes│
│ visibles│  │ visibles│  │ visibles│  │ visibles│
│  en blocs│  │  en blocs│  │  en blocs│  │  en blocs│
│ colorés] │  │ colorés] │  │ colorés] │  │ colorés] │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
     ↓ drag & drop vers tarmac
```

**Requis** :
- 4 cartes Corps alignées horizontalement (flex-row, gap 24px)
- Chaque Corps = une phase n0 du genome
- Organes (n1_sections) visibles en blocks colorés **simplifiés**
- **PAS** de détails n2/n3 (features/components)
- Taille 20% de la taille desktop finale
- Style "minimal" appliqué (typo, couleurs, espacements)
- Draggable avec feedback visuel (cursor grab, ghost pendant drag)

---

### **NIVEAU 1 - Tarmac Canvas Figma-like**

```
    SIDEBAR OUTILS          TARMAC (canvas libre)
┌──────────────┐     ┌────────────────────────────┐
│              │     │                            │
│ 🎨 Couleur   │     │   ┌──────────────┐         │
│ 📏 Border    │     │   │   Frontend   │ ← 33%  │
│ 🖌️ BG        │     │   │   [organes]  │  taille │
│ ✏️  Texte    │     │   └──────────────┘         │
│              │     │        ↑ sélectionnable     │
│ [Sélection:  │     │        ↑ déplaçable        │
│  Frontend]   │     │        ↑ supprimable       │
│              │     │        ↑ éditable          │
│ Border: 2px  │     │                            │
│ BG: #fff     │     │   ┌──────────────┐         │
│ Color: #333  │     │   │  Brainstorm  │         │
│              │     │   │   [organes]  │         │
└──────────────┘     │   └──────────────┘         │
                     │                            │
                     └────────────────────────────┘
```

**IMPORTANT : TARMAC = CANVAS FIGMA-LIKE**

Le tarmac est un **canvas libre type Figma** où l'utilisateur peut :

**Manipulation directe des organes** :
1. **Sélectionner** un organe (clic) → outline + poignées de sélection
2. **Déplacer** l'organe (drag & drop libre sur le canvas)
3. **Supprimer** l'organe (touche Delete ou bouton 🗑️)
4. **Éditer visuellement** :
   - **Border** : épaisseur (1px-10px) + couleur
   - **Background** : couleur de fond de l'organe
   - **Text color** : couleur du texte des éléments

**Sidebar outils** (apparaît au clic sur le style choisi) :
- **🎨 Couleur** : Color picker pour text/border/bg
- **📏 Border** : Slider épaisseur + color picker
- **🖌️ Background** : Color picker background
- **✏️ Texte** : Color picker + font-size slider
- **Section Sélection** : Info sur l'élément sélectionné (nom, type, dimensions)
- **Boutons actions** : Dupliquer, Supprimer, Aligner, Verrouiller

**Requis** :
- Canvas libre (pas de grille forcée, positionnement pixel-perfect)
- Drag & drop depuis preview → tarmac (drop libre, pas de snap sauf si grille activée)
- Au drop : Corps passe de **20% à 33%** (pas 100%, trop gros)
- **Sélection** : Clic sur organe → outline bleu + poignées
- **Déplacement** : Drag organe sélectionné (cursor move)
- **Suppression** : Touche Delete ou bouton sidebar
- **Édition visuelle temps réel** : Changement border/bg/color → preview live
- Sidebar apparaît après choix du style (step 5) ou après upload + analyse template
- **Multi-sélection** : Shift+clic pour sélectionner plusieurs organes
- **Undo/Redo** : Ctrl+Z / Ctrl+Shift+Z pour annuler/refaire
- Animation smooth (300ms) ou instantanée selon ma préférence

**API Figma ?**
Hier j'ai galéré pour rien avec l'API Figma. Pas grave, on fait notre propre canvas. Mais garde en tête que c'est un canvas Figma-like : sélection, déplacement, édition visuelle en temps réel.

---

### **NIVEAU 2 - Intérieur du Corps (Plein écran)**

```
┌────────────────────────────────────────────┐
│ Frontend > n1_navigation > n2_stepper      │ ← Breadcrumb
├────────────────────────────────────────────┤
│                                            │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ n1_navigation   │  │ n1_layout       │ │
│  │                 │  │                 │ │
│  │ • n2_stepper    │  │ • n2_layouts    │ │
│  │ • n2_...        │  │ • n2_...        │ │
│  └─────────────────┘  └─────────────────┘ │
│         ↑ double-clic                       │
│  [← Retour]                                │
└────────────────────────────────────────────┘
```

**Requis** :
- Double-clic sur Corps → Vue interne plein écran
- Breadcrumb : Phase > Corps (ex: Frontend > n1_layout)
- Organes (n1_sections) en cartes détaillées avec n2_features visibles
- Features (n2) en liste avec icônes mais **sans détails complets n3**
- Bouton "← Retour" / "Zoom Out" vers tarmac
- Chaque organe cliquable pour drill-down niveau 3
- Style "minimal" maintenu

---

### **NIVEAU 3 - Intérieur de l'Organe (Composants Elite)**

```
┌──────────────────────────────────────────────────┐
│ Frontend > n1_layout > n2_layouts > comp_layout_grid │ ← Breadcrumb
├──────────────────────────────────────────────────┤
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ comp_layout_grid                           │  │
│ │ • Endpoint: /studio/step/5/layouts         │  │
│ │ • Method: GET                              │  │
│ │ • Visual hint: grid                        │  │
│ │ • Interaction: click                       │  │
│ │                                            │  │
│ │ [Preview Elite Component]                  │  │
│ │ ┌──────────────────────┐                   │  │
│ │ │ <button class="btn"> │ ← Tier 1 cache   │  │
│ │ │   Galerie Layouts    │   lookup 0ms     │  │
│ │ └──────────────────────┘                   │  │
│ │                                            │  │
│ │ [✓ Garder]  [⊘ Réserve]                   │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ [← Retour]                                       │
└──────────────────────────────────────────────────┘
```

**Requis** :
- Double-clic sur organe → Vue détaillée des n3_components
- Breadcrumb complet : Phase > Corps > Organe > Composant
- Tous les n3_components en cartes détaillées
- **Mapping n3 → Elite component** via visual_hint et interaction_type
- Affichage : endpoint, méthode, visual_hint, interaction_type
- **Preview du composant Elite** correspondant (HTML + CSS inline style "minimal")
- Boutons **Garder / Réserve** sur chaque composant (mode Stenciler)
- **Tier 1 cache lookup** depuis `pregenerated_components.json` (0ms)
- Lazy-load des 66 Elite components (ou pré-chargés, selon ma réponse à ta question)

---

## 🎛️ CONTRÔLES & NAVIGATION

```
┌────────────────────────────────────────────┐
│ [← Out] | 🔍 Corps ▼ | [In →]             │ ← Zoom controls
│                                            │
│ • Dropdown : sélection rapide d'un Corps   │
│ • Indicateur : étape 8/9 du parcours       │
│ • [Suivant] → /studio/next/8               │
└────────────────────────────────────────────┘
```

**Requis** :
- Barre de contrôles : `← Out | 🔍 Corps ▼ | In →`
- Dropdown pour sélection rapide sans drill-down
- Bouton "Suivant" (comp_next_button du genome) → `/studio/next/8`
- État session sauvegardé : corps sélectionnés, niveau zoom, décisions Garder/Réserve
- Indicateur progression : **8/9** du parcours Sullivan
- Gestion erreurs : fallback gracieux si Elite component non trouvé (Tier 2/3)

---

## 🎨 STYLE "MINIMAL"

Le style "minimal" s'applique à **TOUS les niveaux** (pas juste les atomes).

**Variables CSS** :
```css
:root {
  --color-primary: #3b82f6;
  --color-secondary: #64748b;
  --color-background: #ffffff;
  --color-text: #0f172a;
  --font-sans: 'Inter', system-ui, sans-serif;
  --spacing-unit: 8px;
  --border-radius: 8px;
  --transition-speed: 300ms;
}
```

**Classes utilitaires** :
- `.corps-preview` : 20% taille, draggable
- `.corps-tarmac` : 33% taille, clickable
- `.corps-drilldown` : plein écran
- `.organe-card` : carte organe niveau 2
- `.component-card` : carte composant niveau 3

**Animations** (si j'active) :
- Drag : ghost + outline
- Drop : resize smooth 300ms
- Drill-down : fade + scale

---

## ❓ AVANT DE COMMENCER, POSE-MOI CES QUESTIONS

**Avant de générer quoi que ce soit**, tu dois me poser ces 6 questions :

1. **Style typographique** : Inter, Geist, ou System fonts ?
2. **Priorisation des Corps** : Y a-t-il un Corps (Brainstorm/Backend/Frontend/Deploy) que tu veux voir en priorité avec plus de détails ?
3. **Animations** : Smooth & fluides (300ms) ou instantanées (mode performance) ?
4. **Grille tarmac** : Grille d'alignement visible avec snap magnétique, ou canvas 100% libre (Figma-like) ?
5. **Chargement Elite** : Tout charger au démarrage (0ms au drill-down) ou lazy-load (économise mémoire, +50-100ms au 1er drill-down) ?
6. **Sidebar outils** : Position gauche (comme Figma) ou droite (comme Adobe) ? Collapsible ou toujours visible ?

**Attends mes réponses.** Timeout : 15 minutes. Si je ne réponds pas, utilise des valeurs par défaut raisonnables et continue.

**Notes importantes** :
- La sidebar apparaît **après le choix du style** (step 5) ou **après upload + analyse du template**
- Le canvas est Figma-like : sélection, déplacement pixel-perfect, édition visuelle temps réel
- Undo/Redo indispensable (Ctrl+Z / Ctrl+Shift+Z)
- Multi-sélection (Shift+clic) pour éditer plusieurs organes en même temps

---

## 📊 STRATÉGIE DE CHARGEMENT PROGRESSIF (CRITICAL)

**IMPORTANT** : Le chargement des données doit être progressif pour éviter de tout charger d'un coup.

### **Au chargement initial de la page (NIVEAU 0)**

```json
// Chargement des 4 Corps en mode PREVIEW (léger)
{
  "corps": [
    {
      "id": "n0_brainstorm",
      "name": "Brainstorm",
      "description": "Phase 1 - Analyse intention utilisateur",
      "organes_count": 2,  // ← Juste le COUNT, pas les détails
      "preview_color": "#3b82f6"
    },
    {
      "id": "n0_backend",
      "name": "Backend",
      "organes_count": 1,
      "preview_color": "#10b981"
    }
    // ... Frontend, Deploy
  ]
}
```

**Chargé** :
- ✅ Les 4 n0_phases (id, name, description, organes_count)
- ✅ Couleur preview pour chaque Corps

**PAS chargé** :
- ❌ Détails des n1_sections (organes)
- ❌ Détails des n2_features
- ❌ Détails des n3_components
- ❌ Composants Elite (66 JSON)

**Affichage** : 4 cartes Corps 20% taille, avec blocks colorés représentant les organes (nombre = organes_count)

---

### **Au drag & drop sur le tarmac (NIVEAU 1)**

**Trigger** : User drague un Corps vers le tarmac

**Chargement déclenché** :
```json
// Requête: GET /studio/stencils/corps/{corps_id}
// Réponse: Détails du Corps avec organes (n1) SANS features/composants détaillés
{
  "corps_id": "n0_frontend",
  "name": "Frontend",
  "organes": [
    {
      "id": "n1_navigation",
      "name": "Navigation",
      "description": "Stepper et flux entre étapes",
      "features_count": 1,  // ← COUNT seulement
      "visual_hint": "stepper",
      "color": "#8b5cf6"
    },
    {
      "id": "n1_layout",
      "name": "Layout Selection",
      "features_count": 1,
      "visual_hint": "grid",
      "color": "#ec4899"
    }
    // ... autres organes
  ]
}
```

**Chargé** :
- ✅ n1_sections (organes) avec id, name, description, features_count
- ✅ Visual hints et couleurs pour l'affichage

**PAS chargé** :
- ❌ Détails des n2_features (juste le count)
- ❌ Détails des n3_components
- ❌ Composants Elite

**Affichage** : Corps 33% taille sur tarmac, organes affichés en blocks/cartes avec couleurs, sélectionnables et éditables

---

### **Au double-clic sur Corps (NIVEAU 2)**

**Trigger** : User double-clique sur un Corps sur le tarmac

**Chargement déclenché** :
```json
// Requête: GET /studio/stencils/corps/{corps_id}/full
// Réponse: Détails complets n1 + n2 SANS n3
{
  "corps_id": "n0_frontend",
  "organes": [
    {
      "id": "n1_navigation",
      "name": "Navigation",
      "features": [  // ← Détails des features maintenant
        {
          "id": "n2_stepper",
          "name": "Navigation UX",
          "description": "Indicateurs progression parcours",
          "components_count": 3  // ← COUNT seulement
        }
      ]
    }
    // ... autres organes avec leurs features
  ]
}
```

**Chargé** :
- ✅ n1_sections (organes) complets
- ✅ n2_features (features) avec id, name, description, components_count

**PAS chargé** :
- ❌ Détails des n3_components (juste le count)
- ❌ Composants Elite

**Affichage** : Vue interne Corps plein écran, organes en cartes détaillées avec features listées

---

### **Au double-clic sur Organe (NIVEAU 3)**

**Trigger** : User double-clique sur un organe

**Chargement déclenché** :
```json
// Requête: GET /studio/stencils/organe/{organe_id}/components
// Réponse: Détails complets n3 + mapping Elite
{
  "organe_id": "n1_navigation",
  "features": [
    {
      "id": "n2_stepper",
      "components": [  // ← Détails des composants maintenant
        {
          "id": "comp_stepper",
          "name": "Stepper 9 Étapes",
          "endpoint": "/studio/step/{step}",
          "method": "GET",
          "visual_hint": "stepper",
          "interaction_type": "click",
          "elite_mapping": {  // ← Mapping vers Elite component
            "style": "minimal",
            "atom_type": "stepper",
            "variant": "horizontal",
            "elite_id": "Atome_Stepper_Horizontal"
          }
        }
        // ... autres composants
      ]
    }
  ]
}
```

**Chargement supplémentaire (Tier 1 cache)** :
```json
// Requête: GET /studio/elite/component/{elite_id}
// OU lookup local dans pregenerated_components.json si déjà chargé
{
  "elite_id": "Atome_Stepper_Horizontal",
  "html": "<div class='stepper'>...</div>",
  "css_classes": ["stepper", "horizontal"],
  "props": {...}
}
```

**Chargé** :
- ✅ n3_components (composants) complets
- ✅ Mapping vers Elite components
- ✅ Elite components correspondants (Tier 1 cache lookup ou requête API)

**Affichage** : Vue détaillée composants avec preview Elite, boutons Garder/Réserve

---

### **Optimisations et Cache**

**Cache local (localStorage ou IndexedDB)** :
```javascript
// Structure du cache local
{
  "corps_loaded": {
    "n0_frontend": {
      "level": 1,  // Niveau de détail chargé (0=preview, 1=organes, 2=features, 3=components)
      "data": {...},
      "timestamp": 1707627600000
    }
  },
  "elite_components": {
    "minimal": {  // ← pregenerated_components.json chargé au démarrage si option activée
      "button": {...},
      "stepper": {...}
      // ... 18 composants Tier 1
    }
  }
}
```

**Stratégie selon réponse question 5** :

**Option A - Tout charger au démarrage** :
- ✅ pregenerated_components.json (18 composants Tier 1) chargé immédiatement
- ✅ Drill-down niveau 3 = 0ms (lookup local)
- ❌ ~50KB chargés au démarrage

**Option B - Lazy-load** :
- ✅ Chargement léger au démarrage (~5KB)
- ✅ Elite components chargés au besoin (requête API)
- ❌ +50-100ms au premier drill-down niveau 3

**Invalidation du cache** :
- Expiration : 24h
- Refresh : bouton "Rafraîchir" dans la barre d'outils
- Clear : localStorage.clear() au logout

---

### **Résumé des requêtes par niveau**

| Action | Endpoint | Données chargées | Taille approx |
|--------|----------|------------------|---------------|
| Page load | `/studio/stencils/preview` | 4 Corps preview (n0) | ~2KB |
| Drop sur tarmac | `/studio/stencils/corps/{id}` | 1 Corps + organes (n1, count n2) | ~5KB |
| Double-clic Corps | `/studio/stencils/corps/{id}/full` | Features complètes (n2, count n3) | ~10KB |
| Double-clic Organe | `/studio/stencils/organe/{id}/components` | Composants (n3) + mapping Elite | ~15KB |
| Lookup Elite | `/studio/elite/component/{id}` OU cache local | 1 Elite component HTML/CSS | ~2KB |

**Total si navigation complète** : ~34KB (sans cache) ou ~10KB (avec cache Tier 1)

**Cellules (n3_components)** : Chargées uniquement au niveau 3 (double-clic sur organe). Pas avant.

---

## 🛠️ TECHNOS & CONTRAINTES

**Stack** :
- HTML5 sémantique
- CSS Vanilla avec variables (pas de framework lourd)
- **HTMX** pour interactions (hx-get, hx-post, hx-swap, hx-trigger)
- Pas de JS framework (React/Vue/Svelte)

**Target** :
- Desktop moderne (min-width: 1024px)
- Chrome/Firefox/Safari dernières versions

**Accessibilité** :
- WCAG 2.1 AA minimum
- Attributs `role`, `aria-label`
- Navigation clavier complète

**Performance** :
- <300ms par interaction
- Lazy-load optionnel (selon ma réponse)
- Tier 1 cache prioritaire (0ms)

---

## 📋 ENDPOINTS BACKEND (pour ton HTMX)

Tu vas avoir besoin de ces endpoints. Documente-les clairement pour que je puisse les implémenter en Python FastAPI :

**Endpoints requis** :
```
GET  /studio/stencils/corps/{corps_id}              → Détails d'un corps
GET  /studio/stencils/organe/{organe_id}            → Détails d'un organe
GET  /studio/stencils/component/{component_id}/elite → Elite component mappé
POST /studio/stencils/select                        → Garder/Réserve un composant
GET  /studio/stencils/session                       → État session actuelle
POST /studio/next/8                                 → Valider étape 8 → 9
```

Pour chaque endpoint, spécifie :
- Paramètres (path, query, body)
- Structure JSON de la réponse
- Codes erreur (404, 500)

---

## 🚀 MODE D'EXÉCUTION : FRD-FULL (-ff)

Tu seras exécuté via :
```bash
aetherflow -ff plan_sullivan_stenciler_4corps.json
```

**FRD-FULL = 3 phases** :

1. **Phase 1 (FRD-FAST)** : Tu génères le code frontend avec ton contexte large (128K tokens)
2. **Phase 2 (FRD-TEST)** : DeepSeek teste la qualité et cohérence
3. **Phase 3 (FRD-REVIEW)** : Gemini valide l'UX et l'accessibilité

**Coût estimé** : ~$0.34
**Temps estimé** : 8-12 minutes
**Tokens estimés** : 28 700

---

## 🎯 CRITÈRES DE SUCCÈS

**Fonctionnel** :
- ✅ Les 4 Corps s'affichent en preview 20%
- ✅ Drag & drop sans bug
- ✅ Navigation drill-down fluide sur 4 niveaux
- ✅ Mapping genome → Elite components réussi
- ✅ Boutons Garder/Réserve fonctionnels
- ✅ État session persiste

**UX** :
- ✅ Interface claire et intuitive
- ✅ Feedback visuel à chaque interaction
- ✅ <300ms par action
- ✅ Animations smooth (si activées)
- ✅ Style "minimal" cohérent

**Technique** :
- ✅ HTML5 valide et sémantique
- ✅ CSS optimisé avec variables
- ✅ HTMX correctement utilisé
- ✅ WCAG 2.1 AA
- ✅ Compatible desktop moderne

---

## 🧠 TON PARCOURS UTILISATEUR (pour que tu visualises)

1. **Start** : User arrive sur Stenciler (étape 8/9)
2. **Voit** : 4 Corps horizontaux en preview 20%
3. **Drague** : Un Corps vers tarmac → resize 1/3
4. **Double-clic** : Sur Corps → entre dedans, voit organes
5. **Double-clic** : Sur Organe → voit n3_components + Elite mappés
6. **Sélectionne** : Garder/Réserve sur composants (Arbitrage)
7. **Navigue** : Avec contrôles zoom entre niveaux
8. **Clique** : "Suivant" → avance vers étape 9
9. **End** : Session sauvegardée, prêt pour finalisation

---

## 💬 MESSAGE FINAL

KIMI, tu es le chef dans ce domaine. Moi je suis une chèvre en frontend. Toi tu es un fauve redoutable.

**Ton job** :
1. Pose-moi tes 5 questions
2. Attends mes réponses (max 15min)
3. Génère le frontend selon mes préférences **exactes**
4. Documente les endpoints pour que je les implémente en backend

**Mon job** :
1. Répondre à tes questions
2. Implémenter les endpoints backend Python FastAPI
3. Ne **JAMAIS** toucher ton code frontend

**Ce que je veux au final** :
Un Stenciler Sullivan magnifique, fluide, accessible, et qui respecte la stratégie Tier 1/2/3. Les 4 Corps du genome explorables avec plaisir, du niveau macro (20% preview) au niveau micro (atomes Elite).

C'est entendu ?

---

**Ton move, KIMI. Pose-moi tes questions.**

---

**François-Jean Dazin**
Boss @ Sullivan
Via Claude (Backend Lead)

11 février 2026, 4h00 AM
