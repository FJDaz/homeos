# Causes des erreurs systématiques après Aetherflow -f / -vfx

## Contexte

Après une exécution `aetherflow -f` ou `-vfx`, les fichiers cibles sont souvent tronqués, mélangés (Python dans un .md) ou partiellement appliqués, ce qui oblige à des corrections manuelles.

## Causes identifiées (Backend/Prod/claude_helper.py)

### 1. Seul le **premier** bloc de code est utilisé

```python
# claude_helper.py ~L291
language, code_content = code_blocks[0]
```

- La fonction `apply_generated_code()` extrait tous les blocs `` ```lang ... ``` `` du step output, mais **n’utilise que `code_blocks[0]`**.
- Si le LLM produit plusieurs blocs (ex. un pour README, un pour homeos/README, puis du Python), **le même premier bloc** est appliqué à **tous** les fichiers du step (`step.context.files`).
- Conséquence : un bloc Python ou un mauvais bloc est écrit dans tous les fichiers (ex. Python dans `docs/04-homeos/README.md` et `homeos/README.md`).

### 2. Un même step output pour plusieurs fichiers

- Dans `proto.py` / `prod.py`, pour chaque step on fait une boucle sur `target_files = step.context.get("files", [])`.
- Pour **chaque** fichier cible, on appelle `apply_generated_code(step_output, target_file, plan_step)` avec **le même** `step_output`.
- Il n’existe **aucune logique** du type « bloc 1 → fichier 1, bloc 2 → fichier 2 ».
- Conséquence : le même (mauvais) premier bloc est répété sur chaque fichier.

### 3. Livrables « tout en markdown » sans bloc

- L’extraction se fait uniquement via des blocs `` ```lang\n...\n``` `` (`_extract_code_blocks()`).
- Si le livrable est du **markdown pur** (ex. ETAT_LIEUX.md) et que le LLM **ne** le met **pas** dans un bloc `` ```markdown ... ``` ``, alors `code_blocks` est vide.
- Comportement actuel : `"No code blocks found"` → `return False` → rien n’est écrit, ou un fallback prend un autre contenu (ex. un tout petit bloc `` ```bash ... ``` `` plus bas) et l’utilise comme seul bloc → fichier **tronqué**.

### 4. Défaut de langage = Python

- Ligne 174 : `language = match.group(1) or "python"` — si le bloc est `` ```\n...\n``` `` (sans langage), on considère que c’est du **Python**.
- Les fallbacks (lignes 182–194) ne cherchent que python / javascript / typescript, pas `markdown` ou `md`.
- Conséquence : du contenu markdown dans un bloc non marqué peut être traité comme du Python ou ignoré.

### 5. Pas de prise en compte de l’extension cible

- Le choix du contenu à appliquer ne dépend **pas** de `target_file.suffix` (.md, .py, etc.).
- On ne cherche pas un bloc dont le langage correspond au fichier (ex. bloc `` ```markdown ``` `` pour un .md).
- Conséquence : pour un .md, si le premier bloc est du Python, on écrit du Python dans le .md.

---

## Synthèse

| Cause | Effet observable |
|-------|------------------|
| Utilisation unique de `code_blocks[0]` | Mauvais bloc (souvent du code) appliqué partout. |
| Même output pour tous les fichiers | Même erreur répétée sur chaque fichier du step. |
| Pas de bloc → pas d’application / fallback fragile | Fichier vide ou tronqué (ex. seul un petit bloc bash). |
| Défaut Python + pas de bloc markdown | Markdown ignoré ou interprété comme code. |
| Pas de matching bloc ↔ extension | .md reçoit du Python ou autre. |

---

## Correctifs implémentés (Backend/Prod/claude_helper.py)

1. **Fichiers .md sans bloc** : si aucun bloc n’est trouvé et que la cible est un `.md`, le contenu du step output est nettoyé (`_extract_markdown_from_output`) et écrit dans le fichier.
2. **Choix du bloc par extension** : `_select_best_block(code_blocks, target_file)` choisit le bloc dont le langage correspond à l’extension (`.md` → `markdown`/`md`/`text`, `.py` → `python`, etc.) au lieu de toujours prendre `code_blocks[0]`.
3. **Blocs non marqués** : un bloc `` ```\n...\n``` `` sans langage est traité comme `text` (et peut être associé à un .md) au lieu de `python`.
4. **Fallback markdown dans l’extraction** : `_extract_code_blocks` inclut les patterns `markdown` et `md` pour détecter les blocs `` ```markdown ... ``` `` et `` ```md ... ``` ``.

Ces changements réduisent les corrections manuelles après `-f` / `-vfx`. Pour aller plus loin : associer bloc i → fichier i quand un step produit plusieurs fichiers (nécessiterait de passer la liste des fichiers à `apply_generated_code` ou d’adapter l’appelant).
