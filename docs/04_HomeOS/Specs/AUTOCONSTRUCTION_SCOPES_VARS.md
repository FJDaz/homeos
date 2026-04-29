# Synthèse : Autoconstruction, Scopes et Variables (HomeOS)

Ce document synthétise les mécanismes de gestion des scopes et des variables d'environnement relatifs à l'autoconstruction du système HomeOS / AetherFlow.

## 1. Les Deux Scopes d'Autoconstruction

Le système distingue deux niveaux de construction qui partagent la même logique mais s'isolent par le "scope".

| Caractéristique | Scope **CONSTRUCTION** (Global) | Scope **PROJECT** (Local) |
| :--- | :--- | :--- |
| **Cible** | Le **Studio HomeOS** lui-même (l'outil) | L'**Interface Utilisateur** finale (le produit) |
| **Stack** | SvelteKit (léger, réactif) | HTML / CSS / JS Vanilla (standard, pur) |
| **Z-Index Layer** | `1000` (Studio) à `10000` (Sullivan UI) | `1` (Base de l'interface) |
| **Philosophie** | Autoconstruction du "Poste de Pilotage" | Autoconstruction du projet utilisateur |

## 2. Variables Clés et Persistance

### Variable de Mode : `HOMEOS_MODE`
Gérée par le `ModeManager`, cette variable définit si l'intelligence (Sullivan/AetherFlow) travaille sur l'outil ou sur le projet.
- **Valeurs** : `CONSTRUCTION`, `PROJECT`.
- **Persistance** : Fichier `.homeos_mode` à la racine.

### Environnement : `AETHERFLOW_ENV`
Définit le niveau de déploiement et de sécurité.
- **Valeur par défaut** : `development`.
- **Rôle** : Influence le comportement des métriques, des logs et des accès API.

### Endpoint Base : `API_BASE` / `PUBLIC_API_URL`
Utilisée par le frontend dynamique pour s'auto-câbler sur le bon backend.
- **Défaut** : `http://127.0.0.1:8000`.
- **Usage** : Infére les endpoints du Génome (`GET /studio/genome`).

## 3. Le Pivot de l'Autoconstruction : Le Génome

Toute l'autoconstruction repose sur le **Génome** (`homeos_genome.json`), qui est le "Contrat sémantique" entre le backend et le frontend. 
- Il n'échange pas de code, mais de la **vérité structurée**.
- Sullivan "déduit" l'interface à partir de ce contrat selon une cascade : **Intention → Corps → Organes → Molécules → Atomes**.

---
*Document généré par simulation de recherche documentaire (AetherFlow Docs).*
