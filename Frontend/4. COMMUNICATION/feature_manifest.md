# Feature Extraction Manifest — stenciler_v2.html → Stenciler Factory
**Produit par Claude (Mission 3A-prep) — 2026-02-16**
**Source :** `Frontend/3. STENCILER/static/stenciler_v2.html` (1540L)

---

## 1. Inventaire des Features

### 1.1 `CSSVariablesFeature` (base)
| Champ | Valeur |
|-------|--------|
| Fichier | `features/base.feature.js` |
| Lignes HTML source | L9-55 (`:root`, `[data-theme="dark"]`, `body`) |
| Description | CSS custom properties (thème light/dark) + reset |
| Dépendances JS | — |
| Taille estimée | ~50L |

### 1.2 `HeaderFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/Header.feature.js` |
| Lignes HTML source | CSS: L57-128 / HTML: L970-979 / JS: L1290-1296 + L1529-1533 |
| Description | Header fixe avec logo, onglets de navigation (BRS/BKD/FRD/DPL), bouton thème |
| Dépendances JS | `NavigationFeature.scrollToSection()` |
| Taille estimée | ~90L |

### 1.3 `GenomeSectionFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/GenomeSection.feature.js` |
| Lignes HTML source | CSS: L153-248 / HTML: L982-996 / JS: L1233-1272 |
| Description | Section 1 — liste des Corps du genome, checkboxes, bouton Valider |
| État interne | `selectedCorps: Set<string>` |
| Dépendances JS | `NavigationFeature.scrollToSection()` |
| Taille estimée | ~130L |

### 1.4 `StyleSectionFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/StyleSection.feature.js` |
| Lignes HTML source | CSS: L250-293 / HTML: L998-1037 / JS: L1302-1309 |
| Description | Section 2 — grille de 8 cartes de style (Minimal, Vercel, Brutalist…) |
| Dépendances JS | `NavigationFeature.scrollToSection()`, `StencilerOrchestratorFeature.initStenciler()` |
| Taille estimée | ~100L |

### 1.5 `PreviewBandFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/PreviewBand.feature.js` |
| Lignes HTML source | CSS: L620-741 / HTML: L1137-1139 (vide, rempli JS) / JS: L1327-1380 |
| Description | Bande horizontale scrollable avec cartes Corps draggables + wireframes SVG |
| Dépendances JS | `GenomeSectionFeature.selectedCorps`, drag events (→ `CanvasFeature`) |
| Taille estimée | ~170L |

**Note Gemini :** Le CSS wireframe (`.wf-step`, `.wf-bar`, `.wf-frame`, `.wf-deploy-btn`, `.wf-arrow` L663-731) appartient à cette feature.

### 1.6 `CanvasFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/Canvas.feature.js` |
| Lignes HTML source | CSS: L743-826 / HTML: L1142-1154 / JS: L1382-1423 + L1464-1494 |
| Description | Zone canvas Fabric.js — drop de Corps, grille de fond, contrôles zoom, placeholder |
| Dépendances JS | `fabric.js` (CDN), `PreviewBandFeature` (dragstart/drop), `ZoomControlsFeature` |
| État interne | `stencilerCanvas: fabric.Canvas`, `zoomLevel: number` |
| Taille estimée | ~160L |

**⚠️ Bug connu :** Aucune erreur canvas ici — les erreurs `'alphabetical'` de la session précédente sont dans `stenciler.js` (autre fichier, canvas différent).

### 1.7 `ZoomControlsFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | Intégré dans `Canvas.feature.js` (pas de fichier séparé) |
| Lignes HTML source | CSS: L787-826 / HTML: L1148-1153 / JS: L1464-1494 |
| Description | Boutons +/-/reset + wheel handler Ctrl+scroll |
| Dépendances JS | `CanvasFeature.stencilerCanvas` |
| Taille estimée | — (bundlé dans Canvas) |

