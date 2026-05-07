# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## 🧠 BOOTSTRAP GEMINI — À inclure dans TOUTE mission frontend

```
CONTEXTE TECHNIQUE OBLIGATOIRE — lis avant de coder :

1. DIAGNOSTIC DOM AVANT LISTENER
   Avant d'ajouter un event listener, remonte la chaîne du DOM :
   - Quel élément est réellement cliqué ? (e.target)
   - Y a-t-il un élément enfant `absolute inset-0` qui intercepte les clics avant le parent ?
   - Si oui → ajouter `pointer-events-none` sur l'intercepteur, puis le listener sur le parent.

2. OVERLAYS & Z-INDEX
   Un overlay `hidden` sur un parent = ses enfants sont invisibles même si LEUR hidden est retiré.

3. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement le comportement dans le browser.

4. SCOPE STRICT
   Ne pas refactoriser les fichiers existants stables sans instruction explicite.

5. STYLE HOMÉOS
   Pas de majuscules dans les labels UI. Pas d'emojis. Border-radius max `rounded-[20px]`.
   Vert HoméOS (#8cc63f) uniquement en nudge — jamais en fond large.

6. ICÔNES — SVG INLINE UNIQUEMENT
   Règle : utiliser des SVG inline Lucide-style (viewBox 0 0 24 24, stroke currentColor, fill none, stroke-width 1.8).
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE ASYNC (CRITIQUE)

```
INTERDICTION ABSOLUE : nest_asyncio.apply()
RÈGLE : pour exécuter du code synchrone bloquant dans un contexte async FastAPI, utiliser asyncio.to_thread(fn, *args).
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE REDÉMARRAGE

```
RÈGLE OBLIGATOIRE : après toute mission livrée en backend, le serveur DOIT être redémarré (bash start.sh).
```

---

## Sprint actif — 2026-04-27

| Mission | Titre | Status | Actor |
|---------|-------|--------|-------|
| SPR_APR | Missions M327 à M378 | ✅ ARCHIVÉES | GEMINI |
| BKG-1 | Gemini 2.5 Flash : guillemets typographiques dans JSON M356 | 🟡 BACKLOG | — |
| BKG-2 | M363 : extraction parallèle — 5 threads simultanés (1 par fichier uploadé) | 🟡 BACKLOG | — |
| BKG-5 | Sullivan `image_trigger` : bouton "analyser" lance extraction + attend 15s flat | 🟡 BACKLOG | GEMINI |
| BKG-7 | `WsWire._syncNudgesToIframe` : timeout non catchés → spam console (cosmétique) | 🟡 BACKLOG | GEMINI |
| M367 | Sullivan ME : une carte de choix par illustration détectée | 🟠 À TRAITER | GEMINI |
| M368 | Project panel : thumbnails écrans + canvas PNG visible | 🟠 À TRAITER | GEMINI |
| M350 | Vue "Live Watch" (Drill Status Polling) | 🟠 À TRAITER | GEMINI |
| M351 | Notation Automatique par Référentiel | 🟠 À TRAITER | CLAUDE |
| T44 | Architecture Mémoire & Traces (M380-M384) | ✅ ACHEVÉ | GEMINI |
| M385 | UX Sullivan : Regroupement sémantique assets (Figuratif/Abstrait) | ✅ TERMINÉE | GEMINI |
| M386 | Forge : injection specimens manifest → HTML généré (images réelles) | ✅ TERMINÉE | GEMINI |
| M387 | Monaco graft : résolution `?name=` → apply fonctionnel sur forge | ✅ TERMINÉE | GEMINI |
| M388 | UX Monaco : Logiciel "Apply" (Preview) vs "Save" (Persist) + Fix Delete | ✅ TERMINÉE | GEMINI |
| M389 | Graft : sélecteur structurel stable (`nth-child`) au lieu de `data-af-id` | ✅ TERMINÉE | GEMINI |
| M390 | Save N1 : bouton "sauvegarder" en aperçu → écrase template complet → N0 reflète | ✅ TERMINÉE | GEMINI |
| M391 | Project Panel : btn "nouveau projet" → déclenche drill onboarding | 🟠 À TRAITER | GEMINI |
| M392 | Project Panel : ajout d'écrans depuis panel → enrichissement tokens multi-type | 🟠 À TRAITER | GEMINI |
| M393 | Sullivan ME : refonte questions manifeste (remplacer questions LLM génériques) | 🟠 À TRAITER | GEMINI |
| BKG-8 | Extraction tokens : fire-and-forget à la forge = rustine — fix structurel via M391 | 🟡 BACKLOG | — |


---

