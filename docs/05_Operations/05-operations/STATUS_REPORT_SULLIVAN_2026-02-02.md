# Status Report — Sullivan

**Date** : 2 février 2026  
**Focus** : Sullivan (IR Arbiter, couche Bayésienne, stratégie composants)

---

## 1. Qui est Sullivan ?

**Sullivan** est l'intelligence frontend d'AETHERFLOW qui :

- **Analyse** : backend (IR, endpoints, topologie) et design (PNG, principes visuels)
- **Infère** : intention → Corps → Organes → Molécules → Atomes (Atomic Design)
- **Génère** : composants HTML/CSS/JS via plans AETHERFLOW
- **Évalue** : SullivanScore (Performance, Accessibilité, Validation)

**Rôle central (Arbiter)** : traduire l'IR technique en expérience utilisateur concrète (mapping IR ↔ composants).

---

## 2. Modes Sullivan actuels

| Mode | Fichier | Rôle |
|------|---------|------|
| **DevMode** | `modes/dev_mode.py` | Collaboration Heureuse : analyse backend → inférence → génération |
| **DesignerMode** | `modes/designer_mode.py` | Génération Miroir : PNG → structure → design principles → génération |
| **FrontendMode** | `modes/frontend_mode.py` | Orchestration multi-modèles (Gemini/DeepSeek/Groq) pour workflows frontend avancés |

**Parcours UX Studio (9 étapes)** : `studio_routes.py` — IR → Arbitrage → Distillation → Genome → Composants → Layout (styles/PNG) → Validation → Génération → Zoom Top-Bottom.

---

## 3. Difficultés rencontrées et résolutions

### Résolues

| # | Problème | Solution |
|---|----------|----------|
| 1 | Images trop volumineuses (Gemini) | `ImagePreprocessor` : resize 1920px, compression JPEG 85 %, ~3MB max |
| 2 | DesignAnalyzer mock | Appel réel à `GeminiClient.generate_with_image()` |
| 3 | Orchestrator limites | `MAX_FILE_SIZE` 50KB→200KB, `MAX_TOTAL_SIZE` 100KB→1MB |
| 4 | SullivanAuditor screenshots | `preprocess_for_gemini` intégré dans `_image_to_base64` |
| 5 | Chunking Gemini timeouts | `CHUNK_THRESHOLD` 30k→15k, `DEFAULT_CHUNK_SIZE` 20k→12k |
| 6 | Alertes « organe absent » (étape 8) | `check_homeostasis` retourne `[]` si `active_functions` vide (parcours layout) |
| 7 | Upload PNG timeout | `DEFAULT_TIMEOUT_SECONDS` 10→30 dans `design_analyzer_fast.py` et `designer_mode.py` |
| 8 | Étape 9 zoom non fonctionnel | `hx-get` sur zones, routes organe/sidebar\|main\|footer, `/studio/finalize` |
| 9 | 404 `/studio/reports/arbitrage` | Nouvelle route `get_arbitrage_report` |
| 10 | Loader upload layout | Overlay spinner + `hx-indicator` pendant l'analyse |

### En attente / partiellement traitées

| # | Problème | Priorité | Référence |
|---|----------|----------|-----------|
| 1 | Inférence top-down générique | Haute | `generic_organe`, `generic_molecule` au lieu d'inférence réelle |
| 2 | Sauvegarde vers Elite Library | Moyenne | Fichiers souvent en temporaire |
| 3 | Couche Bayésienne | Vision | Non implémentée (doc uniquement) |
| 4 | Stratégie hybride pré-génération | Vision | Non implémentée (doc uniquement) |

---

## 4. Vision documentée vs implémentation

### 4.1 Sullivan Arbiter (CE QUE DOIT FAIRE SULLIVAN ARBITER)

**Documenté** :
- Topologie (1.2) → organisation spatiale (Brainstorm, Back, Front, Deploy)
- Endpoints (1.3) → composants d'interaction (ExecuteButton, HealthBadge, SearchBar…)
- Clés IR (1.4) → structure globale (MainDashboard, FeatureNavigation…)
- Architecture Corps/Organes/Molécules/Atomes
- Bibliothèque de composants à pré-générer