### 1.8 `TSLPickerFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/TSLPicker.feature.js` |
| Lignes HTML source | CSS: L439-521 / HTML: L1079-1100 / JS: L1425-1445 |
| Description | Sidebar — 3 sliders TSL (Teinte/Saturation/Luminosité) avec preview en temps réel |
| Dépendances JS | `CanvasFeature` (pour appliquer couleur à l'objet sélectionné — btn Apply) |
| Taille estimée | ~110L |

### 1.9 `ColorPaletteFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/ColorPalette.feature.js` |
| Lignes HTML source | CSS: L400-437 + L523-545 / HTML: L1063-1113 / JS: L1447-1527 |
| Description | Sidebar — toggle Bordure/Fond + 6 swatches de préréglages |
| Dépendances JS | `CanvasFeature` (applique couleur) |
| Taille estimée | ~110L |

### 1.10 `BorderSliderFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/BorderSlider.feature.js` |
| Lignes HTML source | CSS: L547-571 / HTML: L1116-1120 / JS: L1456-1462 |
| Description | Sidebar — slider épaisseur de bordure (0-10px) |
| Dépendances JS | `CanvasFeature` (applique sur objet sélectionné) |
| Taille estimée | ~40L |

### 1.11 `APIStatusFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/APIStatus.feature.js` |
| Lignes HTML source | CSS: L573-611 / HTML: L1122-1131 |
| Description | Sidebar — indicateur connexion API (dot vert/rouge) + boutons "Charger Genome/Styles" |
| Dépendances JS | `fetch` API (backend `/api/genome`, `/api/styles`) |
| Taille estimée | ~70L |

### 1.12 `ComponentsZoneFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/ComponentsZone.feature.js` |
| Lignes HTML source | CSS: L828-965 / HTML: L1156-1211 |
| Description | Barre inférieure — 6 cartes composants statiques (Button/Card/Input/Modal/Table/Tabs) avec wireframes |
| Dépendances JS | `CanvasFeature` (drop futur) |
| Taille estimée | ~190L |

**Note Gemini :** Le CSS wireframe de cette section (`.wireframe-btn`, `.wf-btn-bar`, `.wf-card-header`, etc. L864-965) appartient à cette feature.

### 1.13 `NavigationFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/Navigation.feature.js` |
| Lignes HTML source | JS: L1276-1296 + L1535-1537 |
| Description | `scrollToSection()` + `IntersectionObserver` pour mise à jour des onglets header |
| Dépendances JS | `HeaderFeature` (met à jour `.header-tab.active`) |
| Taille estimée | ~40L |

### 1.14 `StencilerOrchestratorFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | `features/StencilerOrchestrator.feature.js` |
| Lignes HTML source | JS: L1312-1325 |
| Description | `initStenciler()` — point d'entrée qui chaîne l'init de toutes les features Stenciler |
| Dépendances JS | `PreviewBandFeature`, `CanvasFeature`, `TSLPickerFeature`, `ColorPaletteFeature`, `BorderSliderFeature`, `ZoomControlsFeature`, `DeleteFeature` |
| Taille estimée | ~30L |

### 1.15 `DeleteFeature`
| Champ | Valeur |
|-------|--------|
| Fichier | Intégré dans `StencilerOrchestrator.feature.js` |
| Lignes HTML source | JS: L1496-1518 / HTML: L1055-1061 (`#btn-delete`) |
| Description | Suppression de l'objet sélectionné (touche Del/Backspace + bouton sidebar) |
| Dépendances JS | `CanvasFeature.stencilerCanvas` |
| Taille estimée | — (bundlé dans Orchestrator) |

---

## 2. Inventaire des Slots (stenciler_v3.html)

```html
<body>
  <div id="slot-header"></div>          <!-- HeaderFeature -->

  <div class="app-container">
    <!-- Section 1 -->
    <section id="slot-section-genome"></section>

    <!-- Section 2 -->
    <section id="slot-section-style"></section>

    <!-- Section 3 -->
    <section id="slot-section-stenciler">
      <div class="stenciler-workspace">

        <aside id="slot-sidebar">
          <div id="slot-sidebar-header"></div>       <!-- breadcrumb + btn back -->
          <div id="slot-actions"></div>               <!-- btn delete -->
          <div id="slot-color-mode"></div>            <!-- ColorPaletteFeature toggle -->
          <div id="slot-tsl-picker"></div>            <!-- TSLPickerFeature -->
          <div id="slot-color-palette"></div>         <!-- ColorPaletteFeature swatches -->
          <div id="slot-border-slider"></div>         <!-- BorderSliderFeature -->
          <div id="slot-api-status"></div>            <!-- APIStatusFeature -->
        </aside>

        <main class="stenciler-main">
          <div id="slot-preview-band"></div>          <!-- PreviewBandFeature -->
          <div id="slot-canvas-zone"></div>           <!-- CanvasFeature + ZoomControls -->
          <div id="slot-components-zone"></div>       <!-- ComponentsZoneFeature -->
        </main>

      </div>
    </section>
  </div>

  <!-- Scripts features -->
  <script src="js/features/base.feature.js"></script>
  <script src="js/features/registry.js"></script>
  <script src="js/features/Navigation.feature.js"></script>
  <script src="js/features/Header.feature.js"></script>
  <script src="js/features/GenomeSection.feature.js"></script>
  <script src="js/features/StyleSection.feature.js"></script>
  <script src="js/features/PreviewBand.feature.js"></script>
  <script src="js/features/Canvas.feature.js"></script>
  <script src="js/features/TSLPicker.feature.js"></script>
  <script src="js/features/ColorPalette.feature.js"></script>
  <script src="js/features/BorderSlider.feature.js"></script>
  <script src="js/features/APIStatus.feature.js"></script>
  <script src="js/features/ComponentsZone.feature.js"></script>
  <script src="js/features/StencilerOrchestrator.feature.js"></script>
  <script src="js/features/manager.js"></script>
</body>
```

**Contrainte stenciler_v3.html :** CSS variables conservées en `<style>` (L9-55 = 47L) + slots = ~100L max.

---

## 3. Graphe de dépendances

```
CSSVariables (base)
     │
     ▼
NavigationFeature ◄──── HeaderFeature
     │
     ├──► GenomeSectionFeature ──► PreviewBandFeature
     │                                    │
     ├──► StyleSectionFeature             │
     │         │                          ▼
     └──► StencilerOrchestratorFeature → CanvasFeature ◄── TSLPickerFeature
                    │                         │              ColorPaletteFeature
                    ├──► PreviewBandFeature    │              BorderSliderFeature
                    ├──► ZoomControls (bundlé) │
                    └──► DeleteFeature (bundlé)│
                                              ▼
                                    ComponentsZoneFeature (futur drop)

APIStatusFeature → fetch API (indépendant)
```

**Ordre d'init :** Navigation → Header → GenomeSection → StyleSection → StencilerOrchestrator (chain interne)

---

## 4. Données mockées à externaliser

`mockGenome` (L1222-1228) doit migrer vers l'API `/api/genome` — plus de données hardcodées dans les features.
`GenomeSectionFeature` fait un `fetch('/api/genome')` et se render dynamiquement.

---

## 5. Résumé pour Gemini (Mission 3A-work)

**12 fichiers à créer** dans `Frontend/3. STENCILER/static/js/features/` :
1. `base.feature.js` — classe abstraite `StencilerFeature` + `CSSVariables`
2. `Navigation.feature.js`
3. `Header.feature.js`
4. `GenomeSection.feature.js` (avec fetch `/api/genome`)
5. `StyleSection.feature.js`
6. `PreviewBand.feature.js`
7. `Canvas.feature.js` (inclut ZoomControls + Delete)
8. `TSLPicker.feature.js`
9. `ColorPalette.feature.js` (inclut ColorModeToggle)
10. `BorderSlider.feature.js`
11. `APIStatus.feature.js`
12. `ComponentsZone.feature.js`
13. `StencilerOrchestrator.feature.js` (inclut initStenciler)
14. `registry.js`
15. `manager.js`

**Contrainte absolue :** chaque fichier < 200L.
**mockGenome** : à supprimer — remplacer par `fetch('/api/genome')`.
