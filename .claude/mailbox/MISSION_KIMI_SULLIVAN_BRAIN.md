# MISSION : Sullivan Brain v2 - Cerveau Autonome

**Date** : 6 février 2026
**Assigné à** : Kimi (Binôme HomeOS/Sullivan)
**Priorité** : CRITIQUE

---

## 🚨 PROBLÈME

Sullivan est une coquille vide. Il délègue tout à Gemini API et quand ça rate, il ne fait rien.
Les logs montrent : KIMI fait le travail, Sullivan est juste initialisé.

**Sullivan doit fonctionner SEUL, sans Claude/KIMI derrière.**

---

## 🎯 OBJECTIF

Implémenter un **cerveau autonome** pour Sullivan :
1. **MiniLM local** (CPU) pour comprendre les intentions
2. **Patterns HCI** en JSON pour les décisions
3. **Mode AetherFlow casuistique** pour conditionner le jugement

---

## 📐 ARCHITECTURE

```
User Input
    │
    ▼
┌─────────────────────────────────────────┐
│  SULLIVAN BRAIN (local, pas d'API)      │
│                                         │
│  1. MiniLM encode l'input               │
│  2. Match avec patterns HCI             │
│  3. Sélectionne le mode AetherFlow      │
│  4. Exécute l'action appropriée         │
└─────────────────────────────────────────┘
    │
    ▼
Action locale OU appel API (si vraiment nécessaire)
```

---

## 📁 FICHIERS À CRÉER

### 1. `Backend/Prod/sullivan/brain/embedder.py`

```python
"""
MiniLM Embedder - Compréhension locale CPU-friendly.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
from functools import lru_cache

class LocalEmbedder:
    """Embeddings locaux avec MiniLM (CPU, ~30ms par phrase)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        # MiniLM-L6-v2 : 80MB, CPU-friendly, très rapide
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache = {}

    def encode(self, text: str) -> np.ndarray:
        """Encode un texte en vecteur 384D."""
        if text in self.cache:
            return self.cache[text]

        embedding = self.model.encode(text, convert_to_numpy=True)
        self.cache[text] = embedding
        return embedding

    def similarity(self, text1: str, text2: str) -> float:
        """Cosine similarity entre deux textes."""
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

    def find_best_match(self, query: str, candidates: List[str]) -> tuple:
        """Trouve le meilleur match parmi des candidats."""
        query_emb = self.encode(query)

        best_score = -1
        best_match = None

        for candidate in candidates:
            cand_emb = self.encode(candidate)
            score = float(np.dot(query_emb, cand_emb) /
                         (np.linalg.norm(query_emb) * np.linalg.norm(cand_emb)))
            if score > best_score:
                best_score = score
                best_match = candidate

        return best_match, best_score


# Singleton global
embedder = LocalEmbedder()
```

### 2. `Backend/Prod/sullivan/brain/patterns.py`

