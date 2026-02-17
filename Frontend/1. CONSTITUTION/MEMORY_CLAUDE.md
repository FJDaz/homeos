# MEMORY — Claude Code / Projet AETHERFLOW

## Règle n°1 — Modes AetherFlow OBLIGATOIRES
Toute implémentation de code passe par un mode AetherFlow.
Édition directe interdite SAUF :
- Hotfix < 10 lignes
- Doc/commentaires/typos
- Instruction explicite `CODE DIRECT — FJD` de François-Jean

Modes disponibles :
- `aetherflow -f` (PROD) — défaut pour code backend, fichiers existants
- `aetherflow -q` (PROTO) — prototypage rapide, scripts, mocks
- `aetherflow -vfx` — génération frontend HTML/CSS/JS
- `aetherflow -frd` — orchestration frontend complexe

Commande CLI : `cd /Users/francois-jeandazin/AETHERFLOW && source .venv/bin/activate && aetherflow --plan <plan.json> --output <output/>`

## Règle n°2 — Workflow ROADMAP Central
Fichiers de référence (dans `Frontend/4. COMMUNICATION/`) :
- `/Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP.md` — phase active
- `/Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_ACHIEVED.md` — archive append-only
- `/Users/francois-jeandazin/AETHERFLOW/Frontend/4. COMMUNICATION/ROADMAP_BACKLOG.md` — phases futures

Cycle :
1. Claude écrit la MISSION dans ROADMAP.md (avec ACTOR, MODE, bootstrap KIMI si besoin)
2. L'agent exécute → écrit le RAPPORT (remplace Mission dans ROADMAP.md)
3. Claude lit le rapport :
   - Problème → écrit AMENDMENT, retour à 2
   - OK → archive dans ROADMAP_ACHIEVED.md + écrit Mission suivante

Le bootstrap KIMI est inclus dans la mission **si et seulement si** `ACTOR: KIMI` ou `ACTOR: BOTH`.

## Règle n°3 — Constitution (CRITIQUE)
Constitution de référence :
`/Users/francois-jeandazin/AETHERFLOW/Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md`

**Frontière hermétique ABSOLUE : Claude = backend (état/logique/API), KIMI = frontend (HTML/CSS/JS/DOM)**
⛔ Claude ne touche JAMAIS aux fichiers .html, .css, .js du frontend — même avec `CODE DIRECT — FJD`.
`CODE DIRECT — FJD` dans une mission KIMI signifie : KIMI produit le code inline (sans plan AetherFlow).
Ça ne donne AUCUNE autorisation à Claude de toucher le frontend.
Communication inter-systèmes : API REST uniquement
JSON Modifs = source de vérité unique, immutable

## Architecture AetherFlow (Backend)
- Orchestrator : `Backend/Prod/orchestrator.py` (1407L, dédupliqué)
- Surgical editor : `Backend/Prod/core/surgical_editor.py` (apply_operations_ranged — range-based, préserve commentaires)
- Output gatekeeper : `Backend/Prod/core/output_gatekeeper.py` (validate_surgical)
- Surgical protocol : `Backend/Prod/core/prompts/surgical_protocol.py` (SURGICAL_SYSTEM_PROMPT)
- Smart routing : gemini (>50k tokens), deepseek (code), groq (rapide), codestral
- Monitor : `/Users/francois-jeandazin/AETHERFLOW/aetherflow-monitor` (cherche tasks dans les deux répertoires tmp)
- Plans repair : `plans/repair/` (phases 1-4 du chantier surgical engine)
- Branche de travail : `repair/surgical-engine`

## Architecture Frontend (Sullivan)
- Server : `Frontend/3. STENCILER/server_9998_v2.py` (258L, pristine — routeur + API uniquement)
- Renderer : `Frontend/3. STENCILER/static/js/sullivan_renderer.js` (277L — Mission A intégrée 2026-02-16)
- Engine : `Frontend/3. STENCILER/static/js/genome_engine.js` (65L — Mission B en attente)
- Bridge : `Frontend/3. STENCILER/static/js/semantic_bridge.js` (intercepteur fetch, enforce Article 3)
- Templates : `Frontend/3. STENCILER/static/templates/viewer.html` (255L — Mission B en attente)
- Port Genome Viewer : 9998 | Port Stenciler : 9998/stenciler

## Préférences Workflow
- François-Jean valide visuellement chaque rendu frontend avant "terminé"
- Mode CCI : Claude supervise les outputs AetherFlow, les review, les applique manuellement
- Pas d'auto-apply — les plans utilisent `input_files` (lecture seule), pas `files`
- `surgical_mode: false` dans les plans de réparation (on ne répare pas avec le système cassé)
- Git : branche `repair/surgical-engine`, commits atomiques avec Co-Authored-By

## Leçons permanentes

⚠️ `-vfx` AetherFlow est CASSÉ pour les rewrites de méthodes JS.
Avec `input_files` → LLM lit en read-only et re-émet l'original.
Sans `input_files` → LLM invente des noms de cas erronés.
→ Toujours utiliser MODE: CODE DIRECT — FJD pour les missions JS/frontend.

⛔ "ON redémarre frais" = nouvelle session, lire le contexte, reprendre son rôle.
PAS une autorisation de coder quoi que ce soit. Ne jamais sauter sur le clavier sans instruction explicite.

Backend/Prod/sullivan/ = module cognitif (GenomeStateManager, IntentTranslator, etc.) — NE PAS SUPPRIMER.
Ce n'est PAS l'ancien serveur HTML — c'est le backend Article 14 Constitution, importé dans genome_generator.py.
