### Rapport d'Analyse et de Correction pour l'Orchestrateur Aetherflow

#### **Synthèse des Problèmes Identifiés**

L'analyse du comportement de l'orchestrateur via l'exécution du plan `plan_test_api_stenciler.json` a révélé deux problèmes majeurs qui affectent sa fiabilité et son bon fonctionnement :

1.  **Conflit de Concurrence (Race Condition) :** L'orchestrateur tente d'exécuter en parallèle des étapes qui modifient le même fichier, ce qui conduit à la corruption des données.
2.  **Activation Incorrecte du "Surgical Mode" :** Le mode d'édition de code précis ("Surgical") est activé à tort dans le workflow rapide (`-q`), ce qui va à l'encontre de sa conception.

---

#### **Problème 1 : Conflit d'Exécution en Mode Parallèle**

**Description :**
Lors de l'exécution, l'orchestrateur a regroupé les 3 étapes du plan de test dans un seul lot et les a lancées en parallèle.
```
21:38:00 | INFO | Execution order: 1 batches
21:38:00 | INFO | Executing 3 steps in parallel
```
Cependant, chaque étape est conçue pour modifier le fichier `tests/test_api_manual.py`, un fichier Python existant. En s'exécutant simultanément, chaque étape a lu la version *initiale* du fichier, a généré son code, puis l'a écrit. La conséquence est que seule la dernière écriture est conservée dans sa totalité, écrasant ou entrant en conflit avec les modifications des autres.

**Impact :**
-   **Fichiers de sortie corrompus** et incohérents.
-   Résultats imprévisibles et non déterministes.
-   Perte du travail effectué par les étapes qui se font "écraser".

**Piste de Réparation :**
Il faut rendre l'orchestrateur capable de détecter ces conflits et de s'adapter.

-   **Action :** Modifier la méthode `_execute_batch_parallel` dans `Backend/Prod/orchestrator.py`.
-   **Logique à implémenter :**
    1.  Avant de lancer l'exécution parallèle d'un lot, collecter tous les chemins de fichiers cibles pour chaque étape du lot (via `step.context.get("files", [])`).
    2.  Vérifier s'il existe des doublons dans la liste de ces chemins.
    3.  Si un conflit est détecté (un même fichier est ciblé par plusieurs étapes), **forcer l'exécution séquentielle pour l'intégralité de ce lot**.
    4.  Ajouter un log (`logger.warning`) pour notifier l'utilisateur que le mode séquentiel a été forcé en raison d'un conflit.

**Avantage :** Cette correction assure l'intégrité des fichiers sans nécessiter de modification manuelle des plans d'exécution (en ajoutant des dépendances). L'orchestrateur devient plus intelligent et robuste.

---

#### **Problème 2 : Activation Incorrecte du "Surgical Mode"**

**Description :**
Pendant l'exécution en mode rapide (`-q`, alias "PROTO"), les logs ont montré que le "Surgical Mode" était activé.
```
21:38:00 | INFO | Surgical mode: True (execution_mode=FAST, ...)
```
Le "Surgical Mode" est une fonctionnalité avancée et coûteuse en ressources, conçue pour la réécriture précise du code via la manipulation de l'AST (Abstract Syntax Tree) en mode production (`-f`, alias "BUILD" ou "DOUBLE-CHECK"). Il ne devrait pas être activé par défaut en mode `FAST` (`-q`), qui privilégie la vitesse et la légèreté. La condition d'activation actuelle dans la méthode `_execute_step` semble trop permissive, en raison d'un défaut dans l'expression logique.

**Impact :**
-   Ralentissement inutile du mode rapide.
-   Potentiel d'erreurs inattendues ou de comportement non souhaité si l'analyse AST du fichier échoue (comme observé avec `Syntax error in /Users/francois-jeandazin/AETHERFLOW/tests/test_api_manual.py`).
-   Logs prêtant à confusion, masquant le comportement réel et les intentions derrière chaque mode.

**Piste de Réparation :**
La condition qui active le mode "Surgical" dans la méthode `_execute_step` de `Backend/Prod/orchestrator.py` doit être rendue plus restrictive.

-   **Action :** Modifier la méthode `_execute_step` dans `Backend/Prod/orchestrator.py`.
-   **Logique à implémenter :** La variable `surgical_mode` doit être définie de manière à n'être `True` que si toutes les conditions suivantes sont remplies :
    1.  `has_existing_code` est `True` (le fichier existe et contient du code).
    2.  `self.execution_mode` est `BUILD` ou `DOUBLE-CHECK`.
    3.  `has_python_files` est `True`.
    4.  `step.type` est `refactoring` ou `code_generation`.
    5.  Le `step.context` ne force pas explicitement `surgical_mode` à `False`.

    L'expression logique pour `surgical_mode` devrait être révisée pour prioriser la vérification de `self.execution_mode` avant d'évaluer les autres conditions par défaut.

**Avantage :** Rétablit la distinction claire entre le mode de prototypage rapide et le mode de production. Cela rend le mode `-q` plus rapide et plus léger, tout en réservant le mode "Surgical" pour les scénarios où sa précision est requise et appropriée (`-f`).

---

#### **Recommandation**

Je recommande vivement d'appliquer ces deux corrections à l'orchestrateur. La première est **cruciale** pour la fiabilité et l'intégrité des données lors de l'exécution des plans. La seconde est **importante** pour la performance, la clarté et la conformité du comportement de l'orchestrateur avec la philosophie de chaque mode.
