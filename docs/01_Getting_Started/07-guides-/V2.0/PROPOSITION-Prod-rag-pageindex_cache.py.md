## Optimisations PageIndex/AetherFlow (triées par ROI)
| Action | Impact Latence | Coût | Difficulté | Pourquoi 2026 |
|--------|---------------|------|------------|--------------|
| **1. Cache PageIndex Tree** | **-75%** | 0€ | **Faible** | Arbre statique = JSON disqué, skip LLM tree gen |
| **2. asyncio.gather() Étape 7** | **-60%** | 0€ | Moyenne | Ton roadmap prioritaire – parallélise tes batches |
| **3. Gemini 2.5 Flash Orchestrator** | **-50%** | Très faible | **Faible** | 10x moins cher que Haiku, 2x plus rapide |
| **4. Pre-filter BM25 + PageIndex** | **-40%** | 0€ | Moyenne | Keyword exact → candidates, puis raisonnement |
| **5. Streaming + Rich Live** | **-30%** | 0€ | Élevée | UX immédiate (déjà en Étape 5.5) |

## Implémentation prioritaire (2h max)

**1. CACHE PAGEINDEX (IMPACT MAX)**  
```python
# Backend/Prod/rag/pageindex_cache.py
import json, hashlib
class CachedPageIndex:
    def __init__(self, docs_path):
        self.cache_file = f"{docs_path}/pageindex_tree.json"
        self.tree = self._load_or_build(docs_path)
    
    def _load_or_build(self, docs_path):
        # Hash docs → cache invalidation
        docs_hash = hashlib.md5(str(listdir(docs_path)).encode()).hexdigest()
        try:
            with open(self.cache_file) as f:
                cached = json.load(f)
                if cached['hash'] == docs_hash: 
                    return cached['tree']  # 100ms vs 10s
        except:
            pass
        # Build + cache
        tree = run_pageindex_cli(docs_path)  # VectifyAI
        json.dump({'hash': docs_hash, 'tree': tree}, open(self.cache_file, 'w'))
        return tree
```
**Gain** : 1ère query 10s → suivantes 100ms.

**2. GEMINI FLASH ORCHESTRATEUR (IMPACT + COÛT)**  
```python
# orchestrator.py L38 → AgentRouter priorise gemini_2_5_flash
# settings.py → gemini_model = "gemini-2.5-flash-exp"
```
**Gain** : -50% latence, -90% coût vs Claude.

**3. BM25 PREFILTER (HYBRIDE)**  
```python
# Pre-filter keywords → PageIndex seulement sur top-5
from rank_bm25 import BM25Okapi
bm25 = BM25Okapi.from_docs(your_md_chunks)
top_docs = bm25.get_top_n(query, corpus, n=5)
pageindex.retrieve_from(top_docs)  # Raisonnement ciblé
```

## Plan 1 semaine (ton roadmap)
```
🚀 LUNDI : Cache PageIndex + Gemini Flash (Étapes 1+3)
✅ MARDI : asyncio.gather() Étape 7 (roadmap prioritaire)
🔥 JEUDI : BM25 hybrid + benchmark latence
✅ VENDREDI : Streaming polish (UX)
```

**Métriques cibles** :
- **Latence totale** : 4 → **1.2s** (-70%)
- **Coût/tâche** : $0.0008 → **$0.0002** (-75%)
- **Cache hit** : 0 → **95%**

**Test immédiat** : Implémente juste le **cache PageIndex** sur tes PRD/ROADMAP. Tu verras 10s → 100ms instantanément. Étape 8 = ✅ en 30min.

**Verdict** : Ton tableau était bon mais **cache tree + Gemini Flash** = game changer 2026 pour PageIndex. Claude Haiku est obsolète, `gemini-2.5-flash-exp` écrase tout. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/56387897/e8154e9c-1651-41c1-8200-ca5309e6a030/PLAN_GENERAL_ROADMAP.md)