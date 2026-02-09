# Synthèse : Figma Editor Genome & Décision de Retour au Parcours UX Sullivan

**Date** : 2026-02-08  
**Auteur** : FJDaz + Agent IA (Kimi)  
**Fichier** : `/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py`  
**Branche** : `FRONTEND-V1` (poussée sur GitHub)

---

## 1. RÉSUMÉ EXÉCUTIF

### Ce qui a été construit
Un **éditeur visuel Figma-like** intégré dans le Genome Viewer, permettant de manipuler les 9 Corps (phases) du parcours Sullivan via une interface drag & drop avec canvas Fabric.js.

### Décision stratégique
**RETOUR au parcours UX Sullivan défini dans** `Parcours UX Sullivan.md`.

Le Figma Editor était une **tentative de navigation alternative** (visual-first) mais s'écarte du workflow **step-by-step** prévu (IR → Arbiter → Genome → Composants → Upload → Analyse → Dialogue → Validation → Adaptation).

---

## 2. CE QUI A ÉTÉ IMPLÉMENTÉ (Figma Editor V1)

### Architecture technique
```
single-file HTML généré par server_9999_v2.py
├── Vue 1: Genome Browser (hiérarchie N0-N3, checkboxes)
├── Vue 2: Figma Editor (scroll vertical)
│   ├── Row Corps (9 miniatures N0)
│   ├── Sidebar (filtrage contextuel N1/N2/N3)
│   ├── Canvas Fabric.js (1440×900px)
│   ├── Toolbar (zoom, export, delete)
│   └── Breadcrumb (navigation N0›N1›N2)
└── localStorage (persistance blueprints + canvas)
```

### Features complétées

| Phase | Feature | Status | Notes |
|-------|---------|--------|-------|
| **0** | Blueprints pré-générés | ✅ | 5 types (dashboard/table/editor/grid/preview) stockés dans localStorage |
| **1** | Switch Browser→Editor | ✅ | Scroll vertical smooth |
| **2** | Row Corps + Drag&Drop | ✅ | 9 Corps avec wireframes SVG distincts |
| **3** | Navigation hiérarchique | ✅ | Sidebar filtrée par Corps actif, breadcrumb clickable |
| **4** | Brainstorm + Export JSON | ✅ | Modal dimensions, export canvas state |
| **A** | Polissage | ✅ | Zoom, suppression, auto-save, animations |

### Points forts du Figma Editor
1. **Visualisation des 9 Corps** (phases du genome) avec aperçus wireframe distincts
2. **Contextualité** : La sidebar affiche uniquement les organes du Corps sélectionné
3. **Dimensions réelles** : Les Corps apparaissent en 1440×900px (desktop) sur le canvas
4. **Structure Sullivan** : Zones visibles (header/sidebar/content) selon le type
5. **Persistance** : localStorage pour blueprints et état canvas
6. **Export** : JSON complet du canvas pour réutilisation

---

## 3. PROBLÈMES IDENTIFIÉS

### 3.1 Écart par rapport au Parcours UX Sullivan

Le Figma Editor propose une navigation **"carte blanche"** où l'utilisateur peut :
- Sélectionner n'importe quel Corps (N0) à tout moment
- Dropper n'importe où sur le canvas
- Gérer plusieurs Corps simultanément

**Mais le Parcours UX Sullivan prévoit** :
```
1. IR (Intention) → Capture idée brute
2. Arbiter → Validation contraintes techniques  
3. Genome → Fixation topologie (fichier métadonnées)
4. Composants Défaut → Base fonctionnelle immédiate
5. Template Upload → Réception PNG (ou 8 propositions)
6. Analyse → Extraction style/layout du PNG
7. Dialogue → Affinage avec Sullivan (Chat)
8. Validation → Accord final structure
9. Adaptation → Génération HTMX (Top-Bottom: Corps→Organe→Atome)
```

### 3.2 Manques du Figma Editor vs Parcours UX

| Parcours UX | Figma Editor | Impact |
|-------------|--------------|--------|
| **Étape 5** : Upload PNG | ❌ Absent | Fonctionnalité clé manquante |
| **Étape 6** : Analyse visuelle Gemini | ❌ Absent | Pas d'extraction automatique |
| **Étape 7** : Dialogue chat Sullivan | ❌ Absent | Pas de médiation pédagogique |
| **Étape 9** : Top-Bottom par itération | ⚠️ Partiel | Drill-down existe mais pas la validation granulaire |
| **Ghost Mode** (contexte spatial) | ❌ Absent | Perte de contexte en zoomant |
| **Check Homéostasie** | ❌ Absent | Pas de garde-fou design vs Genome |
| **Journal Narratif** | ❌ Absent | Pas de traçabilité pédagogique |

### 3.3 Bugs résiduels (avant décision de pivot)
- Suppression clavier intermitente
- Persistance canvas trop aggressive (reload affiche anciens éléments)
- Double-clic drill-down fonctionne mais pas de "ghost mode" pour le contexte

---

## 4. DÉCISION : RETOUR AU PARCOURS UX SULLIVAN

### Justification
Le Figma Editor est une **belle preuve de concept technique** mais :
1. **S'écarte du workflow pédagogique** prévu pour les étudiants/enseignants
2. **Nécessite trop de code** pour atteindre la qualité d'un Figma réel
3. **Ignore les étapes clés** (upload PNG, analyse Gemini, dialogue)
4. **Pas de valeur ajoutée** par rapport au parcours step-by-step pour le cas d'usage Homeos

### Ce qui est conservé
- **Le serveur** `server_9999_v2.py` (architecture deux-vues fonctionnelle)
- **Les wireframes SVG** des 9 Corps (pour les afficher dans le parcours)
- **Le concept de Blueprints** (structures par type de composant)
- **La navigation N0-N3** (hiérarchie biologique)

