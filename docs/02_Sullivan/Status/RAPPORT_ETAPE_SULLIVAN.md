# Rapport d'étape Sullivan Kernel

**Date** : 28 janvier 2026  
**Version** : 2.2 "Sullivan"  
**Objectif** : Point de reprise clair pour la suite du développement.

---

## 1. Résumé exécutif

- **Phases 1 à 5** : ✅ Implémentées (analyse backend/design, génération, évaluation, Elite Library, etc.).
- **Genome / Studio / Multimodal** : ✅ En place (génome, builder contract-driven, Visual Auditor Gemini, boucle de refinement).
- **ComponentGenerator PROD parsing** : ✅ **CORRIGÉ** (support `fast_draft/` et `build_refactored/` ajouté).
- **À faire** : GénomeEnricher (bayésien), intégration IntentTranslator/STAR, Phase 6–7 (inférence, prévisualisation).

**Note importante** : Le bug de parsing PROD était latent (non bloquant) car `ComponentRegistry` utilise PROTO par défaut (ligne 131 de `registry.py`). La correction permet maintenant d'utiliser le workflow PROD avec ComponentGenerator.

---

## 2. Ce qui est en place

### 2.1 Phases 1–5 (PRD Sullivan)

| Phase | Statut | Composants principaux | Fichiers |
|-------|--------|------------------------|----------|
| **1 – Analyse Backend** | ✅ | `BackendAnalyzer`, `UIInferenceEngine`, `DevMode` | `sullivan/analyzer/backend_analyzer.py`, `ui_inference_engine.py`, `modes/dev_mode.py` |
| **2 – Analyse Design** | ✅ | `DesignAnalyzer`, `DesignerMode` | `sullivan/analyzer/design_analyzer.py`, `modes/designer_mode.py` |
| **3 – Génération** | ✅ | `ComponentGenerator`, `ComponentRegistry` | `sullivan/generator/component_generator.py`, `registry.py` |
| **4 – Évaluation** | ✅ | `PerformanceEvaluator`, `AccessibilityEvaluator`, `ValidationEvaluator`, `SullivanScore` | `sullivan/evaluators/*.py`, `models/sullivan_score.py` |
| **5 – Avancé** | ✅ | Elite Library, `PatternAnalyzer`, `ContextualRecommender`, `KnowledgeBase` | `sullivan/library/elite_library.py`, `analyzer/pattern_analyzer.py`, `recommender/contextual_recommender.py`, `knowledge/knowledge_base.py` |

### 2.2 Genome & Studio (Contract-Driven, Multimodal)

| Élément | Fichier / Commande | Rôle | État |
|--------|---------------------|------|------|
| **Génome** | `Backend/Prod/core/genome_generator.py` | Introspection OpenAPI → `homeos_genome.json` (metadata, topology, endpoints, schema_definitions, x_ui_hint via heuristiques) | ✅ Fonctionnel |
| **Builder** | `sullivan/builder/sullivan_builder.py` | Lit le genome, mappe x_ui_hint → organes HTML (terminal, gauge, form, dashboard, status, **generic**), CSS brutaliste, Fetch JS | ✅ Fonctionnel (fallback `generic` ligne 92, 140) |
| **Visual Auditor** | `sullivan/auditor/sullivan_auditor.py` | Gemini Vision : audit rendu (Clarté, Feedback, Probité), `SullivanScore` + critiques | ✅ Fonctionnel |
| **Refinement** | `sullivan/refinement.py` | Boucle build → screenshot (Playwright) → audit → révision (Gemini text) jusqu'à score > 85 ou max itérations | ✅ Fonctionnel |
| **CLI genome** | `python -m Backend.Prod.cli genome` | Génère `output/studio/homeos_genome.json` | ✅ Fonctionnel (`cli.py:433-442`) |
| **CLI studio** | `python -m Backend.Prod.cli studio` | genome → build → refinement ; `--no-refine` pour build seul | ✅ Fonctionnel (`cli.py:445-483`) |
| **CLI sullivan read-genome** | `python -m Backend.Prod.cli sullivan read-genome` | Charge le genome et affiche metadata, topology, endpoints (table Rich) | ✅ Fonctionnel (`cli.py:520-540`) |

### 2.3 IntentTranslator & STAR (Ébauche)

