# ROADMAP D'IMPLÉMENTATION - SULLIVAN STENCILER

**Version** : 1.2.0
**Date** : 11 février 2026 — Mise à jour : 14:15
**Statut** : Phase 1 COMPLÉTÉE ✅ | Phase 2 EN COURS 🚀 | PARALLÉLISATION ACTIVÉE
**Conformité** : CONSTITUTION_AETHERFLOW v1.0.0 (Article 10 ajouté)

---

## 📊 VUE D'ENSEMBLE

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1  │  Phase 2  │  Phase 3  │  Phase 4  │  Phase 5   │
│  Contrat  │  Backend  │  API REST │  Frontend │ Optimisations│
│  1-2j     │  3-5j     │  2-3j     │  3-5j     │  2-3j      │
└─────────────────────────────────────────────────────────────┘
     ↓           ↓           ↓           ↓           ↓
  ✅ DONE     🚀 NOW      ⏳ NEXT     ⏳ WAIT     ⏳ WAIT
```

**Durée totale estimée** : 11-18 jours
**Mode** : Séquentiel (chaque phase bloque la suivante)

---

## 🎯 PHASE 1 : DÉFINIR LE CONTRAT (1-2 jours) ✅ COMPLÉTÉE

**Objectif** : Établir le contrat d'interface formel entre Backend et Frontend

### Livrables

- [x] **CONSTITUTION_AETHERFLOW.md** — Loi suprême du système (515 lignes, Article 10 ajouté)
- [x] **LETTRE_CTO_CLAUDE_SONNET_4_5.md** — Directives CTO
- [x] **LETTRE_ANALYSES_POUR_KIMI.md** — Brief technique Frontend
- [x] **RECEPTION_KIMI_ACCUSE_RECEPTION.md** — Engagement KIMI
- [x] **API_CONTRACT_SCHEMA.json** — JSON Schema validation (618 lignes)
- [x] **Validation avec KIMI** — Débat sur les 5 questions ouvertes ✅
- [x] **Signature Constitution** — François-Jean + Claude Sonnet 4.5 + KIMI 2.5 ✅
- [x] **PROTOCOLE_VALIDATION_VISUELLE.md** — Workflow validation humaine ✅
- [x] **DETECTEUR_MISSION_FRONTEND.md** — Système détection auto ✅
- [x] **Organisation Frontend/** — Structure complète avec Elite Library ✅

### Actions Claude Backend Lead

- [x] Créer le JSON Schema du contrat
- [x] Signer la Constitution (ligne 497-500)
- [x] Validation KIMI sur les 5 questions :
  1. Format du path → KIMI a choisi `n0[0].n1[2]` ✅
  2. Optimistic updates → KIMI a choisi optimistic avec rollback ✅
  3. Granularité endpoints → KIMI a choisi endpoint générique ✅
  4. Format composants → KIMI a choisi JSON structure ✅
  5. Snapshot → KIMI a choisi hybride (50 modifs OU 5 min) ✅
- [x] Organiser Frontend/ (4 sections : CONSTITUTION, GENOME, STENCILER, COMMUNICATION)
- [x] Copier Elite Library (65 composants) vers Frontend/2. GENOME/
- [x] Créer protocole validation visuelle (Article 10 Constitution)
- [x] Créer système détection mission frontend

### Actions KIMI Frontend Lead

- [x] Lire tous les documents (CONSTITUTION, LETTRES, SCHEMA)
- [x] Signer la Constitution (ligne 502)
- [x] Confirmer acceptation des 5 réponses données
- [x] Valider visuellement le Viewer Genome (http://localhost:9998)
- [x] Créer mocks JSON pour previews 4 Corps

### Critère de succès

✅ **Les deux parties confirment** : "Je peux travailler avec ce contrat" — VALIDÉ 11 fév 2026

---

## 🏗️ PHASE 2 : IMPLÉMENTER LES CLASSES BACKEND (3-5 jours) 🚀 EN COURS

**Objectif** : Construire les 5 piliers du Système Cognitif
**Mode** : Codage manuel (pas via aetherflow) pour rapidité maximale

### Livrables

#### 2.1 `GenomeStateManager` ⭐ Priorité 1

**Fichier** : `Backend/Prod/sullivan/stenciler/genome_state_manager.py`

**API** :
```python
class GenomeStateManager:
    def apply_modification(self, path: str, property: str, value: Any) -> ModificationResult
    def get_modified_genome(self) -> Dict
    def rollback_to(self, snapshot_id: str) -> bool
    def save_checkpoint(self) -> str
    def get_history(self, since: Optional[datetime] = None) -> List[Modification]
    def reconstruct_state(self) -> GenomeState
