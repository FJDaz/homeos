# 🌌 AETHERFLOW : LE GUIDE DU VOYAGEUR (VISION & ARCHITECTURE)

> Ce document est conçu pour toute personne extérieure au projet souhaitant comprendre comment AetherFlow révolutionne la création d'interfaces par l'intelligence artificielle.

---

## 1. La Genèse : Pourquoi AetherFlow ?
Construire une interface moderne est complexe. Souvent, le design (Frontend) est déconnecté de la donnée (Backend). AetherFlow résout cela en faisant du code backend la **Source de Vérité** de l'interface. On ne "dessine" pas une application, on la fait **émaner** de sa logique.

## 2. Le Triumvirat : Trois Agents, Une Mission
Le projet est piloté par trois IA spécialisées qui collaborent selon une **Constitution** stricte :

1.  **🧠 CLAUDE (Le Cerveau / Backend Lead)** : 
    - Il analyse le code Python, les routes API et les modèles de données.
    - Il en déduit une "intention" et produit le **Genome**.
    - Il manipule l'**AST** (Abstract Syntax Tree) pour modifier le code sans le casser.
2.  **🎨 KIMI (L'Esthète / Frontend Lead)** : 
    - Elle reçoit le Genome et le transforme en pixels.
    - Elle gère le HTML sémantique, le CSS et le Design Authority (DA).
    - Sa mission : rendre l'interface belle, haptique et ergonomique.
3.  **🛠️ ANTIGRAVITY (L'Exécuteur / Orchestrator)** : 
    - C'est moi. Je gère l'environnement technique, les bugs de compatibilité (ex: Fabric.js) et le "Surgical Editing" (édition précise de fichiers).
    - Je m'assure que les serveurs (Backend 8000, Frontend 9998) communiquent parfaitement.

## 3. Le Genome : L'ADN de l'Interface
L'interface est traitée comme un organisme vivant décomposé en 4 niveaux hiérarchiques (Atomic Design) :
- **N0 : Corps (Phases)** — Les piliers de l'app (Brainstorm, Backend, Frontend, Deploy).
- **N1 : Organes (Sections)** — Les grands blocs fonctionnels.
- **N2 : Cellules (Features)** — Les fonctionnalités interactives.
- **N3 : Atomes (Components)** — Les éléments de base (bouton, texte, icône).

**Le Drill-Down** : L'utilisateur peut "plonger" dans chaque niveau (N0 -> N1 -> N2 -> N3) pour explorer ou modifier la structure.

## 4. La Vision : Des "Corps Préformés"
C'est le saut technologique majeur que nous préparons :
- **Avant** : On plaçait des éléments vides sur une page.
- **Maintenant** : Lorsqu'on invoque une phase (ex: "Backend"), AetherFlow propose un **Corps déjà structuré**.
- **Comment ?** Grâce à l'inférence. Claude sait quels "organes" sont nécessaires pour un backend de type API. Il les dispose donc automatiquement. L'humain n'est plus un maçon, mais un chef d'orchestre qui ajuste une structure déjà vivante.

## 5. La Stack Technique & Concepts Clés
- **L'AST (Abstract Syntax Tree)** : Au lieu de chercher/remplacer du texte (risqué), nous traitons le code comme un arbre logique. Cela permet des modifications chirurgicales et sûres.
- **Le Lexicon** : Notre dictionnaire universel de styles et de composants. C'est la source de vérité partagée entre Claude (qui décide quoi afficher) et KIMI (qui sait comment l'afficher).
- **La Constitution** : Un ensemble de règles inviolables. Par exemple : *Aucun style CSS ne doit jamais entrer dans le code Python backend.*

## 6. Nos Défis Actuels
- **L'Alignement Spatial** : Garantir que les sidebars et le canvas s'ajustent parfaitement sur tous les écrans (standard à 220px).
- **Le Self-Healing** : Développer la capacité du système à détecter une erreur de syntaxe et à se corriger seul via des boucles de feedback (LangGraph).
- **Le Contexte Contextuel** : Faire en sorte que les composants proposés dans le Stenciler soient toujours ultra-pertinents par rapport à la phase du Genome sélectionnée.

---
*Document rédigé par Antigravity — Février 2026*
