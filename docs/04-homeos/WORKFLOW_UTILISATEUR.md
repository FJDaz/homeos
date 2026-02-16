# Workflow Utilisateur - HomeOS

**Version**: 1.0
**Date**: 10 février 2026
**Statut**: Production

---

## Vue d'ensemble

HomeOS accompagne l'utilisateur dans la création d'une application web complète, de l'idée initiale au déploiement. Le système est organisé en **4 grandes phases** correspondant aux onglets de l'interface.

---

## Phase 1 : Brainstorm (BRS)

### Objectif
Analyser l'intention de l'utilisateur et structurer les besoins fonctionnels.

### Étapes

#### 1. Intent Refactoring
- **Action** : L'utilisateur décrit son projet en langage naturel
- **Système** : Détecte les "organes" (fonctionnalités clés) du futur système
- **Output** : Rapport IR avec liste des organes identifiés

#### 2. Arbitrage
- **Action** : L'utilisateur consulte les stencils (pouvoirs) proposés
- **Système** : Présente des cartes de fonctionnalités avec boutons Garder/Réserve
- **Output** : Sélection validée des fonctionnalités à implémenter

---

## Phase 2 : Backend (BKD)

### Objectif
Définir l'architecture serveur et la gestion des données.

### Étapes

#### 3. Session Management
- **Action** : Configuration de la gestion d'état
- **Système** : Propose architecture sessions (mémoire, Redis, DB)
- **Output** : Configuration backend validée

---

## Phase 3 : Frontend (FRD)

### Objectif
Générer l'interface utilisateur adaptée aux fonctionnalités validées.

### Étapes

#### 4. Layout Selection
- **Action** : L'utilisateur choisit parmi 8 styles de mise en page
- **Système** : Affiche galerie 3×2 avec preview de chaque layout
- **Output** : Mise en page sélectionnée

#### 5. Upload Design
- **Action** : Import d'un fichier design (Figma, Sketch, image)
- **Système** : Analyse le fichier et détecte couleurs, typographie, composants
- **Output** : Palette de couleurs + composants identifiés

#### 6. Dialogue Utilisateur
- **Action** : Affinage via conversation avec Sullivan (agent IA)
- **Système** : Chat avec suggestions contextuelles
- **Output** : Spécifications précisées

#### 7. Validation Composants
- **Action** : L'utilisateur sélectionne les composants UI à générer
- **Système** : Affiche le Genome avec checkboxes par composant
- **Output** : Liste des composants validés (29 max)

#### 8. Adaptation / Zoom Atome
- **Action** : Ajustement fin d'un composant spécifique
- **Système** : Vue détaillée avec paramètres éditables
- **Output** : Composant customisé

---

## Phase 4 : Deploy (DPL)

### Objectif
Préparer et exporter le projet final.

### Étapes

#### 9. Navigation
- **Action** : Vérification du breadcrumb et retours
- **Système** : Affiche arborescence complète du projet
- **Output** : Structure navigable validée

#### 10. Export / Téléchargement
- **Action** : Génération du code final
- **Système** : Crée archive ZIP avec tous les fichiers
- **Output** : Projet téléchargeable

---

## Synthèse des Étapes

| # | Étape | Phase | Type d'interaction |
|---|-------|-------|--------------------|
| 1 | Intent Refactoring | BRS | Texte → Tableau |
| 2 | Arbitrage | BRS | Cartes → Sélection |
| 3 | Session | BKD | Configuration |
| 4 | Layout Selection | FRD | Galerie → Choix |
| 5 | Upload Design | FRD | Fichier → Analyse |
| 6 | Dialogue | FRD | Chat |
| 7 | Validation Composants | FRD | Genome → Checkboxes |
| 8 | Adaptation | FRD | Zoom → Édition |
| 9 | Navigation | DPL | Breadcrumb |
| 10 | Export | DPL | Téléchargement |

---

## Points de Contrôle Utilisateur

À chaque étape, l'utilisateur peut :
- **Revenir** en arrière via breadcrumb
- **Sauvegarder** l'état actuel
- **Annuler** et recommencer
- **Valider** pour passer à l'étape suivante

---

**Note** : Ce workflow est celui implémenté dans l'interface Studio (port 8000) et visualisé dans le Genome Viewer (port 9999).
