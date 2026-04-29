# HOMEOS - Architecture Multi-Agents

**Date** : 9 février 2026
**Objectif** : Définir les agents et tools nécessaires pour automatiser le développement HOMEOS

---

## 1. Vue d'ensemble

```
                    HOMEOS (Majordome)
                         │
    ┌────────────┬───────┼───────┬────────────┐
    │            │       │       │            │
   BRS          BKD     FRD     DPL          QA
 (Business)  (Backend) (Front) (Deploy)   (Quality)
    │            │       │       │            │
 PROTO        BUILD   BUILD   PROD     DOUBLE-CHECK
  mode         mode   +SURG   mode        mode
```

---

## 2. Agents HOMEOS

### 2.1 QA Agent (Gemini) - EXISTANT

**Skills déjà créés** (`gemini_workspace/skills/`) :
- `AuditAssistant.md` - Audit codebase complet
- `PyTypeFixer.md` - Correction erreurs mypy
- `TestFixer.md` - Correction tests pytest

**Mode AetherFlow** : `DOUBLE-CHECK`

---

### 2.2 FRD Agent (À créer) - PRIORITAIRE

**Responsabilités** :
- Génération composants UI depuis Genome
- Intégration Figma-like editor
- Validation design DaisyUI/Tailwind

**Skills à créer** :

#### Skill: GenomeEnricher
```yaml
purpose: Enrichir le genome.json avec métadonnées UI
inputs:
  - genome_base.json
  - endpoints API
  - library DaisyUI
outputs:
  - genome_enrichi.json (N0→N1→N2→N3)
workflow:
  1. Lire genome existant
  2. Mapper endpoints → composants
  3. Inférer hiérarchie biologique
  4. Générer x-ui-hint pour chaque niveau
```

#### Skill: ComponentGenerator
```yaml
purpose: Générer HTML/CSS depuis genome enrichi
inputs:
  - genome_enrichi.json
  - template (Corps actif)
  - design tokens
outputs:
  - HTML component
  - CSS scoped
  - Preview SVG
workflow:
  1. Extraire Corps du genome
  2. Résoudre Organes/Cellules/Atomes
  3. Appliquer design tokens
  4. Générer HTML structuré
  5. Créer preview SVG miniature
```

#### Skill: LayoutBuilder
```yaml
purpose: Construire layout Figma-like
inputs:
  - Corps sélectionnés
  - Dimensions (1440×900)
  - Contraintes (header, sidebar)
outputs:
  - Layout blueprint JSON
  - Fabric.js objects
workflow:
  1. Calculer grid Corps
  2. Positionner éléments
  3. Appliquer constraints Sullivan
  4. Exporter pour Fabric.js
```

#### Skill: DrilldownNavigator
```yaml
purpose: Navigation hiérarchique N0→N3
inputs:
  - genome_enrichi.json
  - niveau courant (N0|N1|N2|N3)
  - filtre (Corps actif)
outputs:
  - enfants du niveau
  - breadcrumb
  - metadata affichage
workflow:
  1. Parser genome au niveau demandé
  2. Filtrer par Corps si spécifié
  3. Construire breadcrumb
  4. Retourner enfants avec metadata
```

**Mode AetherFlow** : `BUILD` + `SURGICAL`

---

### 2.3 BKD Agent (À créer)

**Responsabilités** :
- Routes API `/studio/*`
- Intégration LLM clients
- Orchestration workflows

**Skills à créer** :

#### Skill: RouteGenerator
```yaml
purpose: Générer routes FastAPI depuis specs
inputs:
  - endpoint spec (path, method, params)
  - response model
outputs:
  - Route Python
  - Tests associés
```

#### Skill: WorkflowBuilder
```yaml
purpose: Créer workflows AetherFlow
inputs:
  - étapes workflow
  - mode (PROTO/BUILD/PROD)
outputs:
  - Workflow Python class
  - Plan JSON
```

**Mode AetherFlow** : `BUILD`

---

### 2.4 BRS Agent (À créer)

**Responsabilités** :
- Clarification requirements
- Décomposition user stories
- Priorisation backlog

**Skills à créer** :

#### Skill: RequirementsClarifier
```yaml
purpose: Transformer demande vague en specs claires
inputs:
  - user request (texte libre)
  - contexte projet
outputs:
  - user stories structurées
  - critères d'acceptation
  - questions de clarification
```

**Mode AetherFlow** : `PROTO`

---

### 2.5 DPL Agent (À créer)

**Responsabilités** :
- Build production
- Validation pre-deploy
- Deployment scripts

**Skills à créer** :

