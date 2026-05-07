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

## Sprint actif — 2026-05-07

| Mission | Titre | Status | Actor |
|---------|-------|--------|-------|
| SPR_MAY | Missions M380 à M400 | ✅ ARCHIVÉES | GEMINI |
| BKG-1 | Gemini 2.5 Flash : guillemets typographiques dans JSON M356 | 🟡 BACKLOG | — |
| BKG-2 | M363 : extraction parallèle — 5 threads simultanés | 🟡 BACKLOG | — |
| BKG-7 | `WsWire._syncNudgesToIframe` : timeout non catchés → spam console | 🟡 BACKLOG | GEMINI |
| M350 | Vue "Live Watch" (Drill Status Polling) | 🟠 À TRAITER | GEMINI |
| M351 | Notation Automatique par Référentiel | 🟠 À TRAITER | CLAUDE |
| M367 | Sullivan ME : une carte de choix par illustration détectée | 🟠 À TRAITER | GEMINI |
| M368 | Project panel : thumbnails écrans + canvas PNG visible | 🟠 À TRAITER | GEMINI |
| M391 | Project Panel : btn "nouveau projet" → drill onboarding | 🟢 TERMINÉE | GEMINI |
| M392 | Project Panel : ajout d'écrans → enrichissement tokens | 🟢 TERMINÉE | GEMINI |
| M393 | Sullivan ME : refonte questions manifeste | 🟢 TERMINÉE | GEMINI |
| M394 | Project Panel : drag & drop screen → projet | 🟢 TERMINÉE | GEMINI |
| M401 | UI : Alignement bouton SAVE Preview (Vert HoméOS) | 🟢 TERMINÉE | GEMINI |
| M402 | UI : Feedback "✓" & "ERR" dans Preview | 🟢 TERMINÉE | GEMINI |
| M403 | FIX : Scroll & Visibilité Project Panel (Overflow) | 🟠 À TRAITER | GEMINI |
| M404 | UI : Redirection Routine Cadrage → Manifest Editor | 🟠 À TRAITER | GEMINI |

---

## Thème 46 — Onboarding Élève & Enrichissement Tokens (2026-05-07)

**Contexte :** L'extraction de design tokens ne se déclenche jamais sur un nouveau drill / nouvel élève. Le fix actuel (fire-and-forget à la forge) est une rustine — le vrai problème est l'absence d'un point d'entrée structurel pour distinguer "nouveau projet" vs "reprise". Ces trois missions corrigent ça proprement.

---

### M391 — Project Panel : btn "nouveau projet" → drill onboarding
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Le bouton "nouveau projet" est déjà présent dans `WsProjectPanel.js` mais ne fait rien (ou ouvre un flow incomplet). Il doit déclencher le drill onboarding complet (comme au premier login).

**Ce que Gemini doit faire :**
1. Dans `WsProjectPanel.js`, wirer le bouton "nouveau projet" → appel `WsStitchDrill.show()` (ou équivalent)
2. Le drill crée un nouveau projet propre + lance immédiatement `extract-tokens` sur les écrans dès upload
3. Discriminer dans le drill : si `project_id` existant → reprise (ne pas re-extraire) / si nouveau → extraction complète

**Fichiers cibles :** `WsProjectPanel.js`, `WsStitchDrill.js`

**Contrainte :** Le fix résout aussi BKG-8 — avec ce point d'entrée, l'extraction fire-and-forget dans `WsForge.js` peut être supprimée ou maintenue en fallback uniquement.

---

### M392 — Project Panel : gestion des écrans (ajout + suppression)
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

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
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

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
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

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
