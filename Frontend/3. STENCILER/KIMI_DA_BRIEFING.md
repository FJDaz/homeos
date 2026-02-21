# Briefing Technique : Cibles DOM pour KIMI DA (Stenciler V3)

KIMI, ton travail esthétique est excellent, mais la V3 utilise des **Slots dynamiques**. Pour que ton CSS "mord", tu dois cibler ces structures HTML exactes générées par les Features JS.

## 1. Structure Globale (Slots)
Les conteneurs de haut niveau (Gardiens PAI) :
- `#slot-header` : Barre du haut (48px)
- `#slot-sidebar-left` : Barre gauche (220px)
- `#slot-sidebar-right` : Barre droite (220px)
- `#slot-main` : Zone centrale (Canvas)
- `#slot-preview-band` : Bandeau de prévisualisation (DOIT être en `display: flex` horizontal)

## 2. Cibles HTML par Feature

### Navigation (`#slot-navigation`)
```html
<div class="sidebar-section-title">Navigation</div>
<div class="breadcrumb" id="breadcrumb">Brainstorm</div>
<button class="btn-back hidden" id="btn-back">← Retour</button>
```

### Genome (`#slot-genome`)
```html
<div class="sidebar-section-title">Genome (N phases)</div>
<div class="phases-list">
  <div class="phase-item [selected]" data-id="...">
    <span class="phase-name">Nom</span>
    <span class="phase-confidence">95%</span>
  </div>
</div>
```

### TSL Picker (`#slot-tsl-picker`)
```html
<div class="tsl-picker">
  <div class="tsl-preview color-preview" style="..."></div>
  <div class="tsl-sliders">
    <div class="tsl-row">
      <label>T</label>
      <input type="range" class="tsl-slider hue hue-slider">
      <span class="tsl-value">180°</span>
    </div>
    <!-- Idem pour S et L -->
  </div>
</div>
```

### Components (`#slot-main` -> `.components-section`)
```html
<div class="components-section">
  <div class="sidebar-section-title">Composants</div>
  <div class="components-grid">
    <div class="component-card" data-type="button">
      <div class="wireframe-button"></div>
      <span class="name">Button</span>
    </div>
  </div>
</div>
```

## 3. Variables Obligatoires
Tu DOIS utiliser ces variables (déjà rétablies dans `stenciler.css`) :
- `--bg-primary` : Fond principal
- `--bg-secondary` : Fond sidebars
- `--border-subtle` : Bordures légères
- `--text-primary` : Texte principal

> [!IMPORTANT]
> Ne redéfinis pas les largeurs des sidebars dans ton CSS principal, elles sont verrouillées par PAI à la fin du fichier.

