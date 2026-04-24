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
   - Tester avec : `element.addEventListener('click', e => console.log(e.target))` avant tout patch.

2. OVERLAYS & Z-INDEX
   Un overlay `hidden` sur un parent = ses enfants sont invisibles même si LEUR hidden est retiré.
   Toujours vérifier : `getComputedStyle(el).display` et `el.offsetHeight` avant de déboguer le JS.

3. RÈGLE DE LIVRAISON
   Ne pas marquer TERMINÉ avant d'avoir testé manuellement le comportement dans le browser.

4. SCOPE STRICT
   Ne pas refactoriser les fichiers existants stables sans instruction explicite.

5. STYLE HOMÉOS
   Pas de majuscules dans les labels UI. Pas d'emojis. Border-radius max `rounded-[20px]`.
   Vert HoméOS (#8cc63f) uniquement en nudge — jamais en fond large.

6. ICÔNES — SVG INLINE UNIQUEMENT
   Interdiction absolue : emojis dans les boutons ou actions UI (👁 ✏️ 🗑 etc.).
   Règle : utiliser des SVG inline Lucide-style (viewBox 0 0 24 24, stroke currentColor, fill none, stroke-width 1.8).
   Les SVG doivent hériter de `color` via `stroke="currentColor"` pour rester compatibles avec les tokens HoméOS.
   Taille par défaut : 14×14 ou 16×16 selon le contexte (jamais en rem, toujours en px).
   Pas de CDN icon font, pas de base64, pas de sprite externe.
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE ASYNC (CRITIQUE — Python 3.14 + uvicorn)

```
INTERDICTION ABSOLUE : nest_asyncio.apply() en global dans server_v3.py ou tout fichier importé au démarrage.
RAISON : nest_asyncio patche asyncio.run() d'une façon incompatible avec uvicorn (loop_factory, Python 3.14+).
SYMPTÔME : serveur démarre, accepte les connexions TCP, mais ne répond jamais → page blanche sans erreur console.

RÈGLE : pour exécuter du code synchrone bloquant dans un contexte async FastAPI, utiliser UNIQUEMENT :
  - asyncio.to_thread(fn, *args)          ← préféré pour les fonctions pures
  - loop.run_in_executor(None, fn, *args) ← si accès au loop nécessaire

Jamais : asyncio.run() imbriqué, nest_asyncio, event loop manuel dans une coroutine.
```

---

## 🧠 BOOTSTRAP BACKEND — RÈGLE REDÉMARRAGE (CRITIQUE — livraison back)

```
RÈGLE OBLIGATOIRE : après toute mission livrée en backend (router, route, modèle Pydantic, middleware…),
le serveur DOIT être redémarré avant tout test.

RAISON : uvicorn charge les modules Python au démarrage. Une nouvelle route ajoutée dans un router
ne sera jamais exposée si le serveur n'est pas relancé — elle retournera 404 même si le code est correct.

PROCÉDURE :
  1. Vérifier la livraison dans le fichier .py concerné (grep de la nouvelle route/fonction)
  2. Redémarrer : cd /AETHERFLOW && bash start.sh
  3. Confirmer via curl ou /openapi.json que la route est bien enregistrée
  4. Seulement ensuite tester depuis le navigateur (hard refresh Cmd+Shift+R)

S'applique à : auth_router.py, class_router.py, subject_router.py, bkd_router.py, et tout fichier dans routers/.
```

---

## 🧠 BOOTSTRAP QWEN — RÈGLES DE PERFORMANCE UI (Mission Performance)

```
RÈGLES D'ANIMATION LOW-CPU :
- Utiliser transform/opacity uniquement (pas de width/height/top/left animés).
- will-change: transform sur les éléments animés.
- requestAnimationFrame pour les boucles JS, jamais setInterval pour du visuel.
- Pas de box-shadow animé (recalcul layout).
```

---

## Sprint actif — 2026-04-24

| Mission | Titre | Status | Actor |
|---------|-------|--------|-------|
| M330 | Nettoyage structure ROADMAP.md | 🟢 TERMINÉE | GEMINI |
| M331 | Fix onboarding student — session + drill | 🟢 TERMINÉE | GEMINI |
| M332 | Handoff dev senior — chapitre ROADMAP | 🟢 TERMINÉE | CLAUDE |
| M333 | UX drill : nouveau projet + sortie croix | 🟢 TERMINÉE | GEMINI |
| M334 | Fix impersonation : WsStitchDrill lit sessionStorage | 🟢 TERMINÉE | GEMINI |
| M335 | UX : bouton nouveau projet + header panel | 🟢 TERMINÉE | GEMINI |
| M336 | Fix critique : impersonation localStorage bridge + 401 guard | 🟢 TERMINÉE | CLAUDE |
| M337 | Fix manifest impersonation — JWT decode dans get_active_project_id | 🔴 BLOQUANT | CLAUDE |
| M338 | Tab Dashboard en mode impersonation | 🟡 QUICK-WIN | CLAUDE |

---

### M336 — Fix critique : impersonation localStorage + séparation login/session
**STATUS: 🔴 BLOQUANT | DATE: 2026-04-24 | ACTOR: GEMINI**

> BOOTSTRAP OBLIGATOIRE

**Contexte :** Deux bugs bloquants introduits par les missions précédentes.

**Fichiers :** `teacher_dashboard.html`, `bootstrap.js`, `login.html`, `page_router.py`

---

**Bug 1 — Impersonation : sessionStorage non partagé entre onglets**

`window.open(..., '_blank')` crée un contexte de navigation indépendant. Le `sessionStorage` du dashboard n'est PAS copié dans le nouvel onglet. Résultat : le workspace ouvre avec `?impersonate=1`, bootstrap.js lit un sessionStorage vide, tombe sur le token du prof dans localStorage, envoie ce token aux routes student → 401 → redirect `/login`.

**Fix A — `teacher_dashboard.html` : passer par localStorage temporaire**

Dans la fonction `impersonate()`, remplacer le `sessionStorage.setItem` par un `localStorage.setItem` avec une clé temporaire :

```js
// AVANT
sessionStorage.setItem('homeos_impersonation', JSON.stringify({...}));
window.open('/workspace?impersonate=1', '_blank');

// APRÈS
localStorage.setItem('homeos_impersonation_pending', JSON.stringify({
    token: data.token,
    user_id: data.user_id,
    student_id: studentId,
    class_id: classId,
    active_project_id: data.project_id,  // ← clé correcte attendue par WsStitchDrill
    project_id: data.project_id,
    role: 'student',
    name: data.name
}));
window.open('/workspace?impersonate=1', '_blank');
```

**Fix B — `bootstrap.js` : lire `localStorage.homeos_impersonation_pending` au boot**

Dans le bloc impersonation de bootstrap.js, remplacer la lecture sessionStorage par :

```js
if (isImpersonate) {
    // Lire depuis localStorage (seul moyen de passer data à un _blank tab)
    const pending = JSON.parse(localStorage.getItem('homeos_impersonation_pending') || '{}');
    if (pending.token) {
        session = pending;
        // Déplacer en sessionStorage pour cette session d'onglet
        sessionStorage.setItem('homeos_impersonation', JSON.stringify(pending));
        // Supprimer la clé temporaire pour éviter que d'autres onglets la lisent
        localStorage.removeItem('homeos_impersonation_pending');
    }
}
```

---

**Bug 2 — `/login` : deux formulaires cohabitent (impossible)**

La page `/login` affiche actuellement deux onglets : "Session Code" (CPF) et "Formateur" (email+password). Ces deux flux ne peuvent pas cohabiter sur la même page — UX cassée, confusion prof/apprenant, redirection impersonation vers le mauvais onglet.

**Fix C — `login.html` : une seule forme, prof uniquement**

La page `/login` doit afficher uniquement le formulaire email+password (onglet "Formateur"). Supprimer entièrement le formulaire "Session Code" et la logique `selectContext()`.

Le formulaire CPF session code sera traité dans une mission dédiée sur une URL séparée (ex: `/classroom`). Ne pas l'implémenter ici — le supprimer et laisser la place propre.

**Fix D — `page_router.py` : vérifier que la route `/login` sert bien `login.html`**

Aucun changement attendu — juste vérifier que la route est intacte après modification de login.html.

---

**output attendu :**
- Clic "voir en tant que" → workspace s'ouvre dans un nouvel onglet → drill s'affiche avec la session de l'élève → plus de redirect vers login
- `/login` → formulaire email+password uniquement, pas de session code
- Session de l'onglet impersonation isolée (sessionStorage) → fermeture onglet = session détruite
- Session prof dans l'onglet dashboard intacte (localStorage)

---

### M338 — Tab Dashboard en mode impersonation
**STATUS: 🟡 QUICK-WIN | DATE: 2026-04-24 | ACTOR: CLAUDE — CODE DIRECT**

**Contexte :** En mode `?impersonate=1`, `session` dans bootstrap.js est la session élève (role: 'student'). Le tab Dashboard n'est jamais affiché car le check `session.role === 'prof'` échoue. Le prof perd son accès au Dashboard dans l'onglet workspace impersonation.

**Fix (3 lignes — `bootstrap.js`) :**

```js
// AVANT
if (session.role === 'prof' || session.role === 'admin') {
    if (!isImpersonate) {
        TABS.unshift({ id: 'dashboard', ... });
    }
}

// APRÈS — lire la session prof depuis localStorage (toujours présente)
const profSession = isImpersonate
    ? JSON.parse(localStorage.getItem('homeos_session') || '{}')
    : session;
if (profSession.role === 'prof' || profSession.role === 'admin') {
    TABS.unshift({ id: 'dashboard', ... });
}
```

**Bannière impersonation :** Supprimer le bouton "stop impersonation" cassé. Garder une bannière épurée texte seul ("vue en tant que : X — fermer l'onglet pour revenir au dashboard"). Les vraies restrictions role student sont implémentées en amont (login, AuthMiddleware, drill) — confiance dans les mécanismes existants.

**output attendu :** Tab Dashboard visible en mode impersonation. Clic → retour au dashboard prof. Fermeture onglet = fin de session impersonation.

---

### M337 — Fix manifest impersonation — JWT decode dans get_active_project_id
**STATUS: 🔴 BLOQUANT | DATE: 2026-04-24 | ACTOR: CLAUDE — CODE DIRECT**

**Diagnostic :**

`get_active_project_id(token)` dans `bkd_service.py` résout le projet actif via `WHERE u.token = ?`. Les tokens UUID legacy sont stockés en DB — ça marche. Le token d'impersonation est un **JWT généré à la volée** (`create_access_token({"user_id": s_user_id, "role": "student"})`) — il n'est **pas** en DB. Résultat : lookup retourne None → fallback `homéos-default` → `manifest.json` introuvable → ManifestBox ne s'ouvre pas.

**Périmètre exact :** uniquement en mode impersonation (JWT token). Les tokens UUID legacy (profs, vrais élèves) ne sont pas affectés.

**Fix (`bkd_service.py`, fonction `get_active_project_id`) :**

Après l'échec du lookup legacy, tenter un decode JWT :

```python
def get_active_project_id(token: str = None):
    if token:
        try:
            with bkd_db() as con:
                row = con.execute(
                    "SELECT s.project_id, u.role, u.active_project_id FROM users u "
                    "LEFT JOIN students s ON s.display = u.name "
                    "WHERE u.token = ?", (token,)
                ).fetchone()
                if row:
                    stud_pid, role, user_pid = row
                    if role == 'student' and stud_pid:
                        return stud_pid
                    if role in ('teacher', 'admin', 'prof') and user_pid:
                        return user_pid
        except Exception as e:
            logger.error(f"get_active_project_id: DB error: {e}")

        # Fallback JWT — token non stocké en DB (impersonation)
        if token.startswith('eyJ'):
            try:
                from core.auth_utils import decode_access_token
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get('user_id', '')
                    role = payload.get('role', '')
                    with bkd_db() as con:
                        if role == 'student':
                            # user_id peut être "student_<slug>" ou un vrai UUID FK
                            row = con.execute(
                                "SELECT project_id FROM students WHERE user_id = ?",
                                (user_id,)
                            ).fetchone()
                            if row and row[0]:
                                return row[0]
                        # Si prof JWT (rare) — chercher active_project_id
                        row = con.execute(
                            "SELECT active_project_id FROM users WHERE id = ?",
                            (user_id,)
                        ).fetchone()
                        if row and row[0]:
                            return row[0]
            except Exception as e:
                logger.error(f"get_active_project_id: JWT decode error: {e}")

    return "homéos-default"
```

**Redémarrage serveur obligatoire après livraison.**

**output attendu :** ManifestBox se charge en mode impersonation. Le manifest de l'élève (et non `homéos-default`) est retourné par `/api/manifest/get`.

---

### M335 — Restauration WsStitchDrill.js + Alignement UX Projet
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR Ultra-Précis (Gemini) :**

1. **Nettoyage WsStitchDrill.js** :
   - **Suppression du bouton flottant** : La fonction `createSmallButton()` (bouton "+ Nouveau projet" en bas à droite) a été intégralement supprimée du code.
   - **Simplification de `show()`** : Désormais la fonction appelle directement `createOverlay()` au lieu de vérifier l'état du canvas. Elle s'autolimite au rôle `student` et s'exécute au boot si `active_project_id` est absent.
   - **Fix Session** : Validation de la lecture prioritaire du `sessionStorage` pour l'impersonation.

2. **Refonte WsProjectPanel.js** :
   - **Header Redesign** : Dans `_renderSectionHeader()`, le bouton `+` est maintenant un cercle vert (`#8cc63f`) de 24x24px, avec un plus blanc (SVG) et un effet de scale au survol.
   - **Câblage Drill** : Le `onclick` du bouton `+` dans le panneau latéral appelle désormais `window.WsStitchDrill.show()`. Cela replace le Drill (overlay central + gros bouton rond) au cœur de l'expérience de création.
   - **Visibilité** : Suppression des blocages d'affichage pour les élèves ayant un seul sujet. La section "Projets Personnels" est désormais une ancre permanente dans la sidebar.

3. **Intégration** :
   - Le flux est maintenant : **Panel Project (+) → Drill Overlay (Centre) → Création Projet**.

---



### M334 — Fix impersonation globale : WsStitchDrill + WsProjectPanel
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR (Gemini) :**
- **Impersonation-Awareness** : Les fichiers `WsStitchDrill.js` et `WsProjectPanel.js` lisent désormais la session élève dans le `sessionStorage` (`homeos_impersonation`) quand le paramètre `?impersonate=1` est présent.
- **Project Panel Fix** : Le panneau des projets n'est plus "invisible" en mode impersonation ; il reflète bien le contexte élève.
- **Drill Lifecycle** : Le drill se lance désormais systématiquement en mode "voir en tant que" si l'élève n'a pas de projet actif.
- **Restart Serveur** : Redémarrage effectué pour valider la prise en compte des routes et correctifs.

---


## Thème 37 — Handoff Dev Senior & NLP/HCI

### M330 — Nettoyage structure ROADMAP.md
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR (Gemini) :**
- Suppression des séparateurs `---` redondants.
- Suppression de la version spécification de M328 (doublon).
- Réorganisation chronologique des CRs (M327 → M328 → M329).
- Validation du tableau "Sprint actif" en tête de document.

---

### M333 — UX drill : bouton "nouveau projet" + croix de sortie
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR (Gemini) :**
- **Bouton Centre (Restore)** : Restauration du **gros bouton rond pulsant** d'origine (dégradé HoméOS) au centre du drill. Il est désormais fonctionnel et crée le projet personnel via `/api/projects/create` (autonomie totale).
- **Project Panel Button +** : Ajout d'un bouton `+` vert permanent dans le header de section "Projets Personnels". La section est désormais visible en permanence, même si l'élève n'a qu'un seul sujet (suppression de la règle de masquage "vue directe").
- **Overlay Exit** : Ajout d'une croix de fermeture `×` (SVG Lucide) en haut à droite de l'overlay drill pour permettre de quitter le flux sans effet de bord.

---

### M331 — Fix onboarding student : session + drill flow
**STATUS: 🟢 TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR (Gemini) :**
- `student_login.html` : injection de `session.name` pour le header.
- `WsStitchDrill.js` : bouton "Commencer" ajouté à l'étape des clés API.
- `WsStitchDrill.js` : retry défensif sur l'ouverture de `ManifestBox`.
- `WsStitchDrill.js` : redirection vers Step 0 si `projectId` absent (meilleur UX).

**Fichiers :**
- `Frontend/3. STENCILER/static/templates/student_login.html`
- `Frontend/3. STENCILER/static/js/workspace/WsStitchDrill.js`

**Fix 1 — `student_login.html` : champ `name` manquant dans la session**

Le stockage localStorage de la session ne contient pas de champ `name`, alors que `bootstrap.js` attend `session.name` pour afficher le nom de l'élève dans le header. Ajouter `name` en plus de `display` :

```js
// AVANT (L230 environ)
localStorage.setItem('homeos_session', JSON.stringify({
    token: data.token,
    user_id: data.user_id,
    student_id: data.student_id,
    class_id: data.class_id,
    active_project_id: data.project_id,
    project_id: data.project_id,
    display: data.name,
    role: 'student'
}));

// APRÈS
localStorage.setItem('homeos_session', JSON.stringify({
    token: data.token,
    user_id: data.user_id,
    student_id: data.student_id,
    class_id: data.class_id,
    active_project_id: data.project_id,
    project_id: data.project_id,
    name: data.name,      // ← ajout : bootstrap.js attend session.name
    display: data.name,   // ← conservé : WsStitchDrill lit session.display
    role: 'student'
}));
```

**Fix 2 — `WsStitchDrill.js` : bouton "Commencer à travailler" accessible dès Step 2**

Le bouton `_finishButton()` n'apparaît qu'à Step 3 (manifest) et Step 4. Un élève qui a déjà un manifest assigné par le prof est bloqué à Step 2 (clés API) avec seulement un bouton "Continuer →". Ajouter le bouton "Commencer à travailler" également à Step 2, juste après le bouton `drill-continue-keys` :

```js
// Ajouter après la ligne :
document.getElementById('drill-continue-keys').onclick = () => { currentStep = 3; renderStep(); };

// Ajouter :
const keysSection = document.getElementById('drill-keys-section') || document.querySelector('[data-step="2"]');
if (keysSection) _finishButton(keysSection);
```

**Fix 3 — `WsStitchDrill.js` : ManifestBox defensive retry**

La ligne `btn.onclick = () => { hide(); if (window.ManifestBox) window.ManifestBox.show(); };` dans `_finishButton()` est silencieuse si ManifestBox n'est pas encore chargé. Remplacer par un retry :

```js
// AVANT (dans _finishButton, L511 environ)
btn.onclick = () => { hide(); if (window.ManifestBox) window.ManifestBox.show(); };

// APRÈS
btn.onclick = () => {
    hide();
    const _tryOpen = () => window.ManifestBox ? window.ManifestBox.show() : setTimeout(_tryOpen, 200);
    _tryOpen();
};
```

**Fix 4 — `WsStitchDrill.js` : project_id null → Step 0 au lieu d'erreur**

Dans `loadManifestStep()`, si `projectId` est null, le code affiche "projet non trouvé — contacte ton professeur". Ce message est trompeur : un nouvel élève n'a pas encore de projet, c'est normal. Remplacer le message par un retour à Step 0 ("Créer un projet") :

```js
// AVANT (L347-349)
if (!projectId) {
    showManifestUpload(section, 'projet non trouvé — contacte ton professeur');
    return;
}

// APRÈS
if (!projectId) {
    currentStep = 0;
    renderStep();
    return;
}
```

**input_files :** `student_login.html`, `WsStitchDrill.js`

**output attendu :**
- Login student → `session.name` présent → nom visible dans le header
- Drill : si pas de projet → Step 0 s'affiche (pas d'erreur)
- Clés renseignées à Step 2 → bouton "Commencer à travailler" visible
- Clic "Commencer" → ManifestBox s'ouvre même si chargement lent

