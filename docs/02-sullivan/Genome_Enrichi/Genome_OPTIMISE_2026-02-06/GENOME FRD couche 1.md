# GENOME FRD - Couche 1 : Chronique des implémentations

**Projet** : AetherFlow / HomeOS - Genome Viewer  
**Port** : 9999  
**Date** : Février 2026  
**Version** : 2.1 - Vue hiérarchique biologique  

---

## 1. Fondation et architecture serveur

### 1.1 Infrastructure technique
- **Fichier** : `server_9999_v2.py`
- **Protocole** : HTTP simple (Python `http.server`)
- **Port** : 9999 (dédié, stable)
- **Données** : `genome_inferred_kimi_innocent.json` (29 composants)

### 1.2 Normalisation des données
```python
def normalize_keys(obj):
    # Conversion systématique des clés en minuscules
    # N0_PHASES → n0_phases, N1_Sections → n1_sections
    # Garantit l'uniformité des accès données
```

---

## 2. Architecture de navigation

### 2.1 Système d'onglets (Tabs)
Quatre modes de vue définis :
- **BRS** (Brainstorm) - Placeholder avec picto horloge
- **BKD** (Backend) - Placeholder avec picto couches
- **FRD** (Frontend) - Vue active du Genome (actuellement affichée)
- **DPL** (Deploy) - Placeholder avec picto étoile

### 2.2 Gestion conditionnelle de l'affichage
```javascript
// Masquage du layout principal pour BRS/BKD/DPL
// Affichage complet uniquement pour FRD
if (tabName === 'frd') {
    main.style.display = 'flex';
    placeholders.style.display = 'none';
} else {
    main.style.display = 'none';
    placeholders.style.display = 'block';
}
```

---

## 3. Structure hiérarchique du Genome

### 3.1 Classification en 4 niveaux biologiques

```python
# Classification par visual_hint

# CORPS : Templates et pages conteneurs
corps_items = ['preview', 'table', 'dashboard', 'grid', 'editor', 'list', 'accordion']

# ORGANES : Zones sémantiques et navigation
organes_items = ['stepper', 'breadcrumb', 'status', 'zoom-controls', 'chat/bubble']

# CELLULES : Composants composites interactifs
cellules_items = ['upload', 'color-palette', 'stencil-card', 'detail-card', 
                  'choice-card', 'card', 'form', 'chat-input', 'modal']

# ATOMES : Éléments d'interface indivisibles
atomes_items = ['button', 'launch-button', 'apply-changes']
```

### 3.2 Ordre pédagogique par niveau

**Corps** (ordre de découverte visuelle) :
1. `preview` - Point d'entrée immédiat
2. `table` - Organisation de données
3. `dashboard` - Vue synthétique
4. `grid` - Disposition spatiale
5. `editor` - Création de contenu
6. `list` - Énumération
7. `accordion` - Compression

**Organes** (ordre de navigation) :
1. `stepper` - "Où en suis-je ?"
2. `breadcrumb` - "D'où je viens ?"
3. `status` - "Ça va bien ?"
4. `zoom-controls` - Navigation spatiale
5. `chat/bubble` - Communication