```

**Tests** : `tests/test_genome_state_manager.py`

---

#### 2.2 `ModificationLog` ⭐ Priorité 1

**Fichier** : `Backend/Prod/sullivan/stenciler/modification_log.py`

**API** :
```python
class ModificationLog:
    def append(self, event: Event) -> EventId
    def get_events_since(self, timestamp: datetime) -> List[Event]
    def create_snapshot(self) -> Snapshot
    def get_latest_snapshot(self) -> Snapshot
    def reconstruct_state(self) -> GenomeState
```

**Tests** : `tests/test_modification_log.py`

---

#### 2.3 `SemanticPropertySystem` ⭐ Priorité 2

**Fichier** : `Backend/Prod/sullivan/stenciler/semantic_property_system.py`

**API** :
```python
class SemanticPropertySystem:
    def get_allowed_properties(self, level: int) -> List[PropertyDef]
    def validate_property(self, level: int, property: str, value: Any) -> ValidationResult
    def get_property_type(self, property: str) -> PropertyType
```

**Tests** : `tests/test_semantic_property_system.py`

---

#### 2.4 `DrillDownManager` ⭐ Priorité 3

**Fichier** : `Backend/Prod/sullivan/stenciler/drilldown_manager.py`

**API** :
```python
class DrillDownManager:
    def enter_level(self, node_id: str, target_level: int) -> DrillDownContext
    def exit_level(self) -> DrillDownContext
    def get_current_context(self) -> DrillDownContext
    def get_breadcrumb(self) -> List[BreadcrumbItem]
```

**Tests** : `tests/test_drilldown_manager.py`

---

#### 2.5 `ComponentContextualizer` ⭐ Priorité 3

**Fichier** : `Backend/Prod/sullivan/stenciler/component_contextualizer.py`

**API** :
```python
class ComponentContextualizer:
    def get_available_components(self, level: int, context: Dict, style: str) -> List[ComponentSuggestion]
    def adapt_component(self, component_id: str, modifs: Dict) -> Component
    def get_tier_for_component(self, component_id: str) -> int
```

**Tests** : `tests/test_component_contextualizer.py`

---

### Actions KIMI (en parallèle) 🚀 DÉMARRAGE IMMÉDIAT

**NOUVEAU : Travail parallèle sans dépendance API**

- [ ] **PRIORITÉ 1** : Créer `Frontend/3.STENCILER/mocks/4_corps_preview.json`
  - 4 Corps (Brainstorm, Backend, Frontend, Deploy)
  - Structure : `{ id, name, color, organes: [{name, features_count}] }`
  - Format preview 20% (simplifié)

- [ ] **PRIORITÉ 2** : HTML/CSS Bande de previews
  - Extension `server_9998_v2.py` (après ligne 1422)
  - Section `#stenciler-section` (display:none au départ)
  - Bande horizontale 4 Corps (draggable="true")
  - CSS complet (voir MISSION_STENCILER_EXTENSION.md)

