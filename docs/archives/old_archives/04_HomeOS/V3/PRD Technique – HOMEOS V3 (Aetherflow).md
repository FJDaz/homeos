# PRD Technique – HOMEOS V3 (Aetherflow)

**Version** : 3.0  
**Date** : Mars 2026  
**Statut** : Avant-projet détaillé

---

## 1. Introduction

HOMEOS V3 est un orchestrateur de développement logiciel **standalone** (Backend – BKD) conçu pour transformer une intention utilisateur en code source fonctionnel et structuré. Il s’appuie sur une **architecture hexagonale** garantissant l’indépendance du cœur métier vis-à-vis des infrastructures externes (LLMs, générateurs d’UI, stockage, déploiement). Le système est pensé pour maximiser l’utilisation de ressources gratuites (DeepSeek R1, Gemini Flash) et pour offrir une expérience de développement rapide (mode FAST) ou soignée (mode BUILD).

Le présent document décrit les exigences techniques, les modules, les interfaces et les logiques de fallback nécessaires à la réalisation de HOMEOS V3.

---

## 2. Architecture Globale

L’architecture suit le modèle hexagonal (ports & adaptateurs), où le domaine central est isolé des technologies externes.

```
┌─────────────────────────────────────────────────────────────┐
│                      PORTS D'ENTRÉE                          │
│  (Interfaces utilisateur / déclencheurs)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   CLI    │ │   API    │ │  Monaco  │ │Extension │       │
│  │          │ │(HTTP/REST)│ │  Editor  │ │  Chrome  │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
│       └────────────┼────────────┼────────────┘              │
│                    ▼            ▼                            │
│         ┌────────────────────────────────────┐              │
│         │        Couche de présentation       │              │
│         │   (interprétation des commandes)   │              │
│         └────────────────┬───────────────────┘              │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                         DOMAINE (CŒUR)                       │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Entités :                                             │ │
│  │    • Plan (représentation d'une intention décomposée) │ │
│  │    • Génome (état du projet, arborescence, métadonnées)│ │
│  │    • Trace (capture d'une interaction LLM)            │ │
│  │    • Composant (unité de code générée)                 │ │
│  │                                                         │ │
│  │  Use cases :                                            │ │
│  │    • ExécuterPlan (orchestration d'un plan)            │ │
│  │    • ValiderStructure (cohérence du Génome)            │ │
│  │    • AppliquerModification (édition chirurgicale)      │ │
│  │    • RechercherTrace (interrogation des traces)        │ │
│  │                                                         │ │
│  │  Services :                                             │ │
│  │    • PlanExecutor (exécution pas-à-pas)                │ │
│  │    • SurgicalEditor (manipulation AST/range)           │ │
│  │    • GenomeManager (CRUD sur le Génome)                │ │
│  │    • TraceRepository (accès aux traces)                │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      PORTS DE SORTIE                         │
│  (Interfaces que le domaine appelle)                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  LLMProvider      (génération de texte / code)        │ │
│  │  UIGenerator      (transformation intention → UI)     │ │
│  │  Storage          (persistance du Génome, traces)     │ │
│  │  Deployment       (mise en production)                │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ Adaptateurs   │  │ Adaptateurs   │  │ Adaptateurs   │
│ IA            │  │ UI            │  │ Stockage/DPL   │
│ • DeepSeekR1  │  • UX Pilot      │  • SQLite        │
│ • GeminiFlash │  • TeleportHQ    │  • IndexedDB     │
│ • FallbackLocal│  • Builder.io    │  • Export fichier│
│               │  • FallbackSimple│  • Vercel (opt)  │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

## 3. Modules Principaux

### 3.1 Domaine (Core)
Le domaine est implémenté en Python (ou autre langage backend, à définir) et ne dépend d’aucune bibliothèque externe autre que la bibliothèque standard. Il définit les interfaces (ports) que les adaptateurs doivent implémenter.

**Interfaces de sortie (ports)** :
- `LLMProvider` : `generate(prompt: str, context: dict) -> str`
- `UIGenerator` : `generate_ui(spec: dict) -> str (HTML/CSS/JS)`
- `Storage` : `save_genome(project_id, genome)`, `load_genome(project_id)`, `save_trace(trace)`, `query_trace(filters)`
- `Deployment` : `deploy(project_id, config) -> url`

### 3.2 Adaptateurs d’entrée
- **CLI** : interface en ligne de commande pour lancer des commandes (ex: `homeos run fast "crée un dashboard"`). Utilise le même `UnifiedExecutor` que l’API.
- **API REST** : expose les mêmes fonctionnalités via HTTP (FastAPI). Authentification simplifiée (clé API ou session).
- **Monaco Editor** : intégré dans une interface web (VS Code) permettant l’édition directe et l’exécution de commandes.
- **Extension Chrome (BRS)** : capture les échanges avec les LLMs via monkey-patching de `window.fetch`. Communique avec le backend via une API locale.

### 3.3 Adaptateurs de sortie

#### 3.3.1 LLM
- **DeepSeek R1** : fournisseur principal, gratuit, avec API compatible OpenAI. Utilisé pour toutes les tâches de raisonnement et de génération de code.
- **Gemini 1.5 Flash** : fournisseur secondaire, gratuit (60 requêtes/min), utilisé en fallback ou pour des tâches simples (formatage, correction rapide).
- **FallbackLocal** : ensemble de templates préenregistrés et de réponses génériques utilisées en dernier recours (ex: "service indisponible, voici un exemple statique").

#### 3.3.2 UI (FRD)
- **UX Pilot** (free tier) : premier choix, crédits limités par mois.
- **TeleportHQ** (free tier) : second choix.
- **Builder.io** (free tier) : troisième choix.
- **FallbackSimple** : génère une UI minimaliste avec du CSS basique quand les services externes sont épuisés.

#### 3.3.3 Stockage
- **SQLite** : persistance locale des projets et du Génome.
- **IndexedDB** : utilisé par l’extension Chrome pour stocker les traces côté navigateur.
- **Export fichiers** : possibilité d’exporter le projet sous forme d’archive ZIP.

#### 3.3.4 Déploiement (DPL)
- Optionnel, module pouvant être étendu. Version initiale : export ZIP + instructions manuelles. Plus tard, intégration avec Vercel/Netlify via API.

---

## 4. Logique de Fallback – Majordome LLM

### 4.1 Interface `LLMProvider`
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 2000) -> str:
        pass
```

