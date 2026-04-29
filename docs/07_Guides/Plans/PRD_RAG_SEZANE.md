# PRD : RAG Sezane - Assistant IA Intelligent pour la Mode

**Version** : 1.0 "Sezane Pristine"  
**Date** : 30 mars 2026  
**Statut** : Brouillon Exhaustif  
**Périmètre** : Ce PRD définit les spécifications fonctionnelles et techniques du système RAG (Retrieval-Augmented Generation) pour l'écosystème **Sezane**.

---

## 📋 Table des Matières

1. [Vision et Objectifs](#vision-et-objectifs)
2. [Architecture du Système](#architecture-du-système)
3. [Fonctionnalités Clés](#fonctionnalités-clés)
4. [Standards de Développement (Guidelines Sezane)](#standards-de-développement-guidelines-sezane)
5. [Stack Technique](#stack-technique)
6. [Workflows Utilisateurs](#workflows-utilisateurs)
7. [Roadmap de Développement](#roadmap-de-développement)
8. [Indicateurs de Performance (KPIs)](#indicateurs-de-performance-kpis)

---

## 🎯 1. Vision et Objectifs

**RAG Sezane** est une plateforme d'intelligence artificielle conçue pour unifier l'accès à l'information au sein de la marque **Sezane**. En combinant la puissance des LLM avec les données propriétaires de la marque (catalogues, historique, guides de style), le système agit comme un pont sémantique entre les intentions des utilisateurs et la réalité des produits.

### Objectifs Principaux
- **Shopping Intelligent** : Transformer le moteur de recherche classique en un conseiller de style conversationnel.
- **Souveraineté de la Donnée** : Centraliser et indexer toute la documentation interne pour une récupération instantanée.
- **Cohérence de Marque** : Garantir que chaque interaction (client ou interne) respecte le ton et l'esthétique "Pristine" de Sezane.

---

## 🏗️ 2. Architecture du Système

Conformément à l'architecture **AetherFlow / HomeOS**, RAG Sezane repose sur une séparation stricte entre cognition et rendu.

```
                    Sources de Données (Catalogues, PDF, APIs)
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     RAG Sezane Engine                             │
├──────────────────────────────────────────────────────────────────┤
│  ingestor/          Nettoyage, Chunking sémantique, Embedding    │
│  retriever/         VectorSearch (FAISS/Pinecone), Metadata      │
│  orchestrator/      Hybridation DeepSeek-R1 / Gemini Flash       │
│  cache/             Semantic Cache (optimisation coûts/latence)  │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
              Interface Vanilla JS (Vite.js) - "Pristine UI"
```

---

## ✨ 3. Fonctionnalités Clés

### A. Assistant de Vente Conversationnel (B2C)
- **Conseil Look & Style** : "Quel sac porter avec les mocassins André pour un style vintage ?"
- **Recherche par Occasion** : Inférence sémantique des besoins clients ("tenue de baptême", "look de bureau décontracté").
- **Double-Check Stock** : Validation en temps réel de la disponibilité avant recommandation.

### B. Base de Connaissances "Atelier" (B2B)
- **Fiches Techniques Interactives** : Requêtes sur les spécifications des tissus, provenances et certifications éco-responsables.
- **Guidelines Visuelles** : Accès rapide aux règles de merchandising et de photographie.
- **Assistant SAV** : RAG sur les politiques de retour et procédures de remboursement pour les agents support.

### C. Module Multimodal (Vision)
- **Miroir Intelligent** : Analyse d'une photo importée par l'utilisateur pour suggérer des équivalents Sezane ou compléter un look existant.

---

## 📜 4. Standards de Développement (Guidelines Sezane)

Le projet doit respecter scrupuleusement les **Guidelines RAG Sezane** identifiées lors de l'adaptation pour AETHERFLOW :

- **TDD (Test-Driven Development)** : Développement systématique de tests unitaires avant l'implémentation logique.
- **Architecture "Pristine" Frontend** : Utilisation exclusive de **Vanilla JS** avec le pattern **State/Logic/View**. Aucun framework (React, Vue) n'est autorisé pour maintenir une latence minimale.
- **Principe DRY** : Factorisation maximale des composants UI (Atomes/Molécules) pour éviter toute duplication.
- **Sécurité & Robustesse** : Protection XSS native, isolation des variables d'environnement via `.env`.
- **Limite de Complexité** : Aucun fichier ne doit dépasser **300 lignes**. Au-delà, un refactoring modulaire est obligatoire.

---

## 🛠️ 5. Stack Technique

- **Frontend** : Vanilla JS, Vite.js, CSS Pur (ou Tailwind), Fabric.js (pour les manipulations visuelles).
- **Backend** : FastAPI (Python 3.11+).
- **IA/LLM** : 
  - **Raisonnement** : DeepSeek-R1 (pour la compréhension des intentions complexes).
  - **Génération** : Gemini 1.5 Flash (pour la rapidité et le volume).
- **Base de Données** : 
  - **Vectorielle** : Pinecone ou FAISS pour les embeddings.
  - **Relationnelle** : SQLite pour les métadonnées et le suivi de session.

---

## 🔄 6. Workflows Utilisateurs

### Workflow : "Trouver mon look" (Client)
1. **Saisie** : L'utilisateur exprime une intention ("Je cherche une tenue d'été fleurie").
2. **Retrieval** : Le moteur extrait les produits correspondants du catalogue vectorisé.
3. **Raisonnement** : Le LLM filtre par cohérence stylistique et stock disponible.
4. **Rendu** : Affichage d'un carrousel de produits avec arguments de style personnalisés.

### Workflow : "Vérification Technique" (Employé)
1. **Saisie** : "Quelle est la composition exacte du cuir des bottes High Marais ?"
2. **Retrieval** : Extraction des données depuis les fiches de production PDF.
3. **Réponse** : Citation directe de la source avec lien vers le document technique.

---

## 🗺️ 7. Roadmap de Développement

### Phase 1 : Fondations (Semaine 1-2)
- Mise en place de la pipeline d'ingestion (Catalogues JSON/PDF).
- Configuration de la base vectorielle.
- Création du squelette Frontend "Pristine" (Vite.js).

### Phase 2 : Intelligence & RAG (Semaine 3-4)
- Implémentation du retriever hybride.
- Intégration de DeepSeek-R1 pour l'analyse des intentions.
- Mise en place du cache sémantique.

### Phase 3 : Interface & UX (Semaine 5-6)
- Développement de la Chatbox conversationnelle.
- Intégration du module de vision multimodal.
- Phase de tests TDD intensifs et validation par le `ClaudeCodeValidator`.

---

## 📊 8. Indicateurs de Performance (KPIs)

- **Exactitude du RAG** : > 98% de réponses fondées sur les sources (zéro hallucination).
- **Performance Frontend** : Score Lighthouse Performance > 95.
- **Vitesse de Réponse** : Temps moyen de réponse (TTFT) < 1.5s.
- **Adoption Interne** : Taux d'utilisation quotidien par les équipes "Atelier".

---

*Document généré par AetherFlow Orchestrator sous la supervision de François-Jean Dazin.*
