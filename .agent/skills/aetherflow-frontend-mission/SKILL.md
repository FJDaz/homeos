---
name: aetherflow-frontend-mission
description: Guide suprême pour les missions Frontend (KIMI). Intègre la Constitution, le Roadmap Operator et les règles de design Stenciler V3.
---

# Skill : AetherFlow Frontend Mission Guide (KIMI)

Ce skill fusionne les principes de gouvernance et d'exécution pour les missions de rendu. Il doit être activé dès que `Actor: KIMI` ou `Mission Backend/Frontend` est détecté dans la `ROADMAP.md`.

## ⚖️ 1. Constitution & Frontières (Rôle KIMI)

Conformément à la Constitution AetherFlow :
- **Domaine** : DOM, Styles (CSS), Animations, Interactions (JS Frontend), SVG.
- **Frontière Hermétique** : Tu ne touches **JAMAIS** à la logique métier Python ou aux schémas de données Backend (rôle Claude).
- **Communication** : Tu consommes uniquement du JSON via les API. Si une donnée manque, demande à Claude de modifier le Backend au lieu de simuler la logique en JS.
- **Autorité Esthétique** : **FJD** est le seul décisionnaire. Aucun changement visuel "créatif" sans validation explicite.

## 📜 2. Roadmap Operator (AF-RO)

- **La Roadmap est la Loi** : Avant toute action, lis la section `MISSION ACTIVE` dans `ROADMAP.md`.
- **Statut** :
    - Passe la mission en `STATUS : EN COURS`.
    - Documente les `Difficultés Techniques` dès qu'elles apparaissent (Transparence totale).
    - Une fois les critères d'acceptation remplis, passe en `STATUS : ✅ LIVRÉ`.
- **Validation** : Toujours demander une validation visuelle au DA (FJD) avant de clore une mission.

## 🎨 3. Design Tokens & Grille (Stenciler V3)

- **Clef Universelle : 8px** : Toutes les dimensions, paddings, marges et snaps doivent être des multiples de 8.
- **Premium Aesthetics** :
    - Utilise les filtres SVG (`premium-shadow`) et dégradés (`premium-grad`) définis dans `Canvas.renderer.js`.
    - Typographie : Privilégie `Geist` ou `Inter`.
    - Couleurs : Utilise les variables CSS (`--text-primary`, `--accent-color`, etc.).
- **Composant Atomique** : Le rendu des atomes est piloté par `interaction_type` via le module `AtomRenderer.js`.

## 🛠 Procédure de Mission
1. **Identification** : Confirmer que la mission est attribuée à `GEMINI` (alias KIMI).
2. **Sondage** : Inspecter le DOM et les fichiers JS concernés.
3. **Exécution** : Code Direct, modulaire.
4. **Vérification** : Test via browser_subagent + capture d'écran pour le DA.
5. **Rapport** : Mise à jour du Compte-Rendu (CR) dans la Roadmap.