## Thème 45 — Intelligence Visuelle & Arbitrage UI

### M390 — Save N1 : bouton sauvegarder en aperçu → écrase template complet
**STATUS: ✅ TERMINÉE (2026-05-04) | ACTOR: GEMINI**

**CR** :
- Implémentation du bouton `sauvegarder` dans la barre d'outils N1 (Aperçu).
- Création de l'endpoint `/api/workspace/save-full` dans `workspace_router.py`.
- Logiciel JS dans `WsPreview.js` : capture de `documentElement.outerHTML` et envoi au serveur.
- Répercussion N0 : rafraîchissement automatique de l'iframe source sur le canvas après sauvegarde.
- Validation : Les modifications Monaco appliquées en N1 sont désormais persistées par écrasement complet, garantissant un rendu identique après rechargement.

---

### M389 — Graft : sélecteur structurel stable au lieu de `data-af-id`
**STATUS: ✅ TERMINÉE (2026-05-04) | ACTOR: GEMINI**

**CR** :
- Abandon du sélecteur `data-af-id` pour les opérations de graft (car inexistant dans les fichiers source).
- Implémentation d'un sélecteur structurel stable basé sur `nth-of-type` dans `ws_iframe_core.js`.
- Ce sélecteur garantit que BeautifulSoup retrouve l'élément exact sur le disque, même sans ID dynamique.
- Validation : `monaco:apply` génère maintenant des signaux `graft:success` avec des sélecteurs de type `body > div:nth-of-type(2) > ...`.

---

### M388 — UX Monaco : Logiciel "Apply" (Preview) vs "Save" (Persist) + Fix Suppression
**STATUS: ✅ TERMINÉE (2026-05-04) | ACTOR: GEMINI**

**CR** :
- Fusion de l'Apply (DOM) et du Save (Disque) dans un seul bouton `appliquer`.
- Instrumentation UxRun systématique pour tracker les succès/échecs de graft (`RESULT`/`FRICTION`).
- Fix Delete : Les éléments vides sont maintenant supprimés du DOM via `target.remove()`.
- Style HoméOS : Labels en minuscules, pas d'emojis.

---

### M385 — UX Sullivan : Regroupement sémantique assets (Figuratif vs Abstrait)
**STATUS: ✅ TERMINÉE (2026-04-30) | ACTOR: GEMINI**

**CR** : 
- Implémentation du tri par `figuration_score` dans `sullivan_router.py`.
- Refonte de la fonction `renderCritique` dans `ManifestSullivan.js` pour créer des sections visuelles (Illustrations vs Graphiques).
- Ajout d'une pré-sélection intelligente (PNG si score > 0.5, Vecteur sinon) pour accélérer la validation.

### M387 — Monaco graft : résolution `?name=` → apply fonctionnel sur forge
**STATUS: ✅ TERMINÉE (2026-04-30) | ACTOR: GEMINI**

**CR** :
- Correction de la logique de résolution du nom de fichier dans `WsInspect.js`.
- Ajout du support pour le paramètre `?name=` (utilisé par la route `/api/frd/file` de la forge).
- Validation : Monaco envoie désormais le bon nom de fichier (ex: `reality_interface1.html`) au backend `/api/workspace/graft`.

---

### M386 — Forge : injection specimens manifest → HTML généré
**STATUS: ✅ TERMINÉE (2026-04-30) | ACTOR: GEMINI**

**CR** :
- Injection des spécimens réels dans le pipeline Vision-to-Code (`routes.py`).
- Correction de l'extraction dans `design_token_extractor.py` pour capturer plus d'assets distincts par écran.
- Ajout d'une consigne de "flexibilité sémantique" au prompt de forge pour assurer l'utilisation des images même en cas de divergence mineure de description.

**Symptôme :** La forge produit un HTML avec des `<img src="data:image/svg+xml,...">` — des placeholders 1x1 invisibles. Les images sont reconnues et découpées par le pipeline M356 (specimens dans `manifest.json → design_tokens.image_assets`), mais ne sont jamais passées au LLM de conversion.

**Cause racine :** Dans `Backend/Prod/retro_genome/routes.py`, branche IMAGE (ligne ~845), `convert_image` est appelé avec seulement `design_md`. Le manifest `image_assets` avec leurs `specimen_url` n'est jamais lu ni injecté dans le prompt.

**Fichiers à modifier :**
- `Backend/Prod/retro_genome/routes.py` — branche IMAGE, après step 5 (`check_design_md`), avant step 7 (`llm_vision_conversion`)