---

## Thème 37 — NLP / HCI (Réservé FJD)

> **Ces travaux sont exclusivement menés par FJD. Ne pas déléguer.**

### Vision architecture BERT + Bayesian + MinB/MaxB

FJD se concentre sur l'expérimentation d'une architecture d'inférence locale chip, dont l'objectif est de réduire drastiquement le coût et l'empreinte environnementale de l'inférence LLM, en faisant peser le maximum de décision sur un modèle léger local.

**Pipeline cible :**
```
Contexte large (RAG passages) + message user (500 tokens)
  → BERT all-MiniLM-L6-v2 (cosine sim → intent vector 384d)
  → Bayesian update : prior = sliding window 3 derniers intents
                      evidence = scores RAG + BERT
                      → posterior confidence ∈ [0,1]
  → Routing MinB / MaxB :
      confidence < 0.65 → LLM "clarification" (Min Budget)
      confidence > 0.80 → handler déterministe (Max Budget)
      sinon              → template LLM standard
  → Mistral 7B LoRA (Spinoza) / ou autre LLM cible
```

**État actuel dans `maiathon/Spinoza_Secours_HF/Backend/app_runpod.py` :**
- ✅ BERT `all-MiniLM-L6-v2` chargé
- ✅ 4 intent anchors (accord / confusion / resistance / neutre)
- ✅ Cosine similarity → intent label
- ❌ Score de confiance non retourné
- ❌ Aucun routing MinB/MaxB
- ❌ Aucun prior bayésien (chaque message traité isolément)

