# Addendum Technique - Chargement Hybride des Corps

**Date** : 11 février 2026, 17h00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Objet** : Solution au conflit typo inline vs template par défaut

---

## 🚨 PROBLÈME IDENTIFIÉ

**François-Jean** : "La typo a beau être donnée en inline, le template par défaut domine"

**Diagnostic** :
- Les styles inline sont écrasés par les styles du template
- Problème de spécificité CSS ou de timing de chargement
- Besoin d'une stratégie de chargement "malin" dans le DOM

---

## 🔍 ANALYSE DU PROBLÈME

### Scénario probable

```javascript
// Chargement actuel (KIMI)
function renderPreviewBand(corps) {
  corps.forEach(corp => {
    const preview = document.createElement('div');
    preview.style.fontFamily = corp.typography; // ❌ Écrasé par CSS
    preview.textContent = corp.name;
    container.appendChild(preview);
  });
}
```

**Problème** : Le CSS du template a une spécificité plus haute :
```css
/* Template par défaut - gagne sur l'inline */
.preview-card * {
  font-family: 'Inter', sans-serif !important; /* !important écrase inline */
}
```

---

## ✅ SOLUTIONS PROPOSÉES

### Solution 1 : Hook avec `!important` dynamique

**Principe** : Injecter les styles avec `!important` via `<style>` tag

```javascript
function applyTypographyWithForce(element, fontFamily, corpId) {
  // Créer un style spécifique pour ce Corp
  const styleId = `corp-typo-${corpId}`;

  // Supprimer ancien style si existe
  const oldStyle = document.getElementById(styleId);
  if (oldStyle) oldStyle.remove();

  // Créer nouveau style avec !important
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    .corp-${corpId},
    .corp-${corpId} * {
      font-family: ${fontFamily} !important;
    }
  `;
  document.head.appendChild(style);

  // Ajouter la classe au Corp
  element.classList.add(`corp-${corpId}`);
}

// Usage
function renderPreviewBand(corps) {
  corps.forEach(corp => {
    const preview = document.createElement('div');
    preview.dataset.corpId = corp.id;
    preview.textContent = corp.name;

    // Appliquer typo avec force
    applyTypographyWithForce(preview, corp.typography, corp.id);

    container.appendChild(preview);
  });
}
```

---

### Solution 2 : Attendre le DOM avec MutationObserver

**Principe** : Intercepter l'insertion dans le DOM et forcer les styles après

```javascript
function setupTypographyObserver(corps) {
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1 && node.dataset.corpId) {
          const corpId = node.dataset.corpId;
          const corp = corps.find(c => c.id === corpId);

          if (corp) {
            // Forcer la typo APRÈS insertion dans le DOM
            requestAnimationFrame(() => {
              node.style.setProperty('font-family', corp.typography, 'important');
            });
          }
        }
      });
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  return observer;
}

// Usage
const typographyObserver = setupTypographyObserver(genomeCorps);
```

---

### Solution 3 : Custom Data Attributes + CSS Variables

**Principe** : Utiliser des CSS variables qui ont priorité sur les classes

```javascript
function renderPreviewBandWithVars(corps) {
  corps.forEach(corp => {
    const preview = document.createElement('div');
    preview.dataset.corpId = corp.id;

    // Définir CSS variable sur l'élément
    preview.style.setProperty('--corp-font', corp.typography);
    preview.textContent = corp.name;

    container.appendChild(preview);
  });
}
```

**CSS à ajouter** :
```css
/* Dans le template - utiliser la variable si définie */
.preview-card {
  font-family: var(--corp-font, 'Inter'); /* fallback sur Inter */
}
```

---

### Solution 4 : Hook de post-render

**Principe** : Fournir un hook que KIMI peut appeler après le render

```javascript
// Hook fourni par Backend (via API ou config)
const TYPOGRAPHY_HOOK = {
  // Stratégie 1 : Injection style tag
  applyWithStyleTag: (element, fontFamily, id) => {
    const style = document.createElement('style');
    style.textContent = `.corp-${id} { font-family: ${fontFamily} !important; }`;
    document.head.appendChild(style);
    element.classList.add(`corp-${id}`);
  },

  // Stratégie 2 : setAttribute avec namespace
  applyWithAttribute: (element, fontFamily) => {
    element.setAttribute('data-typo', fontFamily);
    element.style.fontFamily = fontFamily;
  },

  // Stratégie 3 : Remplacer toutes les règles CSS
  overrideAllRules: (element, fontFamily) => {
    const sheet = new CSSStyleSheet();
    sheet.replaceSync(`
      * { font-family: ${fontFamily} !important; }
    `);
    if (element.shadowRoot) {
      element.shadowRoot.adoptedStyleSheets = [sheet];
    } else {
      // Fallback pour pas de shadow DOM
      element.style.setProperty('font-family', fontFamily, 'important');
    }
  }
};

