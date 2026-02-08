# STRATÉGIE DE GÉNÉRATION ET PROPOSITION DE LAYOUTS POUR HOMEOS STUDIO

**Date** : 2026-02-08  
**Version** : 2.0 - Vue hiérarchique biologique  

---

## CONTEXTE : Architecture du Genome en Frontend

L'objectif est de présenter les 29 composants du Genome de manière intelligible pour des utilisateurs non-techniques (75% du public cible), en évitant le jargon technique traditionnel (atomic design abstrait, nomenclature développeur).

---

## MÉTAPHORE BIOLOGIQUE : Corps > Organes > Cellules > Atomes

### Pourquoi cette métaphore ?

| Niveau technique | Analogie biologique | Intuition utilisateur |
|------------------|---------------------|----------------------|
| Templates/Pages | **Corps** | "C'est tout moi, mon enveloppe" |
| Zones fonctionnelles | **Organes** | "Le cœur pompe, le cerveau pense" |
| Blocs d'action | **Cellules** | "Les cellules travaillent ensemble" |
| Éléments simples | **Atomes** | "Les briques de base" |

### Avantages
- **4 niveaux uniquement** (règle cognitive des 4±1 Miller)
- **Termes du quotidien** médical (universel)
- **Hiérarchie évidente** (Corp > Organes > Cellules > Atomes)

---

## CLASSIFICATION DES COMPOSANTS

### Niveau 1 : CORPS (Templates et Pages)
**Définition** : Pages et templates qui structurent l'espace écran

**Ordre d'apparition pédagogique** :
1. `preview` (Aperçu maquette) - Point d'entrée visuel immédiat
2. `table` (Tableaux de données) - Organisation informationnelle
3. `dashboard` (Vue d'ensemble) - Synthèse
4. `grid` (Galeries) - Disposition
5. `editor` (Éditeurs) - Création
6. `list` (Listes) - Énumération
7. `accordion` (Accordéons) - Compression

### Niveau 2 : ORGANES (Zones sémantiques)
**Définition** : Zones fonctionnelles qui guident la navigation

**Ordre d'apparition** (logique de navigation) :
1. `stepper` (Étapes) - "Où en suis-je ?"
2. `breadcrumb` (Fil d'ariane) - "D'où je viens ?"
3. `status` (Indicateurs) - "Ça va bien ?"
4. `zoom-controls` (Navigation) - "Comment je me déplace ?"
5. `chat/bubble` (Dialogue) - "Je communique"

### Niveau 3 : CELLULES (Blocs fonctionnels)
**Définition** : Outils d'interaction réalisant une tâche complète

**Ordre d'apparition** (flux d'interaction) :
1. `upload` (Dépôt de fichiers) - Première action
2. `color-palette` (Couleurs extraites) - Traitement
3. `stencil-card` (Fiches décision) - Choix
4. `detail-card` (Détails) - Exploration
5. `choice-card` (Sélection style) - Personnalisation
6. `card` (Cartes génériques) - Présentation
7. `form` (Formulaires) - Saisie
8. `chat-input` (Entrée dialogue) - Conversation
9. `modal` (Fenêtres modales) - Focus

### Niveau 4 : ATOMES (Éléments indivisibles)
**Définition** : Briques de base de l'interface

**Ordre d'apparition** (fréquence d'usage) :
1. `button` (Boutons génériques)
2. `launch-button` (Lancement actions)
3. `apply-changes` (Validation)

---

## INTERFACE VISUELLE : Row-Based Hierarchical Viewer

### Structure de la Vue Genome (actuelle)

```
┌─────────────────────────────────────────┐
│ Tabs: BRS | BKD | FRD* | DPL           │
├─────────────────────────────────────────┤
│ ┌──────┐  ┌──────────────────────────┐ │
│ │      │  │ Architecture Genome      │ │
│ │ Le   │  │                          │ │
│ │ Genome│  │ ▼ CORPS (7)              │ │
│ │      │  │   Explication pédagogique│ │
│ │ [Stats]│  │   [Grille 4 items]     │ │
│ │      │  │ ──────────────────────── │ │
│ │ Types│  │ ▼ ORGANES (5)            │ │
│ │      │  │   Explication...         │ │
│ └──────┘  │   [Grille 4 items]     │ │
│  Sidebar  │ ──────────────────────── │ │
│           │ ▼ CELLULES (12)          │ │
│           │   Explication...         │ │
│           │   [Grille 4 items]     │ │
│           │ ──────────────────────── │ │
│           │ ▼ ATOMES (5)             │ │
│           │   Explication...         │ │
│           │   [Grille 4 items]     │ │
│           └──────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Caractéristiques visuelles

1. **Rows séparées par filet** (`border-top`) sans fond sous les headers
2. **Flèches Wingdings 2** : 6 (ouvert ▼) / 5 (fermé ▶)
3. **Descriptions pédagogiques** : Explications contextualisées pour chaque niveau
4. **Grille 4 colonnes** : `repeat(4, 1fr)` pour scan rapide
5. **Typographie lisible** : 11-14px (jamais en dessous)

---

## EXPLICATIONS PÉDAGOGIQUES PAR NIVEAU

### Corps
> "Les Corps sont les pages et templates qui structurent l'espace écran. Vous commencez par l'aperçu maquette, puis explorez les rapports, dashboards et éditeurs qui organisent votre travail en espaces cohérents."

### Organes
> "Les Organes sont les zones fonctionnelles qui guident votre navigation. Le stepper vous situe dans le processus, le fil d'ariane vous oriente, les indicateurs d'état vous informent sur la santé du système."

### Cellules
> "Les Cellules sont les outils d'interaction : vous uploadez un design, recevez une palette de couleurs, choisissez des styles, consultez des détails. Chaque Cellule réalise une tâche complète pour construire votre interface."

### Atomes
> "Les Atomes sont les briques de base de l'interface : les boutons que vous cliquez, les lancements d'actions, les validations. Invisibles seuls, ils donnent vie aux Cellules et rendent l'interface interactive."

---

## TRANSITION VERS FIGMA EDITOR

### Déclencheur
Le bouton **"Valider (n)"** dans le sticky header permet de sélectionner des Corps et de basculer vers la Vue Figma Editor.

### Pré-layouts par défaut
**Moment de création** : Au clic sur "Valider" (switch Vue 1 → Vue 2)

**Contenu** :
- Skeleton screen pour Corps en cours de génération
- Miniature aperçu si données existantes
- Warning si dimensions manquantes → Brainstorm modal

### Workflow complet
```
Vue 1 (Genome Browser)
    └─ User coche 3 Corps
    └─ Clique "Valider (3)"
        └─ SWITCH
            └─ Vue 2 (Figma Editor)
                ├─ Row Corps (3 miniatures)
                ├─ User drag un Corps
                ├─ Drop sur canvas
                │   ├─ Si ⚠️ → Brainstorm dimensions
                │   └─ Si ✅ → Fabric.js render
                └─ Double-clic navigation drill-down
```

---

## AVANTAGES DE CETTE APPROCHE

1. **Apprentissage gratuit** : L'ordre reflète le parcours utilisateur réel
2. **Pas de jargon** : Métaphore corporelle universelle
3. **Scalable** : 4 niveaux suffisent pour 29 composants
4. **Préparation Figma** : Les Corps sélectionnés deviennent des objets éditables

---

## FICHIERS CONNEXES

- `PLAN_INTEGRATION.md` : Plan technique d'intégration du Figma Editor
- `UX Phase FRD Clarifé.md` : Spécifications UX détaillées
- `server_9999_v2.py` : Implémentation actuelle (Genome Viewer)
