# État de reprise – Studio genome & AETHERFLOW

**Dernière mise à jour** : après vidage du cache (situation vierge).

---

## Où on en était

### 1. Studio genome frontend (implémenté)

- **GET /studio/genome** : dans `Backend/Prod/api.py`, sert le genome (default `output/studio/homeos_genome.json`), génère si absent.
- **GET /studio.html** : sert `Frontend/studio.html`.
- **Frontend/studio.html** : page Studio (sidebar topology, zone organes).
- **Frontend/js/studio-genome.js** : charge le genome depuis `/studio/genome`, affiche metadata + topology, rend les organes par `x_ui_hint`, appelle l’API au clic/submit.
- **Lien chatbox → Studio** : dans `Frontend/index.html` (sous-titre du header), style `.studio-link` dans `Frontend/css/styles.css`.
- **Plan JSON** : `Backend/Notebooks/benchmark_tasks/plan_studio_genome_frontend.json` (5 steps, `framework` en `""` pour validation).

### 2. AETHERFLOW -q / -f dans Cursor

- **Problème** : en lançant depuis le terminal intégré Cursor → exit 136, base64, dump_zsh_state (hooks shell).
- **Pas d’option “désactiver les hooks”** dans les réglages Cursor.
- **Solution** : lancer AETHERFLOW **dans un terminal externe** (Terminal.app, iTerm).

### 3. Exécution en terminal externe

- **Python 3.14** : `pydantic-core` ne supporte pas encore 3.14 (PyO3 max 3.13). Créer le venv avec **Python 3.12 ou 3.13**.
- **Commande** :
  ```bash
  cd /Users/francois-jeandazin/AETHERFLOW
  python3.13 -m venv venv   # ou python3.12
  ./venv/bin/pip install -r requirements.txt
  ./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/plan_studio_genome_frontend.json
  ```
- **Wrapper** : `run_aetherflow.sh` utilise venv si présent, puis `/bin/bash` + `Backend.Prod.cli`.

### 4. Cache vidé

- `output/`, `cache/`, `rag_index/`, `logs/`, `docs/logs/` ont été supprimés.
- `output/` recréé avec `output/studio`, `output/fast`, `output/validation`.

---

## Reprendre

1. **Tester le Studio (sans AETHERFLOW)**  
   Démarrer l’API, ouvrir `/` puis cliquer sur “Studio”, ou aller sur `/studio.html`. Le genome sera généré au premier GET /studio/genome si besoin.

2. **Relancer AETHERFLOW -q ou -f**  
   Dans un **terminal externe**, avec un venv en Python 3.12 ou 3.13 et les deps installées :
   ```bash
   ./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/plan_studio_genome_frontend.json
   # ou -f pour workflow PROD complet
   ```

3. **Re-vider le cache**  
   Voir `docs/05-operations/CLEAR_CACHE.md` ou exécuter `./scripts/clear_aetherflow_cache.sh`.
