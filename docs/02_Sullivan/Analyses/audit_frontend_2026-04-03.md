# Audit Frontend AetherFlow — État des lieux

**Date :** 2026-04-03
**Scope :** `/Frontend/3. STENCILER/`
**Auditeur :** Qwen Code

---

## 📊 Vue d'ensemble

| Métrique | Valeur |
|---|---|
| Fichiers JS | 70 (15 499 lignes) |
| Fichiers CSS | 9 (7 472 lignes) |
| Templates HTML | 35+ (18 143 lignes) |
| Poids total | **126 MB sur disque** |
| Fichiers morts | ~20 |
| `console.log` en prod | **196** |
| Failles XSS | **6+ critiques** |

---

## 🔴 CRITIQUE — Bloquant pour livraison

### 1. XSS directe via `postMessage`
**Fichier :** `workspace/tracker/ws_iframe_core.js:97`
```js
target.outerHTML = e.data.html  // ← e.data.html non validé, origine non vérifiée
```
N'importe quelle iframe peut injecter du HTML arbitraire dans le DOM parent. Aucune vérification d'origine (`e.origin`) ni de sanitization.

### 2. XSS via `onclick=` interpolé (6+ instances)

| Fichier | Ligne | Pattern |
|---|---|---|
| `font_manager.js` | 150 | `onclick="window.fontManager.deleteFont('${font.slug}')"` |
| `workspace/ws_font_manager.js` | 119 | Même pattern copié-collé |
| `frd/FrdAssets.feature.js` | 27 | `onclick="window.frdApp.assets.copyUrl('${url}', this)"` |
| `frd/FrdAssets.feature.js` | 31 | `onclick="event.stopPropagation(); window.frdApp.assets.remove('${url}', ..."` |
| `sullivan_renderer.js` | 386 | `onclick="${clickHandler}"` — handler string directement interpolé |
| `sullivan_renderer.js` | 395 | `onclick="event.stopPropagation(); window.genomeEngine ? ..."` |

Les données non échappées sont interpolées directement dans des attributs HTML. Un slug ou URL malveillant exécute du code arbitraire.

### 3. 2.1 MB de fichiers temporaires non nettoyés
`static/temp_previews/` — **39 fichiers** dans 6 dossiers UUID, avec artefacts `__MACOSX` (resource forks macOS). Rien à faire en prod, ne devrait pas être versionné.

### 4. 12 fichiers HTML morts à la racine de `static/`
Ces fichiers sont **servis par le serveur** et ne devraient pas exister dans le dossier static :

| Fichier | Poids |
|---|---|
| `REFERENCE_FINALE.html` | 11 KB |
| `REFERENCE_V1.html` | 18 KB |
| `STENCILER_REFERENCE_V1.html` | 64 KB |
| `stenciler_v2.html` | 53 KB |
| `stenciler_unified.html` | 15 KB |
| `stenciler_scroll.html` | 17 KB |
| `genome_canvas.html` | 28 KB |
| `genome_canvas.generated.html` | 13 KB |
| `wireframe_test_7a.html` | 34 KB |
| `test_atoms.html` | 3.6 KB |
| `stenciler-mi-chemin.html` | 4.9 KB |
| `stenciler_REFERENCE.html` | 64 KB |

**Total : ~330 KB de HTML mort servi publiquement.**

### 5. `cadrage_alt.html` — 514 KB avec un blob CSS d'ad-blocker scrapé
Ligne 296 : un `<style>` de **4000+ sélecteurs** (Outbrain, Taboola, Zergnet, etc.) en `display:none!important`. Probablement injecté par un scrape automatique ou une copie depuis une page web polluée par des régies publicitaires.

---

## 🟠 MAJEUR — Architecture

### 6. Fichiers dupliqués (copy-paste)

| Paire | Lignes | Différence |
|---|---|---|
| `font_manager.js` / `workspace/ws_font_manager.js` | 300+ / 280 | Nom de classe différent (`FontManager` vs `WsFontManager`), même logique Sullivan Typography Engine |
| `stenciler_app.js` / `stenciler_app.generated.js` | 400 / 497 | Hooks Sullivan ajoutés dans le `.generated` |
| `viewer.js` / `viewer.generated.js` | 151 / 504 | 3x plus gros, même base avec hooks Sullivan |
| `import_2026-04-01_184239_*.html` / `185313` / `190153` | 9 694 bytes chacun | **Contenu identique**, timestamps différents |

### 7. 9 fichiers CSS avec overlap massif (7 472 lignes)

Trois fichiers "v3" qui devraient n'en faire qu'un :

| Fichier | Lignes | Règles |
|---|---|---|
| `stenciler_v3_final.css` | 1 102 | 147 |
| `stenciler_v3_additions.css` | 1 059 | 145 |
| `stenciler_v3_layout.css` | 486 | 64 |

