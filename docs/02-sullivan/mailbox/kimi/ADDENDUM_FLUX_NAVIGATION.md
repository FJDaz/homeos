# Addendum - Flux Navigation Utilisateur

**Date** : 11 février 2026, 16h30
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Objet** : ⚠️ MANQUANT dans le plan - Transition Genome → Stenciler

---

## 🚨 PROBLÈME IDENTIFIÉ

**François-Jean demande** : "Est-ce que tu as prévu le passage validation génome à choix style ou upload à stenciler ?"

**Réponse** : NON, ce flux n'est PAS prévu dans le plan actuel.

---

## ⚠️ CONTRAINTES CRITIQUES (AJOUT 16h45)

**IMPORTANT** : François-Jean a précisé des contraintes essentielles :

1. **LE LAYOUT EXISTANT NE DOIT PAS BOUGER**
   - Pas de nouvelles sections HTML
   - Pas de déplacement de structure
   - Travail DANS le layout existant (celui qui a été déplacé)

2. **TRANSITIONS IN-PAGE (MÊME PAGE)**
   - Toutes les transitions se font sur la même page
   - Pas de navigation vers d'autres pages
   - Changements de vue via `display: none/block`

3. **SIDEBAR POUR RETOUR/FEEDBACK**
   - La sidebar doit afficher le retour/feedback de navigation
   - Navigation contrôlée depuis la sidebar

4. **STYLE PICKER OU UPLOAD (L'UN OU L'AUTRE)**
   - Ce sont deux chemins alternatifs, pas cumulatifs
   - Style Picker : Choix parmi 65 styles → Stenciler
   - Upload : Template FRD → Stenciler (via classe de lecture, à implémenter plus tard)
   - Référence : Sullivan factory dans la doc

5. **GENOME → STYLE/UPLOAD DÉJÀ IMPLÉMENTÉ**
   - La transition Genome validé → Style Picker/Upload existe déjà
   - C'est dans le layout qui a été déplacé
   - **Trigger manquant** : Style Picker clic OU Upload → Stenciler

---

## 🔄 FLUX UTILISATEUR CORRIGÉ

### Parcours RÉEL (avec contraintes in-page)

```
┌─────────────────────────────────────────────────────────────┐
│ MÊME PAGE - Layout existant déplacé                        │
│                                                             │
│ 1. BRAINSTORM                                               │
│    → Génération Genome                                      │
│    → ✅ Validation Genome                                   │
│                                                             │
│         ↓ (transition in-page, déjà implémentée)           │
│                                                             │
│ 2. STYLE PICKER ou UPLOAD (un ou l'autre)                  │
│    → Option A: Clic sur un style (65 styles)               │
│    → Option B: Upload template FRD                          │
│       (classe lecture template - voir Sullivan factory)    │
│                                                             │
│         ↓ ❓ TRANSITION MANQUANTE ❓                         │
│                                                             │
│ 3. STENCILER                                                │
│    → Bande de previews 4 Corps                             │
│    → Canvas Tarmac drag & drop                             │
│    → Sidebar : outils + navigation/retour                  │
└─────────────────────────────────────────────────────────────┘

SIDEBAR (visible tout le long) :
  - Fil d'Ariane (breadcrumb)
  - Retour/navigation
  - Outils contextuels (selon la vue active)
```

---

## ❌ CE QUI MANQUE ACTUELLEMENT

### 1. **Trigger d'entrée dans le Stenciler**

**Question** : Quand et comment le Stenciler s'affiche ?

**Réponse** :
- **Clic sur un style** (Style Picker) → Affichage Stenciler
- **Upload template réussi** (Upload FRD) → Affichage Stenciler

**État actuel** : Ces triggers ne sont PAS connectés au Stenciler.

---

### 2. **Gestion de l'état global de l'application**

**Besoin** :
```javascript
// État global manquant
const appState = {
  currentView: "brainstorm" | "style_picker" | "upload" | "stenciler",
  genome: null,              // Genome validé
  styleSelected: string | null,
  templateUploaded: boolean,
  stencilerActive: boolean
}
```

**État actuel** : Pas de state management pour les transitions de vue.

---

### 3. **Transition Style/Upload → Stenciler IN-PAGE**

**Besoin** :
1. **Clic sur style** → `appState.styleSelected = styleId` → Afficher Stenciler
2. **Upload réussi** → `appState.templateUploaded = true` → Afficher Stenciler
3. **Affichage Stenciler** : `display: block` sur zone Stenciler (dans layout existant)
4. **Sidebar feedback** : Afficher fil d'Ariane + bouton retour

