# Addendum - Generic Property Enforcer

**Date** : 11 février 2026, 17h15
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Objet** : Hook générique pour forcer TOUTES les propriétés Genome (typo, layout, couleurs, etc.)

---

## 🚨 PROBLÈME GÉNÉRALISÉ

**Observation** : Le conflit typo inline vs template est un cas spécifique d'un problème plus large.

### Propriétés Genome potentiellement écrasées

```javascript
// Toutes ces propriétés du Genome peuvent être écrasées par le template
const genomeProperties = {
  // TYPOGRAPHIE
  typography: "Roboto",           // ❌ Écrasé par template font-family

  // LAYOUT
  layout: "flexbox-vertical",     // ❌ Écrasé par template display/flex

  // COULEURS (preload du Genome)
  primaryColor: "#fbbf24",        // ❌ Écrasé par template --color-primary
  backgroundColor: "#ffffff",     // ❌ Écrasé par template background

  // ESPACEMENTS
  padding: "2rem",                // ❌ Écrasé par template padding
  margin: "1rem",                 // ❌ Écrasé par template margin

  // BORDURES
  borderRadius: "8px",            // ❌ Écrasé par template border-radius
  borderColor: "#e5e7eb"          // ❌ Écrasé par template border-color
};
```

---

## ✅ SOLUTION : PROPERTY ENFORCER GÉNÉRIQUE

### Architecture

**Principe** : Un système unique qui force n'importe quelle propriété Genome avec la bonne stratégie.

```javascript
/**
 * PropertyEnforcer - Force les propriétés Genome sur les éléments DOM
 * Résout les conflits avec les styles du template
 */
class PropertyEnforcer {
  constructor() {
    this.enforcedProperties = new Map(); // Map<elementId, Map<property, styleTag>>
    this.strategyMap = this.buildStrategyMap();
  }

  /**
   * Mapping propriété Genome → stratégie CSS
   */
  buildStrategyMap() {
    return {
      // TYPOGRAPHIE
      typography: (value) => `font-family: ${value}`,
      fontSize: (value) => `font-size: ${value}`,
      fontWeight: (value) => `font-weight: ${value}`,

      // LAYOUT
      layout: (value) => this.mapLayoutToCSS(value),

      // COULEURS
      primaryColor: (value) => `--color-primary: ${value}; color: ${value}`,
      backgroundColor: (value) => `background-color: ${value}`,
      borderColor: (value) => `border-color: ${value}`,

      // ESPACEMENTS
      padding: (value) => `padding: ${value}`,
      margin: (value) => `margin: ${value}`,
      gap: (value) => `gap: ${value}`,

      // BORDURES
      borderRadius: (value) => `border-radius: ${value}`,
      borderWidth: (value) => `border-width: ${value}`,

      // SHADOWS
      shadow: (value) => `box-shadow: ${value}`,

      // AUTRES
      opacity: (value) => `opacity: ${value}`,
      zIndex: (value) => `z-index: ${value}`
    };
  }

  /**
   * Applique une propriété Genome sur un élément avec force
   * @param {HTMLElement} element - Élément cible
   * @param {string} property - Nom propriété Genome (ex: "typography")
   * @param {any} value - Valeur (ex: "Roboto")
   * @param {string} elementId - ID unique de l'élément (ex: "corp-n0_brainstorm")
   */
  enforce(element, property, value, elementId) {
    // Récupérer ou créer le storage pour cet élément
    if (!this.enforcedProperties.has(elementId)) {
      this.enforcedProperties.set(elementId, new Map());
    }
    const elementProps = this.enforcedProperties.get(elementId);

    // Nettoyer ancien style si existe
    if (elementProps.has(property)) {
      elementProps.get(property).remove();
    }

    // Générer le CSS avec la stratégie appropriée
    const cssRule = this.generateCSSRule(property, value, elementId);

    // Créer et injecter le style tag
    const style = document.createElement('style');
    style.id = `enforced-${elementId}-${property}`;
    style.textContent = cssRule;
    document.head.appendChild(style);

    // Stocker
    elementProps.set(property, style);

    // Ajouter classe/data pour ciblage CSS
    element.classList.add(`genome-${elementId}`);
    element.dataset.genomeId = elementId;
  }

  /**
   * Génère une règle CSS avec !important
   */
  generateCSSRule(property, value, elementId) {
    const strategy = this.strategyMap[property];

    if (!strategy) {
      console.warn(`PropertyEnforcer: Unknown property "${property}"`);
      return '';
    }

    const cssProperty = strategy(value);

    // Règle CSS avec sélecteurs multiples et !important
    return `
      .genome-${elementId},
      .genome-${elementId} > *,
      [data-genome-id="${elementId}"],
      [data-genome-id="${elementId}"] > * {
        ${cssProperty} !important;
      }
    `;
  }

  /**
   * Mapping layout sémantique → CSS
   */
  mapLayoutToCSS(layoutValue) {
    const layouts = {
      'flexbox-vertical': 'display: flex; flex-direction: column',
      'flexbox-horizontal': 'display: flex; flex-direction: row',
      'grid-2col': 'display: grid; grid-template-columns: repeat(2, 1fr)',
      'grid-3col': 'display: grid; grid-template-columns: repeat(3, 1fr)',
      'grid-4col': 'display: grid; grid-template-columns: repeat(4, 1fr)',
      'stack': 'display: flex; flex-direction: column; gap: 1rem',
      'inline': 'display: inline-flex; gap: 0.5rem'
    };

    return layouts[layoutValue] || 'display: block';
  }

  /**
   * Applique TOUTES les propriétés d'un Corp/Organe/Feature
   */
  enforceAll(element, genomeNode, elementId) {
    // Liste des propriétés à forcer
    const propertiesToEnforce = [
      'typography',
      'layout',
      'primaryColor',
      'backgroundColor',
      'padding',
      'margin',
      'borderRadius',
      'borderColor',
      'shadow'
    ];

    propertiesToEnforce.forEach(prop => {
      if (genomeNode[prop]) {
        this.enforce(element, prop, genomeNode[prop], elementId);
      }
    });
  }

  /**
   * Nettoie toutes les propriétés forcées
   */
  cleanup() {
    this.enforcedProperties.forEach(elementProps => {
      elementProps.forEach(style => style.remove());
    });
    this.enforcedProperties.clear();
  }
}

// Instance globale
const propertyEnforcer = new PropertyEnforcer();

export { propertyEnforcer };
```

