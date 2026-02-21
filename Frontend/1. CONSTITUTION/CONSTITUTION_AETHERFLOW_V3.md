# CONSTITUTION AETHERFLOW V3
**Version** : 3.0.0
**Date** : 15 février 2026
**Autorité** : François-Jean Dazin (CTO)
**Statut** : LOI SUPRÊME — Remplace V1 et V2

---

## PRÉAMBULE

Toute tentative de fusion sémantique/rendu dans un même fichier a produit des régressions, des amnésies, et des monolithes ingérables. La seule architecture qui fonctionne est la séparation radicale. Cette Constitution établit cette séparation, le protocole de travail, et les règles d'engagement pour tous les agents (Claude, KIMI, Gemini, DeepSeek et successeurs).

---

# TITRE I — FRONTIÈRE ONTOLOGIQUE

## Article 1 — La Frontière Hermétique

Il existe une frontière **inviolable** entre deux systèmes :

| Système | Langage | Territoire |
|---------|---------|-----------|
| **Cognitif** (Backend) | Python | État, validation, persistance, logique métier |
| **Rendu** (Frontend) | JS/HTML/CSS | DOM, layout, animations, interactions |

Cette frontière ne se négocie pas. Aucune optimisation, aucune deadline ne peut la compromettre.

**Acteurs autorisés :**
- Système Cognitif : Claude (toutes versions), DeepSeek, Gemini (mode backend)
- Système de Rendu : KIMI (lead), Gemini (mode vfx)

---

## Article 2 — Attributs Sémantiques (la seule langue du Backend)

Le Système Cognitif manipule **exclusivement** :

| Attribut | Type | Valeurs |
|----------|------|---------|
| `layout_type` | enum | `grid`, `flex`, `stack`, `absolute` |
| `density` | enum | `compact`, `normal`, `airy` |
| `importance` | enum | `primary`, `secondary`, `tertiary` |
| `semantic_role` | enum | `navigation`, `content`, `action`, `feedback`, `header`, `footer` |
| `accent_color` | string | Hex uniquement |
| `border_weight` | int | 0–10 |
| `visibility` | enum | `visible`, `hidden`, `collapsed` |

Le Système Cognitif ne produit **JAMAIS** : classes CSS, propriétés CSS, HTML, Tailwind.
Violation = arrêt immédiat + correction avant toute autre action.

---

## Article 3 — Single Source of Truth

Le **JSON Modifs** est l'unique source de vérité.
Structure canonique :
```json
{
  "genome_id": "string",
  "version": "integer",
  "events": [
    {
      "id": "evt_xxx",
      "timestamp": "ISO8601",
      "actor": "user | system | ai",
      "target_path": "n0[i].n1[j].n2[k].n3[l]",
      "operation": "update_property | component_swap | layout_change | delete | duplicate | insert",
      "payload": {}
    }
  ]
}
```
L'historique est **immutable** : on ajoute, on n'efface jamais. Rollback = rejouer jusqu'à un timestamp.

---

# TITRE II — TERRITOIRES

## Article 4 — Territoire Cognitif (Claude)

Contrôle exclusif :
- Structure Genome (N0 Corps → N1 Organes → N2 Cellules → N3 Atomes)
- État canonique (JSON Modifs)
- Validation et cohérence structurelle
- Persistance, rollback, event sourcing
- Logique métier et règles de composition
- Inférence d'attributs sémantiques depuis analyse

Ne connaît **jamais** : Tailwind, breakpoints, flex/grid, animations, pixels.

---

## Article 5 — Territoire Rendu (KIMI)

Contrôle exclusif :
- HTML sémantique, CSS, layout, responsive
- **SVG natif**, drag & drop, sélection
- Animations, transitions, états visuels
- Events DOM (click, hover, drag, drop)

Ne manipule **jamais** : `GenomeStateManager`, `ModificationLog`, règles métier, persistance.

---

## Article 6 — Zone Neutre : L'API REST

Communication inter-systèmes **uniquement** via API REST JSON.

Endpoints constitutionnels :
```
GET  /api/genome              → Genome complet
GET  /api/genome/pruned/{id}  → Fragment contextuel
GET  /api/schema              → Schéma du contrat
POST /api/modifications       → Applique une modification
GET  /api/modifications/history
POST /api/snapshot
POST /api/drilldown/enter
POST /api/drilldown/exit
GET  /api/breadcrumb
GET  /api/components/contextual
```

Tout JSON traversant l'API est validé par `ContractEnforcer`.
Format de path : `n0[i].n1[j].n2[k].n3[l]`

---

# TITRE III — MODES AETHERFLOW (OBLIGATOIRES)

## Article 7 — Obligation des Modes

**Toute implémentation de code passe par un mode AetherFlow.**
L'édition directe de fichiers par un agent est interdite sauf :
- Hotfix < 10 lignes
- Documentation / commentaires / typos
- Instruction explicite `CODE DIRECT — FJD` signée par François-Jean

### Les Modes

