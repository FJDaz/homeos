# ROADMAP_ACHIEVED — Archive May 2026

### M424-B — Wire Router + Project Panel : Optimisation & Sécurité
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Re-entry Guard** : Protection contre les exécutions concurrentes.
- **Tri** : Affichage ordonné des écrans lors de l'auto-population.
- **Manifest Row** : Ajout d'une ligne d'accès rapide au manifeste (non-draggable) dans le project panel.

### M424-A — Wire Router : auto-population + nettoyage
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Auto-population** : Détection du canvas vide et injection automatique des écrans du storyboard en grille.
- **Nettoyage UX** : Suppression des alertes bloquantes pour un workflow fluide.

### M424 — Wire Router : point d'entrée intelligent état-projet
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Orchestration** : Router intelligent (`WsWireRouter.js`) guidant l'utilisateur selon l'état du projet (import -> annotation -> wire -> preview).
- **Feedback Visuel** : Voiles de couleur sur les shells du canvas (gris/rouge/orange/vert) indiquant l'état d'avancement du câblage par écran.

### M422 — Export Bundle : app multi-écrans → Netlify Drop ready
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Assemblage** : Route backend générant un fichier HTML unique auto-contenu.
- **Router Embarqué** : Inclusion du mini-router et de la logique GSAP (`manifest.wires`) dans le bundle pour un fonctionnement autonome sans serveur (Netlify-ready).

### M421 — Preview Wired : mini-router multi-écrans dans le workspace
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Mode Interactif** : Création d'un router de preview capable de charger dynamiquement les écrans via `postMessage`.
- **Interceptor** : Injection d'un script capturant `navigateTo()` pour simuler la navigation réelle dans l'overlay.
- **Breadcrumb** : Ajout d'une barre de navigation avec historique (back button).

### M420 — Dockerfile + déploiement minimal
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Création d'un Dockerfile optimisé et d'un `docker-compose.yml` pour un déploiement stable (Koyeb/VPS) avec persistance des volumes SQLite et des uploads.

### M419 — Screen Annotation Mode : SVG overlay N8N-like sur preview + Sullivan guide
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Implémentation du mode annotation permettant de dessiner des liens inter-écrans sur le canvas (N0) et de poser des bulles de commentaire SVG directement sur les écrans (N1) pour guider le câblage.

### M418 — Manifest routing : btn-cadrage avec project_id explicite
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **WsProjectPanel.js** : Le bouton de cadrage passe désormais le `project_id` du projet sélectionné.
- **ManifestBox.js** : Support d'un override de `project_id` pour garantir l'ouverture sur le bon manifeste.

### M417 — Sullivan Core : injecter active_screen_id dans le payload LLM
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Injection de l'ID de l'écran actif du canvas dans les requêtes Sullivan Chat pour permettre au LLM de cibler précisément le contexte d'annotation ou de navigation.

### M416 — Forge : injection UxRun natif dans tout HTML généré
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Injection d'un snippet JavaScript natif dans tout HTML produit par la Forge pour capturer les clics sur les éléments interactifs et les logger via UxRun (`FORGE_CLICK`).

### M415 — Wire : persistance manifest.wires[] + ré-édition
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Persistance** : Sauvegarde des connexions détectées dans `manifest.wires[]`.
- **UI** : Affichage des wires sauvegardés dans l'interface, support de la suppression et de la ré-édition des labels/GSAP.
- **Unification** : Le manifest devient la source unique de vérité pour le câblage.

### M414-A — Wire : Topology Vue + Codestral for Wiring
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Extraction Topology** : Remplacement du HTML brut par une topologie simplifiée (IDs, Classes, Intents) pour réduire le contexte.
- **Routage Codestral** : Intégration de Codestral via `CodestralClient.py` pour une génération de code plus performante.
- **Prompt** : Mise à jour du prompt système pour exploiter la topologie multi-écrans.

### M414 — Wire : payload manifest complet + vision globale multi-écrans
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Enrichissement du payload envoyé à Sullivan pour l'analyse Wire : inclusion du texte du manifeste, du storyboard, du flow et des design tokens pour une vision globale du graphe de navigation.

