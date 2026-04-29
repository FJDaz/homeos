# Mode DOUBLE-CHECK standalone

Document de référence : design du mode DOUBLE-CHECK et branchement de `--check` pour qu’il tienne seul.

---

## Design prévu

| Mode | Rôle |
|------|------|
| **DOUBLE-CHECK** | Phase de validation (audit Gemini) sur les sorties d’une exécution. **Doit pouvoir tenir seul** : revalider un `output/` existant sans refaire FAST ni BUILD. |
| **Quick (`-q`)** | **PROTO** = FAST + DOUBLE-CHECK. |
| **Full (`-f`)** | **PROD** = plan + DeepSeek/Codestral (génération + contrôle) + DOUBLE-CHECK. |

En résumé :
- DOUBLE-CHECK = audit (Gemini) qui peut être lancé **seul**.
- `-q` = une run PROTO complète (FAST puis DOUBLE-CHECK).
- `-f` = une run PROD complète (draft → BUILD → DOUBLE-CHECK).

---

## État actuel

- **`-q`** et **`-f`** : DOUBLE-CHECK est bien inclus en fin de workflow (ProtoWorkflow / ProdWorkflow).
- **`--check`** : le mode DOUBLE-CHECK **autonome** n’est pas branché. Le CLI fait uniquement :
  - afficher « Double-check functionality requires plan file. Use --check --plan <plan.json> »
  - sortir avec code 1.  
  Aucune exécution de la phase DOUBLE-CHECK.

---

## Implémentation à prévoir : `--check --plan` (DOUBLE-CHECK seul)

Objectif : `./aetherflow --check --plan <plan.json> [--output <dir>]` exécute **uniquement** la phase DOUBLE-CHECK.

### Idée

1. **CLI** (`Backend/Prod/cli.py`)  
   - Quand `args.check` est vrai, ne plus sortir tout de suite.  
   - Exiger `args.plan` (et optionnellement `args.output`).  
   - Appeler un workflow ou une fonction dédiée « double-check only ».

2. **Données d’entrée**  
   - **Plan** : `args.plan` (même structure que pour `-q`/`-f`).  
   - **Outputs à valider** : répertoire `args.output` ou `settings.output_dir`, sous-dir dérivé du `task_id` ou convention (ex. `output/<task_id>/step_outputs/` ou `output/validation/step_outputs/`).

3. **Logique (s’inspirer de ProtoWorkflow)**  
   - Lire le plan pour avoir la liste des steps.  
   - Pour chaque step, charger le fichier de sortie existant dans `output_dir` (même format que `get_step_output(step_id, output_dir)`).  
   - Construire un **plan de validation** (comme dans `ProtoWorkflow._validate_fast_results`) : une étape « analysis » / « validation » par step, avec le contenu du step output dans le contexte.  
   - Exécuter ce plan de validation avec l’orchestrateur en **`execution_mode="DOUBLE-CHECK"`** (Gemini, pas DeepSeek).  
   - Afficher le résumé (validé / non validé, feedback pédagogique si présent).

4. **Fichiers concernés**  
   - `Backend/Prod/cli.py` : branche `if args.check` → vérifier `args.plan` (et `args.output`), appeler la nouvelle fonction/workflow.  
   - `Backend/Prod/workflows/proto.py` : la logique de `_validate_fast_results` (création du validation plan, exécution en DOUBLE-CHECK) peut être extraite ou réutilisée pour le mode standalone (entrée : plan + output_dir au lieu de `fast_result`).

5. **Convention `output_dir`**  
   - Soit déduire un répertoire par défaut (ex. dernier `output/<task_id>` ou `output/validation`).  
   - Soit exiger `--output` quand on lance `--check`, pour éviter toute ambiguïté.

### Résumé

- **Design** : DOUBLE-CHECK tient seul ; `-q` = FAST + DOUBLE-CHECK ; `-f` = PROD + DOUBLE-CHECK.  
- **À faire** : brancher `--check --plan [--output]` pour exécuter uniquement la phase DOUBLE-CHECK (lecture des step outputs existants + validation Gemini), sans refaire FAST ni BUILD.

---

*Réf. : ProtoWorkflow `_validate_fast_results` (Backend/Prod/workflows/proto.py), CLI `--check` (Backend/Prod/cli.py ~L617–620).*