| Élément | Fichier | État | Détails |
|---------|---------|------|---------|
| **IntentTranslator** | `sullivan/intent_translator.py` | ⚠️ Ébauche basique | Structure STAR (Situation, Transformation, Abstraction, Réalisation) présente, méthodes stub, score bayésien très basique (comptage mots ligne 87-96) |
| **STAR Mappings** | `sullivan/knowledge/star_mappings.json` | ✅ Présent | 4 patterns : Toggle Visibility, Accordion, Modal, Navigation avec variants, transformations, abstractions, réalisations |
| **Intégration STAR** | - | ❌ Non intégré | IntentTranslator non intégré dans le flux Sullivan (recommandations, inférence) |

### 2.4 API & Frontend

**Endpoints API** (`api.py`) :
- ✅ `POST /execute` : Exécution de plans (PROTO/PROD)
- ✅ `GET /health` : Health check
- ✅ `POST /sullivan/search` : Recherche composant via ComponentRegistry (`api.py:366-413`)
- ✅ `GET /sullivan/components` : Liste composants LocalCache + EliteLibrary (`api.py:416-463`)
- ✅ `POST /sullivan/dev/analyze` : Analyse backend DevMode (`api.py:496-520`)
- ✅ `POST /sullivan/designer/analyze` : Analyse design DesignerMode (`api.py:522+`)

**Frontend** : Chatbox Sullivan (toggle, overlay), communication FastAPI.

### 2.5 ComponentGenerator & Registry

**ComponentGenerator** (`sullivan/generator/component_generator.py`) :
- ✅ Génération composants via AETHERFLOW workflows
- ✅ **CORRIGÉ** : Support workflow PROD (`fast_draft/`, `build_refactored/`) et PROTO (`fast/`, `build/`)
- ✅ Parsing code généré (HTML/CSS/JS) depuis step_outputs
- ✅ Enrichissement contexte via KnowledgeBase

**ComponentRegistry** (`sullivan/registry.py`) :
- ✅ Orchestration LocalCache → EliteLibrary → Génération
- ⚠️ Utilise workflow **PROTO par défaut** (ligne 131) → bug PROD parsing était latent
- ✅ Recommandations contextuelles avant génération
- ✅ Évaluation composants après génération

### 2.6 Références utiles

- **PRD Sullivan** : `docs/02-sullivan/PRD_SULLIVAN.md`
- **Résumé contexte** : `docs/01-getting-started/RESUME_CONTEXTE.md`
- **Outputs Sullivan** : `docs/references/technique/REPERTOIRE_OUTPUTS_SULLIVAN.md`
- **Contrat OpenAPI** : `docs/guides/CONTRAT OpenAPI.md`
- **Stratégie cache** : `docs/support/CACHE/SYNTHESE_CACHE_STRATEGIE.md`

---

## 3. Points connus & à traiter

### 3.1 ComponentGenerator & workflow PROD ✅ CORRIGÉ

**État avant correction** :
- `_parse_generated_code` cherchait uniquement dans `fast/`, `build/`, `validation/`
- Workflow PROD écrit dans `fast_draft/`, `build_refactored/`, `validation/`
- **Impact** : En mode PROD, le parser ne trouvait pas les sorties

**Correction appliquée** (`component_generator.py:268-313`) :
- ✅ Détection du workflow (`self.workflow`)
- ✅ Si `workflow == "PROD"` : cherche dans `fast_draft/step_outputs`, `build_refactored/step_outputs`, `validation/step_outputs`
- ✅ Si `workflow == "PROTO"` : cherche dans `fast/step_outputs`, `build/step_outputs`, `validation/step_outputs` (comportement original conservé)
- ✅ Logs indiquent clairement quel répertoire est utilisé
- ✅ Rétrocompatibilité avec PROTO maintenue

**Note** : Le bug était latent car `ComponentRegistry` utilise PROTO par défaut (ligne 131 de `registry.py`). La correction permet maintenant d'utiliser PROD si nécessaire.

### 3.2 GénomeEnricher (bayésien) — non implémenté

**État** : Non implémenté

