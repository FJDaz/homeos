# Mode d’emploi – Sullivan, Genome et Chatbot

**Dernière mise à jour** : 29 janvier 2026  
**Public** : Utilisateurs et développeurs du frontend Sullivan (Chatbox + Studio).

---

## 1. Vision : Genome → Layout inféré → Amendement par le chat

Dans l’esprit du produit :

1. **Sullivan lit le genome** (ex. `homeos_genome.json` servi par `GET /studio/genome`).
2. **Sullivan, via Aetherflow, infère un layout** à partir de cette lecture (topology, endpoints, `x_ui_hint`, schémas) — structure de page, organes, placement.
3. Ce **layout proposé** est présenté à l’utilisateur.
4. L’utilisateur **amende le layout avec Sullivan** via le **chatbot** (souhaits, déplacements, ajouts, simplifications).
5. **Toute inférence** (lecture du genome, proposition de layout, génération de code) est assurée par **Aetherflow** (orchestrateur + LLM : Groq, DeepSeek, Gemini, etc.), **jamais** par un assistant en direct (ex. Claude dans Cursor) qui “invente” du layout ou du code sans passer par les workflows.

En résumé : **Genome → Aetherflow (Sullivan) infère le layout → on amende ensemble via le chatbot ; l’inférence reste toujours côté Aetherflow.**

---

## 2. Règle d’or : qui fait quoi

| Action | Qui | Comment |
|--------|-----|--------|
| **Inférence** (layout à partir du genome, génération de code, proposition de structure) | **Aetherflow** | Plans JSON + workflows PROTO (-q) ou PROD (-f), exécutés par l’orchestrateur (Groq/DeepSeek/Gemini). |
| **Amendement / dialogue** avec l’utilisateur | **Chatbot** (frontend) | Le chat envoie les demandes à l’API Sullivan ; les réponses et la logique métier passent par l’API (et donc Aetherflow/Sullivan côté serveur). |
| **Review, correction manuelle, explication** | Toi (ou Claude en direct dans l’IDE) | Pas d’inférence “sauvage” : tu peux corriger du code, expliquer, guider, mais pas faire générer un nouveau layout ou du nouveau code en dehors d’Aetherflow. |

Donc : **pas d’inférence en direct dans Cursor** pour le layout ou le code Sullivan — uniquement via Aetherflow (plans + workflows).

---

## 3. Ce qui existe aujourd’hui

### 3.1 Genome et Studio

- **Genome** : Fichier `output/studio/homeos_genome.json` (ou équivalent), généré par `Backend/Prod/core/genome_generator.py` à partir de l’OpenAPI de l’API.
- **Exposition** : `GET /studio/genome` (Backend/Prod/api.py) sert ce JSON (metadata, topology, endpoints, schema_definitions). Si le fichier n’existe pas, l’API peut le générer à la volée.
- **Studio** : Page `Frontend/studio.html` + script `Frontend/js/studio-genome.js` qui :
  - charge le genome via `GET /studio/genome`,
  - affiche les **organes** (un par endpoint) selon `x_ui_hint` (terminal, gauge, form, etc.),
  - attache les boutons / formulaires pour appeler les endpoints et afficher les réponses.

Aujourd’hui, le Studio **affiche directement** le contenu du genome (mapping endpoint → organe) ; il n’y a pas encore de **flux dédié** “Sullivan lit le genome → propose un layout inféré” (c’est la cible à atteindre).

### 3.2 Sullivan et Chatbox

- **Chatbox** : Interface (Frontend/index.html + js/app.js) pour discuter avec Sullivan :
  - recherche de composants (`/sullivan/search`),
  - analyse backend DevMode (`/sullivan/dev/analyze`),
  - analyse design DesignerMode (`/sullivan/designer/analyze`),
  - workflows frontend FrontendMode (`/sullivan/frontend/*`),
  - envoi de messages et affichage des réponses.
- **Sullivan** (côté API) : Analyse backend, inférence UI (UIInferenceEngine), génération de composants (ComponentGenerator) via **Aetherflow** (plans, PROTO/PROD). Voir `docs/02-sullivan/PRD_SULLIVAN.md`.

Le lien **Chatbox ↔ Studio** existe (lien “Studio” depuis la chatbox vers `studio.html`). Le dialogue pour **amender un layout** (proposé après lecture du genome) sera le prolongement naturel de ce chat une fois le flux “Sullivan lit le genome → propose layout” en place.

### 3.3 Aetherflow (orchestrateur)

- **Rôle** : Exécuter des **plans** (fichiers JSON) avec des workflows **PROTO** (-q) ou **PROD** (-f). Chaque étape du plan est exécutée par un LLM (Groq, DeepSeek, Gemini, etc.) ; c’est là que toute **inférence** (code, structure, layout) doit avoir lieu.
- **CLI** : `./aetherflow -q --plan <plan.json>` (rapide) ou `./aetherflow -f --plan <plan.json>` (qualité). Voir `docs/01-getting-started/GUIDE_RAPIDE_AETHERFLOW.md`.