Plus `kimi_mess.css` (1 162 lignes — le nom parle de lui-même).

**Sélecteurs dupliqués across fichiers :**

| Sélecteur | Fichiers touchés |
|---|---|
| `.preview-card` | 6 |
| `.active` | 34 contextes |
| `.color-swatch` | 22 |
| `.zoom-controls` | 21 |
| `.dropped-bar` | 18 |
| `.component-card` | 14 |
| `.btn-delete` | 14 |
| `.sidebar-brand` | 13 |
| `.sidebar-section` | 12 |
| `.mode-btn` | 11 |
| `.comp-card` | 11 |

### 8. Aucun bundler, aucun build system

70 fichiers JS chargés via `<script>` individuels. Les `.generated.js` sont des concaténations manuelles. Pas de webpack, vite, esbuild. Pas de minification. Pas de tree-shaking.

### 9. `http://localhost:8000` hardcodé
```js
// stenciler_app.generated.js:165
API_BASE_URL: 'http://localhost:8000'

// viewer.generated.js:142 — même constante dupliquée
API_BASE_URL: 'http://localhost:8000'
```
Impossible à déployer ailleurs sans modifier le code source.

### 10. Pas de fichier centralisé d'API

Les endpoints sont hardcodés dans **15+ fichiers** :

| Préfixe | Fichiers concernés |
|---|---|
| `/api/genome`, `/api/drilldown/*` | `stenciler_app.js`, `genome_engine.js` |
| `/api/sullivan/*` | `font_manager.js`, `sullivan_renderer.js`, `WsChat.js` |
| `/api/frd/*` | `FrdWire.feature.js`, `FrdAssets.feature.js` |
| `/api/workspace/*` | `ws_main.js`, `WsCanvas.js`, `WsPreview.js` |
| `/api/retro-genome/*` | `landing.html`, `viewer.js` |
| `/api/import/*` | `landing.html` |
| `/api/projects/*` | `ws_main.js` |

Aucune constante partagée, aucun client API unifié.

---

## 🟡 MODÉRÉ — Dette technique

### 11. 196 `console.log` en production

Les pires offenders :

| Fichier | Count | Notes |
|---|---|---|
| `stenciler_app.generated.js` | 30+ | Emojis prefixés (`🎨`, `🔧`) |
| `stenciler_app.js` | 20+ | Debug de chaque fonction |
| `stenciler_v3_main.js` | 11 | 11 console en 81 lignes (13% du fichier) |
| `genome_engine.js` | 8+ | Chaque méthode loggue |
| `workspace/WsInspect.js` | 6+ | |
| `semantic_bridge.js` | 4+ | Constructor inclus |

### 12. 27 fichiers mélangent ES modules et globals `window.*`

Le namespace `window` est utilisé comme service locator sans convention de nommage :

```
window.fontManager
window.genomeEngine
window.wsAudit, .wsForge, .wsPreview, .wsCanvas, .wsChat, .wsInspect, .wsWire, .wsFontManager
window.aetherflowGenome, .aetherflowState
window.DrillDownManager
window.stencilerApp
window.G                    ← une seule lettre
window.resolveSubstyle
window.HOMEOS
window.enterPreviewMode, .exitPreviewMode
window.frdApp
window.renderPreviews
```

Cela défait le système de modules ES et rend le dependency tracking impossible.

### 13. 9 entry points avec `DOMContentLoaded`

Chaque fichier s'auto-exécute au chargement :

1. `js/font_manager.js`
2. `js/stenciler_app.js`
3. `js/genome_engine.js`
4. `js/workspace/ws_main.js`
5. `js/workspace/WsWire.js`
6. `js/bootstrap.js`
7. `js/viewer.js`
8. `js/frd/frd_main.js`
9. `js/sullivan_renderer.js`

Aucune documentation de quelle page charge quels scripts. Risque de double-initialisation.

### 14. Fabric.js CDN chargé mais inutilisé

