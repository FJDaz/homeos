# Plan de Refactorisation : Stenciler V2 "Modular Features"

## 🏗 Architecture Proposée : "Feature Generator"

L'objectif est d'extraire la logique et le markup des ~15 features actuellement hardcodées dans `stenciler_v2.html`.

### 1. Structure Technique
- **`BaseFeature` (Classe)** : Gère le template, l'injection et le cycle de vie.
- **`FeatureLibrary`** : Répertoire des modules (TSL Picker, Palette, Zoom, etc.).
- **`LayoutManager`** : Distribue les instances dans les zones (Sidebar, Header, Main).

### 2. Bénéfices
- **Séparation des préoccupations (SoC)** : Le HTML devient un simple "shell" de 50 lignes.
- **Dynamisme** : On peut activer/désactiver des outils en fonction du Génome reçu du Backend.
- **Maintenance** : Un bug dans le Color Picker se corrige dans son module dédié, pas dans un fichier de 1500 lignes.

### 3. Workflow Constitutionnel (Article 15)
1. **Claude (Backend)** : Définit l'architecture (ce document) et le schéma JSON des features.
2. **KIMI (Frontend)** : Implémente les classes JS, déplace le HTML dans les modules et vide le fichier `stenciler_v2.html`.

---
*Ce document fait office de contrat architectural entre le Système Cognitif et le Système de Rendu.*
