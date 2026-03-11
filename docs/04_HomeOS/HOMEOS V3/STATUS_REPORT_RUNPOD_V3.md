# Status Report — RunPod Inference HomeOS V3

**Date** : Dimanche 8 mars 2026  
**Version** : HomeOS V3 "Aetherflow Hybrid"  
**Statut** : Diagnostic Infra — Job en File d'Attente (`IN_QUEUE`)

---

## 1. Résumé de la Situation (Diagnostic au 08/03/2026)

L'infrastructure d'inférence distante sur **RunPod Serverless** a été sollicitée pour valider la chaîne de commande.
- **Dernier Job ID :** `f6df7a94-dcc7-4953-9899-3069982f9799-e1`
- **État Actuel :** `IN_QUEUE` (Mis en file d'attente depuis plus de 10 minutes).
- **Interprétation :** L'API RunPod accepte les requêtes (Authentification OK), mais le worker (GPU) est soit en phase de "Cold Start" prolongé, soit en attente de ressources disponibles sur le cluster RunPod.

---

## 2. Configuration & Paramètres (Effectifs & Opérants)

### Secrets & Environnement (`.env`)
- **Fichier :** `/Users/francois-jeandazin/AETHERFLOW/.env`
- **Variable :** `RUNPOD_API_KEY` (Valide et active).
- **Variable associée :** `IDLE_THRESHOLD=1800` (utilisée par le watchdog).

### Endpoint RunPod (Serverless)
- **Endpoint ID :** `m6j0s0i52pv0gd` (V2 API).
- **URL de Run :** `https://api.runpod.ai/v2/m6j0s0i52pv0gd/run`
- **URL de Status :** `https://api.runpod.ai/v2/m6j0s0i52pv0gd/status/{id}`

### Payload de Test Utilisé
```json
{
    "input": {
        "prompt": "Check status"
    }
}
```

---

## 3. Architecture & Fichiers Impliqués (HomeOS V3)

### Cœur du Système (Backend)
- **`Backend/Prod/api.py`** : Définit les routes FastAPI pour l'interaction Studio/Genome. Gère l'exécution des plans via `ProtoWorkflow` et `ProdWorkflow`.
- **`Backend/Prod/orchestrator.py`** : Logique de routage intelligent entre les différents LLM (Gemini, DeepSeek, Groq, Kimi).

### Scripts & Outils de Déploiement
- **`scripts/runpod_watchdog.py`** : Surveille l'inactivité du pod et déclenche l'arrêt automatique via GraphQL (`stopPod`) pour optimiser les coûts.
- **`Backend/Dockerfile`** : Définit l'image runtime (Python 3.11-slim) utilisée pour le déploiement conteneurisé.
- **`docker-compose.yml`** : Orchestration locale des services API et CLI.

### Contexte & Système de Pensée
- **`01_Context_HOMEOS.md`** : Document de référence pour le "System Prompt" de l'orchestrateur HomeOS (Aetherflow).
- **`docs/04_HomeOS/HOMEOS V3/`** : Nouveau répertoire de centralisation pour la phase V3.

---

## 4. Analyse des Dépendances & Options

| Composant | Option / Modèle | Statut |
| :--- | :--- | :--- |
| **Orchestrateur** | Smart Routing (Context-based) | ✅ Opérationnel |
| **Inférence Cloud** | RunPod Serverless | ⚠️ En attente (Cold Start) |
| **Inférence Locale** | Ollama (Llama3-3B/7B) | ✅ Disponible (Fallback) |
| **Front-end** | SvelteKit + HTMX | ✅ Build prêt |

---

## 5. Hypothèses sur l'Échec de la Tentative Précédente

1. **Cold Start Timeout :** Le worker RunPod n'a pas réussi à démarrer et à répondre dans le délai imparti par le client (souvent 30s ou 60s par défaut).
2. **Payload Mismatch :** Si le worker attend un format `{"input": {"messages": [...]}}` au lieu de `{"input": {"prompt": "..."}}`, il peut rester bloqué ou échouer silencieusement.
3. **Resource Starvation :** Le type de GPU requis pour cet endpoint n'était pas disponible au moment de l'appel.

---

## 6. Prochaines Étapes Sullivan V3

1. **Validation du Worker :** Confirmer le format d'entrée (`input schema`) attendu par le worker sur l'interface RunPod Cloud.
2. **Optimisation du Watchdog :** Ajuster le `IDLE_THRESHOLD` si les cold starts sont trop fréquents.
3. **Enrichissement du Genome :** Mettre à jour `homeos_genome.json` pour inclure les nouveaux endpoints d'inférence asynchrone.

---
*Rapport généré par Sullivan (Aetherflow Engine) — Fin de transmission.*
