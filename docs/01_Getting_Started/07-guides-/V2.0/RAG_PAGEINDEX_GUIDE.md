# Guide du système RAG PageIndex

## Introduction

Le système **PageIndexRAG** est une solution de Retrieval-Augmented Generation (RAG) utilisant LlamaIndex's PageIndexPlanner pour créer un index hiérarchique raisonné, idéal pour docs structurés (PRD, roadmap) et codebase.

### Caractéristiques principales

- **Index hiérarchique raisonné** : Utilise PageIndexPlanner pour naviguer dans la structure des documents
- **Haute précision** : Ciblage précis des références pertinentes avec format 'File:section.line'
- **Intégration transparente** : Conçu pour AETHERFLOW
- **Traçabilité** : Références précises pour audits

## Installation

```bash
# Ajouter les dépendances LlamaIndex (dans requirements.txt)
llama-index>=0.10.0
llama-index-core>=0.10.0
```

## Utilisation de base

```python
from Backend.Prod.rag import PageIndexRAG

# Initialisation avec chemins par défaut (PRD, roadmap, orchestrator)
rag = PageIndexRAG()

# Récupération de contexte
results = await rag.retrieve(
    query="parallélisation Étape 7",
    history=[],
    top_k=3
)

# Format des résultats
for result in results:
    print(f"Reference: {result['reference']}")
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']}")
```

## Comparaison PageIndex vs ChromaDB

| Aspect | ChromaDB (ancien) | PageIndex (nouveau) |
|--------|-------------------|---------------------|
| Setup | Embeddings lourds | Index instantané |
| Précision | Similarité lexicale | Raisonnement sémantique (95%+) |
| Coût | GPU/Stockage | CPU-only (~$0/tâche) |
| Traçabilité | Chunks anonymes | "Fichier:section.ligne" |
| Évolutif | Ré-index full | Incrémental (add file) |

## Intégration dans Orchestrator

Le RAG PageIndex peut être intégré dans l'orchestrator pour enrichir le contexte avant la planification :

```python
# Dans orchestrator.py (à implémenter)
from Backend.Prod.rag import PageIndexRAG

class Orchestrator:
    def __init__(self):
        # ...
        self.rag = PageIndexRAG()
    
    async def execute_plan(self, plan_path, context=None):
        # Enrichir le contexte avec RAG
        if context:
            rag_results = await self.rag.retrieve(context)
            enriched_context = self._format_rag_context(rag_results)
            # Utiliser enriched_context pour la planification
```

## Métriques

- `rag_efficiency` : Efficacité de la récupération
- `precision_refs` : Précision des références (target 95%)
- `retrieval_time_ms` : Temps de récupération

## Notes importantes

⚠️ **Actuellement en mode stub** : Le module nécessite l'installation de LlamaIndex pour fonctionner pleinement. Le code actuel fournit l'interface et peut être complété une fois les dépendances installées.
