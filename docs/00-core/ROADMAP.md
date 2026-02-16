# ROADMAP AETHERFLOW
**Fichier central de travail — une seule phase active à la fois**
Constitution : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`
Archive : `ROADMAP_ACHIEVED.md`

---
<!-- PHASE ACTIVE CI-DESSOUS -->

## PHASE 1 — Wireframes Sullivan Renderer
STATUS: MISSION
MODE: aetherflow -vfx
ACTOR: KIMI

---
⚠️ BOOTSTRAP KIMI — Lire avant toute action
Constitution complète : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md

RÈGLES NON-NÉGOCIABLES :
1. Tu es le Système de Rendu. Tu produis du HTML/CSS/JS uniquement.
2. Tu ne touches jamais GenomeStateManager, ModificationLog, ni aucune logique métier.
3. Tu communiques avec le backend uniquement via API REST (GET /api/genome, etc.)
4. Mode aetherflow -vfx pour cette mission (sauf CODE DIRECT — FJD)
5. Tu ne dis jamais "terminé" sans : commande de lancement + port + URL + description du visible
6. Ton rapport remplace le bloc Mission dans ROADMAP.md
---

### Mission
Refaire les wireframes visuels dans `sullivan_renderer.js`.

Les fonctions actuelles (`generateWireframeCorps`, `generateWireframeOrganes`, `generateWireframeGeneral`) utilisent du HTML inline avec `style=""` sur chaque div — c'est fonctionnel mais pas propre.

**Objectif :** améliorer le rendu visuel des 4 niveaux (Corps, Organes, Cellules, Atomes) dans le Genome Viewer tout en conservant la structure JS existante.

**Fichiers concernés :**
- `Frontend/3. STENCILER/static/js/sullivan_renderer.js` — les méthodes `generateWireframe*`
- `Frontend/3. STENCILER/static/css/viewer.css` — si des classes CSS sont préférables au inline

**Critères de succès :**
- Les 4 niveaux s'affichent correctement sur http://localhost:9998
- Les visual_hints existants (`brainstorm`, `backend`, `frontend`, `deploy`, `analyse`, `choix`, `sauvegarde`, `table`) sont tous couverts
- Le code est lisible (pas de 400px de HTML inline dans une string JS)

**Validation :** lancer `python server_9998_v2.py` depuis `Frontend/3. STENCILER/`, ouvrir http://localhost:9998

### Contexte
- Server : `Frontend/3. STENCILER/server_9998_v2.py` (258L, pristine)
- Renderer : `Frontend/3. STENCILER/static/js/sullivan_renderer.js`
- Templates : `Frontend/3. STENCILER/static/templates/viewer.html`
- Les dead code wireframes Python ont été supprimés — `sullivan_renderer.js` est l'unique source