```python
"""
Patterns HCI - Base de connaissances pour décisions.
"""

from typing import Dict, List, Any
from pathlib import Path
import json

# Patterns HCI en dur (pas de fichier externe pour l'instant)
HCI_PATTERNS = {
    # === NAVIGATION ===
    "navigation_simple": {
        "triggers": ["aller", "ouvrir", "montre", "affiche", "va", "go", "open", "show"],
        "mode": "quick",
        "action_type": "navigate",
        "components": ["link", "button", "menu"],
        "confidence_threshold": 0.6
    },
    "navigation_complexe": {
        "triggers": ["parcours", "workflow", "étapes", "wizard", "steps"],
        "mode": "frontend",
        "action_type": "multi_step",
        "components": ["stepper", "tabs", "breadcrumb"],
        "confidence_threshold": 0.7
    },

    # === DATA DISPLAY ===
    "data_liste": {
        "triggers": ["liste", "tous", "affiche", "montre les", "list", "all", "show all"],
        "mode": "frontend",
        "action_type": "display_list",
        "components": ["table", "list", "cards"],
        "confidence_threshold": 0.65
    },
    "data_detail": {
        "triggers": ["détail", "info", "voir", "profil", "detail", "info", "view"],
        "mode": "frontend",
        "action_type": "display_detail",
        "components": ["card", "stat", "profile"],
        "confidence_threshold": 0.65
    },
    "data_stats": {
        "triggers": ["stats", "statistiques", "métriques", "dashboard", "metrics"],
        "mode": "frontend",
        "action_type": "display_stats",
        "components": ["stat", "chart", "progress"],
        "confidence_threshold": 0.7
    },

    # === FORMS / INPUT ===
    "form_creation": {
        "triggers": ["créer", "ajouter", "nouveau", "create", "add", "new"],
        "mode": "frontend",
        "action_type": "form_create",
        "components": ["form", "input", "button"],
        "confidence_threshold": 0.7
    },
    "form_edit": {
        "triggers": ["modifier", "éditer", "changer", "update", "edit", "change"],
        "mode": "frontend",
        "action_type": "form_edit",
        "components": ["form", "input", "button"],
        "confidence_threshold": 0.7
    },
    "form_search": {
        "triggers": ["chercher", "recherche", "filtrer", "search", "find", "filter"],
        "mode": "frontend",
        "action_type": "form_search",
        "components": ["input", "select", "filter"],
        "confidence_threshold": 0.65
    },

    # === ACTIONS ===
    "action_delete": {
        "triggers": ["supprimer", "effacer", "retirer", "delete", "remove"],
        "mode": "backend",
        "action_type": "delete",
        "components": ["modal", "button", "alert"],
        "confidence_threshold": 0.8  # Plus strict pour actions destructives
    },
    "action_submit": {
        "triggers": ["envoyer", "valider", "soumettre", "submit", "send", "confirm"],
        "mode": "backend",
        "action_type": "submit",
        "components": ["button", "loading", "toast"],
        "confidence_threshold": 0.7
    },

    # === ARCHITECTURE ===
    "arch_analyse": {
        "triggers": ["analyse", "examine", "regarde", "check", "analyze", "review"],
        "mode": "backend",
        "action_type": "analyze",
        "components": [],
        "confidence_threshold": 0.6
    },
    "arch_generate": {
        "triggers": ["génère", "crée le code", "implémente", "generate", "implement"],
        "mode": "production",
        "action_type": "generate",
        "components": [],
        "confidence_threshold": 0.75
    },

    # === DESIGN ===
    "design_layout": {
        "triggers": ["layout", "mise en page", "structure", "disposition"],
        "mode": "designer",
        "action_type": "layout",
        "components": ["drawer", "navbar", "footer", "hero"],
        "confidence_threshold": 0.7
    },
    "design_component": {
        "triggers": ["composant", "widget", "élément", "component", "element"],
        "mode": "designer",
        "action_type": "component",
        "components": [],
        "confidence_threshold": 0.65
    },
    "design_style": {
        "triggers": ["style", "couleur", "thème", "apparence", "color", "theme"],
        "mode": "designer",
        "action_type": "style",
        "components": [],
        "confidence_threshold": 0.7
    }
}

# Mapping Mode AetherFlow
AETHERFLOW_MODES = {
    "quick": {
        "flag": "-q",
        "description": "Actions rapides, navigation",
        "provider": "groq",
        "max_tokens": 150
    },
    "frontend": {
        "flag": "-frd",
        "description": "Génération UI/composants",
        "provider": "deepseek",
        "max_tokens": 2000
    },
    "backend": {
        "flag": "-bkd",
        "description": "Logique métier, API",
        "provider": "deepseek",
        "max_tokens": 2000
    },
    "production": {
        "flag": "-f",
        "description": "Code production",
        "provider": "gemini",
        "max_tokens": 4000
    },
    "designer": {
        "flag": "designer",
        "description": "Analyse visuelle, design",
        "provider": "gemini",  # Vision
        "max_tokens": 2000
    }
}


class PatternMatcher:
    """Match les intentions avec les patterns HCI."""

    def __init__(self, embedder):
        self.embedder = embedder
        self.patterns = HCI_PATTERNS
        self.modes = AETHERFLOW_MODES

        # Pré-calculer les embeddings des triggers
        self._precompute_triggers()

    def _precompute_triggers(self):
        """Pré-calcule les embeddings de tous les triggers."""
        self.trigger_embeddings = {}
        for pattern_name, pattern in self.patterns.items():
            for trigger in pattern["triggers"]:
                if trigger not in self.trigger_embeddings:
                    self.trigger_embeddings[trigger] = self.embedder.encode(trigger)

    def match(self, user_input: str) -> Dict[str, Any]:
        """
        Match l'input utilisateur avec le meilleur pattern.

        Returns:
            {
                "pattern": nom du pattern,
                "confidence": score de confiance,
                "mode": mode AetherFlow,
                "action_type": type d'action,
                "components": composants suggérés,
                "matched_trigger": trigger qui a matché
            }
        """
        input_lower = user_input.lower()
        input_emb = self.embedder.encode(input_lower)

        best_match = None
        best_score = 0
        best_trigger = None

        for pattern_name, pattern in self.patterns.items():
            for trigger in pattern["triggers"]:
                # 1. Match exact (rapide)
                if trigger in input_lower:
                    score = 0.95  # Bonus pour match exact
                else:
                    # 2. Match sémantique
                    trigger_emb = self.trigger_embeddings[trigger]
                    score = float(np.dot(input_emb, trigger_emb) /
                                 (np.linalg.norm(input_emb) * np.linalg.norm(trigger_emb)))

                if score > best_score and score >= pattern["confidence_threshold"]:
                    best_score = score
                    best_match = pattern_name
                    best_trigger = trigger

        if best_match:
            pattern = self.patterns[best_match]
            return {
                "pattern": best_match,
                "confidence": best_score,
                "mode": pattern["mode"],
                "mode_config": self.modes[pattern["mode"]],
                "action_type": pattern["action_type"],
                "components": pattern["components"],
                "matched_trigger": best_trigger
            }

        # Fallback : mode quick par défaut
        return {
            "pattern": "unknown",
            "confidence": 0.0,
            "mode": "quick",
            "mode_config": self.modes["quick"],
            "action_type": "unknown",
            "components": [],
            "matched_trigger": None
        }


# Import numpy pour les calculs
import numpy as np
```

