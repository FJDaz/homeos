# CONTEXTE WORKFLOW - Restructuration Génome HomeOS

**Date**: 10 février 2026, ~20h00
**Session**: Claude Code (Sonnet 4.5)
**Status**: ✅ Missions préparées, prêtes à exécuter
**Prochain step**: Exécution parallèle des 2 missions KIMI

---

## 🎯 OBJECTIF GLOBAL

Corriger la hiérarchie du **Genome Frontend** et améliorer l'UI du **Genome Viewer (port 9999)** pour obtenir une interface opérationnelle avec la bonne structure N0-N3.

---

## 📊 ÉTAT ACTUEL

### Problème Identifié

Le fichier `genome_inferred_kimi_innocent.json` utilise une **hiérarchie incorrecte** :

| Niveau | Actuel (INCORRECT) | Attendu (CORRECT) |
|--------|-------------------|-------------------|
| **N0** | 9 Workflows UX (Intent Refactoring, Arbitrage, etc.) | 4 Corps (BRS, BKD, FRD, DPL) |
| **N1** | Sections | 9 Organes (les workflows actuels) |
| **N2** | Features | Cellules (composants intermédiaires) |
| **N3** | Components | Atomes (éléments UI basiques) |

**Source du problème**: La "Méthode Kimi Innocent" (ligne 64 du fichier méthodologie) définit N0 comme "Les 9 étapes du parcours UX" au lieu des 4 Corps.

### Fichiers Critiques

```
/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/
├── genome_inferred_kimi_innocent.json    # Génome avec hiérarchie incorrecte (29 composants)
└── server_9999_v2.py                     # Serveur HTTP Genome Viewer (Version 2.0 FLAT)
```

**État server_9999_v2.py**:
- Version actuelle: 2.0 (FLAT - pas de hiérarchie Corps/Organes/Atomes)
- Version perdue: 2.1 (HIÉRARCHIQUE avec gradients, collapsible rows)
- Commit avec bon layout: `5aa7b18` - "feat(genome): Vue hiérarchique Corps/Organes/Cellules/Atomes"

---

## 🧠 LOGIQUE DES MISSIONS - POURQUOI 2 MISSIONS PARALLÈLES ?

### Le Problème à 2 Couches

Le Genome Viewer a **2 problèmes indépendants** qui peuvent être résolus en parallèle :

| Couche | Problème | Responsable | Impact |
|--------|----------|-------------|--------|
| **DONNÉES** | Hiérarchie N0-N3 incorrecte dans le JSON | KIMI Innocent | Structure logique du génome |
| **PRÉSENTATION** | UI plate sans hiérarchie visuelle | KIMI Conscient | Affichage et UX |

### Pourquoi "Innocent" vs "Conscient" ?

**KIMI Innocent (Gemini)** :
- **Rôle** : Inférence pure à partir des 4 sources (Doc, Code, Logs, Inférence)
- **Approche** : "Je ne connais rien du projet, je reconstitue tout from scratch"
- **Input** : Les 4 bundles de vérité
- **Output** : Génome restructuré avec N0=Corps, N1=Organes
- **Méthode** : Confrontation systématique, table de mapping, rapport d'incertitudes

**KIMI Conscient (Claude)** :
- **Rôle** : Amélioration UI avec connaissance du contexte existant
- **Approche** : "Je connais l'historique, je restaure et améliore"
- **Input** : Fichier actuel + commit 5aa7b18 + spécifications précises
- **Output** : UI hiérarchique avec 6 améliorations appliquées
- **Méthode** : Modifications ciblées, préservation des wireframes FRD V2

### Comment les Missions se Complètent