### M413 — Sullivan : persistance choix illustration cross-écrans & UX Storyboard
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Persistance** : Support de `asset_hash` pour dédupliquer les choix cross-écrans.
- **UX** : Animation de sortie des cartes après validation et ajout de badges visuels (✓ image / code) dans la grille storyboard.

### M412 — Sullivan : renommage global "scènes" → "storyboard" + grille écrans Col 3
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Nomenclature** : Correction globale vers "storyboard" dans l'UI et les messages.
- **UI** : Remplacement de la revue séquentielle par une grille complète d'écrans dans la colonne Output.
- **Lazy Loading** : Chargement asynchrone des visuels d'écrans (PNG/HTML) dans la grille.

### M411 — ME : refonte layout 4 colonnes (textarea / ask / output / TOC)
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Refonte Layout** : Passage à 4 colonnes fixes (Éditeur, Sullivan Ask, Output, Signets).
- **Ancrage** : Sullivan s'aligne dynamiquement sur le curseur (caret) via l'événement `cursor-moved`.
- **Routage** : Redirection des cartes interactives (Summon, Interview) vers la colonne Output dédiée.

### M410 — Sullivan Storyboard : summon contextuel + UI summon card
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Backend** : Enrichissement des scènes avec le `file_path` des images réelles.
- **UI** : Support des PNG importés dans la Summon Card et activation de la navigation vers le canvas via le bouton "ouvrir dans le forgeur".
- **Core** : Injection des `design_tokens` dans le payload LLM pour un contexte de summon plus précis.

### M409 — Architecture : scinder ManifestSullivan.js → Core / Storyboard / UI
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **Découpage Tripartite** : Scission du fichier historique en trois modules : `ManifestSullivanCore.js` (logique/LLM), `ManifestSullivanScenes.js` (storyboard), et `ManifestSullivan.js` (UI/orchestration).
- **Inclusion** : Mise à jour de `workspace.html` pour charger les modules dans l'ordre requis.

### M408 — SULLIVAN HCI INSTRUMENTATION & UX-RUN 🧪
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **OBJECTIF** : Monitoring systématique et diagnostic de friction Sullivan.
- **INSTRUMENTATION** : 
    - `box_open` / `box_close` (Session duration, geometry).
    - `input_send` / `response_received` (Latency, density, scroll state).
    - `caret_sync` (Throttled real-time position).
    - `scroll` (Visibility tracking via IntersectionObserver).

### M407 — Flow Editor : consommation manifest.flow[] par le Wire
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Câblage de la lecture du graphe de navigation `manifest.flow[]` dans le module Wire pour générer des handlers de navigation JS précis basés sur les liens dessinés.

### M406 — Sullivan ME : bouton "charger" — import fichier texte/markdown
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Ajout d'une fonction d'import local de fichiers .txt ou .md pour charger ou remplacer le contenu du manifeste directement dans l'éditeur.

### M405 — Sullivan ME : bouton TDAH — bionic reading du manifeste
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Ajout d'un mode "bionic reading" dans le Manifest Editor pour faciliter la lecture (mise en gras des premières lettres) sans modifier le markdown source.

### M404 — UI : Redirection Routine Cadrage → Manifest Editor
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Fusion fonctionnelle : le bouton "Routine Cadrage" pilote désormais directement le Manifest Editor au lieu d'ouvrir une page externe.

### M403 — FIX : Scroll & Visibilité Project Panel (Overflow)
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Correction des problèmes de scroll dans le project panel pour garantir la visibilité de tous les projets même en cas d'encombrement.

### M402 — UI : Feedback "✓" & "ERR" dans Preview
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Alignement du feedback visuel post-save dans la preview sur celui du canvas avec utilisation des symboles "✓" et "ERR".

### M401 — UI : Alignement bouton SAVE Preview (Vert HoméOS)
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Harmonisation du bouton de sauvegarde dans l'overlay de preview avec le système de design HoméOS (fond vert #8cc63f, texte blanc).

### M394 — Project Panel : drag & drop screen → projet
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Implémentation du déplacement d'écrans entre projets via drag & drop avec confirmation utilisateur et gestion backend sécurisée des fichiers.

### M393 — Sullivan ME : refonte questions manifeste
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Remplacement du prompt dynamique par une grille de questions pré-établies structurées autour de 4 axes DNMADE (archétype, organes, tokens, lisibilité dev) pour un cadrage plus pertinent.

