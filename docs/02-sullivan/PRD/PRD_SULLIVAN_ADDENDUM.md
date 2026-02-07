# Addendum au PRD Sullivan Kernel

**Référence** : PRD Sullivan Kernel (28 janvier 2026)  
**Date addendum** : 30 janvier 2026  
**Version** : 2.2 "Sullivan"  
**Objet** : Ajouts récents — pipeline « template → écrans câblés », Genome, Studio, Chatbot

---

## Contexte

Le PRD Sullivan du 28 janvier 2026 décrit les **phases 1 à 5** au sens « analyse → génération composants → évaluation → avancé » (BackendAnalyzer, DesignAnalyzer, ComponentGenerator, Evaluators, Elite Library, etc.).  

Le présent addendum documente les **ajouts récents** qui mettent en place le **workflow idéal Sullivan** : **template (image) → HTML → principes graphiques → genome → plan d’écrans → corps (HTML) → chatbot** pour l’affinage par écran. Ces ajouts s’appuient sur le Genome (OpenAPI → `homeos_genome.json`) et le Studio (page d’accueil, organes, API).

---

## 1. Nouveau pipeline « template → écrans câblés »

### 1.1 Chaîne fonctionnelle

| Étape | Entrée | Sortie | Composant principal |
|-------|--------|--------|----------------------|
| 1 | Image (template) | HTML single-file | DesignerMode + design_to_html |
| 2 | Image + structure design | design_principles.json | DesignPrinciplesExtractor |
| 3 | Genome (homeos_genome.json) | screen_plan.json | ScreenPlanner |
| 4 | screen_plan + design_principles | studio_corps.html | CorpsGenerator |
| 5 | Corps 1 + plan | Organes + Chatbot (z-index 10) | Sullivan Chatbot + API |

### 1.2 Référence webdesign

Les tendances utilisées pour interpréter les templates sont décrites dans **`docs/02-sullivan/Références webdesign de Sullivan.md`** (Gumroad, Linear, Tally, Vercel, iA.net, Family, Stripe, Berkshire Hathaway). Le module **design_to_html** charge cette webographie et l’injecte dans le contexte du générateur (Gemini).

---

## 2. Nouveaux composants Sullivan

### 2.1 Template → HTML (Phase 1 pipeline Studio)

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **DesignToHtml** | `sullivan/generator/design_to_html.py` | À partir d’une image (template) et de la structure design, génère un document HTML/CSS/JS single-file (autoconstruction, sans squelette genome). Utilise la webographie Sullivan. |
| **DesignerMode** (extension) | `sullivan/modes/designer_mode.py` | Options `output_html`, `output_html_path` ; option `extract_principles`, `principles_path`. Appel à design_to_html et DesignPrinciplesExtractor selon les flags. |

**Sortie** : `output/studio/studio_index.html` (ou chemin configurable).

### 2.2 Principes graphiques (Phase 2 pipeline Studio)

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **DesignPrinciplesExtractor** | `sullivan/analyzer/design_principles_extractor.py` | À partir d’une image (template), extrait via Gemini Vision les principes graphiques (couleurs, typo, espacements, border_radius, etc.) et les renvoie en JSON. Méthode `save_principles` pour persister en fichier. |

**Sortie** : `output/studio/design_principles.json` (ou chemin configurable).

### 2.3 Plan d’écrans (Phase 3 pipeline Studio)

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **ScreenPlanner** | `sullivan/planner/screen_planner.py` | À partir du genome (`homeos_genome.json`), produit une liste de **corps** (écrans). Chaque corps a un id, un label, une liste d’**organes** (blocs fonctionnels liés aux endpoints) et les endpoints associés. Fonction `plan_screens(genome_path, output_path)`. Helper `generate_corps_html` pour générer du HTML à partir du plan + principes (utilisé en aval). |
| **Planner** | `sullivan/planner/__init__.py` | Export de `plan_screens` et des helpers de chargement. |

**Sortie** : `output/studio/screen_plan.json` (liste de corps avec organes et endpoints).

### 2.4 Génération des corps (Phase 4 pipeline Studio)

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **CorpsGenerator** | `sullivan/builder/corps_generator.py` | Charge `screen_plan.json` et optionnellement `design_principles.json` ; génère un HTML single-file (sections par corps, placeholders par organe, styles dérivés des principes). Écrit `studio_corps.html`. |
| **corps1_chatbot_page** | `sullivan/builder/corps1_chatbot_page.py` | Génération de la page « Corps 1 + chatbot » : section corps 1 (organes issus du plan), widget chatbot en overlay (z-index 10). Utilisée pour l’endpoint `/sullivan/corps/{corps_id}` et la page `studio_corps1_chatbot.html`. |

**Sorties** : `output/studio/studio_corps.html`, `output/studio/studio_corps1_chatbot.html` (et variantes par corps si exposées).

### 2.5 Chatbot Sullivan (Phase 5 pipeline Studio)

| Composant | Fichier | Description |
|-----------|---------|-------------|
| **Sullivan Chatbot** | `sullivan/chatbot/sullivan_chatbot.py` | `get_organes_for_corps(corps_id, screen_plan_path)` : lit le screen_plan et renvoie la liste des organes du corps demandé. `chat(user_message, context)` : dialogue d’affinage UI (prompt Sullivan + Gemini). Pas de code dupliqué ; imports corrects (pathlib.Path, `...models.gemini_client`). |
| **chatbot/__init__.py** | `sullivan/chatbot/__init__.py` | Ré-export de `get_organes_for_corps` et `chat` uniquement (pas de code collé). |

