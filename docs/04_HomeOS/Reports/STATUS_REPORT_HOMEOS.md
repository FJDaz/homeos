# Status Report — Homeos (AETHERFLOW)

**Date** : 31 janvier 2026  
**Version** : 2.2 "Sullivan"  
**Statut** : Beta S1 — Développement actif

---

## Résumé exécutif

**Homeos** est une plateforme d’homéostasie du code qui orchestre des agents IA (AETHERFLOW + Sullivan) pour la génération et la validation de code backend/frontend. Le système est **opérationnel** avec les phases principales du meta plan terminées, le Studio concret (Phase B) en place, et l’Intent Refactoring (Phase C) à faire.

**État global** : 🟢 ~75 % complet

---

## Ce qui est fait

### Meta plan (5 étapes) — terminé

| Étape | Description | Statut |
|-------|-------------|--------|
| 1. Couche méta | Architecture modes (construction/projet), routage agents | ✅ |
| 2. Deux modes | Mode construction (gen, validation) / Mode projet | ✅ |
| 3. CLI | `homeos mode`, `homeos switch --construction\|--project` | ✅ |
| 4. IR | Pipeline, arbiter, représentation standardisée | ✅ |
| 5. Construction bottom-up | Génération incrémentale, validation progressive | ✅ |

### Package homeos/

| Composant | Rôle | Statut |
|-----------|------|--------|
| `core/mode_manager.py` | Gestionnaire central des modes | ✅ |
| `construction/` | Adapters Aetherflow/Sullivan (mode construction) | ✅ |
| `project/` | Adapters Aetherflow/Sullivan (mode projet) | ✅ |
| `ir/pipeline.py`, `ir/arbiter.py` | Pipeline genome, arbitre Sullivan | ✅ |
| `config/construction_config.yaml` | Config z-index, règles validation | ✅ |
| `construction/tests/responsive_test.py` | Test responsive design (unités, @media, flex/grid) | ✅ |

### API Backend (Backend/Prod)

| Endpoint | Rôle | Statut |
|----------|------|--------|
| `GET /studio/genome` | Genome JSON (fallback minimal, jamais 500) | ✅ |
| `POST /execute` | Exécution plans JSON (PROTO/PROD) | ✅ |
| `POST /sullivan/search` | Recherche composants Sullivan | ✅ |
| `GET /sullivan/components` | Liste composants | ✅ |
| `POST /sullivan/designer/upload` | Upload design, analyse Gemini | ✅ |
| `POST /sullivan/dev/analyze` | Analyse backend DevMode | ✅ |
| `GET /studio`, `GET /studio/` | Page Studio (Svelte build) | ✅ |
| `GET /components`, `GET /components/` | Page galerie composants | ✅ |

### Frontend SvelteKit (frontend-svelte)

| Élément | Statut |
|---------|--------|
| Route `/studio` | ✅ Page genome, organes dynamiques |
| Route `/components` | ✅ Galerie composants prégénérés |
| Layout Organes | ✅ CorpsShell + OrganeHeader + Chat |
| ValidationOverlay | ✅ Overlay Sullivan (Accept/Reject/Refine) |
| Proxy Vite `/api` → 8000 | ✅ |
| trailingSlash: 'ignore' | ✅ Évite 404 /studio en dev |
| $state() Svelte 5 | ✅ Réactivité genome/loading/error |
| Composants Atomes/Molécules/Organes/Corps | ✅ Design tokens, design principles |

### Workflows AETHERFLOW

| Workflow | Flag | Statut |
|----------|------|--------|
| PROTO (rapide) | `-q` | ✅ FAST → DOUBLE-CHECK (Gemini) |
| PROD (qualité) | `-f` | ✅ FAST draft → BUILD refactor → validation |
| VerifyFix | `-vfx` | ✅ BUILD → validation → corrections si erreurs |
| Run-and-Fix | `-rfx` | ✅ Commande build/deploy → fix depuis stderr |

### Sullivan Kernel

| Module | Statut |
|--------|--------|
| BackendAnalyzer, UIInferenceEngine | ✅ |
| DevMode, DesignerMode | ✅ |
| ComponentGenerator, ComponentRegistry | ✅ |
| Elite Library, LocalCache | ✅ |
| Evaluators (Performance, Accessibility, Validation) | ✅ |
| PatternAnalyzer, ContextualRecommender | ✅ |

### Tests unitaires

| Fichier | Couverture | Statut |
|---------|------------|--------|
| `test_apply_phase.py` | split structure/code, get_step_output | ✅ |
| `test_verify_fix.py` | _build_fix_plan, _fix_context, genome, _serve_svelte_route | ✅ |
| `test_groq_fallback.py` | Fallback Groq → Gemini (429) | ✅ |
| Autres (registry, component_generator, etc.) | Sullivan core | ✅ |

---

## Corrections récentes (31 jan 2026)

| Problème | Correction |
|----------|------------|
| 404 `/studio` en dev | `trailingSlash: 'ignore'` dans +layout.js |
| 500 SvelteKit (Files + reserved) | Suppression de `+layout.generated.js` |
| 500 `/studio/genome` | Fallback minimal systématique, plus de 500 |
| Genome vide en front | `$state()` pour genome, loading, error (Svelte 5) |
| API routes `/studio`, `/components` | _serve_svelte_route (studio.html \| studio/index.html) |
| Plan fix studio 404 | `plan_fix_studio_404.json` pour AETHERFLOW -vfx |

---

## En cours / à faire

### Phase C — HCI Intent Refactoring

| Élément | Statut |
|---------|--------|
| Layout 3 panels (Intentions / Implémentation / Actions) | ❌ |
| 7 phases visuelles (Inventaire → Gel du genome) | ❌ |
| WebSocket `/ir-updates` | ❌ |
| Composants ir_interface (PhaseIndicator, IntentCard, etc.) | ❌ |
| Overlay IR dans Studio (z-index 10000) | ❌ |

### Améliorations Sullivan

| Sujet | Statut |
|-------|--------|
| Inférence top-down réelle (vs structures génériques) | ⚠️ En cours |
| Sauvegarde/prévisualisation des composants générés | ⚠️ Partiel |

### Effets de bord connus

| Problème | Cause | Action |
|----------|-------|--------|
| `+layout.generated.js` recréé par -vfx | Apply AETHERFLOW écrit mauvais fichier | `rm frontend-svelte/src/routes/+layout.generated.js` |
| ECONNREFUSED 8000 | API non démarrée | `./start_api.sh` |

---

## Démarrage rapide

```bash
# Terminal 1 — API Backend
./start_api.sh

# Terminal 2 — Frontend SvelteKit
cd frontend-svelte && npm run dev

# Puis ouvrir
http://localhost:5173/studio
http://localhost:5173/components
```

```bash
# AETHERFLOW — Exécution plans
./run_aetherflow.sh -q --plan Backend/Notebooks/benchmark_tasks/plan_phase_a.json
./run_aetherflow.sh -f --plan Backend/Notebooks/benchmark_tasks/plan_phase_b.json
./run_aetherflow.sh -vfx --plan Backend/Notebooks/benchmark_tasks/plan_fix_studio_404.json
```

---

## Documents de référence

- **PRD** : `docs/04-homeos/PRD_HOMEOS.md`
- **État des lieux** : `docs/04-homeos/ETAT_LIEUX.md`
- **Point d’étape** : `docs/04-homeos/POINT_ETAPE_HOMEOS.md`
- **Plan Studio** : `.cursor/plans/studio_concret_puis_doc.plan.md`
- **Causes erreurs apply** : `docs/04-homeos/CAUSES_ERREURS_APPLY.md`
