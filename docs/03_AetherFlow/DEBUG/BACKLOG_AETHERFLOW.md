# Backlog AetherFlow — Problèmes Connus & Pistes d'Accélération

> Auteur : Claude Sonnet 4.6
> Date : 2026-02-21
> Statut : Document vivant — à enrichir après chaque run observé

---

## Contexte

AetherFlow est l'orchestrateur de génération de code. Son pipeline PROD (`-f`) enchaîne :
FAST draft (Groq) → BUILD refactor (Deepseek/Gemini) → DOUBLE-CHECK (Claude)

Problèmes identifiés lors du run `plan_phase2_range.json` (2026-02-21).

---

## BL-001 — Latence rédhibitoire sur fichiers > 15k tokens

**Sévérité : CRITIQUE**
**Observé : 2026-02-21, run plan_phase2_range.json**

### Symptôme
Step 1 (code_generation, `surgical_editor.py` 25,734 tokens) → 271 secondes.
Step 2 (code_generation, `surgical_editor.py` + output step 1 = 39,755 tokens) → ~200s (estimé).
Plan complet 3 steps → ~15 minutes minimum.

### Cause

**Smart routing override** : Le plan spécifie `provider: "gemini"` mais le routeur détecte
`estimated_tokens > 15,000` et bascule sur Deepseek avec chunking. Ce n'est PAS un bug du
routeur — c'est le comportement attendu. Le problème est en amont : les fichiers passés en
`input_files` sont entiers (700+ lignes), ce qui gonfle les tokens inutilement.

**Chunking itératif** : 2 chunks × ~77s chacun = 154s de génération pure, sans compter les
retries (chunk 2 timeout systématique, retry +60s). Total réel : 271s.

**Timeout chunk 2 systématique** : Deepseek semble avoir une instabilité sur les requêtes
longues (300s extended timeout). Le pattern est : chunk 1 OK (~50-77s), chunk 2 FAIL → retry
1.0s → chunk 2 OK (~70s).

### Pistes d'accélération

**Court terme (sans refacto):**
1. **Réduire les `input_files`** : Ne pas passer le fichier entier — passer uniquement les
   sections pertinentes. Le plan `step_1` n'a besoin que de `ASTParser` (L53-226), pas des
   700L de `surgical_editor.py`. → **Réduction estimée : 60-70% du token count**.
2. **Forcer le provider dans le plan** : Ajouter `"enforce_provider": true` dans le context
   pour bloquer le routeur auto. Gemini Flash gère 25k tokens sans chunking.
3. **Mode `--sequential` + `-q` (PROTO)** : Pour les tâches de code_generation sur fichiers
   existants, `-q` (FAST draft uniquement, sans BUILD) est suffisant si le plan est bien spécifié.

**Moyen terme (refacto routeur):**
4. **Threshold chunking ajustable** : Actuellement hardcodé à 15,000 tokens. Rendre configurable
   dans le plan JSON : `"chunking_threshold": 30000` pour forcer Gemini sans split.
5. **Context window awareness par provider** :
   - Gemini 1.5 Flash → 1M tokens, pas de chunking nécessaire
   - Deepseek → 64k context, chunking pertinent > 50k
   - Groq → 8k context, chunking pertinent > 6k
   Le routeur devrait utiliser la fenêtre native du provider cible, pas un seuil global.

**Long terme (architecture):**
6. **Plans à steps atomiques < 10k tokens** : Reformuler les plans pour que chaque step
   ne passe que le delta minimal (pas le fichier entier). Pattern : step isolé avec extrait
   de fichier plutôt que fichier complet.
7. **Cache sémantique sur `input_files`** : Si le fichier n'a pas changé depuis le dernier
   run, ne pas le re-tokenizer. Le cache sémantique existe pour les prompts, pas pour les
   fichiers d'entrée.

---

## BL-002 — Provider override ignoré (plan JSON vs smart router)

**Sévérité : MOYENNE**
**Observé : 2026-02-21**

### Symptôme
Plan spécifie `"provider": "gemini"` → router choisit `deepseek` (token count).
L'UI affiche "gemini" comme provider du step, mais les logs montrent "deepseek".
**Trompeur pour le debug.**

### Cause
Le smart router surpasse le provider du plan JSON si le token count dépasse le seuil.
Le champ `provider` dans le plan est une **préférence**, pas une **contrainte**.

### Fix proposé
- Ajouter `"provider_strict": true` dans le context du step pour forcer le provider
  (avec warning si le provider ne peut pas gérer le token count).
- Ou : loguer explicitement "Provider override: plan=gemini → router=deepseek (reason: 25734 tokens > 15000 threshold)".

---

## BL-003 — Timeout systématique sur chunk 2 (Deepseek)