`stenciler.html` charge :
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
```
Mais `Canvas.feature.js` utilise du SVG natif. Fabric.js est du poids mort (~600 KB gzippé).

### 15. `brainstorm_war_room.js` — fichier vide

0 lignes de code, 228 bytes. Fichier fantôme.

### 16. `static/_archive/server_9998_v2.py` — Python dans static

2 831 lignes, 129 KB de code serveur Python dans le dossier de assets statiques. Ne devrait jamais être servi.

### 17. `templates/zip_dist_kimi_agent_sator_interactif/` — app Vite dumpée

App React/Vite complète (bundle CSS 90 KB, JS 108 lignes, index.html) dumpée dans les templates sans documentation d'intégration.

### 18. `templates/reality_frd_editor_ve_base_frd_editor_v2_base.html` — corruption encoding

Le nom contient `ve` au lieu de `v3` — corruption d'encoding filesystem lors d'un copier.

### 19. Fonctions dupliquées (mêmes noms, fichiers différents)

| Fonction | Fichiers |
|---|---|
| `switchTab(element, tab)` | 3+ |
| `toggleAll(source)` | 2+ |
| `toggleCheckbox(id)` | 2+ |
| `toggleSection(header)` | 2+ |
| `updateValidateButton()` | 2+ |

---

## 🟢 MINIME — Hygiène

| Problème | Count | Exemples |
|---|---|---|
| Commentaires `// BUG`, `// FIXME`, `// HOTFIX` | 13 | `Canvas.feature.js:772`, `Canvas.renderer.js:100` |
| Features désactivées en dur | 2 | `stenciler_v3_main.js:32-33` — TSL Picker + Persistence commentés |
| `insertAdjacentHTML` avec styles inline | 4 | `ws_main.js:128,155,176,178` |
| CDN non pinés | 5 | Tailwind Play, Monaco, Geist, Flowbite, Fabric.js |
| Pas de tests | 0 | Aucun fichier `.test.js` ou `.spec.js` |
| Pas de TypeScript | 0 | 100% JS non typé |
| Pas de linter | 0 | Aucun `.eslintrc`, `.prettierrc` |

---

## ✅ Recommandations prioritaires pour livraison

### P0 — Bloquant (avant toute livraison)

| # | Action | Fichiers | Effort |
|---|---|---|---|
| 1 | **Corriger XSS `outerHTML` postMessage** — valider `e.origin` + sanitization | `workspace/tracker/ws_iframe_core.js:97` | 30 min |
| 2 | **Corriger XSS `onclick` interpolé** — utiliser `addEventListener` au lieu de `onclick=` | `font_manager.js`, `ws_font_manager.js`, `FrdAssets.feature.js`, `sullivan_renderer.js` | 2h |
| 3 | **Supprimer fichiers morts** — 12 HTML racine, `temp_previews/`, `_archive/`, `brainstorm_war_room.js` vide | `static/` | 15 min |
| 4 | **Supprimer blob ad-blocker** de `cadrage_alt.html` | `templates/cadrage_alt.html:296` | 5 min |

### P1 — Important (avant release stable)

| # | Action | Fichiers | Effort |
|---|---|---|---|
| 5 | **Fusionner** `font_manager.js` + `ws_font_manager.js` en module partagé | Les 2 fichiers | 1h |
| 6 | **Fusionner** les 3 CSS v3 en un seul fichier | `stenciler_v3_*.css` | 2h |
| 7 | **Nettoyer** les 196 `console.log` — flag `DEBUG` ou suppression | Tous les JS | 3h |
| 8 | **Créer** `api.config.js` centralisé avec toutes les routes | Nouveau fichier + 15 imports | 2h |
| 9 | **Supprimer** Fabric.js CDN inutilisé | `stenciler.html` | 5 min |
| 10 | **Supprimer** app Vite dumpée | `templates/zip_dist_kimi_*/` | 5 min |

### P2 — Dette technique (prochain sprint)

| # | Action | Effort |
|---|---|---|
| 11 | **Documenter** quelle page charge quels scripts (matrice page→scripts) | 2h |
| 12 | **Ajouter** `.gitignore` pour `temp_previews/`, `__MACOSX/`, `*.generated.*` | 15 min |
| 13 | **Standardiser** les globals `window.*` — préfixe unique par module | 4h |
| 14 | **Dédupliquer** `stenciler_app.js` vs `.generated.js`, `viewer.js` vs `.generated.js` | 3h |
| 15 | **Ajouter** ESLint + Prettier config | 1h |
| 16 | **Évaluer** introduction d'un bundler (Vite recommandé) | 1 jour |

---

## 📋 Matrice page → scripts (reconnaissance)

| Page | Scripts chargés | Entry point |
|---|---|---|
| `landing.html` | `bootstrap.js` | `window.HOMEOS` |
| `intent_viewer.html` | `bootstrap.js` | `window.HOMEOS` |
| `frd_editor.html` | `bootstrap.js`, `frd/*.feature.js` | `window.frdApp` |
| `stenciler.html` | `stenciler_v3_main.js`, Fabric.js (mort) | `window.stencilerApp` |
| `workspace.html` | `workspace/ws_main.js` | `window.wsCanvas`, `window.wsChat`, etc. |
| `brainstorm.html` | `brainstorm_war_room.js` (vide) | — |

> ⚠️ Cette matrice est incomplète — basée sur l'analyse des `<script>` tags trouvés. Une passe manuelle de confirmation est recommandée.
