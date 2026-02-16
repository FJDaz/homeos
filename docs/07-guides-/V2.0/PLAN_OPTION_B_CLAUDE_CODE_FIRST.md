# Plan Option B : Claude Code First

## Vision

Transformer AETHERFLOW en **worker pool** appelable par Claude Code. Claude Code reste le cerveau (gratuit via abonnement), AETHERFLOW devient un outil CLI/MCP pour déléguer la génération de code brute aux APIs économiques (DeepSeek, Codestral, Gemini, Groq).

---

## Architecture Cible

```
┌─────────────────────────────────────────────────────────┐
│                    CLAUDE CODE                          │
│              (Abonnement - pas d'API)                   │
│                                                         │
│  • Comprend la demande utilisateur                      │
│  • Analyse le contexte du projet                        │
│  • Décide : faire lui-même OU déléguer                  │
│  • Valide et intègre les résultats                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   AETHERFLOW CLI                        │
│              (Outil appelable par Claude Code)          │
│                                                         │
│  aetherflow generate --task "..." --provider auto      │
│  aetherflow generate --task "..." --provider deepseek  │
│  aetherflow generate --task "..." --provider codestral │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   AGENT ROUTER                          │
│                                                         │
│  Si --provider auto :                                   │
│    • Code génération complexe → DeepSeek V3            │
│    • Édition locale/FIM → Codestral                    │
│    • Analyse rapide → Gemini Flash                     │
│    • Prototypage rapide → Groq Llama                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 PROVIDERS (APIs tierces)                │
│                                                         │
│  DeepSeek   │  Codestral  │  Gemini  │  Groq           │
│  $0.14/1M   │  $0.30/1M   │  Gratuit │  Gratuit*       │
│  tokens     │  tokens     │  (quota) │  (quota)        │
└─────────────────────────────────────────────────────────┘
```

---

## Phases d'Implémentation

### Phase 1 : CLI Simplifiée (1-2 jours)

**Objectif** : Créer une commande `aetherflow generate` que Claude Code peut appeler directement.

**Fichiers à créer/modifier** :

```
Backend/Prod/
├── cli_generate.py      # NOUVEAU - CLI simplifiée
├── models/
│   └── agent_router.py  # NOUVEAU - Router de base
```

**Interface CLI** :

```bash
# Génération simple avec provider explicite
aetherflow generate \
  --task "Crée une fonction Python qui valide un email" \
  --provider deepseek \
  --output generated_code.py

# Génération avec routage automatique
aetherflow generate \
  --task "Crée un middleware JWT pour FastAPI" \
  --provider auto \
  --context "Framework: FastAPI, Auth: JWT" \
  --output middleware.py

# Avec fichier de contexte
aetherflow generate \
  --task "Refactorise cette fonction" \
  --context-file src/utils.py \
  --provider codestral \
  --output refactored.py
```

**Livrables** :
- [ ] `cli_generate.py` avec argparse
- [ ] `agent_router.py` avec sélection basique (deepseek par défaut)
- [ ] Retourne le code sur stdout (pour capture par Claude Code)

---

### Phase 2 : Multi-Provider (2-3 jours)

**Objectif** : Intégrer les 4 providers avec leurs spécialités.

**Fichiers à créer** :

```
Backend/Prod/models/
├── base_client.py       # NOUVEAU - Interface commune
├── deepseek_client.py   # EXISTANT - À adapter
├── codestral_client.py  # NOUVEAU
├── gemini_client.py     # NOUVEAU
├── groq_client.py       # NOUVEAU
├── agent_router.py      # Mise à jour
```

**Interface commune** :

```python
class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: str = "") -> GenerationResult:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def specialties(self) -> List[str]:
        pass
```

**Matrice de routage** :

| Critère | DeepSeek | Codestral | Gemini | Groq |
|---------|----------|-----------|--------|------|
| Code complexe (>100 LOC) | ✅ Primary | | | |
| Édition locale/FIM | | ✅ Primary | | |
| Analyse/parsing | | | ✅ Primary | |
| Prototypage rapide | | | | ✅ Primary |
| Fallback général | ✅ | | | |

**Livrables** :
- [ ] `base_client.py` avec interface abstraite
- [ ] `codestral_client.py` fonctionnel
- [ ] `gemini_client.py` fonctionnel
- [ ] `groq_client.py` fonctionnel
- [ ] `agent_router.py` avec logique de sélection

---

### Phase 3 : Routage Intelligent (1-2 jours)

**Objectif** : Le router analyse la tâche et choisit le meilleur provider.

**Logique de routage** :

