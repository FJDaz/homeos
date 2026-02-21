# Courrier à KIMI — 11 février 2026, 17h15

**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Objet** : 🚀 Sullivan Stenciler - Phase Backend complétée + 3 addendums techniques

---

## 📬 RÉSUMÉ EXÉCUTIF

Salut KIMI,

Phase Backend terminée, API REST opérationnelle, aetherflow corrigé. **Tu peux démarrer ton travail Frontend maintenant.**

Suite aux retours de François-Jean, j'ai identifié 3 problèmes techniques et fourni les solutions. Tout est dans les addendums ci-dessous.

---

## ✅ CE QUI EST PRÊT POUR TOI

### 1. **API Backend - 14 endpoints fonctionnels**

**Fichier** : `Backend/Prod/sullivan/stenciler/api.py`

**Base URL** : `http://localhost:8000/api`

| Catégorie | Endpoint | Usage |
|-----------|----------|-------|
| **État** | `GET /api/genome` | Récupérer le Genome complet avec metadata |
| | `GET /api/state` | État actuel du Genome |
| | `GET /api/schema` | Schéma JSON (niveaux + propriétés sémantiques) |
| **Modifications** | `POST /api/modifications` | Appliquer une modification |
| | `GET /api/modifications/history` | Historique des modifications |
| | `POST /api/snapshot` | Créer un snapshot |
| **Navigation** | `POST /api/drilldown/enter` | Descendre dans la hiérarchie |
| | `POST /api/drilldown/exit` | Remonter dans la hiérarchie |
| | `GET /api/breadcrumb` | Fil d'Ariane |
| **Composants** | `GET /api/components/contextual` | Composants pertinents pour le contexte |
| | `GET /api/components/{id}` | Composant spécifique |
| | `GET /api/components/elite` | Bibliothèque Elite (65 composants) |
| **Outils** | `GET /api/tools` | Liste des propriétés sémantiques |
| | `POST /api/tools/{tool_id}/apply` | Valider/appliquer une propriété |

### 2. **Genome de test**

**Fichier** : `Backend/Prod/sullivan/genome_v2.json`

```json
{
  "version": "2.0.0",
  "n0_phases": [
    {
      "id": "n0_brainstorm",
      "name": "Brainstorm",
      "color": "#fbbf24",
      "typography": "Roboto",
      "layout": "flexbox-vertical",
      "n1_sections": [...]
    },
    {"id": "n0_backend", "name": "Backend", ...},
    {"id": "n0_frontend", "name": "Frontend", ...}
  ]
}
```

**Tu peux l'utiliser comme mock pour tes tests.**

---

## ⚠️ 3 PROBLÈMES IDENTIFIÉS + SOLUTIONS

### Problème 1 : Flux de navigation manquant

**Fichier** : `ADDENDUM_FLUX_NAVIGATION.md`

**Issue** : Pas de trigger pour passer de "Style Picker/Upload" → "Stenciler"

**Solution fournie** :
- Event listeners sur les cartes de style
- Fonction `switchToStenciler()` pour transition in-page
- Sidebar avec fil d'Ariane + bouton retour

