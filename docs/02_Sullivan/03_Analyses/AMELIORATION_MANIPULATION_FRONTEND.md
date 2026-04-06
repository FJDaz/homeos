# Rapport Stratégique : Amélioration de la Manipulation Frontend par l'IA (Sullivan)

**Date** : 3 avril 2026  
**Auteur** : Gemini CLI  
**Contexte** : Architecture AetherFlow / HoméOS — Manipulation d'écrans HTML via Iframe et Monaco Editor.

---

## 1. État des Lieux et Problématiques

Actuellement, Sullivan (Gemini) manipule le frontend via deux canaux :
1.  **Grafting Local** : L'utilisateur sélectionne un élément, une bulle Monaco apparaît, et les modifications sont renvoyées via `/api/workspace/graft`.
2.  **Chat Global** : Sullivan reçoit le HTML complet de l'écran actif et doit renvoyer le HTML complet mis à jour.

**Casse-tête identifié** :
-   **Latence et Coût** : Renvoyer 5000+ caractères de HTML pour changer une couleur est inefficace.
-   **Perte de State** : `document.write` ou `srcdoc` réinitialise le state JS de l'iframe (scripts locaux).
-   **Précision** : Le LLM "voit" le code mais n'a pas la perception spatiale réelle de l'iframe (coordonnées, chevauchements).

---

## 2. Recommandations Stratégiques

### A. Modèle et Configuration
-   **Modèle Préconisé** : **Gemini 2.0 Pro** ou **Gemini 1.5 Pro** (Context Caching).
-   **Configuration** : Passer du mode `FAST` au mode `BUILD` dans le `GeminiClient` pour les requêtes de modification structurelle. 
-   **Context Caching** : Utiliser le cache de contexte de Gemini pour stocker le **Design System (DESIGN.md)** et le **Génome de base**. Cela réduit les tokens d'entrée de 40% et stabilise la "mémoire" visuelle de Sullivan.

### B. Protocole "Surgical Frontend" (Innovation)
Inspiré du protocole chirurgical Python déjà présent dans la codebase, nous devrions implémenter un **DOM Surgical Protocol** :
-   Au lieu de renvoyer tout le HTML, Sullivan renvoie un JSON d'opérations DOM :
    ```json
    {
      "operations": [
        { "type": "update_style", "selector": "#btn-primary", "css": "background-color: #8cc63f;" },
        { "type": "replace_content", "selector": ".card-title", "html": "Nouveau Titre" },
        { "type": "inject_gsap", "target": ".menu", "vars": { "x": 100, "opacity": 0 } }
      ]
    }
    ```
-   **Bénéfice** : Zéro rafraîchissement d'iframe, mise à jour atomique via `postMessage`.

### C. Prompt Système (Architecture Cognitive)
Le prompt système doit évoluer vers une **Architecture Hexagonale de l'Intention** :
1.  **Couche Identité** : "Tu es l'Arbiter de la cohérence visuelle."
2.  **Couche Design System** : Injection dynamique des tokens via RAG ou Variables d'environnement.
3.  **Couche Tracker** : Sullivan doit recevoir un "Plan de l'Iframe" (généré par `ws_iframe_core.js`) incluant les dimensions réelles des éléments cliquables.

### D. RAG et Fine-Tuning
-   **RAG (Retrieval-Augmented Generation)** : Indexer la documentation de **Tailwind CSS** et de **GSAP** spécifiquement. Sullivan ne doit pas deviner les classes, il doit les "chercher" dans une base de connaissance locale pour éviter les hallucinations de syntaxes obsolètes.
-   **Fine-Tuning** : Pas nécessaire dans l'immédiat. Gemini Flash est excellent en "few-shot". Il vaut mieux privilégier un **Dataset d'exemples (Few-shot)** inclus dans le prompt système montrant des transformations `Intent -> DOM Operations`.

---

## 3. Plan d'Action Technique

| Étape | Action | Impact |
| :--- | :--- | :--- |
| **1. Caching** | Activer `cached_content` dans `GeminiClient` pour le `DESIGN.md`. | -30% Latence |
| **2. PostMessage v2** | Étendre `WsInspect.js` pour gérer des mutations JSON complexes. | Fluidité UI |
| **3. Vision Sync** | Envoyer une capture d'écran (Base64) de l'iframe avec le prompt. | Précision visuelle |
| **4. Hybrid logic** | Sullivan génère du code GSAP dans un fichier `logic.js` séparé. | Isolation Code/Data |

---

## 4. Conclusion
Le secret pour ne plus que ce soit un "casse-tête" est de **traiter l'iframe non pas comme un fichier texte, mais comme une cible de commande distante**. Sullivan doit devenir un pilote de DOM plutôt qu'un rédacteur de HTML.

*Rapport généré par l'Intelligence Collective AetherFlow.*