**Sévérité : MOYENNE**
**Observé : 2026-02-21, step_1 et step_2**

### Symptôme
Chunk 1 → OK (~50-77s).
Chunk 2 → FAIL (timeout, `Request error`) → retry 60s → OK.
Pattern 100% reproductible sur le run observé.

### Cause probable
Deepseek API instabilité sur requêtes consécutives à fort token count. La 1ère requête
"chauffe" le rate limiter, la 2ème arrive trop vite. Le retry à 1.0s est insuffisant —
le succès vient 60s plus tard.

### Fix proposé
- Augmenter le délai entre chunks : `inter_chunk_delay: 5s` (au lieu de retry immédiat).
- Ou : alterner les providers entre chunks (chunk 1 = deepseek, chunk 2 = codestral).

---

## BL-004 — Auto-apply status inconnu

**Sévérité : À INVESTIGUER**

### Contexte
MEMORY.md note : "AetherFlow auto-apply NON FONCTIONNEL" (pour JS frontend).
Statut inconnu pour les plans backend Python (code_generation sur fichiers .py).

### À vérifier après run complet
- Est-ce que `output/repair_phase2/` contient les fichiers générés ?
- Est-ce que `surgical_editor.py` a été modifié sur disque ?
- Ou est-ce que l'output est en mémoire uniquement ?

---

## BL-005 — Plans `input_files` trop larges pour le scope réel

**Sévérité : STRUCTURELLE**

### Problème
Les plans actuels passent des fichiers entiers (600-700L) même quand le step ne concerne
qu'une méthode (50L). Le LLM reçoit ~25k tokens de contexte inutile, ce qui :
- Augmente la latence (BL-001)
- Augmente le coût
- Augmente le risque d'hallucination (le LLM "voit" du contexte non pertinent)

### Pratique recommandée pour les futurs plans
Spécifier des extraits de fichier dans les instructions plutôt que le fichier entier :
```json
"input_files": [],
"instructions": "Voici ASTParser.parse() (lignes 53-120) : [extrait collé directement]. Ajoute..."
```
Ou : utiliser un mécanisme d'extraction de section dans le plan loader.

---

## BL-006 — gemini-1.5-flash → 404 en phase BUILD

**Sévérité : HAUTE**
**Observé : 2026-02-21, phase BUILD du run plan_phase2_range.json**

### Symptôme
```
WARNING | Model 'gemini-1.5-flash' not found (404), falling back to next model in cascade
```
La phase BUILD du workflow PROD sélectionne Gemini pour les large contexts (54k tokens).
Le modèle `gemini-1.5-flash` n'est plus disponible → 404.

### Impact
La phase BUILD échoue. Le workflow PROD s'arrête après la phase FAST.
Seule la phase FAST (Deepseek) produit de l'output.

### Fix
Mettre à jour le nom de modèle dans la config Gemini :
- `gemini-1.5-flash` → `gemini-2.0-flash` (ou `gemini-1.5-flash-002`)
- Localisation probable : `models/gemini_client.py` ou `config/`

---

## BL-007 — Auto-apply non fonctionnel (backend Python confirmé)

**Sévérité : STRUCTURELLE**
**Observé : 2026-02-21**

### Symptôme
Après run complet (3 steps FAST phase) : `output/repair_phase2/fast_draft/step_outputs/` contient
`step_1_code.txt`, `step_2_code.txt`, `step_3_code.txt`. Le fichier `surgical_editor.py` source
N'EST PAS modifié.

### Confirmation
MEMORY.md indiquait "AetherFlow auto-apply NON FONCTIONNEL" pour JS frontend.
**Confirmé également pour backend Python.**

### Workaround actuel
CODE DIRECT — appliquer manuellement les outputs du dossier `step_outputs/` via Claude.

### Piste de fix
Tracer le `apply_generated_code()` dans `claude_helper.py` pour `code_generation` :
- `overwrite` mode implémenté (fix 2026-02-21) mais peut-être pas appelé en fin de pipeline
- Vérifier si le pipeline attend une confirmation manuelle avant apply

---

## BL-006 — FIX APPLIQUÉ (2026-02-21)

`gemini-1.5-flash` → `gemini-2.0-flash` dans :
- `Backend/Prod/models/gemini_client.py` : cascades FAST, BUILD, DEFAULT
- `Backend/Prod/config/settings.py` : default + description

Cascades réordonnées : `gemini-2.0-flash` en position 1 (plus de 404 en tête).
**Statut : RÉSOLU**

---

## BL-008 — Absence de veille sur la validité des modèles providers

**Sévérité : STRUCTURELLE**
**Demandé : 2026-02-21**