**État actuel** : Pas de séquence définie pour ces transitions.

---

## ✅ PROPOSITION DE SOLUTION (IN-PAGE)

### Architecture proposée

#### A. **État global** (à ajouter dans layout existant)

```javascript
// State management global - DANS LE LAYOUT EXISTANT
const homeosState = {
  currentView: "brainstorm",     // Vue active (brainstorm/style_picker/upload/stenciler)
  genome: null,                  // Genome validé (JSON)
  styleSelected: null,           // ID du style choisi
  templateData: null,            // Données template uploadé

  // Méthodes de transition IN-PAGE
  onStyleClicked(styleId) {
    this.styleSelected = styleId;
    this.switchToStenciler();
  },

  onTemplateUploaded(templateData) {
    this.templateData = templateData;
    this.switchToStenciler();
  },

  switchToStenciler() {
    // Masquer Style Picker/Upload (dans layout existant)
    this.currentView = "stenciler";

    // Afficher zone Stenciler (déjà dans le DOM)
    const stencilerZone = document.querySelector('.stenciler-zone');
    stencilerZone.style.display = 'block';

    // Mettre à jour la sidebar
    updateSidebarNavigation('stenciler');

    // Initialiser le canvas
    initTarmacCanvas();
    loadGenomeIntoStenciler(this.genome);
  }
};
```

---

#### B. **Flux de transition IN-PAGE**

**1. Genome validé → Style Picker/Upload** (DÉJÀ IMPLÉMENTÉ)
```javascript
// Cette transition existe déjà dans le layout déplacé
// Pas de modification nécessaire
```

**2. Clic sur Style → Stenciler** (NOUVEAU)
```javascript
// Event listener sur les cartes de style
document.querySelectorAll('.style-card').forEach(card => {
  card.addEventListener('click', (e) => {
    const styleId = e.target.dataset.styleId;
    homeosState.onStyleClicked(styleId);
  });
});
```

**3. Upload Template → Stenciler** (À IMPLÉMENTER PLUS TARD)
```javascript
// Référence : Sullivan factory dans la doc
// Classe de lecture du template FRD
async function handleTemplateUpload(file) {
  const templateReader = new SullivanTemplateReader(); // À créer
  const templateData = await templateReader.parse(file);
  homeosState.onTemplateUploaded(templateData);
}
```

**4. Sidebar Navigation** (NOUVEAU)
```javascript
function updateSidebarNavigation(currentView) {
  const sidebar = document.querySelector('.sidebar');

  // Mettre à jour le fil d'Ariane
  const breadcrumb = getBreadcrumb(currentView);
  sidebar.querySelector('.breadcrumb').innerHTML = breadcrumb;

  // Afficher bouton retour si pas sur Brainstorm
  if (currentView !== 'brainstorm') {
    sidebar.querySelector('.back-button').style.display = 'block';
  }
}

function getBreadcrumb(view) {
  const crumbs = {
    brainstorm: 'Brainstorm',
    style_picker: 'Brainstorm > Style',
    upload: 'Brainstorm > Upload',
    stenciler: 'Brainstorm > Style > Stenciler'
  };
  return crumbs[view] || '';
}
```

---

## 📋 TÂCHES POUR TOI (KIMI)

### **PRIORITÉ 0** (NOUVEAU) : Connecter Style/Upload → Stenciler

**Fichier** : Ajouter dans le layout existant (déjà déplacé)

**Modifications** :

1. **Event listeners sur les cartes de style** :
```javascript
// Dans le script du layout existant
document.querySelectorAll('.style-card').forEach(card => {
  card.addEventListener('click', (e) => {
    const styleId = e.target.dataset.styleId;
    homeosState.onStyleClicked(styleId);
  });
});
```

2. **Fonction de transition vers Stenciler** :
```javascript
function switchToStenciler() {
  // Masquer Style Picker (déjà dans le DOM)
  document.querySelector('.style-picker-zone').style.display = 'none';

  // Afficher Stenciler (déjà dans le DOM)
  document.querySelector('.stenciler-zone').style.display = 'block';

  // Mettre à jour sidebar
  updateSidebarNavigation('stenciler');

  // Init canvas
  initTarmacCanvas();
  loadGenomeIntoStenciler(homeosState.genome);
}
```

---

### **PRIORITÉ 1** : Sidebar Navigation/Retour

**Modifications dans la sidebar existante** :

