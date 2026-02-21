# Guide Complet du Monitoring AETHERFLOW

**Date** : 26 janvier 2025  
**Consolidation de** : MONITORING_TEMPS_REEL.md, MONITORING_PARALLELISATION.md, AFFICHAGE_MONITORING.md

---

## 📺 Où s'affiche le Monitoring ?

**Le monitoring s'affiche dans le TERMINAL où vous lancez AETHERFLOW** ✅

### Exemples concrets :

```bash
# Terminal Cursor
python -m Backend.Prod.cli --plan plan.json --output output/
# → Monitoring s'affiche dans le terminal Cursor

# Terminal externe
python -m Backend.Prod.cli --plan plan.json --output output/
# → Monitoring s'affiche dans ce terminal
```

### Compatibilité :

- ✅ **Terminal interactif** : Affichage live avec mise à jour toutes les 2 secondes
- ✅ **Terminal non-interactif** (CI/CD) : Affichage statique (pas de mise à jour live)
- ✅ **Cursor Terminal** : Fonctionne parfaitement
- ✅ **VS Code Terminal** : Fonctionne parfaitement
- ✅ **Terminal système** : Fonctionne parfaitement

---

## 📊 Fonctionnalités du Monitoring

### Affichage en Temps Réel

Le système affiche un tableau mis à jour toutes les 2 secondes avec :

| Colonne | Description |
|---------|-------------|
| **Step** | ID de l'étape (step_1, step_2, etc.) |
| **Type** | Type de tâche (analysis, code_generation, refactoring) |
| **Provider** | Provider utilisé (gemini, deepseek, codestral, groq) |
| **Status** | Statut actuel (✓ Completed, ⟳ Running, ✗ Failed, ○ Pending) |
| **Time** | Temps d'exécution (en secondes) |
| **Tokens** | Tokens utilisés pour cette étape |
| **Cost** | Coût de cette étape |
| **Description** | Description de l'étape (tronquée) |

### Résumé Global

En haut de l'affichage :
- **Plan** : Description du plan
- **Progress** : X/Y steps (Z%)
- **Completed** : Nombre d'étapes réussies
- **Failed** : Nombre d'étapes échouées
- **Elapsed Time** : Temps écoulé depuis le début
- **Total Tokens** : Tokens totaux utilisés
- **Total Cost** : Coût total cumulé

---

## 🔄 Monitoring avec Parallélisation

### Avant Parallélisation

```
Batch 4/6 (2 steps)
├─ step_4 : ⟳ Running (50s)
└─ step_5 : ○ Pending

→ step_4 termine
├─ step_4 : ✓ Completed (50s)
└─ step_5 : ⟳ Running (41s)

Temps total : 91s
```

### Après Parallélisation

```
Batch 4/6 (2 steps)
├─ step_4 : ⟳ Running (50s)  ← EN PARALLÈLE
└─ step_5 : ⟳ Running (41s)  ← EN PARALLÈLE

→ Les deux terminent simultanément
├─ step_4 : ✓ Completed (50s)
└─ step_5 : ✓ Completed (41s)

Temps total : max(50s, 41s) = 50s
Gain : 41s économisés (45% plus rapide)
```

**Point clé** : Plusieurs étapes avec statut "⟳ Running" simultanément !

### Exemple d'Affichage avec Parallélisation

```
┌─────────────────────────────────────────────────────────────┐
│ AETHERFLOW Execution Monitor                                │
├─────────────────────────────────────────────────────────────┤
│ Progress: 4/7 steps (57.1%)                                │
│ Completed: 3 | Failed: 0                                    │
│ Elapsed Time: 120.5s                                        │
│                                                              │
│ ┌──────┬────────────┬────────────┬────────────┬───────────┐ │
│ │ Step │ Type       │ Provider   │ Status     │ Time     │ │
│ ├──────┼────────────┼────────────┼────────────┼───────────┤ │
│ │step_1│ analysis   │ gemini     │ ✓ Completed│ 6.7s     │ │
│ │step_2│ refactoring│ deepseek   │ ✓ Completed│ 48.8s    │ │
│ │step_3│ refactoring│ deepseek   │ ✓ Completed│ 66.7s    │ │
│ │step_4│ refactoring│ deepseek   │ ⟳ Running │ 25.3s    │ │ ← PARALLÈLE
│ │step_5│ refactoring│ deepseek   │ ⟳ Running │ 15.2s    │ │ ← PARALLÈLE
│ │step_6│ code_gen   │ deepseek   │ ○ Pending  │ -        │ │
│ │step_7│ code_gen   │ deepseek   │ ○ Pending  │ -        │ │
│ └──────┴────────────┴────────────┴────────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Utilisation

### Exécution Normale

Le monitoring s'active automatiquement lors de l'exécution d'un plan :

```bash
python -m Backend.Prod.cli --plan Backend/Notebooks/benchmark_tasks/task.json --output output/test
```

**Affichage** :
- Tableau de monitoring mis à jour en temps réel
- Chaque étape affiche son statut au fur et à mesure
- Résumé final à la fin de l'exécution

### Exécution via Python

```python
from Backend.Prod.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = await orchestrator.execute_plan(
    plan_path=Path("plan.json"),
    output_dir=Path("output/test")
)
```

Le monitoring s'active automatiquement.

---

## 🔧 Architecture Technique

### Module `execution_monitor.py`

**Classe principale** : `ExecutionMonitor`

**Méthodes principales** :
- `add_step()` : Ajouter une étape à monitorer
- `start_step()` : Marquer une étape comme démarrée
- `update_step_progress()` : Mettre à jour le message de progression
- `complete_step()` : Marquer une étape comme terminée
- `start_monitoring()` : Démarrer l'affichage live
- `stop_monitoring()` : Arrêter l'affichage live
- `print_final_summary()` : Afficher le résumé final

### Intégration dans Orchestrator

Le monitoring est intégré dans `orchestrator.py` :
- Initialisation avant l'exécution
- Mise à jour à chaque étape
- Arrêt et résumé final après exécution

---

## ⚠️ Problèmes et Solutions

### Problème : Monitoring non visible en arrière-plan

**Cause** : L'exécution en arrière-plan n'a pas de terminal interactif

**Solution** :
- Lancer dans un terminal interactif (pas en arrière-plan)
- Le monitoring détecte automatiquement si le terminal est interactif

### Problème : Plusieurs étapes "Running" simultanément

**Cause** : Parallélisation active

**Solution** : C'est normal ! Le monitoring gère plusieurs étapes en parallèle.

---

## 💡 Avantages

1. **Visibilité Complète** :
   - Vous voyez exactement ce qui se passe à chaque instant
   - Plus d'opacité pendant l'exécution

2. **Débogage Facilité** :
   - Identification rapide des étapes qui échouent
   - Voir quel provider est utilisé pour chaque étape

3. **Suivi des Coûts** :
   - Coûts en temps réel par étape
   - Coût total cumulé visible

4. **Performance** :
   - Temps d'exécution visible pour chaque étape
   - Identification des goulots d'étranglement

---

## 🎯 Prochaines Améliorations Possibles

1. **Export du monitoring** : Sauvegarder l'état du monitoring dans un fichier JSON
2. **Notifications** : Alertes quand une étape échoue
3. **Graphiques** : Visualisation graphique de la progression
4. **Web UI** : Interface web pour le monitoring (futur)

---

**Dernière mise à jour** : 26 janvier 2025