---

## 🎯 USAGE DANS LE STENCILER

### Cas 1 : Charger un Corp avec toutes ses propriétés

```javascript
import { propertyEnforcer } from './property_enforcer.js';

function renderCorpPreview(corp) {
  const preview = document.createElement('div');
  preview.className = 'preview-card';
  preview.textContent = corp.name;

  // Insérer dans le DOM
  container.appendChild(preview);

  // Forcer TOUTES les propriétés du Corp
  requestAnimationFrame(() => {
    propertyEnforcer.enforceAll(preview, corp, corp.id);
  });

  return preview;
}

// Exemple d'usage
const brainstormCorp = {
  id: 'n0_brainstorm',
  name: 'Brainstorm',
  typography: 'Roboto',
  layout: 'flexbox-vertical',
  primaryColor: '#fbbf24',
  backgroundColor: '#fffbeb',
  padding: '2rem',
  borderRadius: '12px'
};

renderCorpPreview(brainstormCorp);
```

### Cas 2 : Forcer UNE propriété spécifique

```javascript
// Si on veut juste forcer la typo
const element = document.querySelector('.some-element');
propertyEnforcer.enforce(element, 'typography', 'Fira Code', 'custom-id-123');
```

### Cas 3 : Charger les 4 Corps de la bande de previews

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

// Appel depuis loadGenomeIntoStenciler
async function loadGenomeIntoStenciler(genome) {
  const corps = genome.n0_phases || [];

  // Nettoyer propriétés précédentes
  propertyEnforcer.cleanup();

  // Render avec enforcement
  renderPreviewBand(corps);
}
```

---

## 🔧 INTÉGRATION BACKEND (OPTIONNEL)

### Endpoint pour générer le CSS complet

Si KIMI préfère charger un CSS pré-généré depuis le Backend :

```python
# Backend/Prod/sullivan/stenciler/api.py

from fastapi.responses import Response

