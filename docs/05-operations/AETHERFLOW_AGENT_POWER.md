# Donner à AETHERFLOW le pouvoir d’agent (comme Claude Code)

## Contexte

**Cas d’usage principal** : régler les erreurs et la **correction en chaîne** qu’on rencontre quand on **build le front** ou qu’on **déploie** — lancer une commande réelle (`npm run build`, deploy), lire l’erreur, corriger le code, relancer, jusqu’à succès. Voir **CORRECTION_BUILD_DEPLOY.md** pour le workflow Run-and-Fix (BuildFix/DeployFix) ciblé sur ce besoin.

**Aujourd’hui** :
- **Claude Code (dans Cursor)** = agent : il a des *outils* (read_file, search_replace, run_terminal, grep, codebase_search, todo_write). Il peut enchaîner : lire un fichier → modifier → lancer une commande → relire → re-modifier, jusqu’à atteindre l’objectif.
- **AETHERFLOW** = exécuteur de plan en *one-shot* par étape : pour chaque step, on construit un prompt (description + contexte + fichiers existants injectés en texte), on appelle une fois le LLM (DeepSeek, Gemini, etc.), on récupère un bloc de texte/code. Pas de boucle, pas d’outils côté AETHERFLOW.

Donc AETHERFLOW ne peut pas, seul, « explorer le repo, modifier un fichier, relancer les tests, corriger en fonction de l’erreur ». Pour donner ce pouvoir d’agent à AETHERFLOW, il faut introduire une **boucle agentique avec outils** pendant l’exécution d’un step.

---

## Écart actuel (résumé)

| Capacité | Claude Code (Cursor) | AETHERFLOW actuel |
|----------|----------------------|--------------------|
| Lire un fichier | ✅ `read_file` | ❌ Uniquement contenu injecté dans le prompt (déjà fait par l’orchestrator pour les `context.files`) |
| Modifier un fichier | ✅ `search_replace` / `write` | ❌ Sortie texte uniquement ; l’application se fait après (workflow ou Claude Code via `apply_generated_code`) |
| Lancer une commande | ✅ `run_terminal` | ❌ Non |
| Recherche dans le code | ✅ `grep` / `codebase_search` | ⚠️ RAG possible pour enrichir le contexte, mais pas d’outil « demande → résultat » pendant le step |
| Planifier / suivre | ✅ `todo_write` | ❌ Non (le plan est fixe, pas de sous-tâches dynamiques) |

---

## Objectif

Permettre à AETHERFLOW, **pendant l’exécution d’un step**, d’enchaîner plusieurs appels LLM et des **actions outil** (lire, éditer, exécuter une commande, chercher), jusqu’à ce que le modèle décide que le step est terminé. Ainsi, un même step peut « lire → modifier → lancer les tests → lire l’erreur → corriger » sans que tout soit prévu à l’avance dans le plan.

---

## Options d’architecture

### Option 1 : Outils dans le Backend (boucle agentique côté AETHERFLOW)

**Idée** : Dans `AgentRouter.execute_step()` (ou une nouvelle méthode `execute_step_agentic()`), au lieu d’un seul `provider.generate(prompt, ...)`, on exécute une boucle :

1. Appel LLM avec **messages** (system + user + éventuels tool_results) et **définition des outils** (read_file, search_replace, run_terminal, list_dir, grep).
2. Si la réponse contient des **tool_calls** (format OpenAI/Anthropic/DeepSeek/Gemini) :
   - Exécuter chaque outil **dans le processus Backend** (Python) : lire fichier, écrire, lancer une sous-commande, etc.
   - Ajouter les résultats aux messages, rappeler le LLM.
3. Répéter jusqu’à ce que le LLM renvoie une réponse « finale » sans tool_calls (ou avec un outil dédié `finish_step`).

**À ajouter côté code** :

- **Définition des outils** (schéma JSON) : `read_file(path)`, `search_replace(path, old_string, new_string)`, `write(path, content)`, `run_terminal(command)`, `list_dir(path)`, `grep(pattern, path)` (et optionnellement `codebase_search(query)` si vous avez des embeddings).
- **Implémentation des outils** : fonctions Python qui s’exécutent dans le Backend, avec `workspace_root` (ex. depuis `settings`) pour résoudre les chemins. Pour `run_terminal`, définir une liste blanche de commandes autorisées ou un sandbox pour limiter les risques.
- **Support tool calling dans les clients** : les APIs DeepSeek, Gemini, etc. proposent du « function calling ». Il faut :
  - Étendre (ou adapter) l’interface des clients pour accepter `messages` + `tools` et retourner `content` + `tool_calls`.
  - Dans la boucle agentique, utiliser cette interface au lieu d’un simple `generate(prompt)`.

