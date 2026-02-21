# Plan de Réparation Chirurgicale v2 — Amendé

> Auteur initial : Gemini Flash 3 (diagnostic)
> Amendement : Claude Opus (architecture, priorisation, réutilisation des composants existants)
> Date : 2025-02-15
> Statut : En attente de validation

---

## 0. Contexte et Diagnostic Confirmé

### Symptomes observés
| # | Symptome | Cause racine | Localisation |
|---|----------|-------------|--------------|
| S1 | Code dupliqué en fin de fichier après exécution | Fallback append quand la chirurgie échoue | `orchestrator.py:1753-1771` |
| S2 | Commentaires et formatting disparus | `astunparse.unparse()` reconstruit depuis l'AST (perd tout ce qui n'est pas dans l'arbre) | `surgical_editor.py:484` |
| S3 | Modification appliquée à la mauvaise classe | `ast.walk` sans filtrage strict + cible ambigue | `surgical_editor.py:694` |

### Bug structurel non détecté par Gemini (CRITIQUE)
| # | Bug | Impact | Localisation |
|---|-----|--------|--------------|
| B1 | **`_execute_batch_parallel` existe en DOUBLE** | Deux implémentations divergentes, la 2e est celle réellement appelée | Copie 1: L260-358, Copie 2: L1331-1505 |
| B2 | **`_execute_step` existe en DOUBLE** | Stratégies de fallback contradictoires (VETO vs append) | Copie 1: L645-922 (VETO), Copie 2: L1507-1786 (append) |
| B3 | `datetime` non importé | `datetime.now()` à la ligne 905 provoque un `NameError` silencieux dans le try/except | `orchestrator.py:905` |

### Composants existants sous-exploités (ignorés par le plan Gemini)
| Composant | Fichier | Rôle | Pertinence |
|-----------|---------|------|------------|
| `OutputGatekeeper` | `core/output_gatekeeper.py` | Validation sémantique pre-apply via KIMI/Claude | Remplace partiellement le SurgicalGuard proposé |
| `PostApplyValidator` | `core/post_apply_validator.py` | Validation syntaxique post-apply + rollback git | Déjà implémenté, pas connecté au mode surgical |
| `BaseLLMClient` | `models/base_client.py` | Interface abstraite `generate()` | Support déjà prévu pour `output_constraint` — idéal pour le Master Protocol |

---

## 1. Principes Directeurs

1. **Pas de nouveau composant si un existant peut être étendu.** On étend `OutputGatekeeper`, on ne crée pas `SurgicalGuard`.
2. **Dédupliquer avant de modifier.** Toucher du code dupliqué sans le fusionner d'abord est une recette pour des régressions.
3. **Chaque phase est testable et déployable indépendamment.** Pas de big bang.
4. **Stratégie de fallback unique et explicite.** VETO (préservation du fichier) est le seul comportement acceptable. Le fallback append est supprimé.

---

## 2. Phases de Réparation

### Phase 1 — Assainissement de l'orchestrateur (prérequis)

**Objectif** : Supprimer les duplications et unifier la stratégie de fallback.

**Fichier** : `orchestrator.py`

#### 1.1 Fusionner `_execute_batch_parallel`
- Supprimer la copie 2 (L1331-1505)
- Conserver la copie 1 (L260-358) qui est plus propre
- Vérifier que la copie 1 inclut bien la détection de conflits fichiers (présente dans la copie 2 mais pas dans la copie 1)
- **Action** : Merger la détection de conflits (L1349-1381) dans la copie 1

#### 1.2 Fusionner `_execute_step`
- Supprimer la copie 2 (L1507-1786)
- Conserver la copie 1 (L645-922) qui implémente la stratégie VETO
- **Décision architecturale** : **VETO uniquement**. En cas d'échec surgical, le fichier est préservé, l'erreur est loggée, le JSON fautif est sauvegardé pour debug. Pas d'append.

#### 1.3 Fix mineur
- Ajouter `from datetime import datetime` en tête de fichier (fix du NameError L905)