### Ce qui doit être refondu
- Remplacer le canvas libre par un **workflow step-by-step** (étapes 1-9)
- Transformer la sidebar en **interface de dialogue** avec Sullivan
- Ajouter l'**upload PNG** et l'analyse visuelle (Gemini)
- Implémenter le **Top-Bottom validation** avec ghost mode
- Ajouter le **check d'homéostasie** (Auditor)

---

## 5. ARCHITECTURE CIBLE (Selon Parcours UX)

### Flow utilisateur attendu
```
┌─────────────────────────────────────────────────────────────────┐
│  ÉTAPE 1-3 : IR / ARBITER / GENOME (déjà existant)             │
│  → Génération du fichier genome.json                            │
├─────────────────────────────────────────────────────────────────┤
│  ÉTAPE 4 : COMPOSANTS DÉFAUT                                    │
│  → Affichage des "Stencils" (schémas filaires)                 │
│  → Validation "Garder/Réserve" par capacité                     │
├─────────────────────────────────────────────────────────────────┤
│  ÉTAPE 5 : CARREFOUR CRÉATIF                                    │
│  → Option A : Upload PNG (analyse visuelle)                     │
│  → Option B : 8 propositions de layouts                         │
├─────────────────────────────────────────────────────────────────┤
│  ÉTAPE 6 : ANALYSE (Designer Vision)                           │
│  → Calque d'architecte sur le PNG                               │
│  → Zones détectées + Hypothèses de placement                    │
│  → Extraction style (border-radius, couleurs...)                │
├─────────────────────────────────────────────────────────────────┤
│  ÉTAPE 7 : DIALOGUE (Collaboration Heureuse)                   │
│  → Chat avec Sullivan pour affiner le matching                  │
│  → Questions sur les ambiguïtés                                 │
├─────────────────────────────────────────────────────────────────┤
│  ÉTAPE 8 : VALIDATION                                           │
│  → Accord final utilisateur                                     │
│  → Figer le plan d'exécution                                    │
├─────────────────────────────────────────────────────────────────┤
│  ÉTAPE 9 : ADAPTATION (Top-Bottom)                             │
│  → Niveau 1 : Corps (layout global)                             │
│  → Niveau 2 : Organe (composant)                                │
│  → Niveau 3 : Atome (détail micro)                              │
│  → Ghost mode + Check homéostasie                               │
└─────────────────────────────────────────────────────────────────┘
```

### Modules à développer (d'après Parcours UX)

| Module | Fichier | Rôle |
|--------|---------|------|
| **Translator** | `identity.py` | Routes JSON → "Intentions" HCI |
| **Stenciler** | `identity.py` | Génère schémas filaires (Blueprints) |
| **Navigator** | `identity.py` | Gère pile stack (zoom in/out) |
| **Auditor** | `identity.py` | Vérifie homéostasie design vs Genome |
| **Upload Handler** | `studio_routes.py` | Réception PNG, preprocessing |
| **Vision Analyzer** | `design_analyzer.py` | Analyse PNG via Gemini |
| **Chat Mediator** | `sullivan_chatbot.py` | Dialogue étape 7 |
| **Distiller** | `identity.py` | Génération HTMX étape 9 |

---

## 6. FICHIERS CONCERNÉS

### Déjà modifiés (branche FRONTEND-V1)
- `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py`
- `docs/02-sullivan/FIGMA-Like/Figma-like_2026_02_08/PLAN_INTEGRATION.md`
- `.cursor/skills/kimi-innocent-genome/SKILL.md`

### À créer/modifier pour Parcours UX
- `Backend/Prod/sullivan/identity.py` (cœur du système)
- `Backend/Prod/sullivan/studio_routes.py` (API HTMX)
- `Backend/Prod/sullivan/design_analyzer.py` (analyse PNG)
- Templates Jinja2 pour les étapes 4-9

---

## 7. RECOMMANDATIONS

### Immédiat
1. **Basculer sur `main`** ou créer branche `parcours-ux-sullivan`
2. **Conserver** `server_9999_v2.py` comme référence technique
3. **Démarrer** l'implémentation de `identity.py` avec les 4 modules (Translator, Stenciler, Navigator, Auditor)

### Court terme
1. Implémenter **Étape 4** (Composants Défaut) avec les Stencils
2. Ajouter **Étape 5** (Upload PNG + 8 propositions)
3. Intégrer **Gemini Vision** pour l'étape 6 (Analyse)

### Moyen terme
1. Développer le **Chat Mediator** pour l'étape 7
2. Implémenter le **Top-Bottom** avec ghost mode (étape 9)
3. Ajouter le **Journal Narratif** pour la valeur pédagogique

---

## 8. CONCLUSION

Le Figma Editor représente une **tentative valable** de navigation visuelle mais ne correspond pas au besoin pédagogique du projet Homeos/Sullivan.

**La force du Parcours UX Sullivan** réside dans sa progression guidée :
- De l'intention brute (IR) → à la topologie fixée (Genome)
- Des composants neutres (Étape 4) → au design personnalisé (Upload PNG)
- De l'analyse automatique (Étape 6) → au dialogue médiateur (Étape 7)
- De la validation globale (Étape 8) → à l'adaptation chirurgicale (Étape 9)

**Le Figma Editor** reste disponible sur la branche `FRONTEND-V1` comme référence et pourrait être réactivé comme **mode "Expert"** optionnel dans une future version.

---

**Fin de la synthèse**  
*Prochaine étape : Implémentation de `identity.py` selon les spécifications du Parcours UX Sullivan*
