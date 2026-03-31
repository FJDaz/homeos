# 🧠 Rapport : Inférence des API Archétypales (Archetypal API Inference)

Ce rapport répond à la problématique de la détection d'architectures complexes (ex: "VSCode-like") à partir d'un PNG et propose une méthode pour automatiser l'inférence des services (APIs) nécessaires.

---

## 🧭 1. Le Problème : Le "Biais de Neutralité"

L'analyzer actuel (`analyzer.py`) a reçu pour consigne de ne **projeter aucune catégorie prédéfinie**. C'est une force pour la fidélité visuelle brute, mais une faiblesse pour l'intelligence fonctionnelle. Il voit des "rectangles" et des "listes" là où un humain voit un "Explorateur de fichiers" et un "Éditeur de code".

---

## 🏛️ 2. Stratégie : L'Inférence par Archétypes

Pour que le système "voie" un VSCode, nous devons implémenter une **Pipeline d'Analyse à Deux Étages**.

### Étage A : Description Topologique (Actuel)
- Extraction des zones : Sidebar (gauche), Editor (centre), Terminal (bas).
- Détection des indices visuels : `visual_hint="tree-view"`, `visual_hint="tabs"`.

### Étage B : Reconnaissance de Pattern (Nouveau)
Interroger Gemini avec un **Catalogue d'Archétypes Métier** :
- **Archétype "IDE"** → Requiert : `FileService`, `TerminalAPI`, `LSP_Client`, `GitManager`.
- **Archétype "Admin Dashboard"** → Requiert : `AnalyticsAPI`, `UserCRUD`, `FilterService`.
- **Archétype "Chatbot Pro"** → Requiert : `MessageHistory`, `StreamingEngine`, `VectorDB_Inference`.

---

## 🔌 3. Comment rendre ces détections possibles ?

### 1. La "Bibliothèque des Intentions"
Nous devons créer un fichier `functional_archetypes.json` qui fait le pont :
*Visual Pattern (Zonage)* + *Visual Hints* ➔ **Functional Intent (API)**.

### 2. Inférence Multimodale "Top-Down"
Modifier le prompt de l'analyzer pour qu'il procède par entonnoir :
1. **Évaluation de l'Archétype** : "À quelle application connue cette structure ressemble-t-elle le plus ?"
2. **Déduction des Intents** : "Si c'est un IDE, quels services sont indispensables pour que ça fonctionne ?"
3. **Injection dans le Genome** : Ajouter automatiquement ces services dans la section `n0_backend` du génome.

---

## 🚀 4. Recommandation Technique : "L'Intent Injector"

Plutôt que d'attendre que l'élève décrive ses APIs, l'analyzer devrait proposer des **intents pré-configurés** basés sur la détection visuelle :

- **Si Sidebar (visual_hint: tree) détectée** ➔ Proposer l'API `GET /api/fs/list`.
- **Si Editor (visual_hint: code) détecté** ➔ Proposer l'API `POST /api/fs/save`.

### Conclusion
Pour passer du "vu" au "compris", nous devons abandonner la neutralité au profit d'une **culture UI/UX partagée** entre le regard de Gemini et les besoins du Backend. C'est ce que nous appellerons la **"Reconnaissance de Signature Fonctionnelle"**.

---
**Status** : Concept validé. Prêt pour prototypage sur `analyzer.py`.
**Auteur** : Antigravity Agent
