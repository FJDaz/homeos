# 05 - Orchestration Small-LLM (VSD Integration)

Ce document définit comment Aetherflow utilise des modèles d'IA ultra-légers et locaux pour faire tourner le système de manière économique et souveraine.

## 1. La Stack VSD (Vigilance - Sullivan - Dynamic)
Inspirée de HomeOS V2, cette stack segmente l'intelligence :

| Module | Rôle | Modèle LLM | Taille cible |
| :--- | :--- | :--- | :--- |
| **Vigilance** | Validation du Pont & Sécurité (Anti-DRive). | DeepSeek-Coder / Qwen2.5 | 1.5B |
| **Sullivan** | Orchestration du Genome & Sémantique. | Llama-3.2 / Gemma-2 | 3B - 8B |
| **Dynamic** | Inférence Bayésienne & Intentions User. | Modèle spécialisé HomeOS | N/A |

## 2. L'Extrême Contextualisation (Prompt Pruning)
Grâce au système de **Hooks**, nous n'envoyons jamais l'intégralité du code au LLM.
- **Le Hook `onInit`** ne reçoit que le Schéma JSON (Grammaire).
- **Le Hook `onNodeEdit`** ne reçoit que l'extrait du Genome concerné (Le membre de la statue).
- **Résultat** : Un modèle de 1.5B paramètres performe mieux qu'un 175B car son champ de vision est focalisé à 100% sur la tâche.

## 3. Communication en Temps Réel
- **WebSockets** : Sullivan (Back) parle au navigateur via un tunnel permanent.
- **Latence Zéro** : Le modèle local répond en millisecondes, permettant une interaction fluide (HCI) impossibles avec les API cloud lentes.

---

## 🚀 Vers un Système Autonome
L'objectif final est qu'Aetherflow puisse s'auto-maintenir sans internet, utilisant uniquement les ressources locales de la machine hôte.
