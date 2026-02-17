---
name: aetherflow-roadmap-operator
description: Protocole d'exécution autonome basé sur la ROADMAP.md pour les agents AetherFlow.
---

# AetherFlow Roadmap Operator (AF-RO)

Ce skill permet à un agent d'agir comme un automate piloté par la `ROADMAP.md`. Il transforme la documentation en instructions exécutables.

## 📜 Principes Fondamentaux
1. **La Roadmap est la Commande** : L'agent ne décide pas de sa tâche, il l'extrait de la section `STATUS: MISSION` dont il est l' `ACTOR`.
2. **Cycle de Vigilance** :
   - Lire `ROADMAP.md`.
   - Identifier la mission active pour son rôle.
   - Exécuter les `Tâches` listées.
   - Valider via `Critères de succès`.
   - Mettre à jour le `STATUS` à `TERMINÉE`.
   - Activer la mission suivante (passer son `STATUS` à `MISSION`).

## 🛠 Procédure d'Exécution
1. **Extraction** : Analyser le fichier `ROADMAP.md` pour trouver le bloc correspondant à la mission en cours.
2. **Sondage (Probe)** : Si la mission est structurelle (Step 2), effectuer des `Technical Probes` (lectures de fichiers, requêtes API, sondages DOM) pour confirmer l'état initial.
3. **Action** : Réaliser les modifications demandées (Code Direct).
4. **Validation Technical** : Vérifier la validité syntaxique et structurelle.
5. **Rapport** : Mettre à jour la Roadmap avec un condensé du `Résultat`.

## 🚫 Limites
- Ne jamais sauter d'étape.
- Si une mission précédente est `EN ATTENTE` ou `MISSION` (non terminée), l'agent doit attendre ou signaler le blocage.
- Ne pas modifier le périmètre de peinture (CSS) si l'agent est un acteur de structure (JS).
