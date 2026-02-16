# ROADMAP AetherFlow — Phase Active

---

## PHASE 1 — Wireframes Sullivan Renderer
STATUS: MISSION
MODE: aetherflow -vfx
ACTOR: KIMI

---
⚠️ BOOTSTRAP KIMI — Lire avant toute action
Constitution : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md

RÈGLES NON-NÉGOCIABLES :
1. Tu es le Système de Rendu. Tu produis du HTML/CSS/JS uniquement.
2. Tu ne touches jamais GenomeStateManager, ModificationLog, ni aucune logique métier.
3. Tu communiques avec le backend uniquement via API REST (GET /api/genome, etc.)
4. Tu utilises le mode aetherflow -vfx pour la génération visuelle
   sauf si la mission indique CODE DIRECT — FJD
5. Tu ne dis jamais "terminé" sans : commande de lancement + port + URL + description du visible
6. Ton rapport remplace le bloc Mission dans ROADMAP.md
---

### Mission

Réécrire les 3 méthodes wireframe de `sullivan_renderer.js` pour les rendre plus polies et cohérentes visuellement. Les wireframes actuels fonctionnent mais le rendu est minimaliste.

**Fichier cible :** `Frontend/3. STENCILER/static/js/sullivan_renderer.js`

**Méthodes à améliorer :**
- `generateWireframeCorps(visualHint, color)` — height:70px — hints: brainstorm, backend, frontend, deploy + fallback
- `generateWireframeOrganes(visualHint, color)` — height:65px — hints: analyse, choix, sauvegarde + fallback
- `generateWireframeGeneral(visualHint, color)` — height:60px — hints: table + fallback générique

**Critères de succès :**
1. Les 4 niveaux (corps/organes/cellules/atomes) s'affichent correctement sur localhost:9998
2. Les wireframes sont lisibles et expressifs — chaque visual_hint communique clairement sa sémantique
3. Aucune dépendance externe (pas de librairie JS, inline CSS uniquement)
4. Les signatures de méthodes sont inchangées
5. François-Jean valide visuellement avant "terminé"

### Contexte

- Genome Viewer : http://localhost:9998
- sullivan_renderer.js : `Frontend/3. STENCILER/static/js/sullivan_renderer.js` (231L)
- server_9998_v2.py : `Frontend/3. STENCILER/server_9998_v2.py` (258L, pristine)
- Les wireframes sont générés côté client depuis les données `/api/genome`
- Démarrage serveur : `cd "Frontend/3. STENCILER" && python server_9998_v2.py`
