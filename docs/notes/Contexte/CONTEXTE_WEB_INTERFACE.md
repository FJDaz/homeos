# Contexte pour Interface Web HTML/CSS/SaaS

**Date** : 26 janvier 2025  
**Objectif** : Implémenter l'interface web pour AetherFlow V2.1

---

## 🎯 État Actuel d'AetherFlow

### Architecture Backend

**Composants principaux** :

1. **Orchestrator** (`Backend/Prod/orchestrator.py`)
   - Exécute des plans JSON
   - Gère les workflows PROTO/PROD
   - Supporte les modes FAST/BUILD/DOUBLE-CHECK
   - Parallélisation des étapes indépendantes
   - Rate limiting par provider

2. **Workflows** (`Backend/Prod/workflows/`)
   - **ProtoWorkflow** : FAST → DOUBLE-CHECK (prototypage rapide)
   - **ProdWorkflow** : FAST → BUILD → DOUBLE-CHECK (qualité maximale)

3. **AgentRouter** (`Backend/Prod/models/agent_router.py`)
   - Routage intelligent vers providers (DeepSeek, Gemini, Groq, Codestral)
   - Gestion cache sémantique et prompt cache
   - Injection guidelines en mode BUILD

4. **Métriques** (`Backend/Prod/models/metrics.py`)
   - `StepMetrics` : Métriques par étape
   - `PlanMetrics` : Métriques agrégées du plan
   - Temps, coûts, tokens, cache hits, etc.

5. **API FastAPI** (`Backend/Prod/api.py`)
   - ✅ Endpoint `/execute` : Exécute un plan
   - ✅ Endpoint `/health` : Health check
   - ⚠️ Basique, pas de WebSocket ni streaming

---

## 📊 Données Disponibles pour l'Interface Web

### Métriques en Temps Réel

**Par étape** :
- `step_id`, `step_description`, `step_type`
- `success` (bool)
- `execution_time_ms`
- `tokens_used`, `input_tokens`, `output_tokens`
- `cost_usd`
- `provider` (deepseek, gemini, groq, codestral)
- `cache_hit` (bool)
- `ttft_ms`, `ttr_ms` (latence)

**Par plan** :
- `total_steps`, `successful_steps`, `failed_steps`
- `total_execution_time_ms`
- `total_cost_usd`
- `total_tokens_used`
- `success_rate`
- `cache_hit_rate`

### Résultats d'Exécution

**Structure** :
```python
{
    "success": bool,
    "plan": Plan object,
    "results": {
        "step_1": StepResult,
        "step_2": StepResult,
        ...
    },
    "metrics": PlanMetrics,
    "workflow": "PROTO" | "PROD"
}
```

**StepResult** :
- `success` (bool)
- `output` (str) : Code généré
- `tokens_used` (int)
- `cost_usd` (float)
- `execution_time_ms` (float)

### Feedback Pédagogique (si `--mentor`)

**Structure** :
```python
{
    "is_valid": bool,
    "score": float (0.0-1.0),
    "passed_rules": List[str],
    "violations": [
        {
            "rule": "TDD" | "DRY" | "SOLID" | ...,
            "location": "Line 42",
            "issue": "Description du problème",
            "explanation": "Pourquoi c'est une violation",
            "suggestion": "Comment corriger",
            "code_reference": "Code snippet"
        }
    ]
}
```

---

## 🔌 API Existante

### Endpoints Disponibles

**POST `/execute`** :
```python
Request: {
    "plan_path": str,
    "output_dir": Optional[str],
    "context": Optional[str]
}

Response: {
    "success": bool,
    "task_id": str,
    "results": Dict[str, StepResult],
    "metrics": Dict[str, Any],
    "output_dir": str,
    "message": str
}
```

**GET `/health`** :
```python
Response: {
    "status": "ok",
    "service": "AetherFlow"
}
```

### Limitations Actuelles

- ❌ Pas de WebSocket pour updates temps réel
- ❌ Pas de streaming des résultats
- ❌ Pas d'endpoint pour upload de plans JSON
- ❌ Pas d'endpoint pour récupérer les logs en temps réel
- ❌ Pas d'endpoint pour les métriques de cache

---

## 🎨 Interface Web Requise

### Fonctionnalités Principales

1. **Dashboard Principal**
   - Upload de plan JSON (drag & drop)
   - Sélection workflow (PROTO/PROD)
   - Option Mentor Mode
   - Bouton Start/Stop

2. **Visualisation Workflow**
   - Graphique du plan avec steps
   - Statuts en temps réel (⏳ Running, ✅ Success, ❌ Failed)
   - Barres de progression par étape

3. **Console Temps Réel**
   - Logs d'exécution en streaming
   - Code généré avec syntax highlighting
   - Filtres par niveau (info, success, error)

4. **Métriques Live**
   - Temps total, coût total, tokens
   - Cache hit rate
   - Métriques par provider
   - Graphiques temps réel

5. **Feedback Mentor** (si activé)
   - Affichage des violations de règles
   - Références de code avec highlighting
   - Suggestions d'amélioration

6. **Navigation Résultats**
   - Liste des fichiers générés
   - Téléchargement des résultats
   - Historique des exécutions

---

## 🛠️ Stack Technique Recommandée

### Backend

**FastAPI** (déjà présent) :
- Étendre avec WebSocket pour streaming
- Endpoints pour upload/download
- Endpoints pour métriques

