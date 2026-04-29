# Répertoire des Outputs Sullivan Kernel

**Date de création** : 28 janvier 2026  
**Dernière mise à jour** : 28 janvier 2026

Ce document liste tous les répertoires et fichiers générés par Sullivan Kernel lors de son fonctionnement.

---

## 📁 Structure Générale

Sullivan génère des outputs dans plusieurs emplacements selon le type d'opération :

1. **Outputs temporaires** (génération de composants)
2. **Cache local** (composants utilisateur)
3. **Elite Library** (composants validés)
4. **Résultats d'analyse** (DevMode, DesignerMode)
5. **Plans de génération** (plans JSON temporaires)

---

## 1. Outputs Temporaires de Génération

### Emplacement
```
/tmp/sullivan_outputs/{plan_id}/
```

### Structure
```
/tmp/sullivan_outputs/
├── component_{uuid}/
│   ├── fast/
│   │   └── step_outputs/
│   │       ├── step_html.txt
│   │       ├── step_css.txt
│   │       └── step_js.txt
│   ├── build/
│   │   └── step_outputs/
│   │       ├── step_html.txt
│   │       ├── step_css.txt
│   │       └── step_js.txt
│   └── validation/
│       └── step_outputs/
│           ├── step_html.txt
│           ├── step_css.txt
│           └── step_js.txt
```

### Description
- **Généré par** : `ComponentGenerator._execute_plan()`
- **Contenu** : Code HTML/CSS/JS généré via AETHERFLOW workflows
- **Durée de vie** : Temporaire (peut être nettoyé par le système)
- **Utilisation** : Parsing du code généré pour créer des `Component` objets

### Code Source
```python
# Backend/Prod/sullivan/generator/component_generator.py:226
output_dir = Path(tempfile.gettempdir()) / "sullivan_outputs" / plan_path.stem
```

---

## 2. Plans de Génération Temporaires

### Emplacement
```
/tmp/sullivan_plans/
```

### Structure
```
/tmp/sullivan_plans/
├── component_{uuid}.json
├── component_{uuid}.json
└── ...
```

### Description
- **Généré par** : `ComponentGenerator._create_generation_plan()`
- **Contenu** : Plans JSON pour génération de composants (HTML, CSS, JS)
- **Format** : Plan JSON conforme au schéma AETHERFLOW
- **Durée de vie** : Temporaire

### Exemple de Plan
```json
{
  "task_id": "uuid-v4",
  "description": "Générer composant frontend pour: {intent}",
  "steps": [
    {
      "id": "step_html",
      "description": "Générer code HTML...",
      "type": "code_generation",
      "complexity": 0.5,
      "estimated_tokens": 2000,
      "dependencies": [],
      "validation_criteria": [...],
      "context": {
        "language": "html",
        "framework": "vanilla",
        "files": ["component.html"]
      }
    },
    ...
  ],
  "metadata": {...}
}
```

### Code Source
```python
# Backend/Prod/sullivan/generator/component_generator.py:203
temp_dir = Path(tempfile.gettempdir()) / "sullivan_plans"
plan_path = temp_dir / f"component_{task_id}.json"
```

---

## 3. Cache Local (Composants Utilisateur)

### Emplacement
```
~/.aetherflow/components/{user_id}/
```

### Structure
```
~/.aetherflow/components/
├── user_1/
│   ├── component_bouton_connexion.json
│   ├── component_formulaire_contact.json
│   └── ...
├── user_2/
│   └── ...
└── ...
```