**Expérience MVP (15-20 lignes, fichier unique) :**
1. Modifier `detecter_contexte()` pour retourner aussi le score de confiance
2. Implémenter le routing 3-way dans `spinoza_repond()`
3. Tester sur 5 inputs benchmark : `"oui"` / `"non c'est faux"` / `"hmmm"` / message mixte / bruit
4. Mesure : le routing change-t-il le comportement de Mistral de manière pédagogiquement pertinente ?

**Point de décision :** si ça marche → Bayesian prior (sliding window conv). Si ça ne marche pas → réviser les anchors ou la granularité des intents.

---

### Axe 2 — NLP Middleware : outil de veille API

Vision : un outil autonome qui surveille les breaking changes des pipelines LLM (DeepSeek, Qwen, Gemini, Groq, MIMO…) et produit un refactor systématique à chaque changement de shape ou de comportement.

Composants à concevoir (roadmap dédiée à rédiger quand BERT MVP validé) :
- **Watcher** : polling changelogs officiels + sampling régulier des API responses
- **Diff detector** : compare shapes avant/après, détecte les dérives de comportement
- **Refactor suggester** : prompt → patch automatique du code appelant

---

### Axe 3 — Sullivan RL

Point de décision conditionnel au résultat du chip tool BERT+Bayesian.

