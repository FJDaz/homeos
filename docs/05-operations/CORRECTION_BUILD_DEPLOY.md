# Correction en chaîne : erreurs de build et de déploiement

## Ce que tu veux

Pouvoir régler automatiquement les **vraies** erreurs qu’on rencontre quand on :
- **build** le front (ex. `npm run build` dans `frontend-svelte` qui casse),
- **déploie** (ex. erreur Vercel/Docker/CI),

sans tout faire à la main : lancer la commande → lire l’erreur → corriger le code → relancer → répéter jusqu’à ce que ça passe.

---

## Situation actuelle

| Besoin | Aujourd’hui |
|--------|-------------|
| Détecter les erreurs | **VerifyFix** utilise un LLM (Gemini) qui *lit le code généré* et signale des problèmes de syntaxe/logique. Il ne lance **pas** de vraie commande (`npm run build`, `docker build`, etc.). |
| Corriger en boucle | VerifyFix fait : BUILD → apply → validation LLM → si invalide, **plan de correction** → exécution du plan → re-validation LLM. Une seule (ou peu) reprise, et la « validation » reste du texte, pas un build réel. |
| Erreurs réelles build/deploy | Aucun workflow ne lance `npm run build` ou un script de déploiement et ne reboucle sur la **sortie réelle** (stderr/stdout) pour corriger. |

Donc : les erreurs **réelles** de build ou de déploiement ne pilotent pas encore une boucle de correction automatique.

---

## Objectif

Un mode ou un workflow **« Run-and-Fix »** (ou **BuildFix** / **DeployFix**) qui :

1. **Lance une commande réelle** (ex. `cd frontend-svelte && npm run build`, ou `vercel deploy --prebuilt`).
2. **Si la commande échoue** (exit code ≠ 0) :
   - récupère stdout + stderr ;
   - envoie au LLM : « Voici l’erreur, voici le contexte (fichiers concernés ou repo), propose des corrections » ;
   - applique les corrections (fichiers modifiés) ;
   - **relance la même commande**.
3. **Répète** jusqu’à succès ou jusqu’à un nombre max de tours (ex. 5).

Pas besoin d’outils dans le LLM pour commencer : une **boucle au niveau workflow** suffit, avec une seule « action » côté Backend : **exécuter une commande** (avec liste blanche pour la sécurité).

---

## Proposition : workflow Run-and-Fix

### Entrées

- **Commande à exécuter** : ex. `cd frontend-svelte && npm run build`, ou un script `./deploy.sh`.
- **Répertoire de travail** : ex. racine du projet ou `frontend-svelte`.
- **Fichiers à fournir au LLM** en cas d’échec : soit liste fixe (ex. `frontend-svelte/src/**`), soit déduits de l’erreur (fichier:ligne dans stderr).
- **Nombre max de tours** : ex. 5.

### Boucle (par tour)

1. **Run** : `subprocess.run(commande, cwd=workdir, capture_output=True, text=True)`.
2. **Si exit code == 0** : succès → fin.
3. **Sinon** :
   - Construire un **prompt** : « La commande suivante a échoué. Sortie standard : … Sortie erreur : … [Contexte : contenu des fichiers X, Y, Z]. Propose des corrections (blocs de code à appliquer, un bloc par fichier, avec en-tête du type `FILE: path/to/file`). »
   - Appel LLM (DeepSeek/Gemini/etc.) → texte de réponse.
   - **Parser la réponse** : extraire les blocs par fichier (comme dans `apply_generated_code` ou une variante).
   - **Appliquer** les modifications aux fichiers.
   - **Retour à l’étape 1** (tour suivant).

### Sécurité

- **Liste blanche de commandes** : n’autoriser que des commandes prédéfinies ou des motifs (ex. `npm run build`, `pnpm build`, `docker build`, `./deploy.sh`). Pas de `rm -rf` ni de commandes arbitraires.
- **Timeout** par exécution (ex. 120 s pour un build).
- **Répertoire de travail** fixé (pas de `cd` depuis la commande utilisateur vers un répertoire sensible).

---

## Où l’implémenter dans le code

1. **Nouveau workflow** (ex. `Backend/Prod/workflows/run_and_fix.py`) :
   - `RunAndFixWorkflow.execute(command=..., workdir=..., files_context=..., max_rounds=5)`.
   - Boucle : run_cmd → si échec, build prompt → `agent_router` (ou un client) pour une étape unique « fix from error » → `apply_generated_code` ou un applicateur dédié → re-run.

2. **Exécution de la commande** :
   - Module ou fonctions dans `Backend/Prod/core/` (ex. `run_sandbox.py`) : `run_allowed_command(command, cwd, timeout_sec) -> (exit_code, stdout, stderr)`. Liste blanche dans config ou en dur au début.

3. **CLI** :
   - Option ou sous-commande, ex. `aetherflow run-and-fix --command "cd frontend-svelte && npm run build" --max-rounds 5`, ou `aetherflow build-fix --frontend` qui fixe la commande et le workdir pour le front Svelte.

4. **Optionnel** : un petit « plan » dynamique d’un seul step par tour (description = « Fix build error: … »), pour réutiliser `apply_generated_code` et le même mécanisme d’application que le reste d’AETHERFLOW.

---

## Résumé

- **Problème** : aujourd’hui, AETHERFLOW ne corrige pas en boucle à partir des **vraies** erreurs de build ou de déploiement (pas d’exécution de `npm run build` / deploy, pas de reprise pilotée par stderr).
- **Solution ciblée** : un workflow **Run-and-Fix** (BuildFix/DeployFix) qui : lance une commande réelle → en cas d’échec, envoie l’erreur + contexte au LLM → applique les corrections → relance la commande, jusqu’à succès ou max de tours.
- **Implémentation minimale** : pas besoin de tool_calling dans le LLM ; une boucle au niveau workflow + un seul « outil » côté Backend (exécuter une commande autorisée) suffit pour couvrir build front et déploiement.

Ensuite, si tu veux aller plus loin (le LLM décide lui-même quelle commande lancer, ou lit/édite des fichiers via des outils), on peut s’appuyer sur le doc **AETHERFLOW_AGENT_POWER.md** (boucle agentique avec outils).