### 3. `Backend/Prod/sullivan/brain/brain.py`

```python
"""
Sullivan Brain - Cerveau autonome principal.
"""

from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

from .embedder import embedder, LocalEmbedder
from .patterns import PatternMatcher, AETHERFLOW_MODES


class SullivanBrain:
    """
    Cerveau autonome de Sullivan.

    Comprend les intentions localement (MiniLM) et décide du mode AetherFlow
    AVANT d'appeler une API externe.
    """

    def __init__(self):
        self.embedder = embedder
        self.matcher = PatternMatcher(self.embedder)
        self.context = {}
        self.history = []

        logger.info("SullivanBrain initialized (local MiniLM)")

    def understand(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprend l'intention de l'utilisateur.

        Args:
            user_input: Message de l'utilisateur
            context: Contexte additionnel (genome, session, etc.)

        Returns:
            Understanding dict avec pattern, mode, action, components
        """
        # 1. Match avec patterns HCI
        match_result = self.matcher.match(user_input)

        # 2. Enrichir avec le contexte si disponible
        if context:
            match_result = self._enrich_with_context(match_result, context)

        # 3. Logger pour apprentissage
        self._log_understanding(user_input, match_result)

        return match_result

    def decide_action(self, understanding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Décide de l'action à prendre basé sur la compréhension.

        Returns:
            {
                "should_call_api": bool,
                "api_provider": str ou None,
                "local_action": str ou None,
                "mode_flag": str,
                "suggested_prompt": str
            }
        """
        mode = understanding["mode"]
        mode_config = understanding["mode_config"]
        action_type = understanding["action_type"]

        # Actions qui peuvent être locales
        local_actions = ["navigate", "display_list", "display_detail"]

        if action_type in local_actions and understanding["confidence"] > 0.8:
            return {
                "should_call_api": False,
                "api_provider": None,
                "local_action": action_type,
                "mode_flag": mode_config["flag"],
                "suggested_prompt": None
            }

        # Sinon, appel API avec le bon provider
        return {
            "should_call_api": True,
            "api_provider": mode_config["provider"],
            "local_action": None,
            "mode_flag": mode_config["flag"],
            "suggested_prompt": self._build_prompt(understanding),
            "max_tokens": mode_config["max_tokens"]
        }

    def _enrich_with_context(self, match: Dict, context: Dict) -> Dict:
        """Enrichit le match avec le contexte."""
        # Si on a un genome, suggérer des composants existants
        if "genome" in context:
            genome = context["genome"]
            if match["components"]:
                # Filtrer les composants qui existent dans le genome
                existing = [c for c in match["components"]
                           if self._component_exists_in_genome(c, genome)]
                match["existing_components"] = existing

        return match

    def _component_exists_in_genome(self, comp_name: str, genome: Dict) -> bool:
        """Vérifie si un composant existe dans le genome."""
        # Parcourir les corps/organes/atomes
        for corps in genome.get("corps", []):
            for organe in corps.get("organes", []):
                for atome in organe.get("atomes", []):
                    if comp_name in atome.get("component_ref", ""):
                        return True
        return False

    def _build_prompt(self, understanding: Dict) -> str:
        """Construit un prompt optimisé pour l'API."""
        mode = understanding["mode"]
        action = understanding["action_type"]
        components = understanding.get("components", [])

        base_prompt = f"Mode: {mode}. Action: {action}."

        if components:
            base_prompt += f" Composants suggérés: {', '.join(components)}."

        return base_prompt

    def _log_understanding(self, user_input: str, result: Dict):
        """Log pour apprentissage futur."""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "pattern": result["pattern"],
            "confidence": result["confidence"],
            "mode": result["mode"]
        })

        logger.debug(f"Brain understood: {result['pattern']} "
                    f"(conf={result['confidence']:.2f}, mode={result['mode']})")


# Singleton global
sullivan_brain = SullivanBrain()
```