#### Critère de validation
- Le fichier passe de ~1786 lignes à ~1000 lignes
- `grep -c "def _execute_batch_parallel" orchestrator.py` retourne 1
- `grep -c "def _execute_step" orchestrator.py` retourne 1
- Tous les tests existants passent

#### Difficulté : MOYENNE
#### Risque si mal fait : ÉLEVÉ (casse toute l'exécution)
#### Gemini seul ? NON — Supervision humaine requise pour la décision VETO vs append

---

### Phase 2 — Range-Based Replacement (fix principal)

**Objectif** : Remplacer `astunparse.unparse()` par un remplacement textuel indexé par AST.

**Fichier** : `core/surgical_editor.py`

#### 2.1 Nouvelle méthode `SurgicalApplier.apply_operations_ranged()`

**Principe** :
```
Source original (texte brut)
     ↓
AST parse → localiser (lineno, col_offset, end_lineno, end_col_offset)
     ↓
Convertir en index de caractères dans le texte original
     ↓
Trier les opérations par position décroissante (bottom-up pour ne pas décaler les offsets)
     ↓
Pour chaque opération :
  - Extraire la sous-chaîne [start:end] du source original
  - La remplacer par le nouveau code
     ↓
ast.parse() sur le résultat pour validation syntaxique
     ↓
Retourner le code modifié
```

**Operations supportées** :
- `modify_method` : Remplacer `source[method_start:method_end]` par `op.code`
- `add_method` : Insérer `op.code` à `source[class_end_offset]` (avant le dernier dedent de la classe)
- `add_import` : Insérer à `source[last_import_end]`
- `add_function` : Insérer à `source[after_imports]`
- `add_class` : Insérer à `source[end_of_file]`
- `replace_import` : Remplacer `source[import_start:import_end]` par `op.new_import`

**Changements dans `ASTParser`** :
- Stocker `col_offset` et `end_col_offset` dans `ASTNodeInfo` (en plus de `line_start` / `line_end`)
- Nouvelle méthode `get_char_range(node_name) -> (start_idx, end_idx)` qui convertit les coordonnées ligne/colonne en index de caractères dans le texte source

**Transition** :
- `apply_operations()` existant reste disponible comme fallback
- Nouvelle méthode `apply_operations_ranged()` est appelée en priorité
- Si elle échoue, on tombe sur l'ancienne méthode (dégradation gracieuse)
- La dépendance à `astunparse` devient optionnelle (uniquement pour le fallback)

#### Critère de validation
- Test : modifier une méthode dans un fichier avec des commentaires → les commentaires sont préservés
- Test : modifier une méthode → le reste du fichier est identique octet par octet
- Test : ajouter un import → les commentaires en tête de fichier sont préservés
- Pas de dépendance à `astunparse` pour le chemin principal

#### Difficulté : HAUTE (c'est le coeur du fix)
#### Risque si mal fait : MOYEN (le fallback sur l'ancien code protège)
#### Gemini seul ? OUI — Le scope est isolé dans `surgical_editor.py`, testable unitairement

---

### Phase 3 — Validation pre-surgical via OutputGatekeeper étendu

**Objectif** : Détecter les ambiguïtés et le "hacode" AVANT d'appliquer les opérations surgical.

**Fichiers** : `core/output_gatekeeper.py`, `core/surgical_editor.py`

#### 3.1 Étendre `OutputGatekeeper` avec un mode surgical

Au lieu de créer un nouveau `SurgicalGuard`, ajouter une méthode :

```python
def validate_surgical(self, operations: List[SurgicalOperation], ast_parser: ASTParser) -> ValidationResult
```

**Vérifications déterministes** (pas de LLM, pas de coût) :
1. **Ambiguïté de cible** : Pour chaque `modify_method`, vérifier que `target` matche exactement 1 noeud dans l'AST. Si 0 → erreur "cible introuvable". Si >1 → erreur "cible ambigue, utiliser Classe.methode".
2. **Pureté lexicale** : Dans chaque `op.code`, vérifier l'absence de patterns de prose LLM (`"Here is"`, `"Note:"`, `"I'll"`, `"```"`, lignes commençant par `#` suivi de prose anglaise/française). Regex simple, pas de LLM.
3. **Dry-run syntaxique** : `ast.parse(op.code)` sur chaque fragment de code avant application.
4. **Types supportés** : Rejeter tout `op_type` hors de `SUPPORTED_OPERATIONS`.