### M392 — Project Panel : ajout d'écrans → enrichissement tokens
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Gestion de l'ajout et de la suppression d'écrans depuis le project panel. L'ajout enrichit les tokens existants et la suppression nettoie les fichiers physiques et l'index.

### M391 — Project Panel : btn "nouveau projet" → drill onboarding
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Câblage du bouton "nouveau projet" pour déclencher le drill onboarding complet, incluant la création de projet et l'extraction automatique des tokens dès l'upload.

### M368-A — AMENDEMENT : ZOOM AU SURVOL DES MINIATURES
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **OBJECTIF** : Faciliter la reconnaissance visuelle sans ouvrir le canvas.
- **DESIGN** : Zoom x2.5 via Tailwind `group-hover/thumb:scale-[2.5]`.
- **Fichiers cibles** : `WsProjectPanel.js`

### M368 — Project panel : thumbnails écrans + canvas PNG visible
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
Affichage des miniatures d'écrans dans le panneau projet et visibilité du canvas PNG pour faciliter la navigation visuelle.

### M367 — Sullivan ME : carte de choix PNG vs code par illustration détectée
**STATUS: ✅ TERMINÉE (2026-05-08) | DATE: 2026-05-08 | ACTOR: GEMINI**
**CR TECHNIQUE** :
- **UI** : Ajout d'une section unifiée "🖼️ illustrations détectées" dans le Manifest Editor.
- **Libellés** : Harmonisation des boutons en `garder en image` / `convertir en code`.
- **Persistance** : Les choix sont stockés dans `manifest.json` (`validated_choice`) et injectés en texte dans la section `### Arbitrage Sullivan (M393)`.
- **Forge Logic** : Modification de `routes.py` pour filtrer les spécimens PNG. Si l'arbitrage est `vector`, le LLM reçoit une instruction impérative de générer du code SVG/CSS à la place de la balise `<img>`.
- **Validation** : Cycle complet (Détection → Arbitrage → Forge) fonctionnel.

### SEC-1 — Git history purge : supprimer ENV_KEYS_CHECK.md de tous les commits
**STATUS: ✅ TERMINÉE (2026-05-05) | DATE: 2026-05-05 | ACTOR: FJD**

**CR** : 
- Purge effectuée manuellement par FJD pour supprimer les fichiers contenant des clés API en clair de l'historique Git.
- Sécurité restaurée.

---

### M393 — Sullivan : mémorisation des choix d'assets entre forges
**STATUS: ✅ TERMINÉE (2026-05-05) | DATE: 2026-05-05 | ACTOR: GEMINI**

**CR** :
- Implémentation de la persistance des choix (png/vector) dans `manifest.json`.
- Ajout de l'endpoint `/api/sullivan/persist-asset-choice`.
- Filtrage des assets déjà validés dans la critique Sullivan.
- **Bonus** : Archivage des choix à la fin du manifeste sous `### Arbitrage Sullivan (M393)` pour éviter la confusion visuelle.

---

### M392 — Sécurité BYOK : chiffrement Fernet des clés API en DB
**STATUS: ✅ TERMINÉE (2026-05-05) | DATE: 2026-05-05 | ACTOR: GEMINI**

**CR** :
- Module `core/key_crypto.py` créé avec Fernet (encrypt/decrypt, fallback gracieux).
- `auth_router.py`, `key_resolver.py` et `stitch_router.py` patchés (encrypt write, decrypt read).
- Script de migration `scripts/migrate_encrypt_user_keys.py` livré (idempotent).
- Migration exécutée : 6 clés BYOK chiffrées en DB (3 users × gemini/groq/deepseek/openai).
- `FERNET_KEY` ajoutée dans `.env` (non commitée).

---

### M391 — Forge granularité : prompt exhaustivité + data-atomic-organ systématique
**STATUS: ✅ TERMINÉE (2026-05-05) | DATE: 2026-05-05 | ACTOR: GEMINI**

**CR** :
- Injection de règles critiques dans `svg_to_tailwind.py`.
- Injection de `data-atomic-organ` obligatoire sur chaque div interactif.
- Normalisation post-forge via BeautifulSoup pour garantir l'exhaustivité des grilles.

---

