# SPEC DE LECTURE V1 — Stenciler

Ce document constitue le "Comprehension Check" du design V1 (source de vérité : `stenciler.css` et `STENCILER_REFERENCE_V1.html`).

---

### Zone 1 : Header
- **Classe principale** : `.stenciler-header`
- **Dimensions** : height → `var(--header-height)` = 48px
- **Background** : `var(--bg-primary)` = #f7f6f2
- **Font** : `Geist` 14px / weight 500 / letter-spacing -0.01em
- **Layout** : flex, align-items: center, justify-content: space-between, padding 0 16px
- **Border** : border-bottom 1px solid `var(--border-subtle)` = #d5d4d0
- **États** : `#theme-toggle:hover` → border-color: `var(--border-warm)` = #c5c4c0

### Zone 2 : Sidebar gauche (Conteneur)
- **Classe principale** : `.sidebar`
- **Dimensions** : width → `var(--sidebar-width)` = 200px
- **Background** : `var(--bg-secondary)` = #f0efeb
- **Font** : Geist (héritage body 12px)
- **Layout** : flex column, overflow-y: auto
- **Border** : border-right 1px solid `var(--border-subtle)` = #d5d4d0

### Zone 3 : Sidebar header
- **Classe principale** : `.sidebar-header`
- **Dimensions** : padding 16px
- **Background** : `var(--bg-secondary)` = #f0efeb
- **Font** : `.sidebar-brand` Geist 20px / weight 800 / letter-spacing -0.02em / Color #7aca6a (Vert HomeOS)
- **Layout** : flex column
- **Border** : border-bottom 1px solid `var(--border-subtle)` = #d5d4d0

### Zone 4 : Section sidebar
- **Classe principale** : `.sidebar-section`
- **Dimensions** : padding-bottom 12px (ou padding 12px 16px)
- **Background** : non défini (transparent)
- **Font** : `.sidebar-section-title` Geist 10px / weight 600 / uppercase / letter-spacing 0.08em / color `var(--text-secondary)` = #6a6a69
- **Layout** : flex column
- **Border** : border-bottom 1px solid `var(--border-subtle)` = #d5d4d0 (sauf `:last-child`)

### Zone 5 : Preview band
- **Classe principale** : `.preview-band`
- **Dimensions** : height → `var(--preview-height)` = 110px
- **Background** : `var(--bg-secondary)` = #f0efeb
- **Font** : `.name` Geist 11px / weight 500
- **Layout** : flex, gap 8px, padding 0 12px, overflow-x: auto
- **Border** : border-bottom 1px solid `var(--border-warm)` = #c5c4c0
- **États** : `.preview-card:hover` → background `var(--bg-hover)` = #e0dfdb | `.dragging` → opacity 0.5

### Zone 6 : Canvas zone
- **Classe principale** : `.canvas-zone`
- **Dimensions** : flex: 1
- **Background** : `var(--bg-primary)` = #f7f6f2
- **Font** : `.canvas-placeholder p` Geist 12px / color `var(--text-muted)` = #999998
- **Layout** : flex center center, relative, overflow: auto
- **Border** : aucune (Grille `::before` → background-size 20px 20px, opacity 0.4 via `linear-gradient` du token `var(--border-subtle)`)

### Zone 7 : Components zone
- **Classe principale** : `.components-zone`
- **Dimensions** : height → `var(--components-height)` = 140px
- **Background** : `var(--bg-secondary)` = #f0efeb
- **Font** : `.components-title` Geist 10px / weight 500 / uppercase / letter-spacing 0.08em
- **Layout** : overflow-y auto, `.components-grid` grid 6 cols, gap 6px
- **Border** : border-top 1px solid `var(--border-subtle)` = #d5d4d0

### Zone 8 : Zoom controls
- **Classe principale** : `.zoom-controls`
- **Dimensions** : position absolute, bottom/right 16px, padding 4px
- **Background** : `var(--bg-secondary)` = #f0efeb
- **Font** : `span` Geist 11px / `button` icons 14px
- **Layout** : flex center, gap 4px
- **Border** : 1px solid `var(--border-subtle)` = #d5d4d0, radius 6px

### Zone 9 : Palette couleurs & Modes
- **Classe principale** : `.color-palette`
- **Dimensions** : `.color-swatch` 28x28px, gap 6px
- **Background** : `.color-mode-toggle` `var(--bg-tertiary)` = #e8e7e3
- **Font** : `.mode-label` 9px
- **Layout** : palette is grid (3 cols), toggle is flex
- **Border** : swatch radius 4px, toggle border 1px solid `var(--border-subtle)` = #d5d4d0

### Zone 10 : Boutons sidebar
- **Classe principale** : `.btn-back`, `.btn-delete`, `.btn-api`
- **Dimensions** : width 100%, padding 6px
- **Background** : `var(--bg-tertiary)` = #e8e7e3 (back/api) | transparent (delete)
- **Font** : Geist 11px (back/delete) or 10px (api)
- **Layout** : flex center, gap 6px (back)
- **Border** : 1px solid `var(--border-subtle)` = #d5d4d0, radius 4px
- **États** : `.btn-delete:hover` → background `rgba(200, 100, 100, 0.08)`, color #c98484
