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
| M403 | FIX : Scroll & Visibilité Project Panel (Overflow) | 🟢 TERMINÉE | GEMINI |
| M404 | UI : Redirection Routine Cadrage → Manifest Editor | 🟢 TERMINÉE | GEMINI |
| M405 | Sullivan ME : bouton TDAH — bionic reading du manifeste | 🟢 TERMINÉE | GEMINI |
| M406 | Sullivan ME : bouton "charger" — import fichier texte/markdown | 🟢 TERMINÉE | GEMINI |

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

---

### M401 — UI : Alignement bouton SAVE Preview (Vert HoméOS)
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Harmonisation du bouton de sauvegarde dans l'overlay de preview avec le système de design HoméOS (Haut de casse, fond vert #8cc63f, texte blanc).

### M402 — UI : Feedback "✓" & "ERR" dans Preview
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Alignement du feedback visuel post-save dans la preview sur celui du canvas (utilisation du checkmark et de "ERR").

### M403 — FIX : Scroll & Visibilité Project Panel (Overflow)
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Correction du bug empêchant de voir/scroller les projets du bas lorsque le panel est encombré. Nécessite une approche CSS plus sûre pour ne pas casser la logique de collapse.

### M404 — UI : Redirection Routine Cadrage → Manifest Editor
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**
Fusion fonctionnelle : le bouton "Routine Cadrage" doit désormais piloter directement le Manifest Editor au lieu d'ouvrir une page externe.

---

### M405 — Sullivan ME : bouton TDAH — bionic reading du manifeste
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

**Contexte :** Le bionic reading est une technique de lecture facilitée par le design typographique. Les premières lettres de chaque mot sont mises en gras (points de fixation), guidant le regard et accélérant la saccade oculaire. Bénéfice spécifique pour les profils TDAH : réduction du bruit visuel, économie cognitive, maintien du focus sur le chemin visuel.

**Ce que Gemini doit faire :**

1. Ajouter un bouton toggle "tdah" dans la barre d'outils du Manifest Editor (Sullivan ME), à droite des boutons existants
2. Au clic : transformer le texte du manifeste affiché en bionic reading — **purement côté client, sans modifier le contenu stocké**
3. Au reclic : revenir au texte normal

**Algorithme bionic (JS pur, sans lib externe) :**
```js
function bionicWord(word) {
    if (word.length <= 1) return `<b>${word}</b>`;
    const fixLen = Math.ceil(word.length / 2);
    return `<b>${word.slice(0, fixLen)}</b>${word.slice(fixLen)}`;
}
function bionicText(text) {
    return text.replace(/\b(\w+)\b/g, (_, w) => bionicWord(w));
}
```

**Périmètre :**
- S'applique uniquement au rendu affiché dans le Manifest Editor (zone de texte ou cards Sullivan)
- Ne touche pas au markdown stocké en base — uniquement le DOM affiché
- Le toggle doit persister pendant la session (pas de reset au rechargement des cards)

**Style du bouton :**
- Label : `tdah` (minuscules, style HoméOS)
- Inactif : border gris clair, texte slate
- Actif : border vert HoméOS (`#8cc63f`), texte vert — même pattern que les autres toggles du ME

**Fichier cible :** `ManifestSullivan.js` (barre d'outils du ME, fonction de rendu des cards)

---

### M406 — Sullivan ME : bouton "charger" — import fichier texte/markdown
**STATUS: 🟢 TERMINÉE | ACTOR: GEMINI**

**Contexte :** Le manifeste peut être corrompu (mauvais projet_id lors d'une sauvegarde) ou absent. L'élève doit pouvoir charger un fichier texte ou markdown depuis son poste pour remplacer le contenu de l'éditeur.

**Ce que Gemini doit faire :**

1. Ajouter un bouton "charger" dans la barre d'outils du ME, à côté des boutons existants
2. Au clic : ouvrir un `<input type="file" accept=".txt,.md">` (invisible, déclenché par JS)
3. Lire le fichier via `FileReader.readAsText()` → injecter le contenu dans `els.editor.value`
4. Déclencher `onTextChange()` pour mettre à jour les signets et la sauvegarde différée
5. Relancer `window.ManifestSullivan.launchCritique()` automatiquement après injection
6. Afficher un feedback discret ("manifeste chargé ✓") pendant 2s dans la barre d'outils

**Contraintes :**
- Pas de call backend pour le chargement — lecture 100% locale via FileReader
- La sauvegarde vers le backend se fait via le mécanisme `saveManifestDeferred()` existant (déjà déclenché par `onTextChange`)
- Accepter `.txt` et `.md` uniquement — ignorer silencieusement les autres formats
- Style du bouton : `charger` (minuscules, style HoméOS), même gabarit que les autres boutons de la barre

**Fichier cible :** `ManifestBox.js` (barre d'outils, à côté du bouton reload existant)