### 4.2 Implémentations
- `DeepSeekProvider` : utilise l’API DeepSeek (endpoint, pas de clé nécessaire actuellement).
- `GeminiProvider` : utilise l’API Gemini (clé gratuite, à configurer dans l’environnement).
- `FallbackLocalProvider` : renvoie des réponses préprogrammées basées sur des mots-clés.

### 4.3 Router / Orchestrateur LLM
Un service `LLMRouter` (dans le domaine ou en adaptateur) implémente la logique de fallback.

```python
class LLMRouter(LLMProvider):
    def __init__(self):
        self.providers = [
            DeepSeekProvider(),
            GeminiProvider(),
            FallbackLocalProvider()
        ]
    
    def generate(self, prompt, **kwargs):
        last_error = None
        for provider in self.providers:
            try:
                return provider.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                # Log l'erreur et continue
        raise Exception(f"Tous les fournisseurs ont échoué : {last_error}")
```

**Stratégies supplémentaires** :
- En mode BUILD, on peut tenter deux fois DeepSeek avant de passer à Gemini.
- On peut marquer les fournisseurs comme "dégradés" temporairement après plusieurs échecs.

### 4.4 Gestion des quotas
- Gemini a une limite de 60 requêtes/minute. Un compteur local (rate limiter) évite de dépasser.
- Pour DeepSeek, pas de quota connu, mais gérer les timeouts.

---

## 5. Détail du module UI (FRD)

### 5.1 Interface `UIGenerator`
```python
class UIGenerator(ABC):
    @abstractmethod
    def generate(self, specification: dict) -> str:
        """Retourne le code HTML/CSS/JS complet."""
        pass
```

### 5.2 Adaptateurs
- `UXPilotAdapter` : utilise l’API REST d’UX Pilot (clé gratuite, crédits).
- `TeleportHQAdapter` : utilise l’API TeleportHQ (clé gratuite, limites).
- `BuilderIOAdapter` : utilise Builder.io (clé gratuite).
- `FallbackUIAdapter` : génère une page simple basée sur des templates.

### 5.3 Router UI (similaire au LLM)
Un routeur tente les fournisseurs dans l’ordre configurable, avec fallback.

