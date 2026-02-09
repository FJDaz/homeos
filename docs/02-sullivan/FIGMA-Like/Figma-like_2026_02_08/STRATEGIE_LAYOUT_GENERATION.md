# STRATÉGIE DE GÉNÉRATION ET PROPOSITION DE LAYOUTS POUR HOMEOS STUDIO

**Date** : 2026-02-08

---

## CONTEXTE : Optimisation de l'Expérience Utilisateur (UX)

L'objectif est de proposer au designer des layouts par défaut pertinents, inférés du Genome, pour minimiser la latence perçue et maximiser la fluidité du processus de création et d'édition au sein d'Homeos Studio.

---

## STRATÉGIE HYBRIDE : Pré-calcul Asynchrone + Raffinement Contextuel

Pour atteindre cet objectif, la stratégie la plus intelligente combine une génération anticipée d'esquisses légères et un raffinement en temps réel au moment de l'interaction utilisateur.

### PHASE 1 : Génération d'Esquisses Basiques (Pré-calcul Asynchrone)

*   **Moment :** **Pendant ou immédiatement après la génération et la distillation du Genome** par `genome_generator.py`.
*   **Action :** Homeos génère en arrière-plan des **blueprints ou esquisses de layouts très légers et basiques** pour *tous les Corps* identifiés dans le Genome.
    *   Ces esquisses sont des interprétations visuelles primaires, utilisant les `x_ui_hint`, `visual_hint` et `inferred_daisy_component`.
    *   Elles peuvent être de simples structures HTML/Tailwind ou des représentations Fabric.js minimales (JSON outline).
*   **Avantages :**
    *   **Réduction de la latence :** Le travail intensif est effectué en avance, réduisant drastiquement le temps d'attente lors de l'interaction directe de l'utilisateur.
    *   **"Meilleure estimation" initiale :** Fournit un point de départ cohérent basé sur l'inférence programmatique.
*   **Mécanisme :**
    *   Tâches asynchrones ou en arrière-plan (ex: `asyncio` en Python).
    *   Stockage de ces esquisses dans un cache local performant, potentiellement aux côtés du `homeos_genome.json`.

### PHASE 2 : Raffinement Contextuel Rapide (À la Demande)

*   **Moment :** **Lorsque l'utilisateur sélectionne un Corps spécifique à éditer** (ex: double-clic sur un Corps dans la "Vue 1" ou drag-and-drop sur le canvas de la "Vue 2").
*   **Action :**
    1.  **Affichage immédiat :** Homeos récupère et affiche instantanément l'esquisse pré-calculée (de la Phase 1) du Corps sélectionné.
    2.  **Raffinement en arrière-plan/quasi temps réel :** Simultanément, Homeos lance un processus de raffinement plus détaillé et contextuel. Ce raffinement intègre :
        *   Les détails précis des Organes et Atomes du Corps.
        *   Les préférences utilisateur ou les directives de design système (s'il y en a).
        *   Des apprentissages issus de Corps similaires validés par l'utilisateur (si le système supporte l'apprentissage).
*   **Avantages :**
    *   **Réponse visuelle instantanée :** L'utilisateur voit immédiatement quelque chose, même si c'est une version simplifiée.
    *   **Pertinence maximale :** La proposition finale est hautement adaptée au contexte d'édition actuel de l'utilisateur.
    *   **Expérience fluide :** La perception de la latence est minimisée, car le raffinement se fait de manière progressive.

---

## EXPLOITATION DU SYSTÈME POUR LA RÉDUCTION DE LA LATENCE

*   **Asynchronicité :** Utiliser des opérations non bloquantes et des tâches en arrière-plan pour la génération des esquisses initiales.
*   **Caching :** Un cache local intelligent est essentiel pour stocker et récupérer rapidement les layouts pré-calculés.
*   **Affichage Progressif :** Toujours afficher une version simple avant la version raffinée.
*   **Inférence Intelligente :** S'appuyer fortement sur les capacités d'inférence visuelle de Sullivan (`visual_inference.py`) et l'`IntentTranslator` pour que les propositions initiales soient déjà très pertinentes.
*   **Feedback & Apprentissage :** Intégrer un mécanisme d'apprentissage pour que les ajustements manuels de l'utilisateur améliorent les futures propositions de layouts.

Cette stratégie garantit une UX optimale en fournissant des réponses visuelles rapides et intelligentes, sans surcharger le système ni ralentir le workflow du designer.