**Code actuel** :
- `genome_generator.py` : Génère genome basique avec `x_ui_hint` via heuristiques simples (`_path_to_ui_hint`, lignes 17-32)
- Pas de module `genome_enricher.py`
- Pas d'inférence bayésienne P(Intention | signaux)
- Pas de `x_priority`, `x_flow_position`, `x_dependency`
- Pas de typologie de rendu enrichie (TerminalEmulator, Gauge, StatusBadge, etc.)

**Référence** : Plan d'optimisation cache (`docs/guides/V2.2/cache/OPTIMISATION_CACHE.md`) mentionne GénomeEnricher comme tâche future

**À faire** :
- Module `Backend/Prod/core/genome_enricher.py` avec inférence bayésienne
- Intégration dans `genome_generator` (option `--enrich` / `--no-enrich`)
- Adaptation du builder pour interpréter `x_priority`, `x_flow_position`, `x_dependency`

### 3.3 Phase 6 (PRD) — inférence & STAR

**Inférence générique** :
- Builder utilise encore `generic` comme fallback (`genome_generator.py:32`, `sullivan_builder.py:92, 140`)
- Réduction structures génériques : Non implémentée
- Amélioration inférence depuis backend : À faire

**STAR** :
- ✅ `intent_translator.py` : Ébauche présente avec structure STAR
- ✅ `knowledge/star_mappings.json` : 4 patterns (Toggle Visibility, Accordion, Modal, Navigation)
- ❌ **Intégration dans flux Sullivan** : Non implémentée
  - IntentTranslator non utilisé dans recommandations (`ContextualRecommender`)
  - IntentTranslator non utilisé dans inférence (`UIInferenceEngine`)
  - Score bayésien très basique (comptage mots) → à améliorer avec embeddings

**À faire** :
- Intégrer IntentTranslator dans `ContextualRecommender` pour recommandations basées STAR
- Intégrer IntentTranslator dans `UIInferenceEngine` pour inférence améliorée
- Améliorer score bayésien avec embeddings (sentence-transformers)
- Réduire utilisation de `generic` en améliorant l'inférence depuis le genome

### 3.4 Phase 7 (PRD) — sauvegarde & prévisualisation

**Sauvegarde** :
- ✅ LocalCache : Implémenté (`sullivan/cache/local_cache.py`)
- ✅ Elite Library : Implémenté (`sullivan/library/elite_library.py`)
- ⚠️ Sauvegarde systématique après génération : Partiellement implémentée (via Registry)

**Prévisualisation** :
- ❌ Non implémentée
- À prévoir : Prévisualisation HTML/CSS/JS des composants générés (serveur local, iframe, etc.)

### 3.5 Divers

- **Auditor / Playwright** : `playwright install chromium` si pas déjà fait
- **Cwd / paths** : Genome, studio et CLI supposent l'exécution depuis la racine du projet (ou chemins absolus adaptés)
- **Tests** : Aucun test pour module Sullivan (26 fichiers) → à ajouter

---

## 4. Commandes de reprise

```bash
# Générer le genome
python -m Backend.Prod.cli genome
python -m Backend.Prod.cli genome -o output/custom/genome.json

# Sullivan lit le genome (résumé avec table Rich)
python -m Backend.Prod.cli sullivan read-genome
python -m Backend.Prod.cli sullivan read-genome -g output/studio/homeos_genome.json

# Studio (genome → build → refinement)
python -m Backend.Prod.cli studio
python -m Backend.Prod.cli studio --no-refine   # build seul
python -m Backend.Prod.cli studio --genome output/studio/homeos_genome.json --base-url http://localhost:8000 --max-iterations 3

# Modes Sullivan classiques
python -m Backend.Prod.cli sullivan dev --backend-path /path/to/backend
python -m Backend.Prod.cli sullivan designer --design /path/to/design.png

# API FastAPI (mode serveur)
python -m Backend.Prod.api
# Puis dans un autre terminal :
curl -X POST http://localhost:8000/sullivan/search -d '{"intent": "bouton toggle", "user_id": "test"}'
curl http://localhost:8000/sullivan/components?user_id=test
```

En cas d'erreurs `base64` / `dump_zsh_state` dans le terminal intégré Cursor : utiliser un terminal externe ou appliquer les contournements décrits dans `docs/05-operations/TROUBLESHOOTING_CURSOR_SHELL.md`.

---

## 5. Prochaines actions suggérées

### Priorité 1 : Court terme (1-2 semaines)

