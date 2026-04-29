# Synthèse Sullivan — Du Brainstorm à l’Implémentation

**Date** : 1er février 2026  
**Sources** : Brainstorm→Implémentation, Partition Filage, Roadmap HTMX, Status Report 01/02/2026

---

## Partie 1 — Synthèse des quatre documents

### 1.1 Du Brainstorm à l’Implémentation (mécanisme et hiérarchie)

Ce document pose la **boussole** du système Homeos : comment passer de l’intention à du code validé, sans surcharge cognitive.

#### Mécanisme central : le « Pop-in » (OOB Swap HTMX)

- **Contexte** : panneau central = **Arbitrage**. L’utilisateur valide un Atome ou un Organe proposé par Sullivan.
- **Action** : clic sur « Valider ».
- **Réponse serveur** : un seul bloc HTML avec :
  1. **Centre** : message de succès (« Atome validé ! ») qui remplace le bouton.
  2. **Droite (OOB)** : fragment `hx-swap-oob="true"` = code définitif du composant.
- **Effet** : sans rechargement, l’élément « saute » du centre vers le **Génome** à droite = **distillation** concrète.

#### Hiérarchie de segmentation (« la Moisson »)

Validation par **unités fonctionnelles** en ordre bottom-up, pour éviter de « balancer 7000 lignes » (TDAH-friendly) :

| Niveau | Nom | Contenu | Arbitrage | Dans le Génome |
|--------|-----|---------|-----------|----------------|
| **1** | Fondation (Cerveau Python) | Endpoints, RAG, méthodes de classe | Lien intention ↔ structure Python | Branche active dans l’arborescence API |
| **2** | Atome / Molécule (ADN visuel) | Boutons, inputs, design tokens, typo | Rendu + CSS | Galerie de composants (Arsenal) |
| **3** | Organe (bloc fonctionnel) | Assemblage d’atomes (formulaire chat, header) | Interaction + cohérence du bloc | Entité « gelée », prête à être posée |
| **4** | Corps (Hôte / Squelette) | Layout global, z-index, CorpsShell | Validation finale de l’assemblage | « Master Plan » qui lie le reste |