```
┌─────────────────────────────────────────────────────────────┐
│                  KIMI INNOCENT (Gemini)                     │
│  ✓ Restructure genome_inferred_kimi_innocent.json           │
│  ✓ Crée genome_restructured_n0_corps.json                   │
│  ✓ 4 Corps → 9 Organes → N Cellules → 29 Atomes            │
│  ✓ Mapping logique validé                                   │
└─────────────────────────────────────────────────────────────┘
                            ║
                            ║  CONVERGENCE
                            ▼
                  genome_restructured_n0_corps.json
                            │
                            ├─→ Chargé par server_9999_v2.py
                            │
┌─────────────────────────────────────────────────────────────┐
│                  KIMI CONSCIENT (Claude)                    │
│  ✓ Modifie server_9999_v2.py                                │
│  ✓ Ajoute hiérarchie visuelle (▼/▲, gradients, icônes)     │
│  ✓ Améliore UX (checkboxes, sizing, noms clairs)           │
│  ✓ Tri par identificabilité                                 │
└─────────────────────────────────────────────────────────────┘
                            ║
                            ▼
                  UI Hiérarchique Complète
                  (Données correctes + Présentation optimisée)
```

### Ordre d'Exécution Recommandé

**PARALLÈLE** (si 2 agents disponibles) :
- Les 2 missions sont **totalement indépendantes**
- Aucune donnée partagée en temps réel
- Gain de temps : ~30-40 min

**SÉQUENTIEL** (si 1 seul agent) :
1. **KIMI Innocent d'abord** → Valider structure génome
2. **KIMI Conscient ensuite** → Charger le nouveau génome dans l'UI

### Points de Vérification Post-Missions

Après exécution des 2 missions :

```bash
# 1. Vérifier cohérence génome
cat genome_restructured_n0_corps.json | jq '.n0_corps | length'
# Attendu: 4

# 2. Vérifier chargement dans server_9999_v2.py
grep -n "genome_restructured_n0_corps.json" server_9999_v2.py
# Attendu: ligne ~50-80 (import du JSON)

# 3. Test intégration
python server_9999_v2.py
open http://localhost:9999
# Vérifier: Hiérarchie 4 niveaux + 29 composants + checkboxes bottom-right
```

---

## 🚀 WORKFLOW EN COURS

### Approche: **2 Missions Parallèles**