#### 3.2 Intégrer dans le pipeline

Dans `SurgicalEditor.apply_instructions()` :
```
parse_instructions() → validate_surgical() → apply_operations_ranged()
```

Le gatekeeper bloque AVANT toute modification de fichier.

#### Critère de validation
- Test : opération avec cible ambigue → rejeté avec message explicite
- Test : code contenant de la prose → rejeté
- Test : type non supporté → rejeté
- Pas d'appel LLM dans cette validation

#### Difficulté : MOYENNE
#### Risque si mal fait : FAIBLE (c'est un filtre, le pire cas = faux positif qui bloque une opération valide)
#### Gemini seul ? OUI avec spec précise

---

### Phase 4 — Master Protocol (prompt système unifié)

**Objectif** : Standardiser le format de sortie surgical pour tous les providers LLM.

**Fichiers** : `models/base_client.py`, `models/agent_router.py`

#### 4.1 Exploiter `output_constraint` existant dans `BaseLLMClient`

Le paramètre `output_constraint` existe déjà dans `BaseLLMClient.generate()`. Il suffit de :

1. Dans `agent_router.py`, quand `surgical_mode=True` :
   ```python
   result = await client.generate(
       prompt=prompt,
       output_constraint="json_surgical"  # nouveau type de contrainte
   )
   ```

2. Dans chaque client (`deepseek_client.py`, `gemini_client.py`, etc.), traduire `output_constraint="json_surgical"` en :
   - **DeepSeek/Groq** : `response_format={"type": "json_object"}` (si supporté) + system prompt
   - **Gemini** : `response_mime_type="application/json"` + `system_instruction`
   - **Claude** : System prompt avec contrainte stricte

3. Le system prompt chirurgical est **centralisé** dans un fichier unique :
   `core/prompts/surgical_protocol.py` (ou `.txt`) — une seule source de vérité.

#### 4.2 Contenu du Master Protocol

```
You are a surgical code editor. Output ONLY a JSON object.
No explanations, no markdown, no prose.

Format:
{"operations": [{"type": "...", "target": "...", "code": "..."}]}

Rules:
- "target" MUST match exactly one entity in the AST summary provided
- "code" MUST be valid Python (parseable by ast.parse)
- Supported types: add_method, modify_method, add_import, replace_import, add_class, add_function
- For methods: target = "ClassName.method_name"
- For FastAPI routes: use add_function with full decorated function
```

#### Critère de validation
- Test : chaque provider retourne du JSON parseable en mode surgical
- Le prompt est chargé depuis un fichier unique, pas hardcodé dans l'orchestrateur

#### Difficulté : MOYENNE
#### Risque si mal fait : MOYEN (peut casser la génération pour un provider spécifique)
#### Gemini seul ? OUI pour l'implémentation, NON pour le design du prompt (nécessite tests multi-provider)

---

## 3. Ordre d'Exécution et Dépendances

```
Phase 1 (Assainissement)
    ↓ prérequis pour tout le reste
Phase 2 (Range-Based Replacement)
    ↓ indépendant de Phase 3
Phase 3 (Validation pre-surgical)    ← peut être fait en parallèle de Phase 2
    ↓
Phase 4 (Master Protocol)            ← nécessite Phase 2+3 terminées
```

**Timeline estimée** :
- Phase 1 : 1 session supervisée
- Phase 2 : 1-2 sessions (la plus complexe)
- Phase 3 : 1 session
- Phase 4 : 1 session

---

## 5. Journal d'Implémentation

### 2026-02-21 — Pre-Apply Validation (hors scope plan initial)

**Auteur :** Claude Sonnet 4.6
**Statut : ✅ IMPLÉMENTÉ — ✅ TESTÉ (`aetherflow -vfx`, sandbox Python)**