**Cellules** (ordre d'interaction) :
1. `upload` - Première action (donner son matériel)
2. `color-palette` - Traitement
3. `stencil-card` - Décision
4. `detail-card` - Exploration
5. `choice-card` - Personnalisation
6. `card` - Présentation
7. `form` - Saisie
8. `chat-input` - Dialogue
9. `modal` - Focus

**Atomes** (ordre d'usage) :
1. `button` - Générique
2. `launch-button` - Action principale
3. `apply-changes` - Validation

---

## 4. Interface utilisateur

### 4.1 Sidebar (barre latérale)

#### Section pédagogique "Le Genome"
Explication en 3 niveaux :
1. **Métaphore** : "ADN de votre application"
2. **Méthode** : "Confrontation de 4 sources"
3. **Organisation** : "Hiérarchie biologique"

#### Indicateurs
- Confiance globale (%)
- Nombre de phases (étapes du workflow)
- Nombre de composants (29)

#### Types de composants
Classification par fonction (pas par nom technique) :
- Indicateurs d'état
- Contrôles de navigation
- Cartes de données
- Visualisation design
- Formulaires de choix
- Actions principales

### 4.2 Vue hiérarchique (contenu principal)

#### Structure de rows
```css
.level-section {
    border-top: 1px solid #e2e8f0;
}
/* Filet au-dessus, rien en dessous */
```

#### Headers collapsibles
- Flèches **Wingdings 2** : 6 (▼ ouvert) / 5 (▶ fermé)
- Pas de fond sous les headers
- Background #fff pour les titres

#### Grille de composants
```css
.component-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}
```

#### Descriptions par niveau
Chaque section accompagnée d'une explication contextualisée :
```
Corps : "Vous commencez par l'aperçu maquette..."
Organes : "Le stepper vous situe dans le processus..."
Cellules : "Vous uploadez un design..."
Atomes : "Les briques de base..."
```

---

## 5. Système de wireframes

### 5.1 Types de wireframes (10+)
| Type | Usage | visual_hint |
|------|-------|-------------|
| status | Indicateurs d'état | LEDs, couleurs |
| zoom-controls | Navigation | Boutons in/out/niveau |
| stencil-card | Fiches décision | Toggle garder/réserve |
| detail-card | Détails techniques | JSON, copier, tester |
| color-palette | Extraction design | Carrés couleurs + specs |
| choice-card | Sélection style | Options avec radio |
| launch-button | Actions principales | Bouton vert accentué |
| apply-changes | Sauvegarde | Double bouton annuler/appliquer |
| table | Listes données | Header + lignes |
| dashboard | Vue synthèse | Stats + graphique mini |
| preview | Aperçu maquette | Zones colorées |
| upload | Zone dépôt | Bordure dashed + icône |

### 5.2 Uniformisation typographique
Augmentation systématique pour lisibilité :
- 6px → 11px
- 7px → 12px
- 8px → 13px
- 9px → 14px

### 5.3 Simplification des labels
Remplacement des termes techniques par du langage naturel :
- "🔭 Navigation" → "Navigation dans l'architecture"
- "Veille du Système" → "Suivi du projet"
- "/api/health" → "État du service"
- "Génération du code" → "Création de votre site"
- "🎨 Style détecté" → "Couleurs extraites de votre design"
- Émojis supprimés → texte ou lettres (S, Go, +, ok)

---

## 6. Styles et design system

### 6.1 Palette HomeOS
- **Vert** : `#7aca6a` (primaire, actions, validation)
- **Bleu** : `#5a9ac6` (secondaire, navigation)
- **Orange** : `#e4bb5a` (accent, attention)

### 6.2 Ombres et profondeur
```css
box-shadow: 0 1px 3px rgba(0,0,0,0.05);  /* Subtil */
box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* Hover */
box-shadow: 0 8px 24px rgba(0,0,0,0.1);  /* Élevé */
```

### 6.3 Bordures et séparation
- `border-top: 1px solid #e2e8f0` pour les rows
- `border-left: 3px solid #7aca6a` pour les explications
- `border-radius: 8px` uniforme

---

## 7. Méthodologie d'inférence

### 7.1 Méthode "Kimi innocent"
Confrontation de 4 sources de vérité :
1. Documentation (README, specs, intentions)
2. Code source (API endpoints, modèles)
3. Logs utilisateur (interactions réelles)
4. Inférence visuelle (comportements attendus)

**Règle** : Quand 3 sources convergent, la confiance est élevée.

### 7.2 Structure du JSON
```json
{
  "genome_version": "3.0-kimi-innocent",
  "n0_phases": [{
    "n1_sections": [{
      "n2_features": [{
        "n3_components": [{
          "id": "comp_xxx",
          "visual_hint": "table|card|button",
          "description_ui": "L'utilisateur voit..."
        }]
      }]
    }]
  }]
}
```

---

## 8. Fichiers livrables

### 8.1 Serveur
- `server_9999_v2.py` - Serveur HTTP avec génération HTML dynamique

### 8.2 Données
- `genome_inferred_kimi_innocent.json` - Structure hiérarchique (29 composants)

### 8.3 Documentation
- `GENOME FRD couche 1.md` - Ce document (implémentations)
- `GENOME FRD couche 2.md` - Logique métier et réflexions

---

## 9. Points d'attention

### 9.1 Dépendances
- Python 3.x (bibliothèque standard uniquement)
- Aucune dépendance externe
- Wingdings 2 pour flèches (fallback système)

### 9.2 Compatibilité
- Navigateurs modernes (Chrome, Firefox, Safari, Edge)
- Optimisé desktop
- Vanilla JS (pas de framework)

### 9.3 Performance
- Génération HTML côté serveur
- Aucune requête API externe
- Temps de chargement < 100ms

---

## 10. Évolution et versioning

### Version 2.1 (actuelle)
- Hiérarchie biologique complète
- Wireframes enrichis et accessibles
- Interface pédagogique

### Prochaines étapes
- Intégration Figma Editor (Vue 2)
- Mode édition des composants
- Export JSON enrichi

---

*Document généré pour AetherFlow - Mode PROD*
