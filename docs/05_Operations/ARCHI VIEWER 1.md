#ARCHI VIEWER
# **PLAN DÉTAILLÉ : VIEWER SANS INFERENCE LOCALE**

## **🎯 OBJECTIF PRIMAIRE**
Dashboard de monitoring de l'apprentissage **sans GPU, sans LLM, sans inférence**.  
Interface de visualisation pure pour KIMI (et Sullivan).

---

## **🏗️ ARCHITECTURE TECHNIQUE COMPLÈTE**

### **1. Stack Backend (Python)**
```yaml
# requirements-viewer.txt
fastapi==0.104.1          # API moderne, async
uvicorn[standard]==0.24.0 # Serveur ASGI
sqlalchemy==2.0.23        # ORM pour abstraction BDD
pydantic==2.5.0           # Validation données
pandas==2.1.4             # Analyse données
plotly==5.18.0            # Génération graphs (côté serveur)
python-multipart==0.0.6   # Upload fichiers
python-jose[cryptography]==3.3.0 # JWT si auth
```

### **2. Base de Données**
```sql
-- Structure SQLite (démarrage) -> PostgreSQL (scale)
CREATE TABLE learning_examples (
    id UUID PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    session_id VARCHAR(255),
    task_description TEXT,
    code_context TEXT,
    success BOOLEAN,
    metrics JSON,  -- {"tests_passed": 3, "execution_time": 2.5}
    tags JSON,     -- ["bug_fix", "auth", "refactor"]
    model_used VARCHAR(100),
    tokens_consumed INTEGER,
    human_feedback TEXT NULL
);

CREATE INDEX idx_timestamp ON learning_examples(timestamp);
CREATE INDEX idx_success ON learning_examples(success);
CREATE INDEX idx_tags ON learning_examples(tags);
```

### **3. Structure des Fichiers**
```
Backend/Prod/viewer/
├── 📁 api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principale
│   ├── endpoints/
│   │   ├── examples.py      # CRUD des exemples
│   │   ├── stats.py         # Statistiques
│   │   ├── export.py        # Export données
│   │   └── search.py        # Recherche
│   └── middleware/
│       ├── auth.py          # Authentification (optionnel)
│       └── logging.py       # Logging requêtes
├── 📁 core/
│   ├── database.py          # Configuration BDD
│   ├── models.py            # Modèles SQLAlchemy
│   ├── schemas.py           # Schémas Pydantic
│   └── config.py            # Configuration
├── 📁 services/
│   ├── stats_service.py     # Calcul statistiques
│   ├── export_service.py    # Service d'export
│   └── cache_service.py     # Cache résultats
├── 📁 utils/
│   ├── data_processor.py    # Traitement données
│   ├── formatters.py        # Formatage sortie
│   └── validators.py        # Validation entrées
├── 📁 static/               # Fichiers statiques
│   ├── index.html
│   └── favicon.ico
├── 📁 tests/
│   ├── test_api.py
│   └── test_services.py
├── 📄 requirements.txt
├── 📄 docker-compose.yml    # Pour PostgreSQL
├── 📄 .env.example          # Variables d'environnement
└── 📄 README.md             # Documentation setup
```

---

## **🚀 PHASES D'IMPLÉMENTATION**

### **Phase 1 : MVP (J1-J3)**
```python
# Backend/Prod/viewer/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./learning.db"
# Plus tard : "postgresql://user:pass@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite only
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### **Phase 2 : API Complète (J4-J7)**
```python
# Backend/Prod/viewer/api/endpoints/examples.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/examples", tags=["examples"])