**Problème résolu :** Le `VerifyFixWorkflow` appliquait le code AVANT la validation Claude (apply Phase 2, check Phase 3). Les injections intempestives atterrissaient sur disque avant qu'elles puissent être bloquées.

**Changement :** `Backend/Prod/workflows/verify_fix.py`

Nouvelle séquence :
```
Phase 1 — BUILD        (Deepseek génère)
Phase 2 — CHECK        (Claude valide l'output en mémoire — rien écrit)
Phase 3 — si OK → APPLY / si KO → passage au fix
Phase 4 — FIX          (Deepseek corrige)
Phase 5 — CHECK fix    (Claude re-valide le fix — rien écrit)
Phase 6 — si OK → APPLY fix / si KO → apply bloqué définitivement
```

**Périmètre :**
- `VerifyFixWorkflow.execute()` uniquement
- `execute_frd_vfx` dans `frd.py` hérite automatiquement (délègue déjà à VerifyFix)
- `frd._apply_generated_code` (runs non-VFX) reste stub vide — inchangé, comportement conservatif maintenu
- `prod.py` et `proto.py` non touchés

**Résultats du test (2026-02-21) :**
- `Surgical mode: False` confirmé pour `code_generation` → résout "All providers failed"
- Phase 2 DOUBLE-CHECK exécutée avant apply ✓
- Phase 3 Apply conditionnel déclenché sur validation OK ✓
- Bug connexe découvert et corrigé : apply en mode `code_generation` sur fichier existant → **append** au lieu d'overwrite → code dupliqué. Correctif `claude_helper.py` : overwrite direct.

**Correctif `claude_helper.py:apply_generated_code()` :**
Pour `code_generation` : suppression du bloc append. Overwrite direct.
Rationale : le LLM reçoit le fichier existant en contexte → génère la version complète → overwrite correct.

**Correctif associé — `orchestrator.py` :**
Critère surgical resserré : `step.type == 'refactoring'` uniquement (retiré `code_generation`).
`code_generation` = le LLM génère le fichier complet → overwrite direct, pas de JSON chirurgical.

**Test final (2026-02-21) — Pipeline complet ✅ VALIDÉ :**
```
Surgical mode: False (step_type=code_generation)  ✓
Phase 1: BUILD (Groq, cache)                       ✓
Phase 2: Validation DOUBLE-CHECK avant apply       ✓
Phase 3: Overwrote target_config.py                ✓
✓ Applied code from step_1                         ✓
```
Fichier résultant : 25L propres, pas de doublon.

---

## 4. Ce qui est SUPPRIMÉ du plan Gemini original

| Proposition Gemini | Raison de suppression |
|---|---|
| Créer un composant `SurgicalGuard` standalone | Redondant avec `OutputGatekeeper` existant — on l'étend |
| Refactorer `BaseLLMClient.generate()` pour ajouter `system_prompt` | Le paramètre `output_constraint` existe déjà — on l'exploite |
| "Logger explicitement chaque Fallback Append" (court terme) | Le fallback append est **supprimé**, pas loggé. Stratégie VETO uniquement. |

## 5. Ce qui est AJOUTÉ par rapport au plan Gemini

| Ajout | Raison |
|---|---|
| Phase 1 (déduplication orchestrateur) | Bug structurel critique non détecté par Gemini |
| Fix `datetime` import manquant | Bug silencieux dans le error handling |
| Transition gracieuse (fallback sur ancien `apply_operations`) | Sécurité : si le range-based replacement échoue, on dégrade proprement |
| Réutilisation des composants existants | Principe d'économie : pas de code neuf si du code existant peut être étendu |

---

## 6. Matrice de Risque par Phase

| Phase | Impact si échec | Réversibilité | Gemini autonome ? |
|---|---|---|---|
| 1 - Assainissement | Casse l'exécution complète | Git revert facile | **NON** — supervision requise |
| 2 - Range-Based | Mode surgical défaillant (fallback existe) | Fallback sur ancien code | **OUI** |
| 3 - Validation | Faux positifs (bloque des ops valides) | Désactivable par flag | **OUI** |
| 4 - Master Protocol | Prompts cassés pour 1+ provider | Revert du prompt | **OUI** avec tests |