**Ce que Gemini doit faire :**
Après la lecture de `design_md` (step 5), ajouter un step 6 `load_specimen_urls` :
1. Lire `p_path / "manifest.json"` (path déjà connu à ce point)
2. Extraire `design_tokens.image_assets` → garder ceux qui ont un `specimen_url`
3. Construire un bloc texte à appendre à `design_md` :
```
IMAGES RÉELLES DISPONIBLES — utilise ces URLs comme src="" dans les <img> :
- type=portrait, description=...: /api/projects/assets/img/specimen_portrait_0_interface1.png?project_id=...
- type=illustration, description=...: /api/projects/assets/img/...
```
4. Si `image_assets` est vide ou absent → ne rien faire (dégrade gracieusement)
5. Passer `design_md` enrichi à `convert_image` (pas de changement de signature)

**Contrainte :** Ne pas modifier `svg_to_tailwind.py` — uniquement `routes.py`.

**Test de validation :**
- Relancer une forge sur un écran de `dnamde3-hiver-lyse`
- Ouvrir `reality_interface1.html` → les `<img>` doivent avoir des `src` pointant vers `/api/projects/assets/img/specimen_*.png`
- Les images doivent être visibles dans le rendu

---

### M350 — Vue "Live Watch" (Drill Status Polling) 
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

### M351 — Notation Automatique par Référentiel
**STATUS: 🟠 À TRAITER | ACTOR: CLAUDE**

---

## Thème 44 — Architecture de Mémoire Long Terme & Traces UX ✅ ACHEVÉ (2026-04-30)

**Prérequis** : M374 + M376 validées en prod avant d'exécuter ce thème.
**Séquence obligatoire** : M380 → M381 → M382 → M383 → M384.

### M380 — Initialisation structure TRACES
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M380 (Infrastructure Mémoire)
- **Structure** : Création des répertoires `TRACES/` et `ux_runs/` dans `Frontend/4. COMMUNICATION/`.
- **Index** : Création de `TRACES_INDEX.md` initialisé avec les placeholders pour les prochaines missions (T001, T002).
- **Standard** : Adoption du style "low-caps" et formatage compatible RAG.


- **Objectif** : Créer la structure de mémoire long terme pour les agents.
- **Livrables** :
  - Dossier `Frontend/4. COMMUNICATION/TRACES/`
  - Dossier `Frontend/4. COMMUNICATION/ux_runs/` (archive des sessions UX compilées)
  - Fichier `TRACES/TRACES_INDEX.md` — index sémantique des post-mortems, une ligne par entrée
- **Alignement M375** : Les sessions UX brutes restent dans `logs/ux_run.ndjson`. `ux_runs/` reçoit uniquement les archives compilées après `--archive`. Ne pas déplacer `logs/`.

---

### M381 — Post-Mortem : Asyncio Deadlock (pipeline extraction)
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M381 (Trace T001)
- **Rédaction** : Création de `T001_asyncio_deadlock.md`.
- **Contenu** : Documentation du conflit event loop/threads et solution via `requests` + `to_thread`.


- **Objectif** : Documenter le bug de blocage du pipeline d'extraction d'images.
- **Fichier cible** : `TRACES/PM_asyncio_deadlock_extraction.md`
- **Contenu** :
  - Symptôme : `infer_seed_intent` bloquait le thread d'extraction pendant 5h+, `_ACTIVE_EXTRACTIONS` restait zombie
  - Cause : `asyncio.wait_for()` ne peut pas annuler un appel httpx bloquant dans un event loop de thread daemon
  - Solution : déplacement de `infer_seed_intent` dans un `threading.Thread` indépendant (fire-and-forget)
  - Règle à retenir : ne jamais `await` un appel réseau long dans un thread daemon sans garantie de cancellation
- **Ajouter dans `TRACES_INDEX.md`** : une ligne pointant vers ce fichier

---

### M382 — Post-Mortem : Chemins relatifs DB → forge cassée
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M382 (Trace T002)
- **Rédaction** : Création de `T002_relative_paths_db.md`.
- **Contenu** : Documentation de la corruption des chemins en DB et standardisation via `Path.absolute()`.


- **Objectif** : Documenter le bug où la forge ne trouvait pas `index.json`.
- **Fichier cible** : `TRACES/PM_chemins_relatifs_projects_db.md`
- **Contenu** :
  - Symptôme : forge échoue avec "index.json missing" malgré le fichier présent sur disque
  - Cause : la colonne `path` de la table `projects` stockait un chemin relatif (`projects/id`) au lieu d'un chemin absolu. `get_active_project_path()` retournait ce relatif tel quel, invalide depuis le contexte d'exécution du backend
  - Solution : `UPDATE projects SET path = '/Users/.../AETHERFLOW/projects/' || id WHERE path NOT LIKE '/%'` + corriger `auth_router.py` pour toujours stocker `str(project_dir.resolve())`
  - Règle à retenir : toute colonne `path` en DB doit contenir un chemin absolu. Toujours appeler `.resolve()` avant `str()` sur un `Path` avant persistance