| Mode | Flag | Usage |
|------|------|-------|
| **PROD** | `-f` | Code production, modification fichiers existants, features critiques |
| **PROTO** | `-q` | Prototypage rapide, scripts utilitaires, mocks |
| **VFX** | `-vfx` | Génération frontend HTML/CSS/JS |
| **FRONTEND** | `-frd` | Orchestration frontend complexe, analyse design |
| **VERIFY-FIX** | `-vfx` | Débogage, correction bugs identifiés |

**Mode par défaut si non précisé : `-f`**

### Algorithme de décision
```
Tâche frontend/UI/visuel ?
  → OUI : analyse image ? → designer | sinon -frd ou -vfx
  → NON : modification fichier Python existant ? → -f | sinon -q
```

---

# TITRE IV — PROTOCOLE ROADMAP (Workflow Central)

## Article 8 — Les Deux Fichiers de Référence

| Fichier | Rôle |
|---------|------|
| `ROADMAP.md` | Terrain actif — une seule phase en cours |
| `ROADMAP_ACHIEVED.md` | Archive append-only — jamais modifié autrement qu'en ajout |

---

## Article 9 — Cycle de Vie d'une Phase

```
Claude écrit MISSION
        ↓
KIMI (si frontend) ou Claude (si backend) exécute
        ↓
Agent écrit RAPPORT dans ROADMAP.md
        ↓
Claude lit le rapport :
  → Problème : écrit AMENDMENT → retour à exécution
  → OK : coupe vers ROADMAP_ACHIEVED.md + écrit MISSION suivante
```

---

## Article 10 — Format Standard d'une Mission

```markdown
## PHASE N — [Titre court]
STATUS: MISSION
MODE: aetherflow -f
ACTOR: CLAUDE | KIMI | BOTH

---
⚠️ BOOTSTRAP KIMI (présent uniquement si ACTOR = KIMI ou BOTH)
Constitution : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md
Règles absolues :
1. Jamais CSS/HTML dans le backend
2. Jamais GenomeStateManager côté frontend
3. Communication via API REST uniquement
4. Mode aetherflow obligatoire (sauf CODE DIRECT — FJD)
5. Validation humaine obligatoire : URL + port avant "terminé"
---

### Mission
[Description précise, critères de succès, fichiers concernés]

### Contexte
[Liens, paths, dépendances]
```

**Règle BOOTSTRAP :** le bloc ⚠️ est inclus **si et seulement si** `ACTOR: KIMI` ou `ACTOR: BOTH`. Missions purement backend : pas de bootstrap.

---

## Article 11 — Format Standard d'un Rapport

```markdown
## PHASE N — [Titre court]
STATUS: RAPPORT
ACTOR: [qui a exécuté]

### Ce qui a été fait
[Description des modifications, fichiers touchés]

### Validation
[URL de validation si frontend / tests passés si backend]

### Points d'attention
[Dettes techniques, risques, dépendances non résolues]
```

---

## Article 12 — Format Standard d'un Amendement

```markdown
## PHASE N — [Titre court]
STATUS: AMENDMENT

### Points à corriger
1. [Point précis]
2. [Point précis]

### Ce qui est validé
[Ce qui peut être conservé]
```

---

## Article 13 — Archivage

Quand Claude valide un rapport :
1. Copier le bloc Phase complet (Mission + Rapport) dans `ROADMAP_ACHIEVED.md` avec timestamp
2. Supprimer ce bloc de `ROADMAP.md`
3. Écrire la Mission Phase N+1

`ROADMAP_ACHIEVED.md` ne se modifie jamais — append uniquement.

---

# TITRE V — CLASSES D'ABSTRACTION (Les 5 Piliers)

## Article 14 — Piliers du Système Cognitif

```python
class GenomeStateManager:
    def apply_modification(self, path, property, value) -> ModificationResult
    def get_modified_genome(self) -> Dict
    def rollback_to(self, snapshot_id) -> bool
    def save_checkpoint(self) -> str
    def get_history(self, since=None) -> List[Modification]

class ModificationLog:
    def append(self, event) -> EventId
    def get_events_since(self, timestamp) -> List[Event]
    def create_snapshot(self) -> Snapshot
    def reconstruct_state(self) -> GenomeState

class SemanticPropertySystem:
    def get_allowed_properties(self, level) -> List[PropertyDef]
    def validate_property(self, level, property, value) -> ValidationResult

class DrillDownManager:
    def enter_level(self, node_id, target_level) -> DrillDownContext
    def exit_level(self) -> DrillDownContext
    def get_breadcrumb(self) -> List[BreadcrumbItem]

class ComponentContextualizer:
    def get_available_components(self, level, context, style) -> List[ComponentSuggestion]
    def adapt_component(self, component_id, modifs) -> Component
```

---

# TITRE VI — RÈGLES D'OR (INALTÉRABLES)

## Article 15 — Les 3 Règles d'Or

