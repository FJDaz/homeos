# 03 - Feuille de Route (Plan de Restauration)

Ce plan détaille les étapes physiques pour passer de l'état actuel (Statue fragile) à une architecture modulaire et saine.

## Phase 0 : Récupération & Sécurisation (Immediate)
1.  **`git stash`** : Mise en sécurité des modifications instables de l'agent KIMI dans un tiroir temporaire.
2.  **`git restore`** : Retour à la version `530b30d` (Buste en grillage sain).

## Phase 1 : Extraction du Squelette
1.  **Création du dossier `/static`** : Nouveau foyer pour tous les actifs (HTML/JS/CSS).
2.  **Dégonglement de `server_9998_v2.py`** : 
    - Suppression des chaînes HTML hardcodées (Templates).
    - Mise en place du `StaticFileHandler` pour servir les nouveaux fichiers.
3.  **Migration des Wireframes** : Passage de Python à une bibliothèque JS (`wireframe_lib.js`).

## Phase 2 : Injection de l'Engine (Hooks)
1.  **Initialisation de `sullivan_engine.js`** : Le chef d'orchestre global.
2.  **Déploiement du Bridge sémantique** : Branchement des appels API sur le validateur de schéma.
3.  **Mise en place des Registres** : Styles, Composants et Outils deviennent des listes dynamiques.

## Phase 3 : Optimisation IA & Offline
1.  **Contextualisation Extrême** : Découpage des prompts IA pour ne charger que le module pertinent via les Hooks.
2.  **Activation Local-First** : Cache Service Workers et persistance navigateur pour l'expérience hors-ligne.
3.  **Tests de Stress** : Vérification du non-régression sur le Drill-down et la Validation.

---

## 🛑 Critères de Succès
- Le fichier `server_9998_v2.py` fait moins de 1000 lignes (contre 4200 aujourd'hui).
- Chaque brique (Viewer, Stenciler) est modifiable sans impacter l'autre.
- Les erreurs de type "amnésie" des agents disparaissent.