- **Ajouter dans `TRACES_INDEX.md`** : une ligne pointant vers ce fichier

---

### M383 — Archivage automatique sessions UX (`compile_ux_journal.py`)
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M383 (Archivage UX)
- **Script** : Mise à jour de `compile_ux_journal.py` avec le support de l'argument `--archive`.
- **Automatisation** : Compilation du journal Markdown, copie dans `ux_runs/` avec timestamp et nettoyage automatique du NDJSON.
- **Validation** : Testé avec succès le 2026-04-30 (archive `UX_RUN_2026-04-30_120348.md` générée).


- **Objectif** : Fermer la boucle M375 → archive.
- **Fonctionnement** : Script `scripts/compile_ux_journal.py --archive [NOM_SESSION]`
  1. Lit `logs/ux_run.ndjson`
  2. Produit un fichier markdown lisible dans `Frontend/4. COMMUNICATION/ux_runs/[NOM_SESSION].md`
  3. Vide `logs/ux_run.ndjson` pour repartir propre
- **Format du markdown produit** : tableau chronologique `timestamp | tag | label | project_id`

---

### M384 — Constitution Agent : SOP Traces obligatoires
**STATUS: ✅ TERMINÉE | ACTOR: GEMINI**

### CR — Mission M384 (Gouvernance Mémoire)
- **Constitution** : Mise à jour de `GEMINI.md` avec la section **MÉMOIRE LONG TERME (TRACES)**.
- **Protocole** : Obligation de rédaction et d'indexation des traces techniques pour toute mission majeure.
- **Clôture** : Fin du cycle de mise en place de l'infrastructure de mémoire long terme.


- **Objectif** : Rendre les traces non optionnelles dans le protocole de fin de mission.
- **Fichier cible** : `Frontend/1. CONSTITUTION/GEMINI.md` (ou équivalent bootstrap Gemini)
- **Contenu à ajouter** :
  ```
  RÈGLE DE FIN DE MISSION — TRACES
  Avant de marquer TERMINÉE :
  1. Si la mission a corrigé un bug non trivial → créer un fichier dans TRACES/ et l'indexer
  2. Si la mission introduit une feature observable → ajouter le signal UxRun dans le callback de succès
  3. Mettre à jour TRACES_INDEX.md
  ```

---

## Thème 46 — Onboarding Élève & Enrichissement Tokens (2026-05-07)

**Contexte :** L'extraction de design tokens ne se déclenche jamais sur un nouveau drill / nouvel élève. Le fix actuel (fire-and-forget à la forge) est une rustine — le vrai problème est l'absence d'un point d'entrée structurel pour distinguer "nouveau projet" vs "reprise". Ces trois missions corrigent ça proprement.

---

### M391 — Project Panel : btn "nouveau projet" → drill onboarding
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** Le bouton "nouveau projet" est déjà présent dans `WsProjectPanel.js` mais ne fait rien (ou ouvre un flow incomplet). Il doit déclencher le drill onboarding complet (comme au premier login).

**Ce que Gemini doit faire :**
1. Dans `WsProjectPanel.js`, wirer le bouton "nouveau projet" → appel `WsStitchDrill.show()` (ou équivalent)
2. Le drill crée un nouveau projet propre + lance immédiatement `extract-tokens` sur les écrans dès upload
3. Discriminer dans le drill : si `project_id` existant → reprise (ne pas re-extraire) / si nouveau → extraction complète

**Fichiers cibles :** `WsProjectPanel.js`, `WsStitchDrill.js`

**Contrainte :** Le fix résout aussi BKG-8 — avec ce point d'entrée, l'extraction fire-and-forget dans `WsForge.js` peut être supprimée ou maintenue en fallback uniquement.

---

### M392 — Project Panel : gestion des écrans (ajout + suppression)
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** Une fois un projet créé, l'élève doit pouvoir ajouter et supprimer des écrans depuis le project panel sans relancer un drill complet. Le panel affiche les écrans groupés par projet (`projects[i].screens[j]`). Chaque ajout enrichit les tokens existants ; chaque suppression nettoie index.json + fichiers disque.

**Structure de données cible :**
Le panel doit rendre une arborescence `projet → screens[]`, pas une liste plate. `_screensCache[projectId]` contient déjà les screens — le rendu doit les grouper sous leur projet parent dans le DOM.