@router.get("/styles/genome.css")
async def get_genome_css():
    """Génère le CSS pour toutes les propriétés du Genome"""
    genome = genome_manager.get_current_state().genome
    corps = genome.get("n0_phases", [])

    css_rules = []

    # Mapping propriétés Genome → CSS
    property_map = {
        "typography": lambda v: f"font-family: {v}",
        "layout": lambda v: map_layout_to_css(v),
        "primaryColor": lambda v: f"--color-primary: {v}; color: {v}",
        "backgroundColor": lambda v: f"background-color: {v}",
        "padding": lambda v: f"padding: {v}",
        "margin": lambda v: f"margin: {v}",
        "borderRadius": lambda v: f"border-radius: {v}",
        "borderColor": lambda v: f"border-color: {v}",
    }

    def generate_rules_for_node(node, node_id):
        rules = []
        for prop, css_fn in property_map.items():
            if prop in node:
                css_property = css_fn(node[prop])
                rules.append(f"""
.genome-{node_id},
.genome-{node_id} > *,
[data-genome-id="{node_id}"],
[data-genome-id="{node_id}"] > * {{
  {css_property} !important;
}}
                """)
        return rules

    # Générer pour chaque Corp
    for corp in corps:
        corp_id = corp.get("id")
        css_rules.extend(generate_rules_for_node(corp, corp_id))

        # Générer pour chaque Section
        for section in corp.get("n1_sections", []):
            section_id = section.get("id")
            css_rules.extend(generate_rules_for_node(section, section_id))

    return Response(
        content="\n".join(css_rules),
        media_type="text/css"
    )


def map_layout_to_css(layout_value: str) -> str:
    layouts = {
        "flexbox-vertical": "display: flex; flex-direction: column",
        "flexbox-horizontal": "display: flex; flex-direction: row",
        "grid-2col": "display: grid; grid-template-columns: repeat(2, 1fr)",
        "grid-3col": "display: grid; grid-template-columns: repeat(3, 1fr)",
        "grid-4col": "display: grid; grid-template-columns: repeat(4, 1fr)",
        "stack": "display: flex; flex-direction: column; gap: 1rem",
    }
    return layouts.get(layout_value, "display: block")
```

### Frontend : Charger ce CSS au démarrage

```javascript
async function loadGenomeStyles() {
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'http://localhost:8000/api/styles/genome.css';
  link.id = 'genome-styles';
  document.head.appendChild(link);
}

// Appeler au chargement du Stenciler
await loadGenomeStyles();
```

---

## 📋 RECOMMANDATION

**Pour KIMI** : 2 options selon complexité

### Option 1 : Frontend pur (PropertyEnforcer JS) ⭐ RECOMMANDÉ
- ✅ Pas de dépendance Backend
- ✅ Dynamique (changements en temps réel)
- ✅ Contrôle total côté Frontend
- ❌ Code JS un peu plus lourd

### Option 2 : Backend CSS généré
- ✅ CSS pré-compilé (plus rapide)
- ✅ Moins de JS côté Frontend
- ❌ Dépendance Backend
- ❌ Moins dynamique (rechargement nécessaire)

**Je recommande Option 1** : PropertyEnforcer JS pour commencer, puis Option 2 si besoin d'optimisation.

---

## 🚀 PROCHAINES ÉTAPES POUR KIMI

### **PRIORITÉ IMMÉDIATE**

- [ ] Créer `Frontend/3.STENCILER/property_enforcer.js`
- [ ] Modifier `renderPreviewBand()` pour utiliser `propertyEnforcer.enforceAll()`
- [ ] Tester avec un Corp complet (typo + layout + couleurs + padding + border)
- [ ] Vérifier dans DevTools que TOUTES les propriétés sont appliquées

### **OPTIONNEL (si besoin)**

- [ ] Backend : Créer endpoint `GET /api/styles/genome.css`
- [ ] Frontend : Charger ce CSS au démarrage du Stenciler

---

## ✅ VALIDATION

**Test complet** :

```javascript
// Test avec un Corp riche en propriétés
const testCorp = {
  id: 'n0_test',
  name: 'Test Corp',
  typography: 'Fira Code',
  layout: 'flexbox-vertical',
  primaryColor: '#6366f1',
  backgroundColor: '#eef2ff',
  padding: '3rem',
  margin: '1rem',
  borderRadius: '16px',
  borderColor: '#c7d2fe',
  shadow: '0 4px 6px rgba(0,0,0,0.1)'
};

renderCorpPreview(testCorp);

// Vérifier dans DevTools Computed Styles :
// ✅ font-family: "Fira Code"
// ✅ display: flex; flex-direction: column
// ✅ color: rgb(99, 102, 241)
// ✅ background-color: rgb(238, 242, 255)
// ✅ padding: 48px (3rem)
// ✅ border-radius: 16px
// ✅ box-shadow: 0 4px 6px rgba(0,0,0,0.1)
```

---

**Statut** : PropertyEnforcer générique prêt pour implémentation.

— Claude Sonnet 4.5, Backend Lead