```
┌─────────────────────────────────────────────────────────────┐
│                  KIMI INNOCENT (Gemini)                     │
│  Mission: Restructurer genome_inferred_kimi_innocent.json   │
│  Output: genome_restructured_n0_corps.json                  │
│  Durée estimée: ~30-45 min                                  │
└─────────────────────────────────────────────────────────────┘
                            ║
                            ║  EN PARALLÈLE
                            ║
┌─────────────────────────────────────────────────────────────┐
│                  KIMI CONSCIENT (Claude)                    │
│  Mission: Améliorer UI server_9999_v2.py (6 tâches)        │
│  Output: server_9999_v2.py modifié + rapport                │
│  Durée estimée: ~45-60 min                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📧 MISSIONS CRÉÉES (Prêtes à Exécuter)

### Mission 1: KIMI INNOCENT (Gemini)

**Fichier**: `/Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/kimi/MISSION_KIMI_INNOCENT_RESTRUCTURATION_GENOME.md`

**Tâche**: Restructurer le génome avec la hiérarchie correcte N0=Corps, N1=Organes

**Inputs**:
- `genome_inferred_kimi_innocent.json` (actuel avec 9 phases à N0)
- `METHODE_KIMI_INNOCENT.md` (méthodologie 4-source confrontation)
- Documentation projet

**Output attendu**:
- `genome_restructured_n0_corps.json` avec structure:
  ```json
  {
    "n0_corps": [
      {
        "id": "corps_brs",
        "name": "BRS - Brainstorm",
        "n1_organes": [
          {
            "id": "organe_ir",
            "name": "Intent Refactoring",
            "n2_cellules": [...]
          }
        ]
      },
      {
        "id": "corps_frd",
        "name": "FRD - Frontend",
        "n1_organes": [...]
      }
    ]
  }
  ```
- `RAPPORT_RESTRUCTURATION_GENOME.md` avec mapping et incertitudes

**Checklist validation**:
- [ ] 4 Corps exactement (BRS, BKD, FRD, DPL)
- [ ] 9 Organes répartis sous les Corps
- [ ] 29 Atomes préservés
- [ ] Noms user-friendly
- [ ] Confidence globale >= 0.80

---

### Mission 2: KIMI CONSCIENT (Claude)

**Fichier**: `/Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/kimi/MISSION_KIMI_CONSCIENT_UI_IMPROVEMENTS.md`

**Tâche**: 6 améliorations UI du Genome Viewer

#### Les 6 Tâches

1. **Checkboxes en bas à droite**
   - Changer `top:12px;right:12px` → `bottom:12px;right:12px`

2. **Réduire taille items + augmenter font-size**
   - Padding: 16px → 12px
   - Font nom: 13px → 14px
   - Font description: 11px → 12px
   - Font endpoint: 10px → 11px

3. **Rows collapsibles hiérarchiques**
   - Implémenter 4 niveaux: Corps > Organes > Cellules > Atomes
   - Headers avec gradients (vert Corps, bleu Organes, rose Cellules)
   - Flèches ▼/▲ pour collapse/expand
   - État initial: Premier Corps + Premier Organe ouverts, reste fermé

4. **Noms user-friendly**
   - 28 mappings fournis (ex: "Vue Rapport IR" → "Tableau des organes détectés")
   - Dictionnaire `USER_FRIENDLY_NAMES` à implémenter

5. **Tri par identificabilité user**
   - Ordre défini: upload, color-palette, preview, chat/bubble... (25 composants)
   - Appliquer tri au niveau Cellules (N2) uniquement

6. **Restaurer commit 5aa7b18**
   - Extraire layout hiérarchique du bon commit
   - Intégrer headers, gradients, icônes (🏛️ ⚙️ 🧬 ⚛️)
   - Préserver wireframes FRD V2 actuels

**Output attendu**:
- `server_9999_v2.py` modifié (in place)
- `RAPPORT_UI_IMPROVEMENTS.md`

**Checklist validation**:
- [ ] Checkboxes bottom-right
- [ ] Taille/font ajustées
- [ ] Hiérarchie 4 niveaux fonctionnelle
- [ ] 28 noms remplacés
- [ ] Tri identificabilité appliqué
- [ ] Headers gradients restaurés

---

## 🔄 MÉTHODOLOGIE "KIMI INNOCENT"

**Source**: `/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Methodologies/METHODE_KIMI_INNOCENT.md`

### Principe

Produire un **Genome Spatialisé N0-N3** exécutable par un dev frontend **sans connaissance préalable du projet**.

### 4 Bundles (Sources de Vérité)

Ordre de priorité (du + faible au + fort):

1. **A - Documentation** (PRD, Vision, Parcours UX) - Basse priorité
2. **B - Code** (Endpoints réels, routes API) - Moyenne priorité
3. **C - Logs** (Appels HTTP, erreurs 200/404) - Haute priorité
4. **D - Inférence** (Composants UI manquants) - Complète

**Règle d'or**: Logs > Code > Doc

### 5 Phases

1. **Lecture Séquentielle** (30 min) - STATUS_REPORT → Parcours UX → PRD → Code
2. **Table de Confrontation** (20 min) - Mapping Phase UX / Endpoints / Statut
3. **Extraction N0-N3** (30 min) - Structure hiérarchique obligatoire
4. **Validation Frontend** (20 min) - "Un dev junior peut-il coder sans questions?"
5. **Rapport d'Incertitudes** (10 min) - Lister les contradictions

### 10 Wireframes FRD V2 Différenciés

| Visual Hint | Usage | Différenciation |
|-------------|-------|-----------------|
| `status` | Check santé projet | 4 LEDs (vertes/grises) |
| `zoom-controls` | Navigation | ← Out / 🔍 Corps ▼ / In → |
| `download` | Export ZIP | Carte fichier + 📥 |
| `chat-input` | Message user | Champ + 📎😊 + envoi |
| `color-palette` | Style détecté | 4 swatches + chips |
| `choice-card` | Sélection style | Radio 2×2 |
| `stencil-card` | Fiche pouvoir | Garder/Réserve |
| `detail-card` | Fiche technique | Endpoint + Copier/Tester |
| `launch-button` | Lancer processus | 🚀 avec action |
| `apply-changes` | Sauvegarder | 💾/↩️ côte à côte |

---

## 🔧 COMMITS IMPORTANTS

### Commit avec bon layout hiérarchique

```bash
git show 5aa7b18:docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py
```

**Contenu attendu**:
- Headers hiérarchiques avec gradients
- Structure Corps > Organes > Cellules > Atomes
- Icônes par niveau (🏛️ Corps, ⚙️ Organes, 🧬 Cellules, ⚛️ Atomes)
- Collapse/expand fonctionnel
- Stats par niveau

**Commits récents pertinents**:
```
c955ba8 docs: Recréation documents GENOME FRD couche 1 et 2
74592a2 docs: Mise à jour STRATEGIE_LAYOUT_GENERATION avec démarche hiérarchique réelle
5aa7b18 feat(genome): Vue hiérarchique Corps/Organes/Cellules/Atomes avec ordre pédagogique ⭐
8420ad2 style(ui): Pictos sans fond blanc
```

---

## 📦 STRUCTURE ATTENDUE FINALE

### Génome Restructuré

```
N0: BRS (Brainstorm)
  └─ N1: Intent Refactoring (Organe)
      └─ N2: Rapport IR (Cellule)
          └─ N3: Tableau organes détectés (Atome)
          └─ N3: Fiche détaillée organe (Atome)
  └─ N1: Arbitrage (Organe)
      └─ N2: Stencils (Cellule)
          └─ N3: Carte pouvoir (Atome)

