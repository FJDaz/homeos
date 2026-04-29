# Résumé de contexte — AETHERFLOW, Studio, Phase 3 A (gros, détaillé)

*Document généré pour reprendre le fil après une longue session. Dernière mise à jour : 2026-02-01.*

---

## 1. Vue d’ensemble du projet

- **AETHERFLOW** : orchestrateur d’agents IA (Claude Code dans Cursor = architecte/orchestrateur ; DeepSeek API = exécuteur ; Claude API = validateur). Utilisé **uniquement pour l’implémentation** (génération de code), pas pour la vérification/review.
- **Homeos** : plateforme “PaaS Studio” (Brainstorm | Back | Front | Deploy). Genome = représentation structurée de l’API (`output/studio/homeos_genome.json`), généré à partir de l’OpenAPI.
- **Sullivan** : moteur d’intelligence frontend (DevMode, DesignerMode, ScreenPlanner, CorpsGenerator, Chatbot). S’appuie sur le genome pour l’inférence UI.
- **Studio** : interface de “filage” en trois colonnes — **Revue (inventaire IR)** | **Arbitrage (validation)** | **Distillation (génome)** — pour valider manuellement les éléments du genome avant de les figer.

---

## 2. Workflows AETHERFLOW (-q vs -f)

| Mode | Commande | Phases | Répertoire utilisé pour l’apply |
|------|----------|--------|----------------------------------|
| **PROTO (-q)** | `./run_aetherflow.sh -q --plan <plan.json>` | FAST (Groq) → Apply → DOUBLE-CHECK (Gemini) | `output_dir/fast` |
| **PROD (-f)**  | `./run_aetherflow.sh -f --plan <plan.json>` | FAST (brouillon) → BUILD (refacto) → Apply → DOUBLE-CHECK | `output_dir/build_refactored` |

- **Apply** : même fonction `apply_generated_code()` (dans `Backend/Prod/claude_helper.py`) pour les deux modes. La seule différence est **la source des step outputs** : en -q on applique le sorti **FAST** ; en -f on applique le sorti **BUILD** (refactoré).
- **Comportement d’écrasement** : pour un fichier cible (ex. `.html`) :
  - Si le step est en **`code_generation`** : le **premier bloc de code** du step output **remplace tout le fichier**. Si le LLM ne génère qu’un fragment (ex. un formulaire seul), toute la page est écrasée par ce fragment — en -q **et** en -f.
  - Si le step est en **`refactoring`** : l’apply **n’écrase pas** ; il écrit dans un fichier séparé (ex. `studio.generated.html`) pour merge manuel.
- **Convention établie** : rapports **IR (inventaire)** → exécution en **-f** (PROD) ; rapports **Arbitrage** → exécution en **-q** (PROTO).

---

## 3. Phase 3 A — Inventaire IR et Arbitrage (état actuel)

### 3.1 Inventaire IR (Étape 1)

- **Plan** : `Backend/Notebooks/benchmark_tasks/plan_phase3a_etape1_chunked.json` (5 steps, output fusionné en un seul fichier).
- **Exécution** : `aetherflow -f` (PROD).
- **Sortie** : `output/studio/ir_inventaire.md` — inventaire détaillé à partir de `output/studio/homeos_genome.json` et `docs/04-homeos/PRD_HOMEOS.md`.
- **Contenu typique** : §1.1 Métadonnées, §1.2 Topologie déclarée (Brainstorm, Back, Front, Deploy), §1.3 Endpoints (tableau méthode/path/x_ui_hint/résumé), §1.4 Clés IR (à remplir après arbitrage), puis description de ce qu’Aetherflow fait, CLI, etc.
- **Fusion des steps** : la logique `output_merge` dans les workflows proto/prod fusionne les sorties des steps listés dans le plan en un seul fichier (ex. `ir_inventaire.md`).

### 3.2 Arbitrage Sullivan (Étape 2)

- **Plan** : `Backend/Notebooks/benchmark_tasks/plan_phase3a_etape2_arbitrage.json` (enrichi pour couvrir genome, modes, workflows, outils CLI).
- **Exécution** : `aetherflow -q` (convention arbitrage en PROTO).
- **Sorties** : `output/studio/arbitrage_phase3a_etape2_aetherflow_q.md`, `arbitrage_phase3a_etape2_aetherflow_f.md`, et version manuelle de référence si besoin.

### 3.3 Interface de validation (Étape 3)

- **Rapport Markdown** : plan `plan_phase3a_etape3_interface_validation.json` → exécution en -q → `output/studio/validation_phase3a_etape3.md` (résumé des points d’arbitrage pour amendements).
- **Option A — Studio HTMX** : plan `plan_phase3a_studio_interface_option_a.json` pour une interface web de validation (triptyque Revue | Arbitrage | Distillation).

---

## 4. Implémentation Studio HTMX (Backend + template)

### 4.1 Backend (`Backend/Prod/api.py`)

- **Routes rapport / genome** :
  - `GET /studio/reports/ir` → contenu de `output/studio/ir_inventaire.md` en fragment HTML (prose).
  - `GET /studio/reports/arbitrage` → rapport arbitrage en fragment HTML.
  - `GET /studio/reports/validation` → rapport validation en fragment HTML.
  - `GET /studio/genome/summary` → résumé du genome (HTML).