### Description
- **Généré par** : `LocalCache.save()`
- **Contenu** : Composants JSON sauvegardés par utilisateur
- **Format** : Fichiers JSON avec métadonnées `Component`
- **Durée de vie** : Permanent (jusqu'à suppression manuelle)
- **Utilisation** : Cache rapide pour éviter régénération

### Format de Fichier
```json
{
  "name": "component_bouton_connexion",
  "sullivan_score": 75.0,
  "performance_score": 80,
  "accessibility_score": 70,
  "ecology_score": 75,
  "popularity_score": 0,
  "validation_score": 80,
  "size_kb": 10,
  "created_at": "2026-01-28T00:00:00",
  "user_id": "user_1",
  "category": "core",
  "last_used": "2026-01-28T00:00:00"
}
```

### Code Source
```python
# Backend/Prod/sullivan/cache/local_cache.py:256
user_cache_dir = self.cache_dir / user_id
component_file = user_cache_dir / f"{component.name}.json"
```

---

## 4. Elite Library (Composants Validés)

### Emplacement
```
components/elite/
```

### Structure
```
components/elite/
├── component_excellent_1.json
├── component_excellent_2.json
├── archived/
│   ├── archived_component_old_1.json
│   └── ...
└── ...
```

### Description
- **Généré par** : `EliteLibrary.add()`
- **Contenu** : Composants avec score Sullivan >= 85
- **Format** : Fichiers JSON identiques au cache local
- **Durée de vie** : Permanent avec archivage automatique
- **Archivage** : Composants non utilisés depuis > 6 mois → `archived/`
- **Retrait** : Composants avec score < 85 → Suppression

### Critères d'Entrée
- Score Sullivan >= `ELITE_THRESHOLD` (85)
- Validation réussie
- Catégorisation automatique (core/complex/domain)

### Code Source
```python
# Backend/Prod/sullivan/library/elite_library.py:25
def __init__(self, path: Path = Path("components/elite/")):
    self.path = path
    self.archive_path = self.path / "archived"
```

---

## 5. Outputs DevMode (Analyse Backend)

### Emplacement
```
output/{custom_path}/sullivan_result.json
```

### Structure
```
output/
├── homeos_frontend/
│   └── sullivan_result.json
├── phase2_sullivan_quick/
│   └── sullivan_result.json
└── ...
```

### Description
- **Généré par** : `DevMode.run()`
- **Contenu** : Résultats d'analyse backend et inférence frontend
- **Format** : JSON avec fonction globale, structure d'intention, structure frontend

### Format de Fichier
```json
{
  "global_function": {
    "product_type": "web-application",
    "actors": ["user"],
    "business_flows": ["CRUD", "Search"],
    "use_cases": ["General usage"]
  },
  "intention_structure": {
    "product_type": "web-application",
    "actors": ["user"],
    "proposed_steps": ["Étape 1", "Étape 2", "Étape 3"],
    "patterns": [],
    "requires_confirmation": true
  },
  "frontend_structure": {
    "Étape 1": {
      "content_zone": {
        "generic_organe": {
          "generic_molecule": [...]
        }
      }
    },
    ...
  }
}
```

### Code Source
```python
# Backend/Prod/sullivan/modes/dev_mode.py:131
if self.output_path:
    self.output_path.mkdir(parents=True, exist_ok=True)
    result_file = self.output_path / "sullivan_result.json"
```

---

## 6. Outputs DesignerMode (Analyse Design)

### Emplacement
```
output/{custom_path}/sullivan_designer_result.json
```

### Structure
```
output/
└── {custom_path}/
    └── sullivan_designer_result.json
```

### Description
- **Généré par** : `DesignerMode.run()`
- **Contenu** : Résultats d'analyse de design PNG et mapping sur structure logique
- **Format** : JSON avec structure design, patterns matchés, structure frontend

### Code Source
```python
# Backend/Prod/sullivan/modes/designer_mode.py:120
if self.output_path:
    self.output_path.mkdir(parents=True, exist_ok=True)
    result_file = self.output_path / "sullivan_designer_result.json"
```

---

## 7. Outputs Validation Evaluator

### Emplacement
```
/tmp/sullivan_validation_outputs/{plan_id}/
```

### Description
- **Généré par** : `ValidationEvaluator.evaluate()`
- **Contenu** : Résultats de validation TDD/DRY/SOLID via AETHERFLOW DOUBLE-CHECK
- **Format** : Outputs AETHERFLOW standard

### Code Source
```python
# Backend/Prod/sullivan/evaluators/validation_evaluator.py:154
output_dir = Path(tempfile.gettempdir()) / "sullivan_validation_outputs" / plan_path.stem
```

---

## 📊 Résumé des Emplacements

| Type | Emplacement | Durée | Généré par |
|------|-------------|-------|------------|
| **Outputs génération** | `/tmp/sullivan_outputs/` | Temporaire | `ComponentGenerator` |
| **Plans génération** | `/tmp/sullivan_plans/` | Temporaire | `ComponentGenerator` |
| **Cache local** | `~/.aetherflow/components/` | Permanent | `LocalCache` |
| **Elite Library** | `components/elite/` | Permanent | `EliteLibrary` |
| **Résultats DevMode** | `output/{path}/sullivan_result.json` | Permanent | `DevMode` |
| **Résultats DesignerMode** | `output/{path}/sullivan_designer_result.json` | Permanent | `DesignerMode` |
| **Outputs validation** | `/tmp/sullivan_validation_outputs/` | Temporaire | `ValidationEvaluator` |
| **Plans JSON (sources)** | `Backend/Notebooks/benchmark_tasks/sullivan_*.json` | Permanent | Plans d'implémentation |

## 📂 Répertoires Réels Trouvés dans le Projet

### Outputs d'Analyse (output/)
```
output/
├── homeos_frontend/
│   └── sullivan_result.json
├── phase2_sullivan_quick/
├── sullivan_phase1/
├── sullivan_phase1_retry/
├── sullivan_phase2/
├── sullivan_phase3/
├── sullivan_phase4/
├── sullivan_phase5/
├── phase2_sullivan_fast/
├── phase2_sullivan_v2/
├── phase2_sullivan_test/
├── phase2_sullivan_clean/
├── phase2_sullivan_full/
└── ...
```

### Plans JSON Sources (Backend/Notebooks/benchmark_tasks/)
```
Backend/Notebooks/benchmark_tasks/
├── sullivan_phase1_dev_mode.json
├── sullivan_phase2_designer_mode.json
├── sullivan_phase3_generator.json
├── sullivan_phase4_scoring.json
├── sullivan_phase5_features.json
├── phase2_sullivan_fast.json
├── phase2_sullivan_fast_v2.json
└── ...
```

---

## 🔍 Commandes Utiles

### Lister tous les outputs Sullivan
```bash
# Outputs temporaires
find /tmp -type d -name "*sullivan*" 2>/dev/null

# Cache local
find ~/.aetherflow -type f 2>/dev/null | grep components

# Elite Library
find components/elite -type f 2>/dev/null

# Résultats d'analyse
find output -name "*sullivan*.json" 2>/dev/null
```

### Compter les composants
```bash
# Cache local
find ~/.aetherflow/components -name "*.json" | wc -l

# Elite Library
find components/elite -name "*.json" ! -path "*/archived/*" | wc -l

# Archivés
find components/elite/archived -name "*.json" | wc -l
```

### Nettoyer les outputs temporaires
```bash
# Supprimer tous les outputs temporaires
rm -rf /tmp/sullivan_outputs/*
rm -rf /tmp/sullivan_plans/*
rm -rf /tmp/sullivan_validation_outputs/*
```

---

## 📝 Notes Importantes

1. **Outputs temporaires** : Les fichiers dans `/tmp/` peuvent être supprimés par le système. Ne pas s'y fier pour du stockage permanent.

2. **Cache local** : Stockage par utilisateur. Chaque utilisateur a son propre répertoire `~/.aetherflow/components/{user_id}/`.

3. **Elite Library** : Composants partagés entre tous les utilisateurs. Archivage automatique après 6 mois d'inactivité.

4. **Résultats d'analyse** : Sauvegardés dans `output/` avec chemin personnalisable. Format JSON standardisé.

5. **Plans JSON** : Générés automatiquement par `ComponentGenerator`. Format conforme au schéma AETHERFLOW.

---

## 🔄 Workflow Complet

```
1. ComponentGenerator._create_generation_plan()
   → /tmp/sullivan_plans/component_{uuid}.json

2. ComponentGenerator._execute_plan()
   → /tmp/sullivan_outputs/{plan_id}/fast|build/step_outputs/

3. ComponentGenerator._parse_generated_code()
   → Parse HTML/CSS/JS depuis step_outputs

4. ComponentGenerator._structure_component()
   → Crée objet Component

5. ComponentRegistry._evaluate_component()
   → Évalue scores (Performance, Accessibilité, etc.)

6. LocalCache.save()
   → ~/.aetherflow/components/{user_id}/{name}.json

7. (Si score >= 85) EliteLibrary.add()
   → components/elite/{name}.json
```

---

**Document créé automatiquement par Sullivan Kernel**  
**Pour questions ou mises à jour, voir** `Backend/Prod/sullivan/`