### 4. `Backend/Prod/sullivan/brain/__init__.py`

```python
"""
Sullivan Brain - Cerveau autonome local.
"""

from .brain import SullivanBrain, sullivan_brain
from .embedder import LocalEmbedder, embedder
from .patterns import PatternMatcher, HCI_PATTERNS, AETHERFLOW_MODES

__all__ = [
    "SullivanBrain",
    "sullivan_brain",
    "LocalEmbedder",
    "embedder",
    "PatternMatcher",
    "HCI_PATTERNS",
    "AETHERFLOW_MODES"
]
```

---

## 🔌 INTÉGRATION

### Modifier `Backend/Prod/sullivan/agent/sullivan_agent.py`

Ajouter au début du process :

```python
from ..brain import sullivan_brain

class SullivanAgent:
    def process_message(self, message: str, context: dict = None):
        # 1. BRAIN comprend localement (PAS d'API)
        understanding = sullivan_brain.understand(message, context)

        # 2. BRAIN décide de l'action
        decision = sullivan_brain.decide_action(understanding)

        # 3. Si action locale possible, exécuter sans API
        if not decision["should_call_api"]:
            return self._execute_local_action(decision["local_action"], understanding)

        # 4. Sinon, appeler l'API avec le bon provider et prompt
        return self._call_api(
            provider=decision["api_provider"],
            prompt=decision["suggested_prompt"],
            max_tokens=decision["max_tokens"]
        )
```

---

## 📦 DÉPENDANCES

Ajouter dans `requirements.txt` :

```
sentence-transformers>=2.2.0
```

Installation :
```bash
pip install sentence-transformers
```

Note : Le modèle MiniLM-L6-v2 (~80MB) se télécharge au premier lancement.

---

## ✅ TESTS

```python
# Test du brain
from sullivan.brain import sullivan_brain

# Test compréhension
result = sullivan_brain.understand("montre moi la liste des utilisateurs")
print(result)
# Expected: pattern=data_liste, mode=frontend, components=[table, list, cards]

result = sullivan_brain.understand("supprime cet élément")
print(result)
# Expected: pattern=action_delete, mode=backend, confidence>0.8

result = sullivan_brain.understand("crée un nouveau formulaire")
print(result)
# Expected: pattern=form_creation, mode=frontend, components=[form, input, button]
```

---

## 🎯 RÉSULTAT ATTENDU

Sullivan avec ce cerveau :
1. **Comprend** l'intention en local (~30ms, CPU)
2. **Décide** du mode AetherFlow approprié
3. **Exécute** localement si possible
4. **Appelle** l'API externe seulement si nécessaire, avec le bon provider

Plus de "Sullivan initialisé mais ne fait rien".

---

*Mission critique pour l'autonomie de HomeOS.*