**API** :  
- `GET /sullivan/corps/{corps_id}/organes` → liste des organes du corps (depuis screen_plan.json).  
- `POST /sullivan/chatbot` → envoi d’un message et du contexte ; réponse du chatbot (Gemini).

---

## 3. CLI — Nouvelles commandes et options

### 3.1 Sullivan

| Commande / option | Description |
|-------------------|-------------|
| `sullivan plan-screens --genome <path> --output <path>` | Génère `screen_plan.json` à partir du genome. Défauts : genome = `output/studio/homeos_genome.json`, output = `output/studio/screen_plan.json`. |
| `sullivan designer --design <image>` | DesignerMode (analyse design). |
| `sullivan designer --extract-principles --principles-path <path>` | Lance l’extraction des principes graphiques et sauvegarde dans le fichier indiqué (défaut : `output/studio/design_principles.json`). |
| `sullivan designer` avec `--output-html` / `output_html_path` | Génère `studio_index.html` à partir du design (design_to_html). |
| `sullivan build` | Build genome → studio_index.html (SullivanBuilder + optionnel refinement). |
| `sullivan read-genome` | Affiche le genome (metadata, topology, endpoints). |

### 3.2 Genome

- `genome` (ou équivalent CLI) : génération de `homeos_genome.json` à partir de l’OpenAPI de l’API (voir `Backend/Prod/core/genome_generator.py`).

---

## 4. API — Nouveaux endpoints (côté projet)

Ces endpoints sont exposés par l’API FastAPI du projet ; ils concernent directement l’usage de Sullivan et du Studio.

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/studio/genome` | Sert le genome (`output/studio/homeos_genome.json`). Si absent, peut déclencher la génération à la volée. |
| GET | `/sullivan/corps/{corps_id}/organes` | Liste des organes du corps `corps_id` (lecture de `output/studio/screen_plan.json`). |
| POST | `/sullivan/chatbot` | Message utilisateur + contexte → réponse du chatbot Sullivan (Gemini). |

**Dépendances côté API** :  
- Import correct depuis `Backend.Prod.sullivan.chatbot.sullivan_chatbot` (`get_organes_for_corps`, `chat`).  
- Route `GET /` enregistrée de façon robuste (fallbacks : studio_index.html, Svelte, Frontend) pour servir le Studio.

---

## 5. Sorties Studio (répertoire `output/studio/`)

| Fichier / répertoire | Rôle |
|----------------------|------|
| `homeos_genome.json` | Genome (metadata, topology, endpoints, schémas). |
| `screen_plan.json` | Plan d’écrans (liste de corps avec organes et endpoints). |
| `design_principles.json` | Principes graphiques extraits du template (optionnel). |
| `studio_index.html` | Page d’accueil Studio (organes, pipeline Brainstorm/Back/Front/Deploy). Peut être générée depuis le design (design_to_html) ou depuis le genome (build). |
| `studio_corps.html` | HTML des corps (sections, placeholders organes) généré par CorpsGenerator. |
| `studio_corps1_chatbot.html` | Page Corps 1 + widget chatbot (z-index 10). |
| `static/` | Répertoire pour assets statiques (CSS, etc.) monté sous `/static` par l’API. |

---

## 6. Corrections et nettoyages effectués (alignement avec l’addendum)

Les points suivants ont été corrigés ou nettoyés pour que le pipeline et l’API fonctionnent de façon cohérente avec la description ci‑dessus :

- **knowledge_base.py** : Suppression du code dupliqué (imports `agent_router`, `task`, `vision_model` et classe DesignAnalyzer collée). Le fichier ne contient plus que la classe `KnowledgeBase`.
- **api.py** : Import des fonctions Sullivan chatbot depuis `.sullivan.chatbot.sullivan_chatbot` ; pas de second `app = FastAPI()` ; route `GET /` toujours enregistrée avec fallbacks (studio_index, Svelte, Frontend) pour éviter 404.
- **sullivan_chatbot.py** : `Path` depuis `pathlib`, `GeminiClient` depuis `...models.gemini_client` ; suppression du code dupliqué en fin de fichier (snippets api.py / corps1_chatbot_page, etc.).
- **sullivan/chatbot/__init__.py** : Contenu limité au ré-export de `get_organes_for_corps` et `chat` (suppression du code collé et de l’import `pydantic.Path` invalide).
- **API** : Démarrage possible sur `0.0.0.0:8000` pour exposition réseau ; création de `output/studio/static` si nécessaire pour le mount `/static`.

---

## 7. Références croisées

- **Workflow idéal Sullivan** : `docs/02-sullivan/SULLIVAN_WORKFLOW_IDEAL.md`
- **Mode d’emploi Genome / Chatbot** : `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md`
- **Références webdesign** : `docs/02-sullivan/Références webdesign de Sullivan.md`
- **PRD HOMEOS** : `docs/04-homeos/PRD_HOMEOS.md` (vision produit, Genome, Studio, roadmap)
- **Répertoire outputs** : `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md`

---

**Addendum au PRD Sullivan Kernel**  
**Dernière mise à jour** : 30 janvier 2026  
**Version** : 2.2 "Sullivan"
