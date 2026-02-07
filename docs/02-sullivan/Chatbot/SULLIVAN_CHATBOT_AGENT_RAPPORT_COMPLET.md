# Sullivan Chatbot-Agent — Rapport Complet

**Date de génération** : 3 février 2026  
**Version** : 2.2  
**Statut** : Documentation technique complète

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du système](#architecture-du-système)
3. [Composants principaux](#composants-principaux)
4. [SullivanAgent — Agent conversationnel](#sullivanagent--agent-conversationnel)
5. [Système de personnalités](#système-de-personnalités)
6. [Mémoire et contexte](#mémoire-et-contexte)
7. [Outils et capacités d'action](#outils-et-capacités-daction)
8. [Modes d'opération](#modes-dopération)
9. [Workflows et intégrations](#workflows-et-intégrations)
10. [Points de terminaison API](#points-de-terminaison-api)
11. [Configuration et personnalisation](#configuration-et-personnalisation)
12. [État actuel et roadmap](#état-actuel-et-roadmap)

---

## Vue d'ensemble

Sullivan Chatbot-Agent est le **système conversationnel intelligent** d'AetherFlow qui transforme les interactions utilisateur en actions concrètes. Contrairement à un simple chatbot, Sullivan combine :

- **Chat naturel** avec mémoire de contexte persistante
- **Partenariat de design** — conseils, suggestions, guidage UX
- **Agent autonome** — exécution d'outils (générer, analyser, modifier)
- **Personnalité configurable** — du professionnel minimaliste au créatif décalé

### Positionnement dans l'écosystème AetherFlow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ÉCOSYSTÈME AETHERFLOW                         │
├─────────────────────────────────────────────────────────────────┤
│  AetherFlow Core     │  Orchestration, Genome, Plan execution   │
│  Sullivan Kernel     │  Design, Frontend, Dev modes             │
│  ⭐ Sullivan Agent   │  ⭐ Chatbot, Partner, Agent autonome ⭐   │
│  HomeOS              │  Mode manager (construction/project)     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture du système

### Vue d'ensemble de l'architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SULLIVAN CHATBOT-AGENT                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   Memory     │  │    Tools     │  │     LLM      │               │
│  │   System     │  │   Registry   │  │   Router     │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                        │
│         └─────────────────┼─────────────────┘                        │
│                           │                                          │
│              ┌────────────┴────────────┐                            │
│              │     SULLIVAN AGENT      │                            │
│              │   (SullivanAgent class) │                            │
│              └────────────┬────────────┘                            │
│                           │                                          │
│         ┌─────────────────┼─────────────────┐                        │
│         ▼                 ▼                 ▼                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  Chat Widget │  │  API REST    │  │  Studio UI   │               │
│  │  (Frontend)  │  │  (FastAPI)   │  │  (Overlay)   │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Stack technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| **Langage** | Python 3.11+ | Backend agent |
| **Framework API** | FastAPI | Endpoints REST |
| **LLM Providers** | Gemini, Groq, DeepSeek | Génération & analyse |
| **Mémoire** | JSON files (~/.aetherflow/sessions/) | Persistance session |
| **Frontend** | HTMX + Vanilla JS | Widget chat |
| **Logging** | Loguru | Traçabilité |

---

## Composants principaux

### Structure des fichiers

```
Backend/Prod/sullivan/
├── agent/                          # 🧠 Cœur de l'agent conversationnel
│   ├── __init__.py                 # Exports principaux
│   ├── sullivan_agent.py           # SullivanAgent (476 lignes)
│   ├── memory.py                   # ConversationMemory, SessionContext
│   ├── tools.py                    # ToolRegistry, 14+ outils
│   └── personalities/              # 🎭 Système de personnalités
│       ├── __init__.py             # Gestionnaire de personnalités
│       ├── base.py                 # Classe de base PersonalityBase
│       ├── sullivan_default.py     # Personnalité pro (214 lignes)
│       └── sullivan_weirdo.py      # Personnalité créative (251 lignes)
│
├── chatbot/                        # 💬 Interface chat legacy
│   ├── __init__.py
│   └── sullivan_chatbot.py         # 66 lignes - version simple
│
├── modes/                          # 🎨 Modes d'opération spécialisés
│   ├── __init__.py
│   ├── dev_mode.py                 # Mode DEV (159 lignes)
│   ├── designer_mode.py            # Mode DESIGNER (331 lignes)
│   ├── frontend_mode.py            # Mode FRONTEND (252 lignes)
│   ├── cto_mode.py                 # Mode CTO (391 lignes)
│   └── plan_builder.py             # Construction de plans
│
├── analyzer/                       # 🔍 Analyse et inférence
│   ├── backend_analyzer.py         # Analyse backend → fonction globale
│   ├── design_analyzer.py          # Analyse images (vision)
│   ├── design_analyzer_fast.py     # Version avec cache
│   ├── design_principles_extractor.py
│   └── ui_inference_engine.py      # Inférence UI (JTBD)
│
├── builder/                        # 🏗️ Génération de code
│   ├── sullivan_builder.py         # Générateur HTML principal
│   ├── refinement.py               # Affinage de code
│   └── corps1_chatbot_page.py      # Template chatbot
│
├── registry.py                     # 📚 Registre de composants
├── knowledge/                      # 🧠 Base de connaissances
│   └── knowledge_base.py           # Patterns, STAR, matching
│
├── auditor/                        # ✅ Validation
│   └── sullivan_auditor.py         # Vérification qualité
│
└── models/                         # 📊 Modèles de données
    └── sullivan_score.py           # Scoring Sullivan
```

---

## SullivanAgent — Agent conversationnel

### Classe principale : `SullivanAgent`

**Fichier** : `Backend/Prod/sullivan/agent/sullivan_agent.py`  
**Taille** : 476 lignes  
**Responsabilité** : Orchestration complète des interactions conversationnelles

#### Fonctionnalités clés

```python
class SullivanAgent:
    """
    Capacités:
    - Chat naturel avec mémoire de contexte
    - Exécution d'outils (générer, analyser, modifier)
    - Personnalité Sullivan (pédagogique, minimaliste)
    - Intégration au parcours UX (9 étapes)
    """
```

#### Initialisation

```python
agent = SullivanAgent(
    session_id="abc123",           # Optionnel (généré auto)
    user_id="user456",             # ID utilisateur
    memory=None,                   # Optionnel (créée auto)
    tools=None,                    # Optionnel (registry global)
    llm_provider="groq",           # "groq" (rapide) ou "gemini" (capable)
)
```

#### Méthodes principales

| Méthode | Description | Latence typique |
|---------|-------------|-----------------|
| `chat(message, context, execute_tools)` | Message → Réponse complète | ~500ms |
| `chat_stream(message, context)` | Streaming temps réel | ~100ms/chunk |
| `update_step(step)` | Met à jour l'étape UX (1-9) | Instantané |
| `set_project(name)` | Définit le projet courant | Instantané |
| `export_session()` | Exporte la session complète | Instantané |
| `clear_history()` | Efface l'historique | Instantané |

#### Pattern d'utilisation

```python
from Backend.Prod.sullivan.agent import create_agent

# Créer un agent configuré
agent = await create_agent(user_id="user123", step=4)

# Chat simple
response = await agent.chat("Je veux créer une page de login")
print(response.content)           # Réponse texte
print(response.tool_calls)        # Outils détectés
print(response.tool_results)      # Résultats exécution

# Streaming
async for chunk in agent.chat_stream("Génère un bouton"):
    print(chunk, end="")
```

### `AgentResponse` — Structure de réponse

```python
@dataclass
class AgentResponse:
    content: str                    # Réponse textuelle
    tool_calls: List[Dict]          # Appels d'outils détectés
    tool_results: List[ToolResult]  # Résultats des exécutions
    session_id: str                 # ID de session
    metadata: Dict[str, Any]        # Métadonnées (step, actions DOM...)
```

---

## Système de personnalités

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              SYSTÈME DE PERSONNALITÉS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌───────────────┐                                         │
│   │ PersonalityBase│  ← Classe abstraite                    │
│   └───────┬───────┘                                         │
│           │                                                  │
│     ┌─────┴─────┐                                            │
│     ▼           ▼                                            │
│ ┌────────┐  ┌────────┐                                       │
│ │Default │  │Weirdo  │  ← ← Ajoutez les vôtres !            │
│ │(Pro)   │  │(Fun)   │                                       │
│ └────────┘  └────────┘                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Personnalités disponibles

#### 1. `SullivanDefault` — Version professionnelle

**Fichier** : `personalities/sullivan_default.py`  
**Usage** : Production, utilisateurs finaux  
**Traits** :

| Trait | Score (1-10) | Description |
|-------|--------------|-------------|
| Pédagogique | 9 | Explique sans jargon |
| Minimaliste | 8 | Concis, pas de blabla |
| Pragmatique | 9 | Orienté solutions |
| Bienveillant | 8 | Encourageant |
| Formel | 4 | Décontracté mais pro |

**Style de réponse** :
- Max 4 phrases
- Emojis autorisés ✅
- Tutoiement
- Pas de markdown lourd

**Exemple** :
```
❌ "Je vais procéder à l'analyse de votre structure..."
✅ "J'ai analysé ton design. Voici les 3 zones principales."
```

#### 2. `SullivanWeirdo` — Version créative (customisable)

**Fichier** : `personalities/sullivan_weirdo.py`  
**Usage** : Développeur, créateur du projet  
**Traits configurables** :

```python
TRAITS = {
    "pédagogique": 8,
    "sarcasme": 6,          # ← Ajustez selon votre style
    "absurde": 5,
    "formel": 1,
    "humour_noir": 4,
    "references_pop": 7,
}
```

**Personnalisation** :
```python
# Variables d'environnement
export SULLIVAN_PERSONALITY=weirdo

# Ou fichier config
~/.aetherflow/config.json
{
    "personality": "weirdo"
}
```

**Philosophie** (extrait du prompt system) :
> "Tu refuses d'exécuter aveuglément une demande si elle te semble mal posée, vide de sens ou inutilement complexe. Dans ce cas, tu proposes une reformulation plus juste."

### Extension — Créer une personnalité

```python
from .base import PersonalityBase

class MonSullivan(PersonalityBase):
    NAME = "MonSullivan"
    ROLE = "Mon assistant perso"
    AVATAR = "🚀"
    
    TRAITS = {
        "pédagogique": 9,
        "enthousiaste": 8,
        # ...
    }
    
    @classmethod
    def get_system_prompt(cls, context=None):
        return "Tu es MonSullivan..."
```

Puis enregistrer :
```python
from . import add_personality
add_personality("monsullivan", MonSullivan)
```

---

## Mémoire et contexte

### `ConversationMemory`

**Fichier** : `Backend/Prod/sullivan/agent/memory.py`  
**Responsabilité** : Persistance et gestion du contexte conversationnel

#### Fonctionnalités

```python
class ConversationMemory:
    """
    Mémoire de conversation avec:
    - Historique complet des messages
    - Résumé pour contexte LLM (fenêtre glissante)
    - Stockage persistant par session
    """
```

#### Structure de données

```python
@dataclass
class Message:
    role: str           # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime
    metadata: Dict      # tool_calls, dom_actions, etc.

@dataclass
class SessionContext:
    session_id: str
    user_id: str
    current_project: Optional[str]
    current_step: int           # Étape UX 1-9
    genome: Optional[Dict]      # Genome du projet
    design_structure: Optional[Dict]
    preferred_style: Optional[str]  # minimal, brutalist...
    mode: str = "normal"        # normal vs expert vs agent
```

#### Stockage persistant

```
~/.aetherflow/sessions/
├── user123_20260203_143052_a1b2c3d4.json
├── user456_20260203_151023_b2c3d4e5.json
└── ...
```

#### Configuration

```python
memory = ConversationMemory(
    session_id="abc123",
    user_id="user456",
    max_history=50,          # Messages conservés
    context_window=10,       # Messages pour LLM
    storage_dir=Path("..."), # Répertoire persistance
)
```

---

## Outils et capacités d'action

### `ToolRegistry` — Registre d'outils

**Fichier** : `Backend/Prod/sullivan/agent/tools.py`  
**Taille** : 1000+ lignes  
**Outils disponibles** : 14+

### Liste complète des outils

#### Outils de Design & Frontend

| Outil | Description | Paramètres clés |
|-------|-------------|-----------------|
| `analyze_design` | Analyse image (vision) | `image_path`, `extract_principles` |
| `generate_component` | Génère HTML/CSS | `description`, `component_type`, `style` |
| `refine_style` | Affine style HTML | `html`, `instruction` |
| `search_components` | Cherche librairie | `query`, `category` |

#### Outils de Code & Projet

| Outil | Description | Paramètres clés |
|-------|-------------|-----------------|
| `analyze_codebase` | Analyse structure code | `path`, `analysis_type` |
| `search_in_code` | Recherche dans code | `query`, `file_pattern` |
| `read_documentation` | Lit fichier doc | `path`, `section` |
| `write_file` | Écrit fichier | `path`, `content` |

#### Outils CTO & Planification

| Outil | Description | Paramètres clés |
|-------|-------------|-----------------|
| `create_plan` | Crée plan JSON | `brief` ou `document_path` |
| `execute_plan` | Exécute plan | `plan_path`, `mode` |
| `get_project_context` | Contexte projet | - |
| `extract_components` | Extrait composants doc | `document_path` |

#### Outils de Validation & Guidance

| Outil | Description | Paramètres clés |
|-------|-------------|-----------------|
| `validate_genome` | Valide cohérence | `genome_json` |
| `get_step_guidance` | Conseils étape | `step` (1-9) |

### Pattern d'appel d'outils

L'agent détecte automatiquement les outils dans les réponses LLM via le pattern :

```
@nom_outil({"param": "valeur"})
```

**Exemple de flux** :

1. **Utilisateur** : *"Génère un bouton rouge"*
2. **LLM** répond : `"Je vais créer ce bouton. @generate_component({"description": "bouton rouge", "component_type": "button"})"`
3. **Agent** parse et exécute l'outil
4. **Agent** génère réponse finale avec résultat

### Actions DOM

Sullivan peut manipuler directement le frontend via :

```
@dom_action({"type": "insertHTML", "selector": "body", "html": "..."})
@dom_action({"type": "setStyle", "selector": "#header", "styles": {...}})
@dom_action({"type": "addClass", "selector": ".card", "className": "active"})
@dom_action({"type": "highlight", "selector": "#element"})
@dom_action({"type": "scrollTo", "selector": "#section"})
```

---

## Modes d'opération

### Vue comparative des modes

| Mode | Usage | Latence | Capacités | Fichier |
|------|-------|---------|-----------|---------|
| **Agent** (`chat`) | Conversation interactive | ~500ms | Mémoire + outils | `sullivan_agent.py` |
| **DevMode** (`dev`) | Backend → Frontend | ~5-15s | Analyse + Inférence | `dev_mode.py` |
| **DesignerMode** (`designer`) | Design → Code | ~10-30s | Vision + Miroir | `designer_mode.py` |
| **FrontendMode** (`frd`) | Workflows frontend | Variable | Multi-modèles | `frontend_mode.py` |
| **CTOMode** (`cto`) | Exécution directe | ~1-5s | Décision + Action | `cto_mode.py` |

### DevMode — Workflow "Collaboration Heureuse"

**Fichier** : `Backend/Prod/sullivan/modes/dev_mode.py`

```python
class DevMode:
    """
    Workflow complet :
    1. Dialogue Stratégique : accord sur N étapes parcours
    2. Maillage des Corps : définition zones contenu
    3. Inférence Technique : cascade Organes → Molécules → Atomes
    4. HCI Mentor : surveillance charge cognitive
    5. Génération 'Miroir' optionnelle
    """
```

**Hiérarchie d'inférence** :

```
Niveau 0 : Intention Suprême (JTBD)
    ↓
Niveau 1 : Corps (zones contenu)
    ↓
Niveau 2 : Organes (blocs fonctionnels)
    ↓
Niveau 3 : Molécules (composants UI)
    ↓
Niveau 4 : Atomes (éléments HTML de base)
```

### DesignerMode — Workflow "Génération Miroir"

**Fichier** : `Backend/Prod/sullivan/modes/designer_mode.py`

```python
class DesignerMode:
    """
    Workflow upload → analyse → génération 'Miroir'
    
    1. Upload design (PNG/JPG/SVG)
    2. Analyser structure avec DesignAnalyzer
    3. Vérifier patterns dans KnowledgeBase
    4. Proposer pattern éprouvé
    5. Générer composants avec 'Miroir'
    """
```

### FrontendMode — Orchestration intelligente

**Fichier** : `Backend/Prod/sullivan/modes/frontend_mode.py`

**Routage automatique des modèles** :

| Tâche | Provider | Condition |
|-------|----------|-----------|
| `analyze_design` | Gemini | Vision obligatoire |
| `generate_components` | Gemini/DeepSeek | >50k tokens → Gemini |
| `refine_style` | Groq | Fallback Gemini |
| `dialogue` | Groq | Fallback Gemini |
| `validate_homeostasis` | Groq | Fallback Gemini |

### CTOMode — Exécution autonome

**Fichier** : `Backend/Prod/sullivan/modes/cto_mode.py`

```python
class CTOMode:
    """
    Sullivan comme Chief Technology Officer.
    Transforme les demandes en langage naturel en exécutions.
    Pas de conversation inutile - que des actions.
    """
```

**Modes de décision** :

```
Demande utilisateur
    ↓
[Analyse CTO] → Classification
    ↓
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ DESIGNER│ FRONTEND│  PROTO  │  PROD   │ DIRECT  │
└────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘
     │         │         │         │         │
  Analyse   Génère    POC rapide  Qualité   Réponse
  image     HTML      Code        Entreprise simple
```

---

## Workflows et intégrations

### Workflow idéal complet (6 phases)

Basé sur `docs/02-sullivan/SULLIVAN_WORKFLOW_IDEAL.md` :

```
Phase 1 : Template → HTML (autoconstruction)
    │
Phase 2 : Extraction principes graphiques
    │
Phase 3 : Câblage genome + plan d'écrans
    │
Phase 4 : Génération des corps (STOP)
    │
Phase 5 : Corps 1 → Organes + Chatbot Sullivan
    │
Phase 6 : Addendum → Questions → Corps 2, 3...
```

### Intégration HomeOS

```
┌─────────────────────────────────────────────────────┐
│                    HOMEOS                           │
├─────────────────────────────────────────────────────┤
│  Mode CONSTRUCTION     │  Mode PROJECT              │
│  ├─ Sullivan Studio    │  ├─ Sullivan Chatbot       │
│  ├─ Z-index 10000      │  ├─ Z-index 10000          │
│  └─ Stack SvelteKit    │  └─ Stack HTML/CSS/JS      │
└─────────────────────────────────────────────────────┘
         │                         │
         └───────────┬─────────────┘
                     │
            ┌────────▼────────┐
            │  SullivanAgent  │
            │  (Core)         │
            └─────────────────┘
```

---

## Points de terminaison API

### Endpoints REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/sullivan/agent/chat` | Chat simple |
| `POST` | `/sullivan/agent/chat/stream` | Chat streaming (SSE) |
| `GET` | `/sullivan/agent/session/{id}` | Détails session |
| `POST` | `/sullivan/agent/session/{id}/clear` | Effacer historique |
| `GET` | `/sullivan/agent/tools` | Lister les outils |
| `POST` | `/sullivan/frontend/analyze` | Analyse design |
| `POST` | `/sullivan/frontend/generate` | Génération composants |
| `POST` | `/sullivan/frontend/refine` | Raffinement style |
| `POST` | `/sullivan/dialogue` | Dialogue conversationnel |
| `POST` | `/sullivan/frontend/validate` | Validation homéostasie |

### Exemples d'appels

```bash
# Chat simple
curl -X POST http://localhost:8000/sullivan/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Je veux créer une page de login",
    "user_id": "user123",
    "step": 4
  }'

# Réponse:
{
  "content": "Parfait ! Pour une page de login...",
  "session_id": "user123_20260202_143052_a1b2c3d4",
  "tool_calls": [],
  "metadata": {"step": 4, "tool_count": 0}
}
```

---

## Configuration et personnalisation

### Variables d'environnement

```bash
# Clés API
GOOGLE_API_KEY=xxx           # Gemini (vision + génération)
GROQ_API_KEY=xxx             # Groq (chat rapide)
DEEPSEEK_API_KEY=xxx         # DeepSeek (code)

# Personnalité
SULLIVAN_PERSONALITY=default # default | weirdo | custom

# Configuration
AETHERFLOW_HOME=~/.aetherflow
```

### Fichier de configuration

```json
// ~/.aetherflow/config.json
{
    "personality": "weirdo",
    "default_llm": "gemini",
    "session_ttl_hours": 48,
    "ui_preferences": {
        "theme": "dark",
        "font_size": 14
    }
}
```

---

## État actuel et roadmap

### ✅ Implémenté

| Fonctionnalité | Statut | Fichier |
|----------------|--------|---------|
| Agent conversationnel | ✅ | `sullivan_agent.py` |
| Mémoire persistante | ✅ | `memory.py` |
| Système d'outils (14+) | ✅ | `tools.py` |
| Personnalités multiples | ✅ | `personalities/` |
| Modes Dev/Designer/Frontend/CTO | ✅ | `modes/` |
| Streaming | ✅ | `chat_stream()` |
| Actions DOM | ✅ | Parser `_parse_response()` |
| Fallback LLM | ✅ | Groq → Gemini |

### 🚧 En développement

| Fonctionnalité | Priorité | Statut |
|----------------|----------|--------|
| Interface web chatbot | Haute | 🚧 Phase 5 |
| Addendum graphique | Haute | 🚧 Phase 6 |
| ScreenPlanner | Moyenne | 🚧 Phase 3 |
| Commandes vocales | Basse | 📋 Roadmap |
| Multi-langues | Basse | 📋 Roadmap |
| Intégration Slack | Basse | 📋 Roadmap |

### 📋 Phases du workflow idéal

| Phase | Description | Statut |
|-------|-------------|--------|
| Phase 1 | Template → HTML | 🚧 En cours |
| Phase 2 | Extraction principes graphiques | 🚧 En cours |
| Phase 3 | Câblage genome + plan écrans | 📋 Planifié |
| Phase 4 | Génération corps (STOP) | 📋 Planifié |
| Phase 5 | Corps 1 + Organes + Chatbot | 📋 Planifié |
| Phase 6 | Addendum + Questions + Corps N+1 | 📋 Planifié |

---

## Références

### Documentation associée

- `docs/02-sullivan/AGENT_CHATBOT_GUIDE.md` — Guide utilisateur agent
- `docs/02-sullivan/FRONTEND_MODE.md` — Documentation FrontendMode
- `docs/02-sullivan/SULLIVAN_WORKFLOW_IDEAL.md` — Workflow complet 6 phases
- `docs/02-sullivan/PRD_SULLIVAN.md` — Spécifications produit
- `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md` — Mode d'emploi

### Fichiers source clés

- `Backend/Prod/sullivan/agent/sullivan_agent.py` — Agent principal (476 lignes)
- `Backend/Prod/sullivan/agent/tools.py` — Outils (1000+ lignes)
- `Backend/Prod/sullivan/agent/memory.py` — Mémoire (248 lignes)
- `Backend/Prod/sullivan/agent/personalities/sullivan_default.py` — Personnalité pro
- `Backend/Prod/sullivan/agent/personalities/sullivan_weirdo.py` — Personnalité créative

---

*Rapport généré le 3 février 2026*  
*Système: AetherFlow v2.2 — Sullivan Chatbot-Agent*