**Implémenté** :
- Mapping heuristique (règles, `intent_patterns.json`, `star_mappings.json`)
- Pas de mapping IR → composants aussi fin que dans le doc

### 4.2 Couche Bayésienne Supérieure

**Documenté** :
- Réseau Bayésien : IR → Intention → Pattern → Composant
- CPT (P(I\|E), P(C\|T,K), P(P\|I,C))
- Fonction d'utilité U(G)
- Gibbs sampling, mise à jour des croyances
- Heuristiques (disponibilité, représentativité, ancrage)

**Implémenté** : Non — reste une vision théorique.

### 4.3 Stratégie hybride de pré-génération

**Documenté** :
- Tier 1 : Core Library (0 ms) — atomes + molécules de base
- Tier 2 : Pattern Library (< 100 ms) — organismes courants
- Tier 3 : Custom Generation (1–5 s) — cas uniques
- Cache intentionnel, « Composant Génome », adaptation contextuelle

**Implémenté** :
- `EliteLibrary`, `ComponentRegistry`, `VisionCache`
- Pas de système à 3 tiers ni de cache intentionnel structuré

### 4.4 Composants de base à prégénérer

**Documenté** :
- **Atomes** : AtomeButton, AtomeInput, AtomeBadge, AtomeIcon
- **Molécules** : MoleculeUpload, MoleculeSearch, MoleculeField, MoleculeMetricCard
- **Organes** : OrganeForm, OrganeNavigator, OrganePreview, OrganeChatbot
- **Corps** : CorpsShell, CorpsSection, CorpsGrid
- **Organes spécifiques** : OrganeSidebar, OrganeCanvas, OrganeHeader (exemples Svelte)

**Implémenté** :
- `SULLIVAN_DEFAULT_LIBRARY` (identity.py) : status_orb, action_stepper, component_card, upload_zone
- `design_principles.json` (Homeos Palette)
- Pas de bibliothèque SvelteKit prégénérée ni de mapping Genome → OrganeForm

---

## 5. Synthèse

| Dimension | État | Commentaire |
|-----------|------|-------------|
| **Parcours UX Studio** | Opérationnel | 9 étapes, zoom, finalize, loader upload |
| **DesignerMode** | Opérationnel | PNG → structure → principes → étape 6 |
| **DevMode** | Opérationnel | Analyse backend → inférence → génération |
| **Arbiter IR → Composants** | Partiel | Heuristiques, pas de mapping exhaustif |
| **Couche Bayésienne** | Non | Vision uniquement |
| **Stratégie hybride** | Non | Vision uniquement |
| **Prégénération SvelteKit** | Non | Liste documentée, pas d'implémentation |
| **Elite Library** | Partiel | Existe, sauvegarde incomplète |

---

## 6. Prochaines étapes suggérées

1. **Court terme** : Renforcer l'inférence top-down (réduire `generic_organe` / `generic_molecule`).
2. **Moyen terme** : Prégénérer les atomes et molécules de base (HTMX ou SvelteKit) selon la liste du doc.
3. **Long terme** : Introduire un cache intentionnel (signature backend → composant adapté).
4. **Recherche** : Prototyper la couche Bayésienne (P(Pattern\|Context)) pour guider la sélection de composants.

---

## Références

- `docs/02-sullivan/PRD_SULLIVAN.md`
- `docs/02-sullivan/CE QUE DOIT FAIRE SULLIVAN ARBITER.md`
- `docs/02-sullivan/Couche Bayésienne Supérieure - Modèle d'Inférence Structurelle.md`
- `docs/02-sullivan/Composants/STRATEGIE HYBRIDES DE PREGENRATION DES COMPOSANTS.md`
- `docs/02-sullivan/Composants/Composant de base à prégénrer.md`
- `docs/02-sullivan/MISSIONS_BLOQUANTES_IDENTITY.md`
