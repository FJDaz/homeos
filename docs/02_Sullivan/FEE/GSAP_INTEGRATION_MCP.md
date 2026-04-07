# Rapport Stratégique : Intégration de GSAP via MCP et Standard LLMS.txt

**Emplacement** : /docs/02_Sullivan/FEE  
**Date** : 3 avril 2026  
**Objet** : Activation des capacités d'animation haute précision pour Sullivan (Mode FEE).

---

## 1. Contexte : Sullivan en tant que Front-End Engineer (FEE)
Dans le cadre de la Mission 160+, Sullivan doit évoluer d'un simple générateur de layout à un ingénieur capable de câbler des interactions complexes. GSAP (GreenSock) est la bibliothèque de référence choisie pour cette couche de dynamisme.

---

## 2. Le Serveur MCP "GSAP Master"
Il n'existe pas de serveur MCP officiel GreenSock, mais le projet communautaire **`gsap-master-mcp-server`** (par bruzethegreat) fait autorité pour transformer un LLM en expert chirurgical de l'animation.

### Capacités exposées :
- **API Totale** : Couverture complète des méthodes (`to`, `from`, `timeline`, `stagger`).
- **Plugins Avancés** : Support natif de `ScrollTrigger`, `SplitText`, `MorphSVG` et `DrawSVG`.
- **Modèles de Production** : Bibliothèque de "best practices" pour les animations de héros, les transitions de pages et les interactions au scroll.
- **Auto-nettoyage** : Gestion automatique des contextes (`gsap.context()`) pour éviter les fuites de mémoire dans les manipulations DOM répétées.

---

## 3. Standard de Documentation `llms.txt`
GSAP a adopté le standard émergent pour les IA en publiant sa documentation structurée à l'adresse : **`gsap.com/llms.txt`**.

- **Avantage** : Permet à Sullivan de mettre à jour ses connaissances en temps réel sans le "bruit" du HTML promotionnel de la documentation standard.
- **Utilisation** : Sullivan peut interroger cette ressource avant toute génération de code FEE pour s'assurer d'utiliser la syntaxe la plus récente et optimisée.

---

## 4. Intégration dans le Workspace AetherFlow

L'intégration de ces outils permet de résoudre le problème de l'animation "au pifomètre" :

### A. Flux de Travail FEE
1. **Intention** : L'utilisateur définit un lien (Wire) entre un bouton et une modale.
2. **Consultation** : Sullivan consulte le serveur MCP GSAP pour trouver le pattern d'ouverture de modale le plus fluide.
3. **Injection** : Sullivan génère le code GSAP et l'injecte dans le fichier `logic.js` du projet actif.

### B. Zéro Hallucination Syntaxique
Grâce aux définitions strictes du MCP, Sullivan ne peut plus inventer de paramètres inexistants pour `ScrollTrigger`. Le code produit est "Build-Ready" dès le premier jet.

---

## 5. Recommandations techniques

| Composant | Action | Impact |
| :--- | :--- | :--- |
| **Proxy MCP** | Installer `npx bruzethegreat-gsap-master-mcp-server@latest` sur le serveur HomeOS. | Sullivan devient un expert certifié GSAP. |
| **RAG Pulse** | Pointer Sullivan vers `gsap.com/llms.txt`. | Mise à jour continue de la connaissance. |
| **FEE Logic** | Séparer le code GSAP dans un bloc `---LOGIC---` dédié (Mission 161). | Meilleure isolation et maintenabilité. |

---

## 6. Conclusion
L'ajout de la couche MCP GSAP est indispensable pour que Sullivan puisse assurer son rôle de FEE. Cela transforme l'animation d'une tâche "décorative" en une **discipline d'ingénierie prévisible et robuste**.

---
*Rapport établi pour l'évolution de la couche d'interaction visuelle AetherFlow.*
