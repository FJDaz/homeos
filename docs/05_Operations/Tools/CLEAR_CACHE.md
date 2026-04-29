# Vider le cache AETHERFLOW

Pour repartir d’une situation vierge (sans cache ni outputs précédents), supprimer les répertoires suivants à la racine du projet :

| Répertoire | Rôle |
|------------|------|
| `output/` | Résultats d’exécution des plans, studio (genome, HTML), fast/validation |
| `cache/` | Cache sémantique et prompt (réponses similaires, embeddings) |
| `rag_index/` | Index RAG (PageIndex / LlamaIndex) |
| `logs/` | Fichiers de log |
| `docs/logs/` | Logs éventuels dans docs |

## Commande (depuis la racine du projet)

```bash
cd /chemin/vers/AETHERFLOW
rm -rf output cache rag_index logs docs/logs
mkdir -p output output/studio output/fast output/validation
```

Ou exécuter le script (si présent) :

```bash
./scripts/clear_aetherflow_cache.sh
```

## Coûts (hors dépôt)

- **~/.aetherflow/costs.json** : suivi des coûts cumulés. Pour repartir à zéro côté coûts :  
  `rm -f ~/.aetherflow/costs.json`

## Après nettoyage

- Le prochain run AETHERFLOW (-q ou -f) reconstruira le cache et l’index RAG si besoin.
- Le genome Studio sera régénéré à la demande (GET /studio/genome ou CLI `genome`).
