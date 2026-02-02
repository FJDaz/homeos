---
name: ""
overview: ""
todos: []
isProject: false
---

# Plan TUI AetherFlow 2.1 - Interface Terminal Utilisateur

## Objectif

Créer une TUI (Terminal User Interface) interactive avec Textual pour permettre aux utilisateurs de :

- Lancer des workflows (PROTO/PROD) depuis l'interface
- Voir l'exécution en temps réel avec monitoring
- Afficher le feedback pédagogique avec --mentor
- Naviguer dans les résultats et logs
- Gérer les plans JSON

## Architecture TUI

### Structure 3 colonnes (comme spécifié)

```
┌─────────────────────────────────────────────────────────────┐
│              🚀 AETHERFLOW TUI - Dashboard                  │
├──────────────┬──────────────┬──────────────────────────────┤
│   COLONNE 1  │   COLONNE 2  │        COLONNE 3             │
│              │              │                              │
│  📋 PLAN     │  💻 CONSOLE  │  📊 MÉTRIQUES                │
│              │              │                              │
│  - Steps     │  - Logs      │  - Temps réel                │
│  - Status    │  - Outputs   │  - Coûts                     │
│  - Progress  │  - Errors    │  - Cache hits                │
│              │              │  - Feedback Mentor            │
├──────────────┴──────────────┴──────────────────────────────┤
│  Footer: Métriques temps réel | [F1] Help | [Q] Quit        │
└─────────────────────────────────────────────────────────────┘
```

## Composants à créer

### 1. Backend/Prod/tui/**init**.py

- Module principal TUI

### 2. Backend/Prod/tui/app.py

- Classe principale `AetherFlowTUI(App)` avec Textual
- Gestion des écrans (Dashboard, Plan Selector, Results Viewer)
- Intégration avec les workflows existants

### 3. Backend/Prod/tui/widgets/

- `plan_panel.py` : Affichage du plan avec steps et statuts
- `console_panel.py` : Logs et outputs en temps réel
- `metrics_panel.py` : Métriques (temps, coûts, cache)
- `mentor_panel.py` : Affichage du feedback pédagogique avec Rich

### 4. Backend/Prod/tui/commands.py

- Commandes pour lancer workflows depuis TUI
- Intégration avec `cli.py` existant

## Fonctionnalités

### Écran Principal (Dashboard)

- Sélection de plan JSON (file picker)
- Choix du workflow (PROTO/PROD)
- Option --mentor toggle
- Boutons Start/Stop/Pause

### Pendant l'exécution

- Colonne 1 : Plan avec progression par step
- Colonne 2 : Logs en temps réel (scrolling)
- Colonne 3 : Métriques live (temps, coûts, cache hits)

### Après exécution

- Affichage du feedback pédagogique si --mentor activé
- Navigation dans les résultats
- Export des résultats

## Intégration avec CLI existant

- Réutiliser `orchestrator.py` et `workflows/`
- Wrapper autour de `cli.py` pour lancer depuis TUI
- Capture des logs pour affichage dans console_panel

## Tests

- Test avec plan réel depuis TUI
- Vérification affichage feedback pédagogique
- Test navigation et interactions