**Boussole anti-brouillard** : incrémental (brique par brique), gratification visuelle (panneau droit en vert #A6CE39), focus unitaire (un segment à la fois dans l’Arbitrage). C’est la **Phase 5 (Construction bottom-up)** du Meta Plan : « On ne construit pas une application, on cultive un génome. »

---

### 1.2 Partition de Filage Homeos (triptyque et protocole)

Ce document définit la **partition opérationnelle** : ordre des agents, hiérarchie de priorité, protocole de validation, commandes et règles TDAH.

#### Ordre des agents (focalisation dynamique)

| Agent | Phase | Action | Sortie | Contrainte |
|-------|--------|--------|--------|------------|
| **AETHERFLOW** | REVUE (Inventaire) | Analyser le PRD → proposer **lots cohérents** | Regroupements par familles (ex. « Lot Boutons », « Lot Formulaire ») | Structurer en familles, pas en éléments isolés |
| **SULLIVAN** | ARBITRAGE (Tamis) | Évaluer par **lots + code couleur** | Validation par familles | Ne solliciter l’User que pour 🟠 et 🔴 |
| **HOMEOS** | DISTILLATION (Gel) | Distiller par lots validés | Code généré par familles | Distiller les 🟢 automatiquement |

**Code couleur Sullivan** : 🟢 Auto-validé (conforme Elite Library) | 🟠 Alerte (déviations mineures) | 🔴 Blocage (incohérences majeures).

#### Hiérarchie de priorité : Sample vs Solo

- **Échantillonnage (Atomes/Molécules)** : validation par **lots de confiance**. User valide un styleguide → Sullivan génère tous les atomes conformes → Homeos distille la famille entière.
- **Focalisation (Organes/Corps)** : validation **granulaire** uniquement ici. Atomes déjà gelés ; Sullivan demande validation pour chaque assemblage unique ; Homeos distille organe par organe.

#### Protocole en 3 étapes

1. **Échantillonnage initial** : AETHERFLOW propose le styleguide → Sullivan marque conformité → User valide → Homeos gèle le styleguide.
2. **Génération par lots** : AETHERFLOW propose lots (Boutons, Inputs, Cartes) → Sullivan analyse (🟢/🟠/🔴) → User valide/gèle/corrige/rejette.
3. **Distillation focalisée** : Homeos écrit dans `genome.json` par lots (lignes 45–51, etc.), avec statut ✅ / ⚠️ / ❌.

#### Commandes opérationnelles

- `note: [résumé de lot]` — consigner les décisions par lots.
- `elite: [famille entière]` — archiver des familles cohérentes (score Sullivan >90 pour tous les éléments).
- `kernel: [règle de lot]` — règle déclenchée quand une famille complète présente un pattern.
- `focus: [organe spécifique]` — forcer la validation granulaire sur un organe critique.

#### Règles « santé mentale »

- Un seul lot à la fois à l’écran.
- Timer d’auto-validation (30 s sans réponse → 🟢 auto-validés).
- Mode zéro-distraction : cacher les 🟢, ne voir que 🔴.
- Barre de progression par lots, pas par éléments.

**Philosophie** : « Valide la règle, pas chaque instance. Concentre ton énergie sur l’assemblage unique, pas sur les briques standardisées. »

---

### 1.3 Roadmap Passage à HTMX (phases concrètes)

La roadmap découpe la **transition Svelte → HTMX** et l’intégration du filage Sullivan en phases séquentielles.

| Phase | Nom | Objectif | Actions clés |
|-------|-----|----------|--------------|
| **1** | Décontamination & Nettoyage | Supprimer le bruit, garder le signal API | Archivage `frontend-svelte/` → `archive_svelte/`, purge routes FastAPI, sanctuarisation Kernel (`homeos/core/`, `ir/`, `construction/`) |
| **2** | Squelette HTMX | Réceptacle visuel du Triptyque | FastAPI sert `index.html`, layout **Revue \| Arbitrage \| Distillation**, endpoints en fragments HTML (OOB Swaps) |
| **3** | Filage avec Cursor (répétition générale) | Validation manuelle du flux avant automatisation | Charger Partition Filage + spec PHASE3_SPEC_FILAGE, échantillonnage (styleguide + lots), focalisation (ex. Chat), glaçage du Génome. *Phase 3 = spec/archive ; implémentation en Phase 3b.* |
| **4** | Reconnexion & Phase C | L’IA Sullivan dans le nouveau corps | Workflow Aetherflow (`-q`, `-f`, `-vfx`) sur panneau Distillation via SSE, code couleur 🟢🟠🔴 dans Arbitrage, Elite Library & Kernel automatisés |
| **5** | Finitions Sullivan | Excellence inférence | Intégration STAR, GénomeEnricher (bayésien), réduction du fallback « generic » |

**Pourquoi cette roadmap** : progressive (IA complexe seulement une fois la tuyauterie manuelle prouvée), ADHD-friendly (Phase 3 pour calibrer Sullivan), zéro-régression (Kernel Sullivan préservé pendant le changement d’interface).

---

### 1.4 Status Report Sullivan (01/02/2026) — État du kernel

Résumé de l’état **Sullivan Kernel seul** (sans AETHERFLOW ni Homeos) :

- **Version** : 2.2 « Sullivan ». **État global** : ~80 % complet.
- **Implémenté** : Phases PRD 1–5 (Analyse Backend, Design, Génération, Évaluation, Avancé), Genome & Studio (Builder, Visual Auditor, Refinement, CLI), API (`/sullivan/search`, `/components`, `/dev/analyze`, `/designer/analyze`, `/designer/upload`, `/preview/{id}`).
- **En cours / partiel** : IntentTranslator (ébauche STAR), intégration STAR non branchée, sauvegarde partielle, inférence top-down partielle (fort usage de `generic`), prévisualisation partielle.
- **Non implémenté** : GénomeEnricher, Phase 6–7 PRD, tests unitaires Sullivan.
- **Contexte TRI REVERT** : kernel Sullivan inchangé ; migration = interface de consommation (Svelte → HTMX), réutilisation des endpoints Sullivan, ValidationOverlay en fragments HTML.

---

## Partie 2 — Tableau de bord synthétique

### Fil conducteur : Brainstorm → Implémentation

```
PRD / Intent
     ↓
AETHERFLOW (Revue)     →  Lots cohérents (familles)
     ↓
SULLIVAN (Arbitrage)   →  🟢 / 🟠 / 🔴 par lot
     ↓
USER                   →  Valide / corrige / rejette (surtout 🟠🔴)
     ↓
HOMEOS (Distillation)  →  genome.json + Arsenal (OOB Swap visuel)
```

### Correspondance Hiérarchie ↔ Roadmap ↔ Partition

| Hiérarchie (Brainstorm) | Partition (Filage) | Roadmap |
|-------------------------|--------------------|--------|
| Niveau 1 Fondation | Échantillonnage (styleguide) | Phase 3 échantillonnage |
| Niveau 2 Atome/Molécule | Lots de confiance, auto 🟢 | Phase 3 lots, Phase 4 code couleur |
| Niveau 3 Organe | Focalisation granulaire | Phase 3 focalisation (ex. Chat) |
| Niveau 4 Corps | Validation assemblage finale | Phase 4–5 Kernel / STAR |
| Pop-in OOB | Distillation par familles | Phase 2 fragments HTML, Phase 4 SSE |

---

## Partie 3 — Sullivan — Status Report consolidé (1er février 2026)

### 3.1 Périmètre

- **Sullivan** : intelligence frontend (analyse backend → inférence structure → génération composants).
- **Ce rapport** : kernel Sullivan + position dans le triptyque AETHERFLOW / Sullivan / Homeos et dans la roadmap HTMX.

---

### 3.2 État par couche

#### A. Kernel Sullivan (code)

| Domaine | Statut | Détail |
|---------|--------|--------|
| Phases PRD 1–5 | ✅ | BackendAnalyzer, DesignAnalyzer, ComponentGenerator, Évaluateurs, Elite Library, PatternAnalyzer, KnowledgeBase |
| Genome & Studio | ✅ | Génome, Builder, Visual Auditor, Refinement, CLI `genome` / `studio` / `sullivan read-genome` |
| API REST | ✅ | `/search`, `/components`, `/dev/analyze`, `/designer/*`, `/preview/{id}` |
| IntentTranslator / STAR | ⚠️ | Ébauche, non branchée dans ContextualRecommender / UIInferenceEngine |
| GénomeEnricher (bayésien) | ❌ | Non implémenté |
| Réduction fallback `generic` | ⚠️ | Partiel, fort usage actuel |
| Tests unitaires Sullivan | ❌ | Absents (~26 fichiers) |

#### B. Interface de consommation (roadmap)

| Élément | Statut | Lien document |
|---------|--------|----------------|
| Svelte (actuel) | En place | — |
| HTMX Triptyque | ❌ | Roadmap Phase 2 |
| OOB Swap (Pop-in) | ❌ | Roadmap Phase 2 + Brainstorm |
| Code couleur Arbitrage 🟢🟠🔴 | ❌ | Roadmap Phase 4, Partition §5 |
| Filage par lots (Cursor) | Spec / archive | Phase 3, Partition, PHASE3_SPEC_FILAGE |
| SSE Distillation (flags -q, -f, -vfx) | ❌ | Roadmap Phase 4 |

#### C. Règles opérationnelles (Partition)

| Règle | Statut |
|-------|--------|
| Validation par lots (pas par élément) | Spec définie, à brancher en Phase 3/4 |
| Échantillonnage (styleguide → atomes) | Spec définie |
| Focalisation (organes/corps uniquement) | Spec définie |
| Commandes `note` / `elite` / `kernel` / `focus` | Spec définie, implémentation à faire |
| Timer auto-validation 30 s, mode zéro-distraction | Spec définie |

---

### 3.3 Synthèse état global

- **Kernel** : ~80 % (Phases 1–5 + Genome/Studio + API). Manquent : STAR intégré, GénomeEnricher, tests, réduction `generic`.
- **Filage + UX** : spec complète (Brainstorm, Partition, Roadmap) ; implémentation à faire à partir de Phase 2–3 (HTMX, OOB, Arbitrage, Distillation).
- **Sanctuarisation** : kernel Sullivan (`homeos/core/`, `ir/`, `construction/`) à ne pas casser pendant la migration interface.

---

### 3.4 Prochaines actions recommandées (consolidées)

**Court terme (1–2 semaines)**  
1. Intégrer IntentTranslator (STAR) dans ContextualRecommender et UIInferenceEngine.  
2. Améliorer le score bayésien (embeddings plutôt que comptage de mots).  
3. Démarrer Phase 1 roadmap (archivage Svelte, purge API, sanctuarisation) si décision de passer à HTMX.

**Moyen terme (≈1 mois)**  
4. Implémenter GénomeEnricher (bayésien).  
5. Réduire l’usage du fallback `generic`.  
6. Ajouter tests unitaires pour le kernel Sullivan.  
7. Phase 2 + 3 roadmap : squelette HTMX, layout Triptyque, filage manuel avec Cursor (échantillonnage + focalisation + glaçage Génome).

**Long terme (2–3 mois)**  
8. Phase 4–5 : code couleur Arbitrage, SSE Distillation, Elite Library & Kernel automatisés, STAR complet, prévisualisation complète.  
9. Documentation et exemples (IntentTranslator, Partition Filage, mode d’emploi Génome/Studio).

---

### 3.5 Références

- **Du Brainstorm à l’Implémentation** — Mécanisme OOB, hiérarchie 4 niveaux, boussole anti-brouillard.  
- **PROMPT CURSOR FILAGE ARBITRGE** — Partition de filage (ordre des agents, lots, commandes, règles TDAH).  
- **ROADMAP Passage à HTMX** — Phases 1–5 transition Svelte → HTMX et filage.  
- **Sullivan — Status Report 01_02_2026** — État détaillé du kernel.  
- **docs/04-homeos/PHASE3_SPEC_FILAGE.md** — Spec technique Phase 3.  
- **docs/04-homeos/STATUS_REPORT_HOMEOS.md** — Vue Homeos incluant Sullivan.  
- **PRD_SULLIVAN.md**, **MODE_EMPLOI_SULLIVAN_GENOME.md**, **RAPPORT_ETAPE_SULLIVAN.md** — Références internes.

---

*Document généré le 1er février 2026 — Synthèse + Status Report Sullivan consolidé.*
