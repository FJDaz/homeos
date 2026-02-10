# MISSION : Implémentation du Serious Monitoring CLI (`--mon`)

**Agent** : KIMI / AetherFlow
**Objectif** : Créer un système de suivi centralisé accessible via la commande `./aetherflow --mon`.

## 🛠 Tâches à accomplir

### 1. Enregistrement du Flag `--mon` dans `Backend/Prod/cli.py`
- Ajouter l'argument `--mon` ou `--monitoring` à l'argument parser principal.
- Si ce flag est présent, le système doit afficher un tableau récapitulatif de l'état actuel d'Aetherflow.

### 2. Développement du `MonitorManager`
- Créer `Backend/Prod/core/monitor_manager.py`.
- Cette classe doit :
    - Lire les métriques d'exécution récentes (depuis `output/metrics_*.json`).
    - Lire l'état des providers depuis `cache/vigilance_status.json`.
    - Calculer le coût total par mode (BRS, BKD, FRD, DPL).
- Générer un tableau `rich` clair montrant :
    - **Mission** : Nom de la mission en cours.
    - **Provider** : Quel API (DeepSeek, Gemini, etc.) est utilisé.
    - **Status** : En cours, Terminé, Erreur.
    - **Progress** : % de complétion.
    - **Coût** : $ accumulé pour cette session/mode.

### 3. Auto-Trigger
- Modifier les points d'entrée des modes de développement (`brs_mode.py`, `DevMode` dans `cli.py`) pour qu'ils déclenchent l'affichage de ce monitoring au démarrage.

## 📊 Critères de succès
- Taper `./aetherflow --mon` affiche un tableau pro et lisible.
- Les coûts sont exacts et mis à jour en temps réel (ou quasi-réel).
- L'admin a une vision claire de la consommation par API.

---
**Mission générée par Antigravity** - 10 février 2026