N0: BKD (Backend)
  └─ N1: Session (Organe)
      └─ ...

N0: FRD (Frontend)
  └─ N1: Layout (Organe)
  └─ N1: Upload (Organe)
  └─ N1: Dialogue (Organe)
  └─ N1: Validation (Organe)
  └─ N1: Adaptation (Organe)

N0: DPL (Deploy)
  └─ N1: Navigation (Organe)
      └─ ...
```

### UI Hiérarchique (server_9999_v2.py)

```html
▼ 🏛️ Corps: FRD - Frontend (5 organes, 15 atomes)
  ▼ ⚙️ Organe: Layout (2 cellules, 3 atomes)
    ▼ 🧬 Cellule: Galerie Layouts (3 atomes)
      ⚛️ [Wireframe: upload] Import fichier design
      ⚛️ [Wireframe: color-palette] Couleurs détectées
      ⚛️ [Wireframe: grid] Choix mise en page
    ▲ 🧬 Cellule: Sélection Style (1 atome)
  ▲ ⚙️ Organe: Upload
  ▲ ⚙️ Organe: Dialogue
  ▲ ⚙️ Organe: Validation
  ▲ ⚙️ Organe: Adaptation
▲ 🏛️ Corps: BRS - Brainstorm
▲ 🏛️ Corps: BKD - Backend
▲ 🏛️ Corps: DPL - Deploy
```

---

## ⚠️ POINTS D'ATTENTION

### NE PAS Modifier

- **Wireframes existants** (lignes 58-467 de server_9999_v2.py) - Corrects et optimisés
- **Visual hints** - Correspondent aux spécifications FRD V2
- **Endpoints** - Validés par confrontation code/logs

### Préserver

- **29 composants exactement** (pas plus, pas moins)
- **Méthodes HTTP** correctes (GET, POST, PUT, DELETE)
- **Confidence globale** >= 0.80

### Dangers Potentiels

1. **Perte de composants** lors de la restructuration N0-N3
2. **Mapping incorrect** des workflows vers les Corps
3. **Régression UI** si wireframes FRD V2 sont touchés
4. **Incohérence** entre génome restructuré et UI affichée

---

## 🎬 PROCHAINES ÉTAPES

### Exécution Parallèle des Missions

**Option A: Rester sur Claude Code**
```bash
# Terminal 1 - KIMI Innocent (via Gemini API externe)
python execute_mission_kimi_innocent.py