#### Skill: BuildValidator
```yaml
purpose: Valider build avant deploy
inputs:
  - codebase path
  - target environment
outputs:
  - rapport validation
  - blockers list
  - deploy clearance (bool)
```

**Mode AetherFlow** : `PROD`

---

## 3. Tools Transversaux

### Tool: FileEditor
```yaml
purpose: Édition chirurgicale de fichiers
operations:
  - read_file(path, offset?, limit?)
  - write_file(path, content)
  - replace(path, old, new)
  - insert_at(path, line, content)
constraints:
  - Backup avant modification
  - Validation syntaxe post-edit
```

### Tool: CommandRunner
```yaml
purpose: Exécution commandes shell
operations:
  - run(command, timeout?)
  - run_background(command)
  - check_output(command)
constraints:
  - Sandbox mode par défaut
  - Logging complet
```

### Tool: ReportGenerator
```yaml
purpose: Génération rapports structurés
formats:
  - markdown
  - json
  - html
templates:
  - audit_report
  - mission_cr
  - progress_status
```

### Tool: MailboxManager
```yaml
purpose: Communication inter-agents
operations:
  - send_mission(agent, mission_md)
  - read_cr(agent)
  - list_pending()
path: .claude/mailbox/
```

---

## 4. Priorités d'implémentation

### Phase 1 : FRD Agent (IMMÉDIAT)

| Skill | Priorité | Bloque |
|-------|----------|--------|
| GenomeEnricher | 🔴 P0 | Tout le FRD |
| DrilldownNavigator | 🔴 P0 | Studio integration |
| ComponentGenerator | 🟠 P1 | Previews |
| LayoutBuilder | 🟠 P1 | Figma-like |

### Phase 2 : BKD Agent

| Skill | Priorité |
|-------|----------|
| RouteGenerator | 🟠 P1 |
| WorkflowBuilder | 🟡 P2 |

### Phase 3 : BRS + DPL

| Agent | Priorité |
|-------|----------|
| BRS RequirementsClarifier | 🟡 P2 |
| DPL BuildValidator | 🔵 P3 |

---

## 5. Structure de fichiers proposée

```
Backend/Prod/sullivan/agents/
├── __init__.py
├── base_agent.py              # Classe abstraite
├── qa_agent/
│   ├── __init__.py
│   ├── agent.py
│   └── skills/
│       ├── audit_assistant.py
│       ├── py_type_fixer.py
│       └── test_fixer.py
├── frd_agent/
│   ├── __init__.py
│   ├── agent.py
│   └── skills/
│       ├── genome_enricher.py
│       ├── component_generator.py
│       ├── layout_builder.py
│       └── drilldown_navigator.py
├── bkd_agent/
│   └── ...
├── brs_agent/
│   └── ...
└── dpl_agent/
    └── ...
```

---

## 6. PLAN D'EXÉCUTION - PARCOURS UX SULLIVAN

### Assignation des agents

| Agent | Responsabilité | Mailbox |
|-------|----------------|---------|
| **KIMI** | FRD Lead (Steps 4-9) | `docs/02-sullivan/mailbox/kimi/` |
| **Gemini** | QA + Vision | `docs/02-sullivan/mailbox/gemini/` |
| **Claude** | Coordination + BKD | Direct |

---

### Checklist Parcours UX Sullivan

#### ✅ Étapes Complétées
- [x] **Step 1-3** : IR / Arbiter / Genome → `genome_inferred_kimi_innocent.json` prêt
- [x] **Step 4** : Stenciler (Composants Défaut)
  - [x] Créer classe `Stenciler` dans `identity.py` (lignes 577-767)
  - [x] Générer SVG wireframes pour 9 Corps (9 types visuels)
  - [x] Interface keep/reserve
  - [ ] Route API `/studio/stencils` (à faire Step 4.5)
  - [x] Tests unitaires (25 tests)
  - **CR** : `.claude/mailbox/kimi/CR_STEP4_STENCILER.md`

#### ✅ Étapes Complétées (suite)
- [x] **Step 4.5** : Routes API Stenciler
  - [x] `GET /studio/stencils` → Liste Corps + SVG
  - [x] `POST /studio/stencils/select` → Marquer keep/reserve
  - [x] `GET /studio/stencils/validated` → Genome filtré
  - [x] Tests unitaires (15 tests)
  - **Agent** : KIMI
  - **CR** : `.claude/mailbox/kimi/CR_STEP4_ROUTES_API.md`
  - **HANDOFF** : Déposé pour Gemini QA