### M390 — Save N1 : bouton sauvegarder en aperçu → écrase template complet
**STATUS: ✅ TERMINÉE (2026-05-04) | DATE: 2026-05-04 | ACTOR: GEMINI**

**CR** :
- Implémentation du bouton `sauvegarder` dans la barre d'outils N1 (Aperçu).
- Création de l'endpoint `/api/workspace/save-full` dans `workspace_router.py`.
- Logiciel JS dans `WsPreview.js` : capture de `documentElement.outerHTML` et envoi au serveur.
- Répercussion N0 : rafraîchissement automatique de l'iframe source sur le canvas après sauvegarde.
- Validation : Les modifications Monaco appliquées en N1 sont désormais persistées par écrasement complet.

---

### M389 — Graft : sélecteur structurel stable au lieu de data-af-id
**STATUS: ✅ TERMINÉE (2026-05-04) | DATE: 2026-05-04 | ACTOR: GEMINI**

**CR** :
- Abandon du sélecteur `data-af-id` pour les opérations de graft.
- Implémentation d'un sélecteur structurel stable basé sur `nth-of-type` dans `ws_iframe_core.js`.
- Validation : `monaco:apply` génère maintenant des signaux `graft:success`.

---

### M388 — UX Monaco : Logiciel "Apply" (Preview) vs "Save" (Persist) + Fix Suppression
**STATUS: ✅ TERMINÉE (2026-05-04) | DATE: 2026-05-04 | ACTOR: GEMINI**

**CR** :
- Fusion de l'Apply (DOM) et du Save (Disque) dans un seul bouton `appliquer`.
- Instrumentation UxRun systématique pour tracker les succès/échecs de graft.
- Fix Delete : Les éléments vides sont maintenant supprimés du DOM.

---

### M385 — UX Sullivan : Regroupement sémantique assets (Figuratif vs Abstrait)
**STATUS: ✅ TERMINÉE (2026-04-30) | DATE: 2026-04-30 | ACTOR: GEMINI**

**CR** : 
- Implémentation du tri par `figuration_score` dans `sullivan_router.py`.
- Refonte de la fonction `renderCritique` dans `ManifestSullivan.js`.

---

### M387 — Monaco graft : résolution ?name= → apply fonctionnel sur forge
**STATUS: ✅ TERMINÉE (2026-04-30) | DATE: 2026-04-30 | ACTOR: GEMINI**

**CR** :
- Correction de la logique de résolution du nom de fichier dans `WsInspect.js`.
- Ajout du support pour le paramètre `?name=`.

---

### M386 — Forge : injection specimens manifest → HTML généré
**STATUS: ✅ TERMINÉE (2026-04-30) | DATE: 2026-04-30 | ACTOR: GEMINI**

**CR** :
- Injection des spécimens réels dans le pipeline Vision-to-Code (`routes.py`).
- Correction de l'extraction dans `design_token_extractor.py`.

---

### T44 — Architecture Mémoire & Traces (M380-M384)
**STATUS: ✅ ACHEVÉ (2026-04-30) | DATE: 2026-04-30 | ACTOR: GEMINI**

**CR** :
- Création de la structure `TRACES/`.
- Post-mortems T001 et T002 rédigés.
- Archivage UX automatisé.
- Constitution mise à jour.
### M399 — Sullivan UxRun : instrumentation complète frontend + backend
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**

**CR TECHNIQUE :**
Instrumentation de bout en bout pour le diagnostic laser.
- **Backend** : Wrapper global `_ux_log` dans `sullivan_router.py`. Logs : `chat_sent`, `chat_ok`, `chat_error`, `critique_launched`, `storyboard_bootstrap_started`.
- **Frontend** : Tracker `_sullivanLog` dans `ManifestSullivan.js`. Instrumentation des callbacks UI et retours API.

---

### M398 — Sullivan Scène Summon + Hot-Swap assets (HCI primitif)
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**

**CR TECHNIQUE :**
- **Screen Summon** : Sullivan peut maintenant "invoquer" une scène du storyboard via un tool-call. Affichage d'une carte visuelle avec aperçu iframe du template généré.
- **Hot-Swap Assets** : Commande Sullivan pour basculer un asset entre PNG et Vecteur. Mise à jour immédiate du manifest et feedback visuel.

---

### M397 — Sullivan HCI Audit : Instrumentation Metrics
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**

