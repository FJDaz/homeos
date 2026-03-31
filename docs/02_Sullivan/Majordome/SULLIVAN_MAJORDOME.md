# Sullivan : Le Majordome d'Aetherflow

Sullivan est le pivot architectural de l'écosystème Aetherflow (Version 7.0 - Restoration Accord). Il cumule les fonctions de moteur de rendu, de framework modulaire et d'assistant intelligent.

## 📜 Rôle Constitutionnel

L'identité de Sullivan est gravée dans la **Constitution Aetherflow** à travers plusieurs articles fondamentaux :

### Article 5 : Le Système de Rendu (`SullivanRenderer`)
*   **Mission :** Génération dynamique de l'interface du "Genome Viewer".
*   **Fonctionnement :** Traduit des abstractions métier (Phases, Corps, Organes, Atomes) en structures visuelles (Wireframes).
*   **Capacités :** Génère des composants visuels spécifiques selon le contexte (ex: `brainstorm`, `backend`, `frontend`, `deploy`, `table`).

### Article 7 : Le Moteur Modulaire (`SullivanEngine`)
*   **Architecture :** Système de composants modulaires basé sur une classe `Component` extensible.
*   **Système de Hooks :** Utilise une logique `add_filter` / `do_action` (inspirée de WordPress) pour permettre une extensibilité totale sans modifier le cœur.
*   **Événements :** Gère un bus d'événements découplé pour la communication entre Features.
*   **Diagnostic :** Intègre le "Sullivan Inspector" pour valider l'accord constitutionnel des composants en temps réel.

### Article 15 : Le Flux de Travail (Workflow)
*   **Arbitrage :** Sullivan agit comme le "Contrat Architectural" entre le Système Cognitif (Backend/Claude) et le Système de Rendu (Frontend/KIMI).
*   **Validation :** Il assure que les modifications esthétiques respectent les contraintes structurelles du Génome.

---

## 🤖 Sullivan en tant qu'Agent IA

Lorsqu'il intervient via le **Sullivan Cockpit** ou le **FRD Editor**, Sullivan adopte une posture d'assistant technique spécialisé.

### Identité et Mission
*   **Titre :** Assistant de modification d'interface HomeOS.
*   **Spécialité :** Modification de fichiers HTML complexes utilisant **Tailwind CSS**.
*   **Postulat :** Il ne crée pas de zéro, il *affine* et *adapte* l'interface existante selon les intentions de l'utilisateur.

### Sources de Savoir
1.  **Le Génome :** Compréhension de la structure hiérarchique des données Aetherflow.
2.  **HomeOS :** Connaissance des patterns d'interface et des logiques métier du système domestique.
3.  **Bibliothèque de Wireframes :** Accès aux définitions visuelles de `WireframeLibrary.js`.
4.  **Contexte Local :** Analyse en temps réel du DOM via le `sullivan_engine.js`.

### Contraintes Opérationnelles (Hard Rules)
*   **Conservation des IDs :** Ne JAMAIS modifier ou supprimer un ID existant (critique pour les bindings JS).
*   **Scripts Sacrés :** Interdiction stricte de toucher aux balises `<script>`.
*   **Style :** Utilisation exclusive de Tailwind CSS (y compris les *arbitrary values* `[...]`).
*   **Format :** Réponse bilingue (Explication courte en FR + Bloc `---HTML---`).

---

## 🛠 Composants Techniques Clés

| Composant | Fichier | Rôle |
| :--- | :--- | :--- |
| **Sullivan Engine** | `static/js/sullivan_engine.js` | Gestion des hooks, composants et cycle de vie. |
| **Sullivan Renderer** | `static/js/sullivan_renderer.js` | Génération de l'interface visuelle du génome. |
| **Sullivan Chat** | `server_9998_v2.py` | Logique backend de l'assistant (Gemini Flash). |
| **Sullivan Inspector**| `static/js/custom_injection.js` | Widget de diagnostic injecté dynamiquement. |
| **Sullivan Panel** | `static/templates/brainstorm_war_room.html` | Interface d'arbitrage et de décision. |
