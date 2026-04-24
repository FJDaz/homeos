# Diag-4 : Parcours Élève — Audit Réalisé

## Onboarding & Login

- **Porte d'entrée** : `student_login.html`.
- **Authentification** : `auth_router.py` crée une session via UUID.
- **Problème de Synchronisation** : L'activation du projet dès le login via `active_project.json` (L651 de `auth_router.py`) peut être écrasée si plusieurs élèves se connectent en même temps ou si un prof manipule le dashboard au même moment.

---

## Workspace & Canvas UI

- **Chargement Différé** : `ws_main.js` utilise un `setTimeout` de 50ms pour initialiser les modules.
- **Bloquage I/O** : `workspace.html` effectue une requête **synchrone** (L51: `xhr.open(..., false)`) pour activer le projet.
  > [!WARNING]
  > Cela peut causer un freeze total du navigateur de l'élève (spinner figé) pendant plusieurs secondes si le serveur SQLite est verrouillé.

---

## Import & Moteur d'Inférence (M151)

L'importation de fichiers (`import_router.py`) est un morceau robuste mais risqué :
1. **Surgical ID Injection** : L'injection systématique d'IDs via BeautifulSoup nettoie le DOM, mais peut ralentir l'import sur des pages massives (> 1Mo).
2. **Inférence Statique** : L'extraction des archetypes et composants (L192-250) est effectuée dans le cycle de requête.
3. **Double Ecriture** : Le système écrit dans `imports/index.json` ET crée un fichier dans `static/templates/`. Si l'un échoue, on a une désynchronisation (import visible mais template 404).

---

## Le "Stitch Loop"

- **Mécanisme** : `WsStitchDrill.js` et `WsStitchSync.js`.
- **Workflow** : L'élève génère un méga-prompt -> l'envoie à Stitch -> Stitch renvoie du code via un webhook ou un poll de dossier.
- **Risque** : `WsStitchSync` fait du polling. Si 30 élèves polluent le backend en même temps avec des requêtes de 1Mo, le serveur Stenciler tombera.

---

## Recommandations V4

1. **[CRITIQUE] Asynchronisme Frontend** : Supprimer l'activation synchrone dans `workspace.html`. Utiliser `fetch` et afficher un spinner de chargement propre.
2. **[IMPORTANT] Task Queue pour l'Import** : Déporter l'inférence (M151) et l'injection d'IDs dans des background tasks (FastAPI `BackgroundTasks`) pour libérer la réponse immédiate.
3. **[IMPORTANT] WebSocket pour le Sync** : Remplacer le polling `WsStitchSync` par des WebSockets ou Server-Sent Events (SSE) pour réduire la charge serveur.
4. **[UX] Persistence Locale** : Utiliser `IndexedDB` côté élève pour mettre en cache les imports déjà chargés et éviter de re-fetcher tout le manifest à chaque refresh.
