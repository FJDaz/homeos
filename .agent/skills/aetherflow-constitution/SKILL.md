---
name: aetherflow-constitution
description: Garantit le respect strict des rôles Claude (Backend) et KIMI (Frontend) selon la Constitution AetherFlow.
---

# Skill : Constitution AetherFlow

Ce skill doit être consulté avant toute modification de code dans le projet AETHERFLOW.

## ⚖️ Règle Fondamentale : La Frontière Hermétique

Conformément aux Articles 1 et 15 de la Constitution :

### 🧠 CLAUDE (Cognitif / Backend)
- **Domaine** : État, Logique métier, API, Python, JSON.
- **Interdiction** : NE JAMAIS TOUCHER au code de rendu (HTML, CSS, JS).
- **Modification autorisée** : Fichiers dans `Backend/`, endpoints dans les serveurs Python.

### 🎨 KIMI (Rendu / Frontend)
- **Domaine** : DOM, Styles, Animations, Interactions (JS Frontend).
- **Interdiction** : Ne connaît pas la logique métier complexe.
- **Communication** : Uniquement via API REST JSON.

## 🛠 Procédure de Travail
1. Toujours vérifier le `Actor` dans `ROADMAP.md`.
2. Si `Actor: KIMI`, Claude doit déléguer les modifications de fichiers JS/CSS à l'agent Frontend.
3. Si `Actor: Claude`, l'agent ne doit modifier que les structures de données.

## 🚨 En cas de conflit
Le respect de la Constitution prévaut sur la complétion d'une Mission. En cas de doute, Claude s'arrête et demande validation.
