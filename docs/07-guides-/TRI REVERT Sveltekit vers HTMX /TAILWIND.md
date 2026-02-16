##TRI REVERT Sveltekit vers HTMX /TAILWIND
## 🛠️ Phase 1 : Extraction et Mise en Sécurité (Le "Vault")

L'objectif est d'isoler ce qui fonctionne (ton cerveau IA) de ce qui casse (le front-end actuel).

* **Archivage du Front-end** : Déplace le dossier `frontend-svelte/` vers `archive_svelte/`. On arrête de se battre contre le proxy Vite et les erreurs 404/500 liées au routing SvelteKit.
* **Sanctuarisation du Kernel Sullivan** : On ne touche à rien dans `homeos/core/`, `homeos/ir/` et `homeos/construction/`. Ces modules sont ton capital intellectuel.
* **Nettoyage AETHERFLOW** : Supprime les routines de correction automatique qui visaient à réparer les fichiers Svelte (ex: `+layout.generated.js`), car ces fichiers n'existeront plus.

---

## 🏗️ Phase 2 : Reconstruction du "Studio Homeos" (HTMX)

On repart sur une base saine : un seul serveur, un seul langage dominant (Python), et du HTML pur.

* **Structure Monolithique** : Création d'un dossier `templates/` dans ton backend actuel.
* **Le Layout "Designer" (`index.html`)** :
* **Header** : Intégration de Tailwind CSS (via CDN pour l'instant) et HTMX (14kb).
* **Sidebar (Arsenal)** : Route FastAPI `GET /studio/components` qui renvoie la liste des composants validés.
* **Chat (L'Intention)** : Formulaire HTMX qui `POST` vers ton endpoint Sullivan existant.
* **Éditeur (Le Corps)** : Zone centrale pilotée par `hx-target`.



---

## 🚀 Phase 3 : Migration des Workflows (Le "Pont")

On reconnecte tes workflows AETHERFLOW (`-q`, `-f`, `-vfx`) à ton interface.

* **Refactor des Endpoints** : Modifie tes routes FastAPI pour qu'elles puissent répondre en HTML partiel (fragments) au lieu de JSON brut quand la requête vient de HTMX.
* **Streaming de l'Inférence** : Utilise les Server-Sent Events (SSE) pour que Sullivan "stream" le code directement dans ton éditeur central, évitant ainsi la latence des providers.
* **Validation Sullivan** : Ton `ValidationOverlay` (Accept/Reject/Refine) devient un simple fragment HTML envoyé par le serveur après chaque génération.

---

## 🎨 Phase 4 : Pivot de la Phase C (HCI Intent Refactoring)

Puisque la Phase C est à 0 %, c'est le moment idéal pour la construire nativement en HTMX.

* **Layout 3 Panels** : Mise en place des panneaux "Intentions / Implémentation / Actions" via des `<div>` fixes.
* **Gestion d'État Simplifiée** : Utilise le cache local de Sullivan (LocalCache) pour gérer l'historique des modifications sans avoir besoin de `$state()` Svelte.
* **Indicateurs de Phase** : Utilise `hx-indicator` pour montrer visuellement quelle phase (Inventaire → Gel du génome) est en cours de traitement par Sullivan.

---

## 📉 Ce qu'on Reverte (La "Trash List")

| Élément | Raison |
| --- | --- |
| **Proxy Vite / Port 5173** | Source de conflits de ports et de latence inutile. |
| **`+layout.js` & `trailingSlash**` | Complexité de routage inutile pour une application de pilotage IA. |
| **Compilation Svelte Build** | Trop rigide pour Sullivan qui doit pouvoir injecter du code "sale" ou "brut" pour validation. |

---

### Prochaine étape pour toi :

Veux-tu que je te génère le code du **`main.py`** qui fusionne tes endpoints actuels (Studio/Genome) avec le moteur de rendu HTMX pour que tu puisses voir le premier composant s'afficher sans Svelte ?