**Où brancher** :  
Soit dans `orchestrator._execute_step()` (mode « agentic » si un flag ou un type de step le demande), soit dans `agent_router.execute_step()` quand un paramètre `agentic=True`. La boucle vit là ; les outils sont exécutés dans le même processus que le CLI (répertoire de travail = racine du projet).

**Avantages** : Comportement autonome, reproductible, sans dépendance à Cursor.  
**Inconvénients** : Implémentation et maintenance des outils, gestion de la sécurité (surtout `run_terminal`), et il faut que chaque provider (DeepSeek, Gemini, …) expose bien le tool calling.

---

### Option 2 : Déléguer les outils à Cursor (MCP ou API locale)

**Idée** : AETHERFLOW ne possède pas les outils lui-même ; quand le LLM demande « lire le fichier X » ou « exécuter la commande Y », AETHERFLOW envoie la requête à un **service qui tourne dans Cursor** (ou à un serveur MCP que Cursor pilote). Ce service exécute read_file, search_replace, run_terminal, etc. et renvoie le résultat à AETHERFLOW, qui l’injecte dans la conversation LLM.

**Implémentation possible** :

- Un petit serveur (FastAPI ou MCP) côté Cursor/IDE qui expose des endpoints ou des outils MCP : `read_file`, `edit_file`, `run_terminal`, …
- AETHERFLOW (Backend) en mode agentic : le LLM émet des « tool calls » dont les noms correspondent à ces outils ; le Backend les envoie au serveur Cursor (HTTP ou MCP), reçoit le résultat, et le renvoie au LLM.

**Avantages** : Réutilisation des mêmes outils que Claude Code (même espace de travail, même sécurité que l’IDE).  
**Inconvénients** : Dépendance à un processus Cursor/serveur ; configuration réseau (localhost, tokens, etc.) ; plus complexe à faire tourner en CI ou « headless ».

---

### Option 3 : Hybride (recommandé pour démarrer)

- **Par défaut** : garder le comportement actuel (one-shot par step, pas d’outils).
- **Mode agentic** : activable par flag (ex. `--agentic`) ou par type de step (ex. `"type": "agentic"` dans le plan). Quand activé, utiliser **Option 1** (outils dans le Backend) avec une liste d’outils minimale et sûre :
  - `read_file`, `list_dir`, `grep` (lecture seule) ;
  - `search_replace` / `write` (écriture dans le workspace) ;
  - `run_terminal` avec liste blanche (ex. `python -m pytest`, `ls`, `git status`) ou désactivé en premier temps.

Cela permet d’ajouter le pouvoir d’agent sans casser les plans existants et en limitant la surface d’attaque.

---

## Emplacements dans le code (Option 1 / 3)

1. **Définition des outils**  
   Nouveau module, ex. `Backend/Prod/tools/` ou `Backend/Prod/agent/` :  
   - Schémas JSON des outils (pour l’API du LLM).  
   - Implémentation Python : `read_file(workspace_root, path)`, `search_replace(...)`, etc.

2. **Boucle agentique**  
   - Soit dans `AgentRouter` : `execute_step_agentic(step, context, tools_registry)` qui en interne fait la boucle LLM ↔ tool_calls ↔ execution.  
   - Soit dans `Orchestrator._execute_step()` : si `step.type == "agentic"` ou si `settings.agentic_steps` est True, appeler cette nouvelle voie au lieu de `agent_router.execute_step()` classique.

3. **Clients LLM**  
   - Adapter au moins un client (ex. DeepSeek ou Gemini) pour accepter une liste de `tools` et un format `messages` (avec rôle et contenu), et retourner dans la réponse les `tool_calls` et le contenu texte.  
   - La boucle agentique utilise cette API jusqu’à réponse sans tool_calls (ou avec un marqueur de fin).

4. **Sécurité**  
   - `run_terminal` : liste blanche de commandes ou sous-processus avec timeout et droits limités.  
   - Chemins : restreindre à `workspace_root` pour éviter de lire/écrire en dehors du projet.

---

## Résumé

- **Aujourd’hui** : AETHERFLOW = un appel LLM par step, texte en sortie ; pas d’outils, pas de boucle.  
- **Pour lui donner le même genre de pouvoir qu’un agent** : introduire une **exécution agentique** par step (boucle LLM + outils).  
- **Recommandation** : Option 3 (hybride) avec outils implémentés dans le Backend (Option 1), activables via flag ou type de step, avec un premier jeu d’outils limité et sécurisé (`read_file`, `list_dir`, `grep`, `search_replace`/`write`, et éventuellement `run_terminal` restreint).

Une fois cette boucle et ces outils en place, AETHERFLOW pourra, sur les steps concernés, enchaîner lecture / édition / commandes de la même façon que Claude Code enchaîne les outils dans Cursor.
