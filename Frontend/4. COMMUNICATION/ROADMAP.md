# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Mission 35 — Retro-Genome Reality View Engine (Multi-pass)

**STATUS: ✅ LIVRÉ**
**ACTOR: ANTIGRAVITY**
**DATE: 2026-03-11**

### Objectif
Générer un rendu HTML/CSS ultra-fidèle (Reality View) via une architecture de génération en 3 passes pour compenser les approximations des LLMs Vision.

### Réalisations
- [x] **Génération Multi-pass** : Pipeline Structure (HTML) → Styling (CSS Pro) → Review (DA Visual Check).
- [x] **Exigence Design** : Intégration des règles Flexbox/Grid/Gap/Clamp dictées par FJD.
- [x] **Monitoring Sullivan** : Feedback temps réel de la progression des passes dans l'UI.
- [x] **Routage Dual-Viewer** : Bascule automatique Blueprint (KIMI) vs Reality (Gemini) selon l'état de validation.

---

## Mission 34C — Workflow Validation : Intent → Reality

**STATUS: ✅ LIVRÉ**
**ACTOR: GEMINI (Frontend + Backend)**
**DATE: 2026-03-11**

### Réalisations
- [x] **`intent_viewer.html`** : Bouton de validation finalisé avec chaînage API.
- [x] **`server_9998_v2.py`** : Persistance via `validated_analysis.json`.
- [x] **Indicateur de statut** : Polling du backend vers le loader frontend.

---

## Mission 36 — Sullivan Cockpit : Conversational Refinement (Chat)

**STATUS: 🔴 EN COURS (PLANNING)**
**ACTOR: ANTIGRAVITY**
**DATE: 2026-03-11**

### Objectif
Activer le chatbot Sullivan pour permettre à l'utilisateur d'amender "en direct" les propositions graphiques de la Reality View via un dialogue naturel soutenu par la vision Gemini.

### Tâches
- [ ] **API Endpoint** : Créer `/api/retro-genome/chat` acceptant le feedback + HTML actuel.
- [ ] **Sullivan Refine** : Étendre le `HtmlGenerator` pour gérer les "Updates" chirurgicales (Prompt Refactoring).
- [ ] **UI Sync** : Connecter le bouton "Envoyer" et rafraîchir l'Iframe au retour du code.
- [ ] **System Prompt Sullivan** : Injecter les règles d'exigence AetherFlow dans le flux conversationnel.

---

## Mission 33 — BERT Semantic Intent Router (Spinoza Backend)

**STATUS: 🔴 À FAIRE**
**DATE: 2026-03-10**
**ACTOR: CLAUDE**
**MODE: aetherflow -q**
**SCOPE: `/Users/francois-jeandazin/Antigravity/maiathon/Spinoza_Secours_HF/Backend/`**

### Problème
`detecter_contexte()` dans `app_runpod.py` (L162) est du **keyword matching naïf** (regex/`in` sur liste de mots).
BERT (`all-MiniLM-L6-v2`) n'est ni importé ni chargé dans ce Backend.
`sentence-transformers` est absent de `requirements.runpod.txt`.
Résultat : la détection d'intent est fragile et littérale — insensible au sens réel du message.

### Objectif
Remplacer `detecter_contexte()` par un **router sémantique BERT** :
- Charger `all-MiniLM-L6-v2` via `SentenceTransformer` au démarrage (après `load_model()`)
- Encoder le message utilisateur → vecteur 384d
- Cosine similarity contre des **ancres d'intent** pré-encodées
- Retourner l'intent dominant : `accord` / `confusion` / `resistance` / `neutre`

### Tâches

#### `requirements.runpod.txt`
- [ ] Ajouter `sentence-transformers>=2.7.0`

#### `app_runpod.py` — Initialisation
- [ ] Importer `SentenceTransformer`, `util` depuis `sentence_transformers`
- [ ] Définir `INTENT_ANCHORS` (dict de phrases de référence par classe) :
  - `accord` → ["oui", "je suis d'accord", "exactement", "tout à fait", "voilà"]
  - `confusion` → ["je comprends pas", "c'est quoi", "pourquoi", "je vois pas le rapport", "je sais pas"]
  - `resistance` → ["non", "mais", "pas d'accord", "c'est faux", "n'importe quoi", "je peux pas"]
  - `neutre` → ["bonjour", "raconte-moi", "dis-moi", "alors", "et alors"]
- [ ] Charger `bert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")` après `load_model()`
- [ ] Pré-encoder les ancres : `anchor_embeddings = {intent: bert_model.encode(phrases, convert_to_tensor=True) ...}`

#### `app_runpod.py` — Remplacer `detecter_contexte()`
- [ ] Nouvelle implémentation cosine similarity (supprimer l'ancienne keyword-based)
- [ ] Logger l'intent retenu avec ses scores pour debug RunPod

### Critères de sortie
- `detecter_contexte("je comprends pas")` → `"confusion"` (pas `"neutre"`)
- `detecter_contexte("non c'est faux")` → `"resistance"`
- `detecter_contexte("oui tout à fait")` → `"accord"`
- Logs RunPod affichent l'intent + scores cosine
- Build Docker passe avec `sentence-transformers` dans requirements

---

## BACKLOG

- [ ] MISSION 27 : CHATBOT PÉDAGOGIQUE (GEMINI API)
- [ ] MISSION 26 : RAG ENGINE SYSTEM
- [ ] MISSION 29 : CONTRÔLEUR HOMEOS NATIVE (EMBED FIGMA + GUI RETRO-GENOME)