**WebSocket** :
- Streaming des logs en temps réel
- Updates de statut des steps
- Métriques live

### Frontend

**HTML/CSS/JavaScript Vanilla** (pour Mac 2016) :
- Pas de framework lourd (React/Vue)
- CSS Grid/Flexbox pour layout
- WebSocket API native
- Syntax highlighting : Prism.js ou Highlight.js

**Structure** :
```
frontend/
├── index.html          # Dashboard principal
├── css/
│   └── styles.css      # Styles principaux
├── js/
│   ├── app.js          # Logique principale
│   ├── websocket.js    # Gestion WebSocket
│   └── charts.js       # Graphiques métriques
└── assets/
    └── icons/          # Icônes SVG
```

---

## 📋 Endpoints API à Créer/Étendre

### Endpoints Existants (à améliorer)

1. **POST `/execute`** ✅
   - Ajouter support WebSocket pour streaming
   - Retourner task_id immédiatement
   - Permettre polling ou WebSocket pour résultats

### Nouveaux Endpoints à Créer

2. **POST `/upload-plan`**
   - Upload fichier JSON plan
   - Validation du schéma
   - Retourne plan_id

3. **GET `/plan/{plan_id}`**
   - Récupère les détails d'un plan

4. **GET `/execution/{execution_id}/status`**
   - Statut d'une exécution en cours
   - Métriques partielles

5. **GET `/execution/{execution_id}/logs`**
   - Logs d'exécution (streaming via WebSocket)

6. **GET `/execution/{execution_id}/results`**
   - Résultats complets d'une exécution

7. **GET `/execution/{execution_id}/feedback`**
   - Feedback pédagogique (si mentor activé)

8. **GET `/metrics/cache`**
   - Statistiques du cache sémantique

9. **WebSocket `/ws/execution/{execution_id}`**
   - Streaming logs temps réel
   - Updates de statut
   - Métriques live

---

## 🔄 Flux d'Exécution Web

```
1. Utilisateur upload plan.json (drag & drop)
   ↓
2. Frontend envoie POST /upload-plan
   ↓
3. Backend valide et stocke → retourne plan_id
   ↓
4. Utilisateur sélectionne workflow (PROTO/PROD) + options
   ↓
5. Frontend envoie POST /execute avec plan_id
   ↓
6. Backend démarre exécution → retourne execution_id immédiatement
   ↓
7. Frontend ouvre WebSocket /ws/execution/{execution_id}
   ↓
8. Backend stream :
   - Logs en temps réel
   - Updates de statut des steps
   - Métriques partielles
   ↓
9. Quand terminé :
   - Frontend récupère résultats GET /execution/{execution_id}/results
   - Affiche code généré avec syntax highlighting
   - Affiche métriques finales
   - Affiche feedback mentor (si activé)
```

---

## 📁 Structure de Fichiers Proposée

```
AETHERFLOW/
├── frontend/                    # NOUVEAU
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── app.js
│   │   ├── websocket.js
│   │   ├── charts.js
│   │   └── syntax-highlight.js
│   └── assets/
│       └── icons/
│
├── Backend/Prod/
│   ├── api.py                  # À étendre avec WebSocket
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # Routes REST
│   │   ├── websocket.py       # Routes WebSocket
│   │   └── models.py          # Modèles Pydantic
│   └── ...
```

---

## 🎯 Priorités d'Implémentation

### Phase 1 : MVP (Semaine 1)

1. ✅ Étendre FastAPI avec endpoints de base
2. ✅ Créer HTML/CSS dashboard statique
3. ✅ Upload de plan JSON (drag & drop)
4. ✅ Affichage plan avec steps
5. ✅ Bouton Start → POST /execute
6. ✅ Affichage résultats (sans streaming)

### Phase 2 : Temps Réel (Semaine 2)

1. ⏳ WebSocket pour streaming logs
2. ⏳ Updates de statut en temps réel
3. ⏳ Métriques live
4. ⏳ Barres de progression

### Phase 3 : Polish (Semaine 3)

1. ⏳ Syntax highlighting code généré
2. ⏳ Graphiques métriques
3. ⏳ Feedback mentor visuel
4. ⏳ Navigation historique

---

## 🔧 Dépendances Techniques

### Backend

- ✅ FastAPI (déjà présent)
- ⏳ `python-socketio` ou `websockets` pour WebSocket
- ✅ `uvicorn` pour serveur ASGI

### Frontend

- ⏳ Prism.js ou Highlight.js (syntax highlighting)
- ⏳ Chart.js ou D3.js (graphiques - optionnel, peut être simple CSS)
- ✅ WebSocket API native (navigateur)

---

## 📝 Notes Importantes

1. **Performance Mac 2016** :
   - Pas d'animations lourdes
   - CSS optimisé (pas de transitions complexes)
   - JavaScript vanilla (pas de framework)

2. **Compatibilité** :
   - Navigateurs : Safari 10+, Chrome 60+, Firefox 55+
   - Pas de polyfills nécessaires pour WebSocket

3. **Sécurité** :
   - Validation côté serveur des plans JSON
   - Limite taille upload (ex: 10MB max)
   - CORS configuré pour développement

---

**Prêt pour implémentation** : ✅  
**Prochaine étape** : Créer la structure frontend et étendre l'API FastAPI