# Terminal 2 - KIMI Conscient (via Claude actuel)
# Exécuter les 6 tâches manuellement
```

**Option B: Passer à Antigravity**
1. Copier le contexte (ce fichier)
2. Copier les 2 missions depuis `.claude/mailbox/kimi/`
3. Exécuter en parallèle avec Gemini + Claude

**Option C: Séquentiel (plus sûr)**
1. KIMI Innocent d'abord (restructuration génome)
2. Vérifier output
3. KIMI Conscient ensuite (UI improvements)
4. Vérifier intégration

### Validation Finale

Une fois les 2 missions terminées:

```bash
# 1. Vérifier structure génome
cat genome_restructured_n0_corps.json | jq '.n0_corps | length'  # Doit être 4

# 2. Démarrer serveur
cd docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/
python server_9999_v2.py

# 3. Tester UI
open http://localhost:9999
# Vérifier:
# - Hiérarchie collapsible visible
# - 29 composants affichés
# - Checkboxes en bas à droite
# - Noms user-friendly
```

---

## 📊 MÉTRIQUES DE SUCCÈS

### Génome Restructuré
- [ ] 4 Corps (BRS, BKD, FRD, DPL)
- [ ] 9 Organes répartis logiquement
- [ ] 29 Atomes préservés (aucun perdu)
- [ ] Tous les Atomes ont: endpoint, method, visual_hint, layout_hint, interaction_type, description_ui
- [ ] Confidence >= 0.80
- [ ] Rapport d'incertitudes fourni

### UI Améliorée
- [ ] Checkboxes bottom-right (ligne 455)
- [ ] Padding 12px (ligne 454)
- [ ] Font-sizes augmentées (+1px sur 3 niveaux)
- [ ] 4 niveaux hiérarchiques fonctionnels
- [ ] Collapse/expand opérationnel
- [ ] Premier Corps + Premier Organe ouverts par défaut
- [ ] 28+ noms user-friendly appliqués
- [ ] Tri identificabilité respecté
- [ ] Headers gradients restaurés
- [ ] Wireframes FRD V2 intacts

### Intégration Globale
- [ ] Génome JSON parsable (pas d'erreur syntaxe)
- [ ] Serveur démarre sans erreur
- [ ] 29 composants s'affichent correctement
- [ ] Navigation hiérarchique fluide
- [ ] Validation composants fonctionnelle
- [ ] Pas de régression visuelle

---

## 🔗 FICHIERS DE RÉFÉRENCE

### Documentation
```
/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/
├── Methodologies/METHODE_KIMI_INNOCENT.md
├── Genome_Enrichi/Genome_OPTIMISE_2026-02-06/
│   ├── genome_inferred_kimi_innocent.json
│   └── server_9999_v2.py
└── FIGMA-Like/Figma-like_2026_02_08/
    ├── PLAN_INTEGRATION.md
    └── STRATEGIE_LAYOUT_GENERATION.md
```

### Missions
```
/Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/kimi/
├── MISSION_KIMI_INNOCENT_RESTRUCTURATION_GENOME.md     (Gemini)
├── MISSION_KIMI_CONSCIENT_UI_IMPROVEMENTS.md           (Claude)
└── CONTEXT_WORKFLOW_GENOME_2026_02_10.md              (Ce fichier)
```

### Plan Mode
```
/Users/francois-jeandazin/.claude/plans/snuggly-roaming-barto.md
```

---

## 💡 CONSEILS POUR LA REPRISE

### Si Switch vers Antigravity

1. **Copier ce contexte** + les 2 missions
2. **Lire le commit 5aa7b18** en premier pour comprendre le layout perdu
3. **Commencer par KIMI Innocent** (restructuration génome) car c'est le + critique
4. **Ne pas toucher aux wireframes** (lignes 58-467)

### Si Continuer sur Claude Code

1. **Exécuter les missions séquentiellement** (plus sûr que parallèle)
2. **Vérifier chaque output** avant de passer à la suivante
3. **Commit intermédiaire** après chaque mission réussie

### En Cas de Blocage

- **Incertitude mapping Corps**: Consulter `/docs/04-homeos/PRD_HOMEOS_ETAT_ACTUEL.md`
- **Erreur syntaxe JSON**: Utiliser `jq` pour valider
- **Régression UI**: Revenir au commit avant modifications

---

**Fin du contexte - Ready to resume! 🚀**