@router.get("/")
async def get_examples(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    success: Optional[bool] = None,
    tags: Optional[List[str]] = Query(None),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Récupère les exemples avec filtres"""
    query = db.query(LearningExample)
    
    if success is not None:
        query = query.filter(LearningExample.success == success)
    
    if tags:
        query = query.filter(LearningExample.tags.contains(tags))
    
    if start_date:
        query = query.filter(LearningExample.timestamp >= start_date)
    
    if end_date:
        query = query.filter(LearningExample.timestamp <= end_date)
    
    return query.offset(skip).limit(limit).all()
```

### **Phase 3 : Statistiques (J8-J10)**
```python
# Backend/Prod/viewer/services/stats_service.py
class StatsService:
    async def get_dashboard_stats(self, db: Session, days: int = 30):
        """Calcule toutes les stats pour le dashboard"""
        
        # 1. Métriques de base
        total_examples = await self._count_examples(db)
        success_rate = await self._calculate_success_rate(db, days)
        
        # 2. Par catégorie
        by_category = await self._group_by_tags(db, days)
        
        # 3. Tendances temporelles
        daily_trends = await self._get_daily_trends(db, days)
        
        # 4. Performance modèles
        model_performance = await self._compare_models(db, days)
        
        return {
            "summary": {
                "total_examples": total_examples,
                "success_rate": f"{success_rate:.1%}",
                "avg_execution_time": await self._avg_execution_time(db),
                "total_tokens": await self._sum_tokens(db)
            },
            "categories": by_category,
            "trends": daily_trends,
            "models": model_performance,
            "top_patterns": await self._identify_top_patterns(db, days)
        }
```

### **Phase 4 : Frontend Simple (J11-J14)**
```html
<!-- Backend/Prod/viewer/static/index.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>AETHERFLOW Learning Viewer</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        /* CSS minimaliste mais fonctionnel */
        .dashboard { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
        .card { padding: 20px; border-radius: 8px; background: #f5f5f5; }
        .success { color: #10b981; }
        .failure { color: #ef4444; }
    </style>
</head>
<body>
    <h1>📊 AETHERFLOW Learning Dashboard</h1>
    
    <div class="dashboard">
        <div class="card" id="total-examples">...</div>
        <div class="card" id="success-rate">...</div>
        <div class="card" id="avg-time">...</div>
        <div class="card" id="total-tokens">...</div>
    </div>
    
    <div>
        <canvas id="trend-chart" width="800" height="300"></canvas>
    </div>
    
    <div>
        <h3>Derniers exemples</h3>
        <table id="examples-table">
            <thead><tr><th>Date</th><th>Description</th><th>Succès</th><th>Tags</th></tr></thead>
            <tbody></tbody>
        </table>
    </div>
    
    <script src="dashboard.js"></script>
</body>
</html>
```

---

## **🔧 COMMANDES DE DÉMARRAGE**

### **Setup Local (5 minutes)**
```bash
# 1. Clone/Création structure
mkdir -p Backend/Prod/viewer && cd Backend/Prod/viewer

# 2. Environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# 3. Installation dépendances
pip install fastapi uvicorn sqlalchemy pydantic pandas

# 4. Initialisation BDD
python -c "
from core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('✅ Base de données initialisée')
"

# 5. Lancer le serveur
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### **API Immédiatement Disponible**
```
GET    /api/health                 # Santé du service
GET    /api/examples               # Liste exemples
GET    /api/examples/{id}          # Détail exemple
GET    /api/stats                  # Statistiques
GET    /api/stats/daily            # Tendances quotidiennes
GET    /api/stats/categories       # Par catégorie
GET    /api/export/json            # Export JSON
GET    /api/export/csv             # Export CSV
POST   /api/search                 # Recherche avancée
```

---

## **📊 MÉTRIQUES AFFICHÉES**

### **Section 1 : Vue d'ensemble**
```
🎯 Taux de succès global : 87.5% (+2.1% sur 7j)
📈 Total exemples : 1,247
⚡ Temps moyen d'exécution : 2.3s
🔢 Tokens consommés : 4.8M
```

### **Section 2 : Performance par domaine**
```javascript
// Données pour graphique
{
  "code_generation": {"examples": 450, "success": 0.92},
  "bug_fixing": {"examples": 320, "success": 0.76},
  "refactoring": {"examples": 280, "success": 0.88},
  "test_generation": {"examples": 197, "success": 0.81}
}
```

### **Section 3 : Tendances temporelles**
```
📅 Évolution sur 30 jours :
- Semaine 1 : 78% → Semaine 2 : 82% → Semaine 3 : 85% → Semaine 4 : 87.5%
- Amélioration : +9.5% en 30 jours
```

### **Section 4 : Derniers exemples (table)**
| Date | Description | Succès | Tags | Modèle | Tokens |
|------|-------------|---------|------|--------|--------|
| 2026-01-20 | Fix auth middleware | ✅ | [bug, auth] | Mistral 7B | 1,240 |
| 2026-01-20 | Add user profile API | ✅ | [feature, api] | Mistral 7B | 2,150 |

---

## **🔗 INTÉGRATION AVEC KIMI EXISTANT**

### **Option 1 : API Directe**
```python
# Dans le code existant de KIMI
import requests

class KIMIViewerIntegration:
    def __init__(self, viewer_url="http://localhost:8000"):
        self.viewer_url = viewer_url
    
    def log_example(self, example_data):
        """Envoie un exemple au viewer"""
        response = requests.post(
            f"{self.viewer_url}/api/examples",
            json=example_data,
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 201
    
    def get_insights(self):
        """Récupère des insights pour amélioration"""
        stats = requests.get(f"{self.viewer_url}/api/stats").json()
        
        # Logique KIMI pour adapter sa classification
        if stats["success_rate"] < 0.7:
            return {"action": "increase_code_review"}
        elif stats["categories"]["bug_fixing"]["success"] < 0.6:
            return {"action": "focus_bug_patterns"}
        
        return {"action": "continue"}
```

### **Option 2 : Fichier Partagé**
```python
# Écriture dans un fichier JSON partagé
import json
from datetime import datetime

def log_to_shared_file(example):
    log_entry = {
        **example,
        "timestamp": datetime.now().isoformat(),
        "kimi_version": "1.2.3",
        "workflow_id": "kim123"
    }
    
    with open("/shared/learning_logs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## **🚢 DÉPLOIEMENT PRODUCTION**

### **Option A : Docker Simple**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  viewer:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data  # Persistance SQLite
    environment:
      - DATABASE_URL=sqlite:///./data/learning.db
```

### **Option B : Serverless (Vercel/Render)**
```python
# Pour Vercel/Serverless
# api/main.py doit être adapté
```

---

## **📈 ROADMAP POST-VIEWER**

### **Semaine 3 : Ajouts**
- [ ] Filtres avancés (regex sur code)
- [ ] Comparaison A/B de modèles
- [ ] Alertes email/webhook
- [ ] Intégration Git (liens vers commits)

### **Semaine 4 : Évolutions**
- [ ] Plugin VS Code
- [ ] API GraphQL
- [ ] Role-based access (Sullivan, KIMI, Admin)
- [ ] Backup automatique

---

## **🎯 LIVRABLES POUR KIMI**

### **À J+7 :**
- ✅ API REST complète
- ✅ Dashboard web basique
- ✅ Base SQLite avec 1 mois de rétention
- ✅ Script d'import des données existantes

### **À J+14 :**
- ✅ Filtres et recherche
- ✅ Graphiques interactifs
- ✅ Export données
- ✅ Documentation API

### **À J+30 :**
- ✅ Intégration continue
- ✅ Monitoring perf
- ✅ Plugin VS Code
- ✅ Alerting

---

## **📞 SUPPORT & MAINTENANCE**

### **Endpoints de monitoring :**
```
GET /api/health        # Status service
GET /api/metrics       # Métriques Prometheus
GET /api/logs/tail     # Derniers logs
```

### **Variables d'environnement :**
```bash
DATABASE_URL=sqlite:///./learning.db
# ou DATABASE_URL=postgresql://user:pass@host/db
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000
ENABLE_AUTH=false  # true pour production
```

---

**Ce plan donne à KIMI :**
1. **Un système opérationnel en 3 jours**
2. **Zéro dépendance GPU/LLM**
3. **Une API propre pour intégration**
4. **Une base pour les phases suivantes (VLM, fine-tuning)**

**Première action :** `mkdir -p Backend/Prod/viewer` et copier le `requirements.txt`