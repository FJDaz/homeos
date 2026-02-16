# 🛡️ Charte de Développement & Supervision AETHERFLOW

Ce document définit les garde-fous pour garantir la robustesse, la sécurité et la maintenabilité du code généré par AETHERFLOW.

## 1. Flux de Travail (Workflow)

* **Test-Driven Development (TDD) :** Toute nouvelle fonctionnalité doit inclure des tests unitaires complets. Pour le code généré :
  - Générer les tests avec le code (dans le même fichier ou fichier séparé selon la taille)
  - Ou créer une étape séparée de génération de tests dans le plan
  - Couverture minimale : 80% pour code critique
  
* **Unité d'Itération :** On itère par **User Story** complète (ex: "API REST avec authentification") et non par fonction isolée.

* **Audit de Session :** Le mode DOUBLE-CHECK valide automatiquement la sécurité et la logique du code généré.

## 2. Architecture & Maintenabilité

* **DRY (Don't Repeat Yourself) :** Toute logique ou bloc de code répété plus de deux fois doit être extrait dans une fonction utilitaire ou un module partagé. Privilégier la factorisation plutôt que le copier-coller.

* **Point de Bascule (Refactoring) :** Dès qu'un fichier dépasse **300 lignes**, le code doit être découpé en modules séparés avec une structure claire.

* **Structure Backend (Python/FastAPI) :**
  - **Models** : Classes de données (Pydantic models, SQLAlchemy models)
  - **Services** : Logique métier (business logic)
  - **Controllers/Routes** : Endpoints API (FastAPI routers)
  - **Utils** : Fonctions utilitaires partagées

* **Principes SOLID :** Priorité à la **Responsabilité Unique**. Une fonction/classe = une tâche.

## 3. Sécurité & Robustesse

* **Variables d'Environnement :** Aucune clé API ou secret dans le code. Utilisation exclusive de fichiers `.env` et de `settings.py` (Pydantic Settings).

* **Validation des Entrées :** Toujours valider les entrées utilisateur avec Pydantic pour les APIs.

* **Gestion des Erreurs :** Utiliser des exceptions appropriées et des codes HTTP corrects (400, 401, 403, 404, 500).

* **Isolation :** Utiliser Docker pour isoler les services et garantir la parité dev/prod.

## 4. Qualité du Code

* **Type Hints :** Toujours utiliser les type hints Python pour améliorer la maintenabilité.

* **Docstrings :** Documenter toutes les fonctions publiques avec des docstrings (format Google ou NumPy).

* **Linter :** Code doit respecter les standards (Ruff/Flake8, Black pour formatage).

* **Tests :** Code généré doit inclure :
  - Tests unitaires pour chaque fonction
  - Tests d'intégration pour les APIs
  - Tests de validation pour les modèles

## 5. Spécificités par Mode d'Exécution

### Mode FAST
* **Objectif :** Vitesse pure, code fonctionnel
* **Guidelines appliquées :** Minimales (vitesse prioritaire)
* **Usage :** Prototypage, scripts, itérations rapides

### Mode BUILD
* **Objectif :** Qualité, maintenance, respect de la charte
* **Guidelines appliquées :** Toutes (TDD, DRY, SOLID, Structure)
* **Usage :** Code de production, refactoring, architecture complexe

### Mode DOUBLE-CHECK
* **Objectif :** Validation sécurité et logique
* **Guidelines appliquées :** Sécurité uniquement
* **Usage :** Audit final avant commit

## 6. Instructions pour Génération de Code

### Code Génération (Mode BUILD)
```
Task: {description}

Guidelines:
- TDD: Generate code with comprehensive unit tests
- DRY: Extract repeated logic into reusable functions/modules
- SOLID: Single Responsibility Principle - one function/class = one task
- Structure: Separate Models (data), Services (business logic), Controllers (API)
- Type Hints: Use Python type hints for all functions
- Docstrings: Document all public functions
- Error Handling: Proper exception handling with appropriate HTTP codes

Generate code following these guidelines.
```

### Refactoring (Mode BUILD)
```
Task: {description}

Guidelines:
- DRY: Factorize repeated code into reusable functions
- SOLID: Ensure single responsibility per function/class
- Structure: Maintain Models/Services/Controllers separation
- Tests: Update or add tests for refactored code

Refactor the code following these guidelines.
```

## 7. Lexique de Supervision

* **Intent :** On code pour répondre à une intention utilisateur (le "quoi"), pas juste pour exécuter une tâche technique (le "comment").

* **Validation :** Le code généré doit respecter les `validation_criteria` définis dans le plan.

* **Maintenabilité :** Le code doit être facile à comprendre et modifier par d'autres développeurs.

---

**Note :** Ces guidelines sont injectées automatiquement dans les prompts du mode BUILD. Le mode FAST génère du code fonctionnel sans ces contraintes pour maximiser la vitesse.
