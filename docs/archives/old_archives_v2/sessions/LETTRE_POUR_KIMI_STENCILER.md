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

### **NIVEAU 1 - Tarmac (1/3 taille)**

```
         TARMAC (zone de travail)
    ┌──────────────────────────────┐
    │                              │
    │    ┌──────────────┐          │
    │    │   Frontend   │ ← 33%    │
    │    │              │   taille  │
    │    │  [organes +  │          │
    │    │   détails]   │          │
    │    └──────────────┘          │
    │         ↑ double-clic         │
    └──────────────────────────────┘
```

**Requis** :
- Zone tarmac centrée avec bordure dash (drop zone visuelle)
- Drag & drop depuis preview → tarmac
- Au drop : Corps passe de **20% à 33%** (pas 100%, trop gros)
- Au drop : Chargement progressif des détails des organes (n1 avec n2)
- Feedback visuel pendant drag (ghost + outline sur tarmac)
- Corps sur tarmac devient cliquable pour drill-down
- Animation smooth (300ms) ou instantanée selon ma préférence

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

**Avant de générer quoi que ce soit**, tu dois me poser ces 5 questions :

1. **Style typographique** : Inter, Geist, ou System fonts ?
2. **Priorisation des Corps** : Y a-t-il un Corps (Brainstorm/Backend/Frontend/Deploy) que tu veux voir en priorité avec plus de détails ?
3. **Animations** : Smooth & fluides (300ms) ou instantanées (mode performance) ?
4. **Grille tarmac** : Grille d'alignement visible (snap) ou canvas libre ?
5. **Chargement Elite** : Tout charger au démarrage (0ms au drill-down) ou lazy-load (économise mémoire, +50-100ms au 1er drill-down) ?

**Attends mes réponses.** Timeout : 15 minutes. Si je ne réponds pas, utilise des valeurs par défaut raisonnables et continue.

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