#### ✅ Étapes Complétées (suite 2)
- [x] **QA Step 4** : Validation Stenciler + Routes
  - [x] Tests : 14/16 passed (87.5%)
  - [x] 2 échecs attendus (genome vide)
  - [x] Verdict : GO pour Step 5 ✅
  - **Agent** : Sonnet (Gemini bloqué)
  - **CR** : `CR_QA_STEP4_SONNET.md`

#### ✅ Étapes Complétées (suite 3)
- [x] **Step 5** : Carrefour Créatif
  - [x] Upload Handler PNG
  - [x] 8 propositions layout (Minimaliste, Brutaliste, etc.)
  - [x] Template HTML `studio_step_5_choice.html`
  - [x] Tests unitaires (11 tests - 100% ✅)
  - **Agent** : KIMI
  - **QA** : Gemini (11/11 tests passés)
  - **CR** : `CR_QA_STEP5.md`

#### 🔴 Étape En Cours
- [ ] **Step 6** : Designer Vision (Analyse PNG)
  - [ ] Intégration Gemini Vision API
  - [ ] Extraction couleurs, typo, spacing
  - [ ] Génération style guide JSON
  - **Agent** : Gemini (Vision) + KIMI (UI)
  - **Mission** : À créer

#### ⬜ Étapes À Venir

- [ ] **Step 5** : Carrefour Créatif
  - [ ] Upload Handler PNG
  - [ ] 8 propositions layout
  - **Agent** : KIMI

- [ ] **Step 6** : Designer Vision (Analyse)
  - [ ] Intégration Gemini Vision
  - [ ] Calque architecte sur PNG
  - [ ] Extraction style automatique
  - **Agent** : Gemini (Vision) + KIMI (UI)

- [ ] **Step 7** : Collaboration Heureuse (Dialogue)
  - [ ] Chat Mediator Sullivan
  - [ ] Questions ambiguïtés
  - **Agent** : KIMI

- [ ] **Step 8** : Validation
  - [ ] Accord final utilisateur
  - [ ] Figer plan exécution
  - **Agent** : KIMI

- [ ] **Step 9** : Adaptation (Top-Bottom)
  - [ ] Niveau 1 : Corps (layout)
  - [ ] Niveau 2 : Organe (composant)
  - [ ] Niveau 3 : Atome (détail)
  - [ ] Ghost mode
  - [ ] Check homéostasie (Auditor)
  - **Agent** : KIMI + Gemini (QA)

---

### QA Checkpoints (Gemini)

| Après Step | Check |
|------------|-------|
| Step 4 | Valider structure Stenciler |
| Step 6 | Valider extraction Vision |
| Step 9 | Audit final code généré |

---

## 7. Historique des missions

| Date | Agent | Mission | Status |
|------|-------|---------|--------|
| 8 fév | Gemini | Audit Phase 1-3 | ✅ Terminé (7/10) |
| 9 fév | KIMI | Step 4 Stenciler (classe) | ✅ Terminé (25 tests) |
| 9 fév | Gemini | Migrer KIMI Client vers HF (gratuit) | ✅ Terminé |
| 9 fév | KIMI | Step 4.5 Routes API Stenciler | ✅ Terminé (15 tests) |
| 9 fév | Gemini | Fixer tests échoués (107 → <50) | ⏸️ Suspendu (trop complexe) |
| 9 fév | Gemini | QA Step 4 | ❌ Bloqué (tournait en rond) |
| 9 fév | Sonnet | QA Step 4 (prise en charge) | ✅ Terminé (14/16 tests, GO) |
| 9 fév | KIMI | Step 5 Carrefour Créatif | ✅ Terminé (11 tests) |
| 9 fév | Sonnet | Fix mailbox paths | ✅ Corrigé (KIMI → docs/02-sullivan/) |
| 9 fév | Gemini | QA Step 5 (seconde chance) | ✅ Réussi (11/11, verdict GO) |
| 9 fév | - | Step 6 Designer Vision | 📋 À préparer |

---

## 8. Prochaine action

**Missions actives** :
- `MISSION_KIMI_STEP5_CARREFOUR_CREATIF.md` (KIMI - Step 5 Upload + 8 propositions)
- `MISSION_GEMINI_QA_STEP5.md` (Gemini - Seconde chance, chemins corrigés)

**Missions suspendues** :
- `MISSION_GEMINI_TEST_FIXES.md` (Gemini - trop complexe, à reprendre plus tard)
- `MISSION_GEMINI_QA_STEP4_SIMPLE.md` (Gemini - QA prise en charge par Sonnet)

Workflow Step 4 :
1. ✅ KIMI crée classe Stenciler
2. 🔄 KIMI crée routes API
3. ⏳ Gemini valide (QA)
4. → Step 5