---

## 4. Mode d’emploi pas à pas

### 4.1 Prérequis

- Python 3.12 ou 3.13, venv activé, dépendances installées (`pip install -r requirements.txt`).
- Clés API configurées (`.env`) pour les providers utilisés (Groq, DeepSeek, Gemini, etc.) selon `docs/01-getting-started/INSTALLATION.md` ou `.env.example`.

### 4.2 Démarrer l’API

```bash
# À la racine du projet
./start_api.sh
```

L’API écoute sur `http://127.0.0.1:8000`. Vérifier : `http://127.0.0.1:8000/health`.

### 4.3 Générer le genome (si besoin)

Le genome est utilisé par le Studio et (dans la vision) par Sullivan pour inférer le layout.

```bash
# Génération explicite du fichier genome
./venv/bin/python -m Backend.Prod.cli genome --output output/studio/homeos_genome.json
```

Si tu ne le génères pas à l’avance, le premier `GET /studio/genome` peut déclencher la génération côté API (si implémenté).

### 4.4 Ouvrir le frontend

- **Chatbox (accueil)** : `http://127.0.0.1:8000/`
- **Studio (vue genome)** : `http://127.0.0.1:8000/studio.html`  
  Tu peux aussi aller au Studio depuis le lien “Studio” dans la chatbox.

### 4.5 Utiliser la Chatbox avec Sullivan

- Saisir un message ou utiliser les actions proposées (recherche composant, DevMode, DesignerMode).
- Les réponses et l’inférence sont gérées par l’API (Sullivan + Aetherflow), pas par un assistant en direct.

### 4.6 Utiliser le Studio

- La page charge `GET /studio/genome` et affiche un organe par endpoint (selon `x_ui_hint`).
- Tu peux cliquer sur les boutons (Fetch, Refresh, etc.) pour appeler les routes et voir les réponses.

### 4.7 Faire de l’inférence (layout, code) via Aetherflow

Pour toute **inférence** (ex. “proposer un layout à partir du genome”, “générer du code”) :

1. **Créer ou réutiliser un plan** (JSON) qui décrit les étapes (ex. “Lire le genome”, “Proposer un layout”, “Exposer le layout au frontend”).
2. **Lancer un workflow** :
   - `./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/<ton_plan>.json` (PROTO),
   - ou `./run_aetherflow.sh -f --plan <plan>.json` (PROD).
3. Les sorties (code, structure) sont produites par l’orchestrateur Aetherflow ; tu peux les intégrer au repo ou à l’API selon le plan.

Ne pas demander à un assistant en direct (Claude dans Cursor) de “générer le layout à partir du genome” : l’inférence doit rester dans Aetherflow.

---

## 5. Évolution prévue : Sullivan lit le genome et propose un layout

À venir (aligné avec ta description) :

1. **Sullivan lit le genome** (via l’API ou un service qui consomme `GET /studio/genome` ou le fichier).
2. **Un workflow Aetherflow** (plan + étapes) :
   - prend le genome en entrée,
   - fait inférer par le LLM un **layout** (structure de page, organes, placement, libellés),
   - renvoie une description de layout (ex. JSON ou structure utilisable par le frontend).
3. Le **frontend** (Studio ou une vue dédiée) affiche ce **layout proposé**.
4. L’utilisateur **amende le layout** en discutant avec le **chatbot** ; les demandes sont traitées par l’API (Sullivan/Aetherflow) pour mettre à jour le layout ou régénérer des parties.

Tant que cette chaîne n’est pas en place, le Studio continue d’afficher le genome “brut” (un organe par endpoint) ; le mode d’emploi ci‑dessus reste valable, avec la règle : **inférence = Aetherflow, amendement = chat.**

---

## 6. Références

- **PRD Sullivan** : `docs/PRD_SULLIVAN.md`
- **Plan genome + frontend** : `docs/plans/plan_genome_frontend_self_construction.md`
- **Aetherflow (quick start)** : `docs/01-getting-started/GUIDE_RAPIDE_AETHERFLOW.md`
- **Installation** : `docs/01-getting-started/INSTALLATION.md`
- **Double-check chatbox** : `docs/02-sullivan/DOUBLE_CHECK_CHATBOX_SULLIVAN.md`


# Mode d'emploi du Sullivan Genome UI

Ce document explique comment configurer et utiliser l'interface utilisateur (UI) du Sullivan Genome, développée avec SvelteKit.

## Frontend SvelteKit

L'interface utilisateur de Sullivan Genome est une application SvelteKit située dans le répertoire `frontend-svelte/`.

### Prérequis

Assurez-vous d'avoir Node.js et npm (ou yarn/pnpm) installés sur votre système.

### Installation et Démarrage (Développement)

Pour installer les dépendances et lancer le serveur de développement :

1.  Naviguez dans le répertoire du frontend :