- **Validation / distillation** :
  - `POST /studio/validate` : enregistre une entrée de validation (section_id, section_title, verdict, items cochés) dans `output/studio/distillation_entries.json`.
  - `GET /studio/distillation/entries` : renvoie les entrées validées (affichées dans la colonne Distillation).
- **Studio** : `GET /studio/` sert `Backend/Prod/templates/studio.html` (ou redirige vers `/studio.html` si Frontend présent).

### 4.2 Template `Backend/Prod/templates/studio.html`

- **Stack** : HTML, Tailwind (CDN), HTMX (cdn 1.9.10).
- **Layout** : grille 3 colonnes (responsive 1 col mobile, 3 col desktop).
- **Colonne 1 — Revue** : chargement du rapport IR via `hx-get="/studio/reports/ir"` au load.
- **Colonne 2 — Arbitrage** :
  - Formulaire **1.2 Topologie déclarée** : checkboxes (Brainstorm, Back, Front, Deploy), hidden `section_id=1.2`, `section_title=Topologie déclarée`, `verdict=Garder` ; submit → `POST /studio/validate`, target `#distillation-entries`, swap `beforeend`.
  - Formulaire **1.3 Endpoints** : une checkbox par endpoint (POST /execute, GET /health, GET /studio/genome, …), hidden `section_id=1.3`, `section_title=Endpoints`, `verdict=Garder` ; même mécanisme de submit.
  - Bloc chargement rapport arbitrage complet : `hx-get="/studio/reports/arbitrage"`.
  - Lien vers `/studio/genome`.
- **Colonne 3 — Distillation** :
  - `#distillation-entries` : chargé au load via `hx-get="/studio/distillation/entries"`, et mis à jour par les submits des formulaires (beforeend).
  - Résumé genome : `hx-get="/studio/genome/summary"`.
  - Lien “Voir le genome”.

### 4.3 Problème rencontré avec l’apply AETHERFLOW sur `studio.html`

- Lors de l’ajout du formulaire **1.3 Endpoints** via un plan AETHERFLOW (`plan_studio_arbitrage_1_3_endpoints.json`) exécuté en -q, le step a généré **uniquement le fragment** (le formulaire). Comme le step était en `code_generation`, `apply_generated_code` a **remplacé tout le contenu de `studio.html`** par ce fragment.
- **Correction** : restauration manuelle du `studio.html` complet (structure + formulaires 1.2 et 1.3), puis insertion manuelle du formulaire 1.3 à sa place.
- **Leçon** : pour des modifications **partielles** d’un fichier existant, soit mettre le step en **`refactoring`** (apply écrit dans un `.generated.html` pour merge manuel), soit exiger dans le plan/prompt que le LLM produise **tout le fichier** (page complète), pas seulement le fragment.

---

## 5. Fichiers et chemins clés

| Rôle | Chemin |
|------|--------|
| Genome | `output/studio/homeos_genome.json` |
| Inventaire IR | `output/studio/ir_inventaire.md` |
| Rapports arbitrage | `output/studio/arbitrage_phase3a_etape2_*.md` |
| Rapport validation | `output/studio/validation_phase3a_etape3.md` |
| Entrées distillation (validations) | `output/studio/distillation_entries.json` |
| Template Studio | `Backend/Prod/templates/studio.html` |
| API (routes studio) | `Backend/Prod/api.py` |
| Apply (écriture fichiers) | `Backend/Prod/claude_helper.py` → `apply_generated_code()` |
| Workflows | `Backend/Prod/workflows/proto.py` (-q), `Backend/Prod/workflows/prod.py` (-f) |
| Plans Phase 3 A | `Backend/Notebooks/benchmark_tasks/plan_phase3a_*.json`, `plan_studio_arbitrage_1_3_endpoints.json` |

---

## 6. Corrections / améliorations déjà apportées (rappel)

1. **`project_root`** : calcul corrigé dans l’orchestrator pour que le genome et le PRD soient bien trouvés par le LLM.
2. **`input_files`** : schéma du plan et orchestrator étendus pour injecter des fichiers en lecture seule dans le prompt (contexte renforcé).
3. **Markdown** : dans `claude_helper`, pour les cibles `.md`, suppression automatique des fences externes (````markdown ... ````) pour éviter le double encadrement.
4. **IR chunké** : plan en 5 steps avec `output_merge` pour produire un seul `ir_inventaire.md` sans dépasser les limites de tokens.
5. **Studio** : routes API + template HTMX avec formulaires 1.2 et 1.3 et stockage des validations en JSON.

---

## 7. Suite possible

- Valider les éléments IR via l’interface Studio (cocher Topologie, Endpoints, etc.) et consulter la colonne Distillation.
- Enchaîner sur d’autres sections de l’IR (ex. §1.4 Clés IR, modes, workflows) : soit nouveaux formulaires HTMX (en les ajoutant manuellement ou en plan avec step **refactoring** / prompt “fichier complet” pour éviter l’écrasement).
- Phase 3b (spec dans `docs/04-homeos/PHASE3_SPEC_FILAGE.md`) : implémentation du filage complet (lots atomes, organe Chat, glaçage du genome).
- Plan global : `.cursor/plans/studio_concret_puis_doc.plan.md` (Phases A consolidation/doc, B Studio concret, C HCI Intent Refactoring).

---

*Fin du résumé de contexte.*