```python
class AgentRouter:
    def select_provider(self, task: str, context: str = "") -> str:
        # Analyse par mots-clés et patterns
        task_lower = task.lower()

        # Codestral : éditions locales, refactoring précis
        if any(kw in task_lower for kw in ["refactor", "rename", "extract", "fix", "edit", "modify"]):
            return "codestral"

        # Gemini : analyse, parsing, documentation
        if any(kw in task_lower for kw in ["analyze", "parse", "explain", "document", "review"]):
            return "gemini"

        # Groq : prototypage rapide, brainstorming
        if any(kw in task_lower for kw in ["prototype", "draft", "quick", "sketch", "brainstorm"]):
            return "groq"

        # DeepSeek : génération de code complexe (défaut)
        return "deepseek"
```

**Livrables** :
- [ ] Logique de sélection par analyse de tâche
- [ ] Support `--provider auto` dans CLI
- [ ] Logging du provider sélectionné

---

### Phase 4 : Intégration Claude Code (1 jour)

**Objectif** : Documenter et tester l'usage depuis Claude Code.

**Workflow type** :

```
Utilisateur : "Crée un module d'authentification JWT pour mon API FastAPI"

Claude Code (réflexion interne) :
  - Tâche de génération de code complexe
  - Je vais déléguer à AETHERFLOW

Claude Code exécute :
  $ aetherflow generate \
      --task "Crée un module d'authentification JWT complet pour FastAPI avec:
              - Modèle User avec hash password
              - Endpoints /register, /login, /me
              - Middleware de vérification JWT
              - Configuration via variables d'environnement" \
      --provider auto \
      --context "Framework: FastAPI, DB: SQLAlchemy, Auth: python-jose"

AETHERFLOW :
  - Router sélectionne DeepSeek (code complexe)
  - DeepSeek génère le code
  - Retourne sur stdout

Claude Code :
  - Lit le code généré
  - Valide la qualité
  - Intègre dans le projet (crée les fichiers)
  - Peut demander des corrections si nécessaire
```

**Livrables** :
- [ ] Guide d'utilisation pour Claude Code
- [ ] Exemples de prompts types
- [ ] Tests end-to-end

---

## Configuration

**Variables d'environnement** (.env) :

```ini
# DeepSeek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-coder

# Codestral (Mistral)
MISTRAL_API_KEY=xxx
CODESTRAL_MODEL=codestral-latest

# Gemini
GOOGLE_API_KEY=xxx
GEMINI_MODEL=gemini-1.5-flash

# Groq
GROQ_API_KEY=xxx
GROQ_MODEL=llama-3.3-70b-versatile

# Defaults
DEFAULT_PROVIDER=deepseek
DEFAULT_TIMEOUT=60
DEFAULT_MAX_TOKENS=4000
```

---

## Structure Finale

```
Backend/Prod/
├── __init__.py
├── __main__.py
├── cli_generate.py          # CLI simplifiée pour Claude Code
├── cli.py                   # CLI existante (plans JSON)
├── api.py
├── orchestrator.py
├── config/
│   ├── __init__.py
│   └── settings.py          # Mise à jour avec nouveaux providers
├── models/
│   ├── __init__.py
│   ├── base_client.py       # Interface commune
│   ├── deepseek_client.py   # Adapté
│   ├── codestral_client.py  # Nouveau
│   ├── gemini_client.py     # Nouveau
│   ├── groq_client.py       # Nouveau
│   ├── agent_router.py      # Nouveau
│   ├── plan_reader.py
│   ├── metrics.py
│   └── claude_validator.py
└── prompts/
    └── system_prompts.py    # Prompts par provider
```

---

## Estimation Effort

| Phase | Durée | Complexité |
|-------|-------|------------|
| Phase 1 : CLI Simplifiée | 1-2 jours | Faible |
| Phase 2 : Multi-Provider | 2-3 jours | Moyenne |
| Phase 3 : Routage Intelligent | 1-2 jours | Faible |
| Phase 4 : Intégration | 1 jour | Faible |
| **Total** | **5-8 jours** | |

---

## Avantages de cette approche

1. **Coût minimal** - Claude Code gratuit (abonnement), APIs tierces très économiques
2. **Simplicité** - Pas de plan JSON complexe, juste une commande CLI
3. **Flexibilité** - Claude Code décide quand déléguer
4. **Évolutif** - Facile d'ajouter de nouveaux providers
5. **Debuggable** - Chaque appel est traçable

---

## Décisions différées (Phase future)

- Intégration MCP (Model Context Protocol) pour appel natif depuis Claude
- Cache des résultats pour éviter les appels redondants
- Métriques et dashboard de coûts
- Support du streaming pour les longues générations
- Mode batch pour plusieurs tâches

---

## Prochaine Action

Commencer par **Phase 1** : créer `cli_generate.py` et `agent_router.py` de base avec DeepSeek uniquement, puis tester l'appel depuis Claude Code.