### Problème
Les noms de modèles sont hardcodés dans les cascades de `gemini_client.py` et dans les
defaults de `settings.py`. Lorsque Google (ou un autre provider) déprécie un modèle,
AetherFlow échoue silencieusement en 404 (BL-006 en est l'exemple parfait).

Il n'existe aucun mécanisme pour :
- Détecter qu'un modèle n'est plus disponible (404 ≠ erreur critique, juste `WARNING`)
- Alerter l'utilisateur qu'une mise à jour de la config est nécessaire
- Vérifier périodiquement la liste des modèles disponibles chez chaque provider

### Impact observé
Build phase cassée pendant une durée inconnue (probablement depuis la dépréciation
de `gemini-1.5-flash` par Google, vraisemblablement fin 2025). Passé inaperçu.

### Pistes

**Court terme :**
1. **Ajouter un `health_check()` dans `GeminiClient`** : Au démarrage, tester le modèle
   primaire avec un ping minimal (1 token). Si 404 → logger `ERROR` (pas `WARNING`) +
   afficher dans l'UI du monitor.
2. **Séparer les niveaux de log** : 404 sur modèle primaire = `ERROR`, 404 sur fallback = `WARNING`.

**Moyen terme :**
3. **Script de veille `check_model_versions.py`** : Interroger les endpoints provider
   (`/v1/models` pour OpenAI-compat, `/v1/models` pour Google) et comparer avec la
   config locale. Générer un rapport `MODELS_AUDIT.md`.
4. **Intégrer dans le monitor** : Afficher un badge "⚠️ 2 modèles dépréciés" dans
   `aetherflow-monitor` si le health check détecte des 404.

**Long terme :**
5. **Auto-update des cascades** : Si un modèle est 404, le retirer automatiquement de
   la cascade et l'enregistrer dans un fichier `deprecated_models.json` pour audit humain.

---

## BL-009 — RAG auto-inject non maîtrisé

**Sévérité : STRUCTURELLE**
**Observé : 2026-02-21, run plan_9B_substyle.json**

### Symptôme

Chaque step reçoit automatiquement 3 chunks RAG injectés dans son prompt, indépendamment
de la pertinence de ces chunks pour la tâche courante.

Observé sur `plan_9B_substyle.json` (step_1 + step_2, zero `input_files`) :
- Tokens attendus : ~800 (step_1) et ~600 (step_2)
- Tokens réels : ~2249 (step_1) et ~1857 (step_2)
- Inflation par step : **+1500 tokens minimum** dus aux chunks RAG

### Impact secondaire : misclassification

Le step_2 (code_generation simple, provider=gemini) a été routé vers le slot
"Vision/multimodal" probablement parce que le contenu des chunks RAG injectés contenait
des termes qui ont déclenché le classifieur de tâche. Le routing était incorrect.

### Cause

Le pipeline AetherFlow injecte systématiquement des résultats de `rag_index` dans chaque
step prompt. Il n'existe aucun moyen de désactiver ce comportement au niveau du plan JSON.
Pour les tâches à instructions auto-suffisantes (code collé dans `instructions`), ce RAG
est du bruit pur — il ne fait qu'augmenter latence, coût et risque de misclassification.

### Fix proposé

Ajouter une option `"rag": false` dans le `context` du step pour désactiver l'injection :

```json
"context": {
  "provider": "gemini",
  "rag": false,
  "instructions": "..."
}
```

Comportement attendu : si `rag: false`, le pipeline saute la phase de retrieval et n'injecte
aucun chunk dans le prompt. Le prompt final = system prompt + instructions uniquement.

**Long terme :** rendre le RAG opt-in (default `false`) plutôt qu'opt-out pour les plans
où `input_files: []` — si aucun fichier en entrée, le RAG est probablement inutile.

---

## Run Log — 2026-02-21

| Run | Plan | Steps | Status final | Durée step_1 | Durée step_2 | Note |
|-----|------|-------|-------------|--------------|--------------|------|
| 11:45 | plan_phase2_range.json | 3 | FAST ✅ / BUILD ❌ | 271s | 247s | Chunk 2 timeout systématique (retry OK) — BUILD stoppé : gemini-1.5-flash 404 |

**Qualité du code généré (FAST phase) :**
- step_1 (`get_char_range()`) : ✅ propre, complet, bien structuré. Rewrite entier de ASTParser.
- step_2 (`apply_operations_ranged()`) : non audité (timeout run)
- step_3 (`apply_operations()` fallback) : non audité (timeout run)

**Verdict :** AetherFlow -f peut générer du code backend de qualité. Le pipeline de livraison
(apply sur disque) est cassé. Fixer BL-006 + BL-007 pour avoir un pipeline E2E fonctionnel.