---

## 6. Module Traces (BRS)

### 6.1 Capture
- L’extension Chrome injecte un script qui surcharge `window.fetch` et `window.XMLHttpRequest`.
- Pour chaque requête vers les domaines des LLMs (chat.openai.com, claude.ai, etc.), on capture :
  - URL
  - Méthode
  - Headers (sans tokens)
  - Body (requête et réponse)
  - Timestamp
- Les données sont stockées dans IndexedDB localement.

### 6.2 Synchronisation avec le backend
- L’extension peut envoyer périodiquement les traces à l’API HOMEOS (endpoint `/api/traces`).
- Le backend les stocke dans SQLite, associées à un projet et un utilisateur.

### 6.3 API de recherche
- `GET /api/traces?q=...&project=...&from=...` pour interroger.
- Recherche plein texte sur le contenu des prompts et réponses.

---

## 7. Surgical Edit & Gestion du Génome

### 7.1 Principe
Le **Génome** est une représentation structurée du projet : arborescence des fichiers, métadonnées, dépendances, etc. Il est stocké en JSON.

Le **Surgical Editor** permet de modifier le code source de façon précise sans réécrire l’intégralité du fichier. En V3, on utilise une approche **Range Replacement** (par regex / localisation) plutôt que l’AST complet, pour plus de robustesse.

### 7.2 Interface
```python
class SurgicalEditor:
    def apply_edit(self, file_path: str, edits: List[Edit]) -> bool:
        """
        edits: liste de tuples (start_line, end_line, new_content)
        ou (search_pattern, replacement)
        """
        pass
```

### 7.3 Intégration avec le domaine
Le `PlanExecutor` appelle le `SurgicalEditor` pour chaque modification planifiée. Le `GenomeManager` met à jour le Génome après chaque changement.

---

## 8. Modes d’exécution : FAST et BUILD

Ces deux modes sont implémentés par le même `UnifiedExecutor` mais avec des paramètres différents.

### 8.1 Mode FAST
- **Objectif** : réponse rapide (< 3s) avec un code fonctionnel mais non optimisé.
- **Paramètres** :
  - LLM : DeepSeek (ou fallback rapide)
  - Température élevée (0.4) pour plus de créativité
  - Pas de validation structurelle poussée
  - Génération directe du code, sans planification complexe
- **Sortie** : code "sale" + audit listant les défauts potentiels.

### 8.2 Mode BUILD
- **Objectif** : code propre, architecture hexagonale, tests (90s).
- **Paramètres** :
  - LLM : DeepSeek (avec plusieurs tentatives) ; si échec, Gemini
  - Température basse (0.1)
  - Planification multi-étapes (décomposition, génération de squelette, remplissage)
  - Validation du Génome après chaque étape (rétro-génome)
  - Génération de documentation et tests unitaires basiques
- **Sortie** : projet structuré, prêt à être déployé.

---

## 9. Contraintes Techniques

- **Langage backend** : Python 3.11+ (pour la richesse des bibliothèques et la facilité d’expérimentation).
- **Containerisation** : L’ensemble du moteur Aetherflow doit pouvoir être containerisé (Docker) pour une distribution standalone.
- **Base de données** : SQLite pour les projets, pas de serveur DB externe requis.
- **API** : FastAPI pour l’interface REST.
- **CLI** : Typer ou argparse.
- **Frontend d’édition** : Intégration de Monaco Editor via une simple page HTML/JS servie par le backend.
- **Extension Chrome** : JavaScript vanilla, pas de framework lourd.

---

## 10. Glossaire

| Terme | Définition |
|-------|------------|
| **Aetherflow** | Nom technique du moteur d’orchestration. |
| **BKD** | Backend (HOMEOS). |
| **BRS** | Business Requirements Shell – module de capture des traces. |
| **FRD** | Frontend Delegation – génération d’UI via services externes. |
| **DPL** | Deployment – module de mise en production. |
| **Génome** | Représentation interne de l’état d’un projet. |
| **Rétro-Génome** | Processus de validation et correction de la structure après modifications. |
| **Surgical Edit** | Modification précise du code (par range ou AST). |
| **Plan** | Séquence d’actions à exécuter pour réaliser une intention. |
| **Trace** | Capture d’une interaction avec un LLM. |

---

**Document approuvé pour le développement de HOMEOS V3.**