- Si le chip tool est validé → Sullivan devient le sujet d'expérimentation RL : reward signal pédagogique, RLHF local, évaluation de la pertinence des réponses.
- Si le chip tool échoue → trouver un remplacement (distillation, fine-tune direct Mistral, RAG enrichi), avant de revenir à Sullivan.

*Pas d'action avant validation BERT MVP.*

---

## Handoff Dev Senior

> Document complet : [docs/04_HomeOS/Handoff/DEV_ONBOARDING.md](../../docs/04_HomeOS/Handoff/DEV_ONBOARDING.md)

---

### M327 — Impersonation (Showroom Prof)
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR (Gemini) :**
- Route `/api/auth/impersonate` fonctionnelle (auth_router.py).
- Bouton "Voir en tant que" (icône œil Lucide) sur le dashboard.
- Mode impersonation actif via `sessionStorage` for l'isolation des onglets.
- Bandeau d'alerte rouge injecté dans le workspace avec bouton "Stop".
- Bouton "Dashboard" masqué programmatiquement durant l'impersonation.
- Redirection automatique vers /teacher lors de l'arrêt de l'impersonation, avec conservation de la classe active (`class_id`).

---

### M328 — Panel Admin : gestion des users
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR (Gemini) :**
- Nouvel onglet "Utilisateurs" visible uniquement par les admins.
- CRUD complet des utilisateurs (Rôles, Reset MDP, Suppression).
- Intégration dans `teacher_dashboard.html` avec design HoméOS (760px).
- Routes backend sécurisées dans `admin_router.py`.

---

### M329 — Finalisation UI & HoméOS Compliance
**STATUS: ✅ TERMINÉE | DATE: 2026-04-24 | ACTOR: GEMINI**

**CR (Gemini) :**
- Largeur `.main` fixée à 760px dans le dashboard prof pour la cohérence.
- Suppression radicale de TOUS les emojis restants (📄, 📁, 🎓, 🎨, 👁, ↑, ✓).
- Remplacement systématique par des SVGs inline (Lucide-style).
- Nettoyage des libellés (Passage de "Voir en tant que" en attribut `alt`).

---

## Thème 35 — Dashboard Prof : Suivi & Analytics

> Ce thème concerne la visibilité en temps réel de l'avancement des étudiants et la gestion granulaire des sujets.

### M350 — Vue "Live Watch" (Drill Status Polling) 
**STATUS: 🟠 À TRAITER | ACTOR: GEMINI**

### M351 — Notation Automatique par Référentiel
**STATUS: 🟠 À TRAITER | ACTOR: CLAUDE**