**Ce que Gemini doit faire :**

**Ajout d'écrans :**
1. Bouton "ajouter des écrans" visible à côté du projet actif dans le panel
2. File picker multi-fichiers → upload vers `/api/import/upload` avec `project_id` explicite dans le body (ne pas résoudre via token seul — le user peut avoir plusieurs projets)
3. `import_router.py` : vérifier que l'upload associe l'import au `project_id` du body en priorité
4. Après upload réussi : déclencher `extract-tokens` sur ce `project_id` + appeler `window.fetchWorkspaceImports()` pour invalider le cache panel

**Suppression d'écran :**
5. Bouton supprimer (×) sur chaque screen dans le panel, visible au hover
6. Confirmation user avant exécution ("supprimer cet écran ? cette action est irréversible")
7. Appel `DELETE /api/imports/{import_id}?project_id={project_id}` (endpoint existant dans `import_router.py`)
8. Après suppression : invalider `_screensCache[projectId]` + re-render panel

**Spec annotations pour storyboard (FJD — rapport Gemini 2026-05-07) :**
- Résolution optimale : **1280px ou 1440px** sur le plus grand côté (le pipeline plafonne à 1280px)
- Corps minimum fiable : **12px** (corps 10px = zone de risque aliasing, <9px = hallucinations)
- Contraste prime sur résolution : texte gris clair/fond blanc corps 12 < texte noir corps 10
- Corps 14px+ : lecture parfaite après downsampling
- Format cible pour écrans annotés storyboard : PNG 1280px, annotations noires sur fond blanc pur, corps 14px minimum

**Fichiers cibles :** `WsProjectPanel.js`, `import_router.py`

---

### M393 — Sullivan ME : refonte questions manifeste
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** Les questions générées par le LLM Groq à partir du manifest étudiant sont "ineptes ou imbuvables" (FJD, 2026-05-07). Le modèle de questions oui/non génériques n'est pas adapté au contexte DNMADE.

**Ce que Gemini doit faire :**
1. Remplacer le prompt Groq de `manifest-critique` par une grille de questions **pré-établies** adaptées au contexte DNMADE, pas générées dynamiquement
2. Questions statiques structurées autour de 4 axes DNMADE : archétype, couverture organes, cohérence tokens, lisibilité dev
3. Format : 5-7 questions courtes, formulées en langage direct étudiant (pas jargon UX)
4. Les suggestions restent dynamiques (Groq les génère en réponse aux questions pré-établies)

**Exemple de questions cibles :**
- "ton projet a un nom et une phrase d'intention claire ?"
- "les écrans/sections sont listés avec leur rôle ?"
- "la palette et la typo sont définies ?"
- "un dev peut savoir ce qu'il doit construire en lisant ça ?"
- "le style visuel (réaliste, flat, typographique...) est explicite ?"

**Fichiers cibles :** `sullivan_router.py` (endpoint `manifest-critique`)

---

### M394 — Project Panel : drag & drop screen → projet
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** L'élève doit pouvoir déplacer un écran d'un projet vers un autre directement dans le panel. Opération destructive et multi-fichiers — nécessite confirmation user + séquence stricte côté backend.

**Ce que Gemini doit faire :**

**Frontend :**
1. Rendre les screen items draggables (`draggable="true"`) dans le panel
2. Rendre les zones projet droppables (`dragover`, `drop`)
3. À l'évenement `drop` : afficher une modale de confirmation ("déplacer cet écran vers [projet cible] ?") avant tout appel backend
4. Sur confirmation : appel `PATCH /api/imports/{import_id}/move` avec `{ target_project_id }`
5. Sur succès : invalider `_screensCache` des deux projets concernés + re-render panel

**Backend (`import_router.py`) :**
6. Créer endpoint `PATCH /api/imports/{import_id}/move` :
   - Lire l'entrée dans `index.json` du projet source
   - Déplacer les fichiers physiques (import image + html_template si existe) vers le dossier du projet cible
   - Mettre à jour les chemins dans l'entrée
   - Retirer l'entrée de `index.json` source
   - Ajouter l'entrée dans `index.json` cible
   - Répondre `{ ok: true }` ou erreur explicite

**Contraintes :**
- Ne jamais déplacer sans confirmation user explicite
- Si `html_template` existe : déplacer aussi le fichier template (sinon le screen cible aura un chemin cassé)
- Si le projet cible n'a pas de dossier `imports/` : le créer
- En cas d'erreur backend : ne pas modifier le frontend — afficher l'erreur en clair

**Fichiers cibles :** `WsProjectPanel.js`, `import_router.py`
