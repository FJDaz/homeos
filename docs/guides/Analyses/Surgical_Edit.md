# Mode Surgical Edit (aetherflow -f)

## Contexte

En workflow **Full** (`aetherflow -f`), lorsqu’un step modifie des **fichiers Python existants** (référencés dans `step.context.files`), AETHERFLOW active automatiquement le **mode Surgical Edit**.

Au lieu de demander au LLM un fichier complet (risque de merge manuel, imports cassés, nommage incohérent), le LLM produit des **instructions de modification structurées (JSON)** qui sont appliquées précisément via l’AST.

## Activation

- **Condition** : `aetherflow -f` (workflow PROD) **et** au moins un fichier Python existant dans `step.context.files`.
- **Détection** : automatique ; pas de flag à passer.
- **Fallback** : si le parsing AST échoue ou si le LLM ne renvoie pas de JSON valide, le comportement revient au mode normal (fichier complet ou merge manuel).

## Flux

1. L’orchestrator charge les fichiers existants et parse l’AST des `.py`.
2. Le prompt inclut la **structure AST** (classes, méthodes, imports) et demande un **JSON d’opérations**.
3. Le LLM renvoie un objet `{ "operations": [ ... ] }`.
4. `SurgicalEditor` parse les opérations, les applique à l’AST, régénère le code, valide la syntaxe.
5. En cas de succès : le fichier cible est mis à jour. En cas d’échec : fallback vers le mode normal (pas d’écrasement du fichier).

## Types d’opérations supportés

| Type            | Description                    | Champs requis / utiles                    |
|-----------------|--------------------------------|-------------------------------------------|
| `add_method`    | Ajouter une méthode à une classe | `target`, `code`, `position`, `after_method` |
| `add_import`    | Ajouter un import              | `import` ou `code`                        |
| `replace_import`| Remplacer un import           | `old`, `new`                              |
| `add_class`     | Ajouter une classe            | `code`, `position`, `after_class`         |
| `add_function`  | Ajouter une fonction module   | `code`, `position`, `after_function`      |
| `modify_method` | Remplacer une méthode         | `target`, `code`                          |

## Gestion des erreurs

- **Validation des opérations** : chaque opération est validée (type supporté, champs requis) avant toute modification.
- **Validation de la syntaxe** : après régénération du code, `ast.parse()` est utilisé ; en cas d’erreur, le mode surgical échoue et le fallback normal est utilisé.
- **Fichier original** : en échec, le fichier n’est pas écrasé ; l’appelant reçoit le code original pour restauration si besoin.
- **Logs** : warnings/info en cas de fallback (instructions invalides, syntaxe incorrecte, erreur d’application).

## Fichiers concernés

- **Module** : `Backend/Prod/core/surgical_editor.py` (ASTParser, SurgicalInstructionParser, SurgicalApplier, SurgicalEditor).
- **Intégration** : `Backend/Prod/orchestrator.py` (détection mode surgical, injection contexte AST), `Backend/Prod/models/agent_router.py` (prompt), `Backend/Prod/claude_helper.py` (application des instructions si appel depuis Claude Code).

## Limites actuelles

- **Langage** : Python uniquement (fichiers `.py`).
- **Modifications** : add/replace pour méthodes, imports, classes, fonctions ; pas de refactoring complexe (renommage global, déplacement de blocs).
- **modify_method** : implémenté comme remplacement complet de la méthode par du nouveau code.

## Référence

Voir le plan d’implémentation : `.cursor/plans/surgical_edit_mode_dffa6f8c.plan.md`.