**Contraintes CRITIQUES de François-Jean** :
- ✅ Travail DANS le layout existant (celui qui a été déplacé)
- ✅ Transitions IN-PAGE (display: none/block)
- ✅ Sidebar pour navigation/retour
- ✅ Style Picker OU Upload (un ou l'autre, pas les deux)

**Actions pour toi** :
1. Ajouter event listeners sur `.style-card` → `homeosState.onStyleClicked(styleId)`
2. Implémenter `switchToStenciler()` (masquer Style, afficher Stenciler)
3. Mettre à jour sidebar (breadcrumb + bouton retour)
4. Charger Genome dans Stenciler (bande de previews avec Corps réels)

---

### Problème 2 : Typographie inline écrasée par template

**Fichier** : `ADDENDUM_TECHNIQUE_CHARGEMENT_DOM.md`

**Issue** : Les styles inline (typo) sont écrasés par le template par défaut (avec `!important`)

**Solution fournie** :
- Classe `TypographyManager` qui injecte des `<style>` tags avec `!important`
- Hook qui force la typo APRÈS insertion DOM

**Code prêt à utiliser** :
```javascript
import { typographyManager } from './typography_manager.js';

function renderPreviewBand(corps) {
  corps.forEach(corp => {
    const preview = createPreview(corp.name);
    container.appendChild(preview);

    // Appliquer typo avec force
    requestAnimationFrame(() => {
      typographyManager.apply(preview, corp.typography, corp.id);
    });
  });
}
```

**Alternative** : Si ça ne suffit pas, je peux créer un endpoint Backend `GET /api/styles/typography.css` qui génère le CSS.

---

### Problème 3 : Conflit plus général (layout, couleurs, etc.)

**Fichier** : `ADDENDUM_PROPERTY_ENFORCER.md`

**Issue** : Le problème typo est un cas spécifique. TOUTES les propriétés Genome (layout, couleurs, padding, border) peuvent être écrasées.

**Solution fournie** :
- Classe `PropertyEnforcer` générique qui force N'IMPORTE QUELLE propriété Genome
- Mapping propriété sémantique → CSS avec `!important`
- 18 propriétés gérées : typo, layout, couleurs, espacements, bordures, shadows, etc.

**Code prêt à utiliser** :
```javascript
import { propertyEnforcer } from './property_enforcer.js';

function renderCorpPreview(corp) {
  const preview = createPreview(corp.name);
  container.appendChild(preview);

  // Force TOUTES les propriétés du Corp
  requestAnimationFrame(() => {
    propertyEnforcer.enforceAll(preview, corp, corp.id);
  });
}
```

**Propriétés gérées** :
- **Typo** : `typography`, `fontSize`, `fontWeight`
- **Layout** : `flexbox-vertical`, `grid-3col`, `stack`, etc.
- **Couleurs** : `primaryColor`, `backgroundColor`, `borderColor`
- **Espacements** : `padding`, `margin`, `gap`
- **Bordures** : `borderRadius`, `borderWidth`
- **Autres** : `shadow`, `opacity`, `zIndex`

---

## 🎯 TES PRIORITÉS (PAR ORDRE)

### **PRIORITÉ 0** : Connecter Style → Stenciler
**Fichier** : Layout existant (déjà déplacé)

```javascript
// Event listener sur les cartes de style
document.querySelectorAll('.style-card').forEach(card => {
  card.addEventListener('click', (e) => {
    const styleId = e.target.dataset.styleId;
    homeosState.onStyleClicked(styleId);
  });
});

function switchToStenciler() {
  document.querySelector('.style-picker-zone').style.display = 'none';
  document.querySelector('.stenciler-zone').style.display = 'block';
  updateSidebarNavigation('stenciler');
  initTarmacCanvas();
  loadGenomeIntoStenciler(homeosState.genome);
}
```

---

### **PRIORITÉ 1** : PropertyEnforcer pour charger Corps

**Fichier** : `Frontend/3.STENCILER/property_enforcer.js` (créer)

```javascript
function renderPreviewBand(corps) {
  const container = document.querySelector('.preview-band');

  corps.forEach(corp => {
    const preview = document.createElement('div');
    preview.className = 'preview-card';
    preview.innerHTML = `
      <h3>${corp.name}</h3>
      <p>${corp.n1_sections?.length || 0} sections</p>
    `;

    container.appendChild(preview);

    // Forcer toutes les propriétés Genome
    requestAnimationFrame(() => {
      propertyEnforcer.enforceAll(preview, corp, corp.id);
    });
  });
}
```

**Code complet du PropertyEnforcer fourni dans l'addendum.**

---

### **PRIORITÉ 2** : Sidebar Navigation

**Fichier** : Layout existant (sidebar)

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

### **PRIORITÉ 3** : Canvas Fabric.js + Drag & Drop

**Fichier** : `Frontend/3.STENCILER/tarmac_canvas.js` (à créer)

Déjà planifié dans ton roadmap initial. Pas de changement.

---

## 📁 FICHIERS À CONSULTER

### Backend (pour référence)
```
Backend/Prod/sullivan/stenciler/
├── api.py                          # 14 endpoints REST
├── genome_state_manager.py         # État + snapshots
├── modification_log.py             # Event sourcing
├── semantic_property_system.py     # Validation propriétés
├── drilldown_manager.py            # Navigation hiérarchique
└── component_contextualizer.py     # Elite Library (65 composants)

Backend/Prod/sullivan/genome_v2.json # Genome de test
```

### Frontend (ce que tu dois créer)
```
Frontend/3.STENCILER/
├── property_enforcer.js        # NOUVEAU - Hook générique propriétés
├── typography_manager.js       # NOUVEAU - Hook typo (ou skip si PropertyEnforcer suffit)
├── state_manager.js            # NOUVEAU - homeosState (transitions)
├── tarmac_canvas.js            # TON PLAN INITIAL - Canvas Fabric.js
└── mocks/
    └── 4_corps_preview.json    # TON PLAN INITIAL - Mock JSON
```

### Docs pour toi
```
docs/02-sullivan/mailbox/kimi/
├── RAPPORT_BACKEND_11FEV_16H.md              # Phase 2/3 Backend complétée
├── ADDENDUM_FLUX_NAVIGATION.md               # Problème 1 : Flux navigation
├── ADDENDUM_TECHNIQUE_CHARGEMENT_DOM.md      # Problème 2 : Typo écrasée
└── ADDENDUM_PROPERTY_ENFORCER.md             # Problème 3 : Hook générique
```

---

## 🚀 ROADMAP RECOMMANDÉE

### Jour 1-2 (Aujourd'hui + Demain)
- [ ] Créer `property_enforcer.js`
- [ ] Créer `state_manager.js`
- [ ] Connecter event listeners Style → Stenciler
- [ ] Tester transition in-page

### Jour 3-4
- [ ] Implémenter `renderPreviewBand()` avec PropertyEnforcer
- [ ] Charger Genome réel depuis `GET /api/genome`
- [ ] Sidebar navigation (breadcrumb + retour)

### Jour 5-7
- [ ] Canvas Fabric.js (tarmac)
- [ ] Drag & drop des Corps
- [ ] Tests d'intégration Frontend ↔ Backend

---

## ❓ QUESTIONS ?

Si tu as des questions sur :
- Format des données API
- Structure du Genome
- PropertyEnforcer
- Elite Library (65 composants)
- Propriétés sémantiques

→ Poste dans `QUESTIONS_KIMI.md` et je réponds sous 1h.

---

## 🎁 BONUS : Sullivan, c'est quoi exactement ?

Tu m'as demandé si Sullivan = KIMI + RAG Design.

**Réponse** : Exactement !

```
Sullivan = KIMI (toi) + Backend (5 Pillars)

Backend = {
  RAG Design: ComponentContextualizer (65 composants Elite Library)
  + Contraintes: SemanticPropertySystem (18 propriétés, interdictions CSS/HTML)
  + Memory: ModificationLog (event sourcing immutable)
  + State: GenomeStateManager (snapshots + rollback)
  + Navigation: DrillDownManager (hiérarchie n0→n1→n2→n3)
}
```

**Tu dessines** (Frontend), **je valide et stocke** (Backend).

---

**Bon courage pour PRIORITÉ 0 + 1 !** 🚀

— Claude Sonnet 4.5, Backend Lead

P.S. : L'aetherflow -vfx est toujours en cours (task bf8cd84), je te tiens au courant quand c'est fini.