```javascript
function updateSidebarNavigation(view) {
  const sidebar = document.querySelector('.sidebar');

  // Fil d'Ariane
  const breadcrumb = {
    brainstorm: 'Brainstorm',
    style_picker: 'Brainstorm > Style',
    stenciler: 'Brainstorm > Style > Stenciler'
  }[view];

  sidebar.querySelector('.breadcrumb').textContent = breadcrumb;

  // Bouton retour
  if (view !== 'brainstorm') {
    sidebar.querySelector('.back-button').style.display = 'block';
  }
}
```

---

### **PRIORITÉ 2** : Charger Genome dans Stenciler

**Fonction à ajouter** :
```javascript
function loadGenomeIntoStenciler(genome) {
  const corps = genome.n0_phases || [];
  renderPreviewBand(corps); // Utiliser les Corps du Genome
}
```

---

## 🎯 FLUX COMPLET RÉVISÉ (IN-PAGE)

### Nouveau parcours utilisateur

```
┌────────────────────────────────────────────────────────┐
│ LAYOUT EXISTANT (une seule page)                      │
│                                                        │
│ 1. Zone Brainstorm (visible)                          │
│    → Génération Genome                                 │
│    → Validation Genome ✅                              │
│                                                        │
│         ↓ (transition in-page, DÉJÀ IMPLÉMENTÉE)      │
│                                                        │
│ 2. Zone Style Picker/Upload (visible après validation)│
│    → Clic sur une carte de style                      │
│         OU                                             │
│    → Upload template FRD (plus tard)                   │
│                                                        │
│         ↓ (NOUVEAU : event listener → transition)     │
│                                                        │
│ 3. Zone Stenciler (cachée → visible au clic)          │
│    → Bande de previews (4 Corps du Genome)            │
│    → Canvas Tarmac drag & drop                        │
│    → Sidebar : fil d'Ariane + bouton retour           │
│                                                        │
└────────────────────────────────────────────────────────┘

PAS DE CHANGEMENT DE PAGE
PAS DE NOUVELLE SECTION HTML
TOUT SE PASSE DANS LE LAYOUT EXISTANT
```

---

## ⚠️ DÉPENDANCES BACKEND

**API disponibles** :
- ✅ **GET /api/genome** → Genome complet (déjà créé)
- ✅ **GET /api/components/elite** → 65 composants Elite Library (déjà créé)

**API à ajouter** (si besoin) :
- **GET /api/styles** → Liste des 65 styles avec metadata (optionnel, peut être côté Frontend)

**État actuel** : Les API essentielles existent déjà (Phase 3 complétée).

---

## 🚀 PROCHAINES ÉTAPES

### Pour KIMI (Frontend) - PRIORITÉ

**Travail dans le layout existant UNIQUEMENT** :

- [ ] **Priorité 0** : Ajouter event listeners sur les cartes de style (clic → Stenciler)
- [ ] **Priorité 1** : Implémenter `switchToStenciler()` (masquer Style, afficher Stenciler)
- [ ] **Priorité 2** : Mettre à jour sidebar avec fil d'Ariane + bouton retour
- [ ] **Priorité 3** : Charger Genome dans Stenciler (bande de previews avec Corps réels)

**Upload template (plus tard)** :
- [ ] Créer classe `SullivanTemplateReader` (voir Sullivan factory dans la doc)
- [ ] Event listener upload → `onTemplateUploaded()` → Stenciler

### Pour Claude (Backend) - OPTIONNEL

- [ ] Endpoint `GET /api/styles` (si KIMI en a besoin, sinon skip)

---

## ✅ QUESTIONS RÉSOLUES (François-Jean)

1. **Le Style Picker est-il obligatoire** avant le Stenciler ?
   - **Réponse** : Style Picker OU Upload (l'un ou l'autre, pas les deux)
   - Transition Genome → Style/Upload DÉJÀ IMPLÉMENTÉE dans layout existant

2. **Upload FRD : obligatoire ou optionnel** ?
   - **Réponse** : Optionnel (alternative au Style Picker)
   - Classe de lecture template à implémenter plus tard (ref : Sullivan factory)

3. **Les 65 styles** : Où sont-ils stockés ?
   - **Réponse** : Elite Library accessible via `GET /api/components/elite`
   - 65 composants préchargés dans `ComponentContextualizer`

4. **Layout existant** :
   - **Réponse** : NE PAS MODIFIER le layout existant (celui qui a été déplacé)
   - Toutes les transitions IN-PAGE
   - Sidebar pour navigation/retour

---

**Statut** : KIMI peut démarrer l'implémentation avec ces clarifications.

— Claude Sonnet 4.5, Backend Lead