**CR TECHNIQUE :**
- Ajout de `answer_len` pour calcul de densité.
- Logging des frictions : `critique_reloaded`, `panel_dragged`.
- Signal `manual_edit_after_sullivan` (Indirect Apply).

---

### M395 — Sullivan : Bootstrap Scènes manifest (LLM → storyboard[])
**STATUS: ✅ TERMINÉE (2026-05-05) | DATE: 2026-05-05 | ACTOR: GEMINI**

**CR TECHNIQUE :**
- Intégration de la structure `scenes` (précédemment storyboard) dans le manifest de Sullivan.
- Le LLM peut désormais proposer un découpage en scènes (scènes annotées) avec IDs et rôles structurels.

---

### M394 — Sullivan : Reset asset-choice backend (plomberie pour M398)
**STATUS: ✅ TERMINÉE (2026-05-05) | DATE: 2026-05-05 | ACTOR: GEMINI**

**CR TECHNIQUE :**
- Endpoint `/api/sullivan/reset-asset-choice` pour nettoyer les arbitrages passés.

---

### BKG-5 — Sullivan `image_trigger` : instrumentation UxRun
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**

**CR TECHNIQUE :**
- Résolu par l'instrumentation directe dans `ManifestSullivan.js`. Chaque déclenchement d'analyse est logué via le système UxRun global.

---

### M377 — `project_id` dans UxRun
**STATUS: ✅ TERMINÉE (2026-05-07) | DATE: 2026-05-07 | ACTOR: GEMINI**

**CR TECHNIQUE :**
- Instrumentation via `UxRunHooks.js` assurant que chaque log envoyé au serveur contient le `project_id` actif, permettant le filtrage par session.

---

### HOTFIX — Wire Router : alert legacy + filtre imports + storyboard réancré
**STATUS: ✅ TERMINÉE (2026-05-09) | DATE: 2026-05-09 | ACTOR: CLAUDE CODE DIRECT**

**Contexte :** Session de debugging live sur le projet élève Lilou Serre (dnamde3-serre-lilou). Gemini avait échoué à corriger les 4 bugs M424-B (D&D cassé à chaque tentative). Claude a opéré en CODE DIRECT — exception bloquant prod élève.

**3 fixes appliqués :**

**1. Alert "Sélectionnez un screen sur le canvas d'abord." (WsChat.js + WsChatMain.js)**
- Cause : bloc Mission 147 (`currentMode === 'wire'`) dans WsChat.js et WsChatMain.js — code mort depuis M424 (Wire Router), mais encore actif et déclenché avant le router.
- Fix : suppression du bloc, remplacement par un commentaire indiquant que le mode wire est géré par WsWireRouter.
- Fichiers : `static/js/workspace/WsChat.js`, `static/js/workspace/chat/WsChatMain.js`

**2. Filtre imports visuels (WsWireRouter.js + WsProjectPanel.js)**
- Cause : `manifest_kimi.md` stocké dans index.json avec `type: "html"` (default backend) → apparaissait dans le panel ET était candidat à l'import canvas.
- Fix : filtre par extension de fichier (`['html','htm','png','jpg','jpeg','gif','svg','webp']`) dans `_populateCanvasFromStoryboard()` et dans `WsProjectPanel.fetchProjectScreens()` (avant mise en cache).
- Fichiers : `WsWireRouter.js`, `WsProjectPanel.js`

**3. Bug architectural storyboard (WsWireRouter.js)**
- Cause : `_populateCanvasFromStoryboard()` itérait sur `manifest.storyboard[]` (2 items abstraits générés par Sullivan depuis le texte) au lieu des imports réels (5 PNG). Résultat : 2 shells au lieu de 5 sur le canvas, IDs abstraits (`screen-1`, `screen-2`) incohérents avec les vrais import IDs → `_applyShellOverlays` ne trouvait aucun shell.
- Fix : la fonction itère désormais directement sur `imports[]` (triés par nom). Chaque shell reçoit `data-screen-id = import.id`. Après population, `PUT /api/projects/{pid}/manifest` recale `manifest.storyboard[]` avec les vrais IDs d'import — storyboard ancré sur la réalité, pas sur la fiction LLM.
- Fichier : `WsWireRouter.js` (`_populateCanvasFromStoryboard`)
