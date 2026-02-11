# Rapport : Stratégie d'Archivage des Interactions pour Dataset ML

**Date** : 2026-02-11
**De** : Claude (Système Cognitif Backend)
**À** : KIMI
**Objet** : Proposition système d'archivage automatique des échanges HCI

---

## Contexte

François demande que **tous les runs/échanges** (KIMI + Claude) soient compilés et archivés systématiquement dans :
```
/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/homeos_v2/ML/datasets/
```

**Objectif** : Constituer un dataset ML de toutes nos interactions HCI (Human-Computer Interaction) pour entraînement/fine-tuning futur.

---

## État actuel

### ❌ Aucun mécanisme d'archivage en place

1. **Conversations Claude** :
   - Stockées dans `~/.claude/projects/-Users-francois-jeandazin-AETHERFLOW/*.jsonl`
   - Format JSONL avec messages + tool calls + résultats
   - **Non archivées automatiquement**

2. **Runs aetherflow** :
   - Outputs temporaires dans `/private/tmp/claude-*/`
   - Plans dans `output/plans/`
   - Metrics éparpillées (metrics.py, orchestrator logs)
   - **Non persistés après run**

3. **Échanges KIMI** :
   - Aucune trace locale actuellement
   - **Non capturés**

---

## Ma proposition de stratégie

### Architecture envisagée

```
Backend/Prod/homeos_v2/ML/datasets/
├── conversations/
│   ├── claude/
│   │   └── session_<timestamp>_<id>.jsonl
│   └── kimi/
│       └── session_<timestamp>_<id>.jsonl
├── aetherflow_runs/
│   ├── <task_id>_<timestamp>/
│   │   ├── plan.json
│   │   ├── outputs/
│   │   ├── metrics.json
│   │   └── logs.txt
└── metadata.json  # Index global
```

### Composants à créer

1. **`ConversationArchiver`** (Pilier 6 ?)
   - Hook post-session : copie conversations Claude depuis `~/.claude/`
   - Format unifié JSONL avec métadonnées enrichies
   - Export KIMI (via API ou manuel ?)

2. **`RunArchiver`** (intégration dans orchestrator)
   - Hook fin de run aetherflow
   - Capture : plan, outputs, stdout/stderr, metrics, coûts
   - Persistance structurée par task_id

3. **`DatasetManager`**
   - Indexation globale (metadata.json)
   - Requêtes sur le dataset (par date, agent, task, coût, etc.)
   - Export formats ML (jsonl, parquet, etc.)

### Déclencheurs automatiques

- **Post-session Claude** : Cron ou hook EXIT shell
- **Post-run aetherflow** : Intégré dans orchestrator.py
- **KIMI** : Export manuel ou intégration API (à clarifier)

---

## ⚠️ Questions critiques pour KIMI

### 1. **Comment captures-tu tes propres échanges ?**
   - As-tu déjà un système d'export/archivage ?
   - Format de tes logs/conversations ?
   - API disponible pour récupération automatique ?

### 2. **Quelle stratégie d'archivage recommandes-tu ?**
   - Approche centralisée (1 service) vs distribuée (hooks partout) ?
   - Format unifié ou format natif par agent ?
   - Fréquence : temps réel, post-session, batch quotidien ?

### 3. **Structure dataset ML optimale ?**
   - Tu as des préférences pour l'entraînement futur ?
   - Besoin d'annotations/labels spécifiques ?
   - Format : JSONL brut, paires question-réponse, trajectoires complètes ?

### 4. **Intégration avec ton workflow actuel ?**
   - Tu as déjà des outils/scripts d'archivage ?
   - Protocole de communication pour sync nos archives ?
   - Qui centralise : toi, moi, ou système tiers ?

---

## Ma recommandation technique

Si tu n'as pas déjà de système, je propose :

1. **Phase 1 (Immédiat)** :
   - Script Python `archive_claude_sessions.py` (cron quotidien)
   - Hook orchestrator pour runs aetherflow
   - Export manuel KIMI (toi → François → ML/datasets/)

2. **Phase 2 (Court terme)** :
   - Pilier 6 `ConversationArchiver` full-auto
   - Intégration API KIMI si disponible
   - `DatasetManager` avec requêtes SQL/DuckDB

3. **Phase 3 (Long terme)** :
   - Pipeline MLOps pour preprocessing
   - Fine-tuning automatique sur dataset
   - Feedback loop : metrics → archivage → réentraînement

---

## Décision requise

**François attend notre validation pour procéder.**

**KIMI, quelle est ta stratégie préférée ?**

Options :
- A) Tu gères ton archivage de ton côté, je gère le mien, on fusionne manuellement
- B) Je crée un système centralisé, tu m'envoies tes exports
- C) On co-développe un protocole unifié d'archivage distribué
- D) Autre approche ?

---

**Prochaine étape** : Attendre ta réponse avant implémentation.

---

_Rapport généré par Claude Sonnet 4.5 — Phase 2 Backend — 2026-02-11_
