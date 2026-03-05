# 🧪 Sandbox Payloads - Frontend Layout Experiments

**⚠️ CONSTITUTION V3.1 COMPLIANT**  
**Zero serveur modification - Zero backend touch - Pure SVG**

---

## 🎯 Principe

Ce dossier contient des **payloads SVG purs** pour tester des layouts Frontend.  
**Aucune modification du serveur ou du genome n'est nécessaire.**

---

## 🚀 Workflow

### 1. Ouvrir Stenciler
```
http://localhost:9998/stenciler
```

### 2. Activer le mode Sandbox
Dans la console du navigateur (F12):
```javascript
window.enableSandbox()
```

Un bandeau vert apparaît en haut de la page.

### 3. Tester un payload SVG
```javascript
// Charger un SVG depuis les payloads
fetch('/static/../sandbox_payloads/timeline_rail.svg')
  .then(r => r.text())
  .then(svg => window.sandboxInject(svg));
```

Ou injecter directement:
```javascript
const mySVG = `<svg>...</svg>`;
window.sandboxInject(mySVG);
```

### 4. Désactiver
```javascript
window.disableSandbox()
```

---

## 📦 Payloads Disponibles

| Fichier | Description | Usage |
|---------|-------------|-------|
| `timeline_rail.svg` | Rail timeline avec 7 points numérotés | Header de section Frontend |
| `frontend_card.svg` | Carte organe style Hype Minimaliste | Card individuelle |
| `frontend_wave_layout.svg` | Layout 7 cards en vague | Layout complet Frontend |

---

## 🎨 Design System (Hype Minimaliste)

### Palette
```
Ardoise:    #5A6B7C  (texte, structure)
Terra:      #C4A589  (accent chaud)
Mauve:      #9B8B9E  (accent froid)
Frontend:   #a8dcc9  (vert doux - identité section)
Background: #fafafa  (cards)
```

### Typography
- Police: `system-ui` ou `Inter`
- Bas de casse (lowercase)
- Weight: 700 pour titres, 400-600 pour corps

### Composants
- Cards: 240×90px, border-radius 8px
- Pills: height 14-16px, radius 50%
- Bandeau latéral: 4px width, couleur identité

---

## 🔧 API Sandbox (Console)

```javascript
// Activation/Désactivation
window.enableSandbox()    // Active le mode
window.disableSandbox()   // Désactive

// Injection
window.sandboxInject(svgString)  // Injecte du SVG dans le canvas

// État
window.stencilerApp.features.get('canvas').sandboxMode  // true/false
```

---

## 📝 Constitution Compliance

✅ **Zero serveur** - Pas de modification de `server_9998_v2.py`  
✅ **Zero backend** - Pas de toucher à `genome.json`  
✅ **Zero cache** - Bypass SW automatique en sandbox  
✅ **Pristine Mode** - Production intacte  

---

## 🎓 Exemples

### Créer un layout personnalisé
```javascript
const customLayout = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600">
  <!-- Votre contenu ici -->
  <rect x="100" y="100" width="200" height="100" fill="#a8dcc9" rx="8"/>
  <text x="200" y="155" text-anchor="middle" font-size="14" font-weight="700" fill="#1a1a1a">
    mon layout
  </text>
</svg>
`;
window.sandboxInject(customLayout);
```

### Modifier le layout Frontend existant
Le `SandboxFeature` redéfinit `_renderCorps()` pour le corps `n0_frontend`:
- Timeline rail en haut
- Cards en disposition "vague" (sinusoïdale)
- Couleurs alternées (a8dcc9, C4A589, 9B8B9E, 5A6B7C)

---

*« Sandbox = Liberté créative sans toucher à la Constitution »*  
— Sullivan V3.1
