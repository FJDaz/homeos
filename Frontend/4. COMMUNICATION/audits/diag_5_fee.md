# Diag-5 : FEE (Front End Engineer) — Audit Réalisé

## Architecture du Studio

- **Composant** : `WsFEEStudio.js` (Labo Photo "Camera Raw").
- **Technologie** : Orchestration GSAP côté client, génération de code via Sullivan FEE (LLM) côté backend.
- **Référentiel d'Effets** : `fee_presets.json` contient 18 "recettes" d'animation servant de base à l'IA.

---

## Flux d'Animation & Hot-Reload

1. **Maillage** : Sullivan FEE identifie les organes via `data-af-id` (injectés à l'import, voir Diag-4).
2. **Hot-Reload** : Injection dynamique dans l'iframe via `postMessage` (`FEE_INJECT_GSAP`). Cela fonctionne sans recharger la page, offrant une boucle de feedback immédiate.
3. **Application (Graft)** : Sauvegarde dans `logic.js` du projet.

---

## Goulots d'Étranglement & Freezes

> [!WARNING]
> **SYNCHRONICITÉ BACKEND**
> Les calls `/api/bkd/fee/chat` et `/api/bkd/fee/apply` sont les points de friction majeurs.

- **Défaut** : Le backend attend que le LLM génère le code ET que le disque soit écrit avant de répondre. Si le LLM met 5s, le worker FastAPI est bloqué, et si SQLite est sollicité par un autre client (Teacher Dashboard), c'est le **Lockout permanent**.
- **Coverage Scanning** : `scanTriggers` scanne tout le fichier `logic.js` à chaque ouverture du studio. Sur un projet mature avec 500 lignes de JS, le coût CPU côté frontend devient non-négligeable.

---

## État de la Dette (GSAP Studio)

- **Isolation** : Le studio est asynchrone par rapport au Canvas principal, ce qui est une bonne chose.
- **Droit à l'erreur** : Actuellement, pas de "Undo" efficace si un Graft corrompt `logic.js`. On écrase le fichier ou on ajoute à la fin (append).
- **Z-Index Warfare** : Le studio utilise un z-index massif (9000). Il peut masquer des modales critiques ou des alertes système.

---

## Recommandations V4

1. **[CRITIQUE] Threading & Streams** : Migrer `/api/bkd/fee/chat` pour utiliser des **Streaming Responses**. Voir Sullivan générer le code caractère par caractère évite le timeout et réduit la sensation de freeze.
2. **[IMPORTANT] Gestionnaire de Version `logic.js`** : Ne plus faire de "Graft" destructif. Implémenter un système de rollback ou de couches d'animations (layers).
3. **[IMPORTANT] Optimisation du Scan** : Stocker l'inventaire des animations dans le `manifest.json` plutôt que de parser `logic.js` via Regex au runtime.
4. **[UX] Timeline Visualizer** : Ajouter une barre de temps (SeekBar) réelle dans le studio pour inspecter les animations `scroll-trigger` sans avoir à scroller l'iframe manuellement.