1. ✅ **CORRIGÉ** : `ComponentGenerator._parse_generated_code` pour PROD (`fast_draft`, `build_refactored`)
2. **Intégration IntentTranslator** : Intégrer dans `ContextualRecommender` et `UIInferenceEngine` pour améliorer recommandations et inférence
3. **Amélioration score bayésien** : Utiliser embeddings (sentence-transformers) au lieu de comptage mots dans `intent_translator.py:score_mapping()`

### Priorité 2 : Moyen terme (1 mois)

4. **GénomeEnricher** : Concevoir et implémenter le module bayésien, intégration dans `genome_generator`, adaptation builder
5. **Réduction generic_*** : Améliorer inférence depuis backend pour réduire utilisation de `generic` comme fallback
6. **Tests Sullivan** : Ajouter tests unitaires et d'intégration pour les 26 fichiers du module

### Priorité 3 : Long terme (2-3 mois)

7. **Phase 6 complète** : Intégration STAR complète dans flux Sullivan, réduction structures génériques
8. **Phase 7** : Prévisualisation composants générés
9. **Documentation** : Exemples d'utilisation, guide d'intégration IntentTranslator

---

## 6. Annexe technique

### 6.1 Détails d'implémentation

**ComponentGenerator PROD parsing** (`component_generator.py:268-313`) :
- Détection workflow : `self.workflow` (défini dans `__init__`, ligne 44)
- PROD : Cherche dans `fast_draft/step_outputs`, `build_refactored/step_outputs`, `validation/step_outputs`
- PROTO : Cherche dans `fast/step_outputs`, `build/step_outputs`, `validation/step_outputs`
- Logs : `logger.info()` indique le répertoire trouvé

**IntentTranslator** (`intent_translator.py`) :
- Structure STAR : Classes `Situation`, `Transformation`, `Abstraction`, `Realisation`
- Méthodes stub : `parse_query()`, `search_situation()`, `propagate_star()`, `score_mapping()`
- Score bayésien : Très basique (comptage mots dans description, ligne 87-96)
- Intégration : Aucune intégration dans flux Sullivan

**STAR Mappings** (`knowledge/star_mappings.json`) :
- 4 patterns : Toggle Visibility, Accordion, Modal, Navigation
- Chaque pattern contient : `variants`, `transformations`, `abstraction`, `realisation` (template HTML/JS)

**Builder generic fallback** (`sullivan_builder.py`) :
- Ligne 92 : `hint = endpoint.get("x_ui_hint", "generic")`
- Ligne 140 : Fallback HTML avec `data-hint="generic"`
- Fréquence : Utilisé quand `x_ui_hint` n'est pas défini ou ne correspond à aucun hint connu

**Registry workflow** (`registry.py:131`) :
- `workflow="PROTO"` par défaut dans `ComponentGenerator` initialisation
- TODO ligne 127 : "Permettre choix workflow (PROTO vs PROD) selon contexte"

### 6.2 Fichiers modifiés récemment

- ✅ `Backend/Prod/sullivan/generator/component_generator.py` : Correction parsing PROD (28 jan 2026)

### 6.3 Solutions proposées

**GénomeEnricher** :
- Créer `Backend/Prod/core/genome_enricher.py`
- Implémenter inférence bayésienne P(Intention | signaux techniques)
- Typologies : Criticality (`x_priority`), Flow (`x_flow_position`, `x_dependency`), Rendering (`x_component`)
- Intégration : Option `--enrich` dans `genome` CLI

**Intégration IntentTranslator** :
- Modifier `ContextualRecommender` pour utiliser `IntentTranslator.propagate_star()`
- Modifier `UIInferenceEngine` pour utiliser `IntentTranslator.score_mapping()` avec embeddings
- Améliorer `score_mapping()` avec sentence-transformers au lieu de comptage mots

**Réduction generic_*** :
- Améliorer `_path_to_ui_hint()` dans `genome_generator.py` avec plus d'heuristiques
- Utiliser GénomeEnricher pour enrichir `x_ui_hint` avec inférence bayésienne
- Adapter builder pour gérer plus de hints spécifiques

---

**Dernière mise à jour** : 28 janvier 2026  
**Corrections appliquées** : ComponentGenerator PROD parsing ✅