- [ ] **PRIORITÉ 3** : Préparer Canvas Fabric.js
  - Layout sidebar + canvas (HTML structure)
  - CDN Fabric.js chargé
  - Événements drag/drop (handlers vides pour l'instant)
  - Sidebar outils (color picker, border slider)

- [ ] **PRIORITÉ 4** : Valider design avec François-Jean
  - Screenshot previews
  - Validation UX/couleurs/layout

### Critère de succès

✅ Tous les tests passent
✅ API mock fonctionnelle (sans persistence)
✅ Code review validé

---

## 🔌 PHASE 3 : CRÉER LES ENDPOINTS REST (2-3 jours) ⏳ EN ATTENTE

**Objectif** : Exposer les classes via API REST Flask/FastAPI

### Livrables

**Fichier** : `Backend/Prod/sullivan/stenciler/api.py`

#### 3.1 Routes État

```python
@app.route('/api/genome/<genome_id>', methods=['GET'])
@app.route('/api/genome/<genome_id>/state', methods=['GET'])
@app.route('/api/schema', methods=['GET'])
```

#### 3.2 Routes Modifications

```python
@app.route('/api/modifications', methods=['POST'])
@app.route('/api/modifications/history', methods=['GET'])
@app.route('/api/snapshot', methods=['POST'])
```

#### 3.3 Routes Navigation

```python
@app.route('/api/drilldown/enter', methods=['POST'])
@app.route('/api/drilldown/exit', methods=['POST'])
@app.route('/api/breadcrumb', methods=['GET'])
```

#### 3.4 Routes Composants

```python
@app.route('/api/components/contextual', methods=['GET'])
@app.route('/api/components/<component_id>', methods=['GET'])
@app.route('/api/components/elite', methods=['GET'])
```

#### 3.5 Routes Outils

```python
@app.route('/api/tools', methods=['GET'])
@app.route('/api/tools/<tool_id>/apply', methods=['POST'])
```

### Tests d'intégration

**Fichier** : `tests/test_api_integration.py`

- [ ] Tester tous les endpoints via `pytest`
- [ ] Vérifier conformité JSON Schema
- [ ] Tester error handling (404, 400, 500)

### Actions KIMI

- [ ] Finir rendu avec mocks (drag & drop simulé)
- [ ] Préparer appels API (fetch() commentés)
- [ ] Tester endpoints via curl/Postman

### Critère de succès

✅ API complète testable via curl/Postman
✅ Toutes les réponses conformes au JSON Schema
✅ Tests d'intégration passent

---

## 🎨 PHASE 4 : INTÉGRATION FRONTEND/BACKEND (3-5 jours) 🚀 KIMI LEAD

**Objectif** : Connecter KIMI à l'API REST réelle

### Livrables

#### 4.1 Extension `server_9998_v2.py`

**Procédure** : Suivre scrupuleusement MISSION_STENCILER_EXTENSION.md

- [ ] ÉTAPE 0 : Lire et comprendre
- [ ] ÉTAPE 1 : Vérifier fichier existant (1422 lignes)
- [ ] ÉTAPE 2 : Créer backup
- [ ] ÉTAPE 3 : Ajouter code après ligne 1422
- [ ] ÉTAPE 4 : Tester
- [ ] ÉTAPE 5 : Restaurer si échec

#### 4.2 Code à ajouter

**Section 1** : CSS (styles Stenciler)
**Section 2** : HTML (bande previews + canvas + sidebar)
**Section 3** : JavaScript (Fabric.js + event handlers + API calls)

#### 4.3 Fonctionnalités

- [ ] Bande de previews (4 Corps à 20%)
- [ ] Drag & drop vers canvas
- [ ] Canvas Fabric.js fonctionnel
- [ ] Sidebar avec outils (color picker, border slider)
- [ ] Event handlers (click, double-click, drag, drop)
- [ ] Appels API REST (fetch)
- [ ] Optimistic updates avec rollback
- [ ] Feedback visuel (animations, toasts)

### Actions Claude

- [ ] Support debugging si réponses API incorrectes
- [ ] Ajustements classes backend si bugs détectés

### Critère de succès

✅ Workflow complet fonctionnel :
- Choix style → Scroll vers Stenciler
- Drag Corps → Canvas
- Drill-down (double-clic)
- Modification couleur/border
- Persistance des modifs

✅ Aucune régression du Viewer existant

---

## ⚡ PHASE 5 : PERSISTANCE ET OPTIMISATIONS (2-3 jours) ⏳ EN ATTENTE

**Objectif** : Performance et robustesse

### Livrables Backend (Claude)

#### 5.1 Cache Intelligent

- [ ] Tier 1 : Composants Elite en mémoire (0ms)
- [ ] Tier 2 : Adaptation LLM avec cache (< 100ms)
- [ ] Tier 3 : Génération from scratch (1-5s)

#### 5.2 Persistance Multi-niveaux

- [ ] Mémoire : État reconstruit
- [ ] localStorage : Modifs en cours (KIMI gère)
- [ ] Cache Redis : Sessions actives
- [ ] SQLite : Audit trail long terme

#### 5.3 Snapshots Automatiques

- [ ] Toutes les 50 modifications
- [ ] Tous les 5 minutes
- [ ] Sur action user explicite

#### 5.4 Compression

- [ ] JSON Modifs compressé si > 100KB
- [ ] Gzip sur réponses API

### Livrables Frontend (KIMI)

#### 5.5 Optimisation Rendu

- [ ] Debounce sur events drag (60ms)
- [ ] Throttle sur scroll (100ms)
- [ ] Lazy loading images
- [ ] Virtual scrolling si > 100 organes

#### 5.6 Progressive Enhancement

- [ ] Skeleton loader si API > 300ms
- [ ] Graceful degradation si API down
- [ ] Offline mode (lecture seule depuis localStorage)

### Critère de succès

✅ Latence < 100ms pour actions courantes
✅ Canvas maintient 60 FPS
✅ Aucune fuite mémoire (test 1h d'utilisation)
✅ Charge initiale < 2s

---

## 📅 PLANNING DÉTAILLÉ

### Semaine 1 (J1-J7) — MODE PARALLÈLE ACTIVÉ ⚡

| Jour | Claude (Backend) | KIMI (Frontend) | Synchronisation |
|------|------------------|-----------------|-----------------|
| **J1** | ✅ Phase 1 complétée | ✅ Phase 1 complétée | Constitution signée |
| **J2** | GenomeStateManager + tests | Mocks JSON 4 Corps | — |
| **J3** | ModificationLog + tests | HTML/CSS Bande previews | — |
| **J4** | SemanticPropertySystem + tests | Canvas Fabric.js setup | — |
| **J5** | DrillDownManager + ComponentContextualizer | Event handlers (mocks) | — |
| **J6** | Routes API État + Modifications | JavaScript complet (mocks) | Code review croisé |
| **J7** | Routes API Navigation + Composants | Tests unitaires JS | Tests API avec curl |

### Semaine 2 (J8-J12) — INTÉGRATION ⚡

| Jour | Claude (Backend) | KIMI (Frontend) | Synchronisation |
|------|------------------|-----------------|-----------------|
| **J8** | Tests intégration API | Remplacer mocks par fetch() | Point sync 1 |
| **J9** | Debug API si besoin | Intégration API GET genome | Tests E2E début |
| **J10** | Debug API si besoin | Intégration API POST modifs | Tests E2E suite |
| **J11** | Ajustements backend | Intégration API drilldown | Tests E2E complet |
| **J12** | Code review final | Polish UX + animations | Démo François-Jean |

### Semaine 3 (J15-J18)

| Jour | Phase | Acteur Principal | Livrables |
|------|-------|------------------|-----------|
| **J15** | Phase 5 | KIMI + Claude | Polish, edge cases |
| **J16** | Validation | François-Jean | Recette fonctionnelle |
| **J17** | Documentation | Claude + KIMI | README, guide utilisateur |
| **J18** | Déploiement | Équipe | Mise en production |

---

## 🚨 RISQUES ET MITIGATIONS

### Risque 1 : KIMI ne respecte pas le contrat

**Probabilité** : Moyenne
**Impact** : Critique
**Mitigation** :
- ContractEnforcer avec JSON Schema (validation automatique)
- Tests d'intégration systématiques
- Code review avant merge

### Risque 2 : Performance du JSON Modifs

**Probabilité** : Moyenne
**Impact** : Moyen
**Mitigation** :
- Snapshots périodiques (Phase 2)
- Reconstruction incrémentale
- Compression si nécessaire (Phase 5)

### Risque 3 : Complexité de l'inférence

**Probabilité** : Faible
**Impact** : Moyen
**Mitigation** :
- InferenceEngine produit uniquement sémantique
- Tests unitaires stricts
- Pas de génération HTML/CSS

### Risque 4 : Fuite de responsabilités

**Probabilité** : Moyenne
**Impact** : Critique
**Mitigation** :
- Code reviews systématiques
- Checklist "Règles d'Or" avant merge
- Tests de frontière (scénarios extrêmes)

### Risque 5 : Dérive du scope

**Probabilité** : Élevée
**Impact** : Moyen
**Mitigation** :
- Focus sur MVP (bande previews + drag + drill + modif)
- Features avancées (Figma) en Phase 6 (future)
- Validation François-Jean à chaque phase

---

## 📊 MÉTRIQUES DE SUCCÈS

### Phase 1

- ✅ Constitution signée par CTO + Claude + KIMI
- ✅ JSON Schema validé
- ✅ 5 questions débattues et tranchées

### Phase 2

- ✅ 100% tests unitaires passent
- ✅ Coverage > 80%
- ✅ API mock fonctionnelle

### Phase 3

- ✅ Tous endpoints testables via curl
- ✅ Conformité JSON Schema 100%
- ✅ Tests d'intégration passent

### Phase 4

- ✅ Workflow complet fonctionnel
- ✅ Aucune régression Viewer
- ✅ User peut modifier et persister

### Phase 5

- ✅ Latence < 100ms (actions courantes)
- ✅ 60 FPS sur canvas
- ✅ Charge initiale < 2s

---

## 🔄 PROCESSUS DE VALIDATION

### À chaque fin de phase

1. **Demo** : Présentation à François-Jean
2. **Validation** : Go / No-Go pour phase suivante
3. **Rétrospective** : Qu'est-ce qui a bien / mal fonctionné ?
4. **Ajustements** : Mise à jour roadmap si nécessaire

### Critère de passage à la phase suivante

❌ **Bloquant** : Si échec critère de succès → STOP, correction
✅ **Non-bloquant** : Warnings OK, on continue mais on note

---

## 📝 CHECKLIST FINALE (Avant Production)

### Conformité Constitutionnelle

- [ ] Aucun CSS dans les classes Backend
- [ ] Aucun GenomeStateManager dans le code Frontend
- [ ] Communication uniquement via API REST JSON
- [ ] JSON Modifs = Single Source of Truth
- [ ] Historique immutable vérifié

### Tests

- [ ] Tests unitaires Backend (100%)
- [ ] Tests unitaires Frontend (optionnel, mais recommandé)
- [ ] Tests d'intégration API (100%)
- [ ] Tests end-to-end (workflow complet)
- [ ] Tests performance (latence, FPS)

### Documentation

- [ ] README technique
- [ ] Guide utilisateur
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Architecture Decision Records (ADR)

### Déploiement

- [ ] Backup base de données
- [ ] Rollback plan préparé
- [ ] Monitoring activé (logs, métriques)
- [ ] Healthcheck endpoint (`/api/health`)

---

## 🎯 PROCHAINES ÉTAPES IMMÉDIATES

### Aujourd'hui (J1)

**Claude** :
- [x] Créer JSON Schema ✅
- [ ] Signer Constitution
- [ ] Attendre validation KIMI

**KIMI** :
- [ ] Lire tous les documents
- [ ] Signer Constitution
- [ ] Confirmer acceptation du contrat

**François-Jean** :
- [x] Signer Constitution ✅
- [ ] Valider que Phase 1 est terminée → GO pour Phase 2

---

## 📞 POINTS DE CONTACT

**Questions contrat/architecture** : Claude Sonnet 4.5 (Backend Lead)
**Questions frontend/rendu** : KIMI 2.5 (Frontend Lead)
**Décisions stratégiques** : François-Jean Dazin (CTO)
**Arbitrage conflits** : Claude Opus 4.5 (Arbitre Constitutionnel)

---

**Roadmap vivante** — Mise à jour quotidienne — Version 1.0.0

**Dernière mise à jour** : 11 février 2026, 18h00