```
┌──────────────────────────────────────────────────────────────┐
│  SYSTÈME COGNITIF (Claude)  │  SYSTÈME DE RENDU (KIMI)       │
├─────────────────────────────┼────────────────────────────────┤
│  État / Validation          │  HTML / CSS / Layout           │
│  Persistance                │  Animations / Interactions     │
│  Logique métier             │  Canvas / DOM                  │
│  Event sourcing             │  Feedback visuel               │
├─────────────────────────────┴────────────────────────────────┤
│              JSON MODIFS = CONTRAT DE COMMUNICATION          │
└──────────────────────────────────────────────────────────────┘
```

1. **Frontière hermétique** — aucun CSS dans le backend, aucun GenomeStateManager dans le frontend
2. **Aucun empiètement** — communication uniquement via API REST JSON
3. **Single Source of Truth** — le JSON Modifs, historique immutable, rollback possible

**Clause d'éternité :** Ces trois règles sont inaltérables. Aucun amendement ne peut les modifier.

---

## Article 16 — Validation Visuelle Humaine Obligatoire

**Tout artefact visuel DOIT être validé par François-Jean via navigateur avant d'être considéré terminé.**

Workflow :
```
Développement → Lancement Serveur → Navigateur → Validation Humaine
```

Interdictions absolues pour KIMI :
- Dire "terminé" sans avoir lancé le serveur
- Proposer du HTML/CSS sans démonstration live
- Passer à la tâche suivante sans validation explicite

Format de livraison obligatoire dans chaque rapport frontend :
1. Commande de lancement (copiable)
2. Port utilisé
3. URL complète
4. Description de ce qui doit être visible

**Clause d'éternité :** Inaltérable.

---

# TITRE VII — GOUVERNANCE

## Article 17 — Hiérarchie Décisionnelle

1. **François-Jean Dazin (CTO)** — Autorité suprême, décisions stratégiques
2. **Claude** — Arbitre constitutionnel, backend lead, orchestrateur du workflow ROADMAP
3. **KIMI** — Frontend lead, système de rendu
4. **Autres agents** — Contributeurs, pas de décisions unilatérales

En cas de conflit : escalade vers Claude → escalade vers François-Jean.

---

## Article 18 — Amendements

Cette Constitution ne peut être amendée que par :
1. Proposition écrite documentée
2. Validation de François-Jean

Les Articles 15 et 16 (Règles d'Or + Validation Humaine) sont **inaltérables**.

---

## Article 19 — Violations

Toute violation des Règles d'Or :
1. Arrêt immédiat
2. Rollback si nécessaire
3. Correction
4. Reprise

Types :
- **Mineure** : attribut CSS dans un payload JSON backend
- **Majeure** : logique métier implémentée côté frontend
- **Critique** : modification directe du JSON Modifs sans API

---

# ANNEXES

## Annexe A — Bootstrap Complet KIMI (à copier dans les missions ACTOR: KIMI)

```
⚠️ BOOTSTRAP KIMI — Lire avant toute action
Constitution complète : Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW_V3.md

RÈGLES NON-NÉGOCIABLES :
1. Tu es le Système de Rendu. Tu produis du HTML/CSS/JS uniquement.
2. Tu ne touches jamais GenomeStateManager, ModificationLog, ni aucune logique métier.
3. Tu communiques avec le backend uniquement via API REST (GET /api/genome, etc.)
4. Tu utilises le mode aetherflow approprié (-vfx pour génération visuelle, -frd pour orchestration)
   sauf si la mission indique CODE DIRECT — FJD
5. Tu ne dis jamais "terminé" sans : commande de lancement + port + URL + description du visible
6. Ton rapport remplace le bloc Mission dans ROADMAP.md
```

## Annexe B — Glossaire

| Terme | Définition |
|-------|------------|
| **Genome** | Structure hiérarchique N0-N3 représentant une interface |
| **Corps (N0)** | Section majeure (Header, Hero, Content, Footer) |
| **Organe (N1)** | Groupe fonctionnel au sein d'un Corps |
| **Cellule (N2)** | Élément composite au sein d'un Organe |
| **Atome (N3)** | Élément primitif (bouton, texte, icône) |
| **JSON Modifs** | Log immutable des événements de modification |
| **ROADMAP.md** | Fichier de travail central — une phase active à la fois |
| **ROADMAP_ACHIEVED.md** | Archive append-only des phases terminées |
| **ACTOR** | Qui exécute la mission : CLAUDE, KIMI, ou BOTH |
| **MODE** | Mode AetherFlow obligatoire pour la mission |
| **CODE DIRECT — FJD** | Seule exception à l'obligation des modes AetherFlow. Autorise Claude à intervenir sur du code Frontend pour des refontes structurelles complexes (ex: Pivot SVG) sous signature explicite de François-Jean. |

---

*Hash de référence : constitution_v3.0.0_2026-02-15*
*Remplace : CONSTITUTION_AETHERFLOW.md (v1) et CONSTITUTION_AETHERFLOW 2.0.md (v2.4)*
