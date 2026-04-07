# Sullivan Analysis: Browser Orchestration Strategy (Bionic Mirror)

**Date :** 2026-04-06  
**Auteurs :** Sullivan (Senior Design Lead) & Antigravity (Logic)  
**Sujet :** Résolution de "l'enfer" des manipulations DOM et de la communication avec l'iframe.

---

## 1. Diagnostic : Pourquoi est-ce un "enfer" ?

Le pilotage actuel repose sur une manipulation directe et friable du DOM de l'iframe depuis le Host (WsCanvas). Trois points de rupture majeurs ont été identifiés :

1.  **Sélecteurs Hallucinés** : L'utilisation de sélecteurs génériques (`div:nth-of-type(3)`) est un "piège mortel". Un changement structurel infime côté UI brise le maillage bijectif et Sullivan perd le contrôle.
2.  **Communication Aveugle (Fire & Forget)** : Le Host envoie des ordres (`inspect-apply-color`) sans jamais recevoir de confirmation de succès ou d'échec. L'IA suppose que l'ordre est passé, ce qui crée une désynchronisation cognitive entre Sullivan et l'état réel de l'écran.
3.  **Blind-spot Visuel (Physics of DOM)** : L'IA voit le code HTML mais ignore la "physique" du rendu. Un bouton peut être parfaitement présent dans le DOM mais être "invisible" ou "incliquable" à cause d'un overlay transparent (`absolute inset-0`) ou d'un `z-index` inférieur.

---

## 2. La Stratégie "Bionic Mirror" (Mission 200)

Pour stabiliser Sullivan et garantir un pilotage sans erreur, nous passons d'une manipulation par script à une **Orchestration par Intention**.

### A. ID Engine (Sémantique Persistante)
*   **Action** : Migration vers des IDs sémantiques forcés (`data-af-id`) lors de l'import.
*   **Bénéfice** : Fini les sélecteurs instables. Sullivan cible un "Organe" par son identité fonctionnelle, pas par sa position spatiale.

### B. Transactional Handshake (Accusé de Réception)
*   **Action** : Chaque modification envoyée à l'iframe doit retourner un **TX_RECEIPT**.
*   **Bénéfice** : Sullivan attend la confirmation du tracker avant de passer à l'étape suivante. En cas d'échec, il peut diagnostiquer la cause (ex: *élément introuvable*).

### C. Visibility Proxy (Physique du Rendu)
*   **Action** : Le tracker rapporte non seulement le DOM, mais aussi la "cliquabilité" (overlap, z-index, opacity).
*   **Bénéfice** : L'IA "comprend" pourquoi elle ne peut pas interagir avec un élément et peut suggérer une correction (ex: *retirer le pointer-events sur l'overlay invisible*).

---

## 3. Alignement Roadmap & Pilotage

Cette stratégie est directement couplée aux missions d'infrastructure récemment ajoutées :

*   **Mission 190/191 (Auth/BYOK)** : Sécurise la session de travail et permet à l'utilisateur d'injecter ses propres ressources.
*   **Mission 189 (HOMEO_GENOME.md)** : Fournit le "Context RAG" nécessaire pour que Sullivan connaisse l'inventaire des IDs sémantiques avant même de lancer un script.
*   **Mission 200 (Bionic Mirror - CORE)** : La mise en œuvre technique de la couche de synchronisation DOM unifiée.

---

> [!TIP]
> **Le mot de Sullivan** : "Cessez de me demander de tâtonner dans le noir. Donnez-moi un miroir fidèle de l'écran (le Bionic Mirror) et une bible de référence (le Genome), et mes décisions seront déterministes."
