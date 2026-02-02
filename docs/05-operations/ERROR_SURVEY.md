# Survey — Toutes les anomalies du système

**Scope** : le survey couvre **toutes les anomalies du système** — pas seulement Aetherflow. Sont enregistrés : erreurs Aetherflow (step, apply, validation), corrections Cursor/Claude, et toute autre anomalie (build, deploy, API, timeout, clés, CLI, workflow, etc.).

AETHERFLOW enregistre automatiquement les **erreurs** qu’il produit ; la commande `report-correction` permet d’enregistrer des **corrections** manuelles ; le code peut appeler `log_anomaly()` pour toute autre **anomalie système**. Tout est compilé dans un répertoire dédié avec **titre**, **date**, **nature** et **proposition de solution**.

**Indépendance** : l’archivage automatique **ne dépend pas** de `report-correction`. La lecture (`aetherflow survey`) affiche toutes les entrées, quel que soit l’origine.

---

## Natures d’anomalies (exemples)

| Nature | Description |
|--------|-------------|
| `step_failed` | Step Aetherflow retourne success=False |
| `step_exception` | Exception pendant l’exécution d’un step |
| `apply_failed` | Échec d’application du code généré (fichier) |
| `validation_failed` | Step marqué invalide par DOUBLE-CHECK |
| `build_error` | Échec de build (npm, docker, etc.) |
| `deploy_error` | Échec de déploiement |
| `api_error` | Erreur API (provider, quota, etc.) |
| `timeout` | Timeout (requête, commande) |
| `key_missing` | Clé API manquante ou invalide |
| `balance_low` | Solde / quota insuffisant |
| `cli_error` | Erreur CLI (argument, plan manquant, etc.) |
| `workflow_failed` | Échec d’un workflow (VerifyFix, RunAndFix, etc.) |
| `correction_applied` | Correction manuelle Cursor/Claude |
| `other` | Autre anomalie |

---

## Répertoire

- **Par défaut** : `output/aetherflow_error_log/`
- **Config** : variable d’environnement `AETHERFLOW_ERROR_LOG_DIR` (ou `settings.error_log_dir`).

À la première utilisation, un `README.md` est créé dans ce répertoire.

---

## Contenu enregistré automatiquement (Aetherflow + système)

| Événement | Nature | Déclencheur |
|-----------|--------|-------------|
| Step échoué | `step_failed` | Orchestrator : un step retourne `success=False` |
| Exception step | `step_exception` | Orchestrator : exception pendant l’exécution d’un step |
| Apply échoué | `apply_failed` | PROTO / PROD / VerifyFix : `apply_generated_code` a échoué pour un fichier |
| Validation échouée | `validation_failed` | PROTO / PROD / VerifyFix : step marqué invalide par DOUBLE-CHECK |

Chaque entrée génère :
- un fichier **`.md`** : titre, date, nature, source, proposition de solution, erreur brute (optionnel), step/fichier/plan/workflow ;
- un fichier **`.json`** : métadonnées (title, date, nature, source, step_id, file_path, etc.).

Nom des fichiers : `YYYY-MM-DD_HH-MM-SS_<slug>.md` et `.json`.

---

## Enregistrer une correction (Cursor / Claude)

Quand tu corriges manuellement une erreur produite par Aetherflow, enregistre-la pour alimenter le survey :

```bash
aetherflow report-correction \
  --title "Bloc Python appliqué dans un .md" \
  --nature "correction_applied" \
  --solution "Choisir le bloc par extension (claude_helper _select_best_block) ; ne pas utiliser code_blocks[0] pour tous les fichiers." \
  --source cursor \
  --file "docs/04-homeos/README.md" \
  --step "step_2" \
  --error "No code blocks found"
```

Options :
- **--title** / **-t** : titre court (obligatoire)
- **--solution** / **-s** : description de la correction (obligatoire)
- **--nature** / **-n** : type (défaut : `correction_applied`)
- **--source** : `cursor` ou `claude` (défaut : `cursor`)
- **--file** / **-f** : fichier concerné (optionnel)
- **--step** : step concerné, ex. step_1 (optionnel)
- **--error** : message d’erreur brut (optionnel)

Exemple minimal :

```bash
aetherflow report-correction -t "Fix import manquant" -s "Ajout de l'import manquant dans le fichier."
```

---

## Plans : rapports et inventaires

Pour les tâches « rapport » ou « inventaire » (ex. IR : genome vs PRD), le LLM doit recevoir les **sources** en entrée. Utiliser `context.input_files` dans le plan pour les fichiers en lecture seule (genome, PRD, etc.) ; ils sont injectés dans le prompt sous « Reference data (read-only) » et ne sont pas utilisés pour l’apply. Garder `context.files` pour le seul livrable (ex. `output/studio/ir_inventaire.md`). Sinon le LLM n’a pas les données et produit un rapport générique ou incomplet.

---

## Utilisation

- **Analyse** : parcourir `output/aetherflow_error_log/` pour voir les erreurs récurrentes et les corrections appliquées.
- **Amélioration** : s’en servir pour prioriser les correctifs (apply, validation, step prompts) et documenter les patterns de correction Cursor/Claude.

---

## Référence code

- **Module** : `Backend/Prod/core/error_survey.py` — `log_entry()`, `log_aetherflow_error()`, `log_correction()`, `log_anomaly()`, `list_entries()`
- **Config** : `Backend/Prod/config/settings.py` — `error_log_dir`
- **Hooks** : `orchestrator.py` (step failed/exception), `workflows/*` (apply failed, validation failed). Pour d’autres anomalies (build, API, CLI), appeler `log_anomaly()` depuis le code concerné.