// KIMI peut utiliser le hook
function renderWithHook(corps) {
  corps.forEach(corp => {
    const preview = createPreview(corp);
    container.appendChild(preview);

    // Appliquer le hook APRÈS insertion
    TYPOGRAPHY_HOOK.applyWithStyleTag(preview, corp.typography, corp.id);
  });
}
```

---

## 🎯 RECOMMANDATION

**Pour KIMI** : Utiliser **Solution 1 + Solution 4** (combo)

### Implémentation recommandée

**Fichier** : `Frontend/3.STENCILER/typography_manager.js`

```javascript
/**
 * Gestionnaire de typographie pour les Corps
 * Résout les conflits avec les styles du template
 */
class TypographyManager {
  constructor() {
    this.appliedStyles = new Map();
  }

  /**
   * Applique une typographie en forçant la priorité
   * @param {HTMLElement} element - Élément cible
   * @param {string} fontFamily - Police à appliquer
   * @param {string} corpId - ID du Corp (pour namespace)
   */
  apply(element, fontFamily, corpId) {
    const styleId = `corp-typo-${corpId}`;

    // Nettoyer ancien style si existe
    if (this.appliedStyles.has(corpId)) {
      this.appliedStyles.get(corpId).remove();
    }

    // Créer style avec !important
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      .corp-${corpId},
      .corp-${corpId} *,
      [data-corp-id="${corpId}"],
      [data-corp-id="${corpId}"] * {
        font-family: ${fontFamily} !important;
      }
    `;

    document.head.appendChild(style);
    this.appliedStyles.set(corpId, style);

    // Ajouter classe + data attribute
    element.classList.add(`corp-${corpId}`);
    element.dataset.corpId = corpId;
  }

  /**
   * Nettoie tous les styles appliqués
   */
  cleanup() {
    this.appliedStyles.forEach(style => style.remove());
    this.appliedStyles.clear();
  }
}

// Instance globale
const typographyManager = new TypographyManager();

// Export pour utilisation
export { typographyManager };
```

**Usage dans le render** :

```javascript
import { typographyManager } from './typography_manager.js';

function renderPreviewBand(corps) {
  const container = document.querySelector('.preview-band');

  corps.forEach(corp => {
    // Créer preview
    const preview = document.createElement('div');
    preview.className = 'preview-card';
    preview.textContent = corp.name;

    // Insérer dans le DOM
    container.appendChild(preview);

    // Appliquer typo APRÈS insertion (critique)
    requestAnimationFrame(() => {
      typographyManager.apply(preview, corp.typography, corp.id);
    });
  });
}
```

---

## 🔧 ALTERNATIVE : CSS Custom Properties

Si la Solution 1 est trop invasive, alternative plus propre :

**Backend** : Fournir un fichier CSS généré dynamiquement

```python
# Dans sullivan/stenciler/api.py

@router.get("/styles/typography.css")
async def get_typography_css():
    """Génère le CSS des typographies des Corps"""
    genome = genome_manager.get_current_state().genome
    corps = genome.get("n0_phases", [])

    css_rules = []
    for corp in corps:
        corp_id = corp.get("id")
        typography = corp.get("typography", "Inter")

        css_rules.append(f"""
.corp-{corp_id},
.corp-{corp_id} * {{
  font-family: {typography} !important;
}}
        """)

    return Response(
        content="\n".join(css_rules),
        media_type="text/css"
    )
```

**Frontend** : Charger ce CSS au démarrage

```javascript
// Dans le layout existant
async function loadTypographyStyles() {
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'http://localhost:8000/api/styles/typography.css';
  document.head.appendChild(link);
}

// Appeler au chargement du Genome
await loadTypographyStyles();
```

---

## 📋 TÂCHES POUR KIMI

### **PRIORITÉ IMMÉDIATE** : Résoudre conflit typo

- [ ] Créer `typography_manager.js` (Solution 1)
- [ ] Modifier `renderPreviewBand()` pour utiliser `typographyManager.apply()`
- [ ] Tester avec plusieurs Corps (différentes polices)
- [ ] Vérifier que les styles inline ne sont plus écrasés

### **ALTERNATIVE** (si problème persiste)

- [ ] Backend : Créer endpoint `GET /api/styles/typography.css`
- [ ] Frontend : Charger ce CSS au démarrage du Stenciler
- [ ] Vérifier que les règles CSS sont appliquées

---

## 🚀 VALIDATION

**Test à faire** :

```javascript
// Test avec 3 Corps différents
const testCorps = [
  { id: 'n0_brainstorm', name: 'Brainstorm', typography: 'Roboto' },
  { id: 'n0_backend', name: 'Backend', typography: 'Fira Code' },
  { id: 'n0_frontend', name: 'Frontend', typography: 'Poppins' }
];

renderPreviewBand(testCorps);

// Vérifier dans DevTools :
// - Computed styles montrent Roboto pour Brainstorm
// - Computed styles montrent Fira Code pour Backend
// - Computed styles montrent Poppins pour Frontend
```

---

**Statut** : Solution prête pour implémentation KIMI.

— Claude Sonnet 4.5, Backend Lead
