# SVG War Room Design Spec

## 1. Palette couleurs
| Hex | Occurences | Rôle/Zone |
| :--- | :--- | :--- |
| #FFFFFF | 3 | Fond principal du canevas et des zones de travail |
| #F9F9F9 | 1 | Fond secondaire (Zone War Room après header) |
| #F2F3F5 | 5 | Zones de contrôle / inputs secondaires |
| #E4E6EA | 17 | Boutons neutres ou fonds de cartes secondaires |
| #EFEFEF | 1 | Séparateur cockpit (Stroke 1.57px) |
| #D1D4D9 | 4 | Bordures / Éléments structurels légers |
| #9CA2AD | 4 | Éléments d'interface secondaires |
| #999999 | 31 | Boutons d'action / Cartes (fill) |
| #7F7A66 | 2 | Bordure extérieure du canevas (Stroke 0.58px) |
| #666666 | 96 | Texte principal (flattened paths) et icônes |
| #333333 | 6 | Lignes de grille et diviseurs majeurs (Stroke 0.5px) |
| #626AE8 | 3 | **Accent Gemini** (Indigo) - Indicateurs d'état |
| #A58DE0 | 1 | **Accent DeepSeek** (Mauve) - Indicateur d'état |
| #8CC63F | 4 | **Accent Groq / Sullivan** (Vert Signature) - Branding |
| #5EC069 | 2 | **Validation / Succès** (Vert Brillance) - Cercle cockpit |
| #000000 | >1 | Texte additionnel (paths) |

## 2. Layout global
- **Dimensions viewport** : 2570 x 1736 px
- **Zones identifiées** :
    - **Header** : 2570 x 64 px (Top: 0)
    - **Sidebar** : 554 x 1736 px (Left: 0)
    - **Grille War Room** : Largeur 2016px (commence à x=554)
    - **Colonnes** : 4 colonnes de 504px chacune.
- **Gouttières entre zones** : 0px (séparation par filets de 0.5px #333333)

## 3. Typographie
*Note : Le texte est aplati en tracés vectoriels dans le SVG (paths).*
| Niveau | font-family | font-size | font-weight | Couleur |
| :--- | :--- | :--- | :--- | :--- |
| Titres (Providers) | *ambigu* | ~16-18px | Bold | #000000 |
| Body Text (SSE) | *ambigu* | ~14px | Regular | #666666 |
| Labels Cockpit | *ambigu* | ~12px | Medium | #666666 |
| Boutons | *ambigu* | ~14px | Semi-bold | #FFFFFF / #666666 |

## 4. Zones nommées — détail
### Header
- Dimensions : 2570x64px
- Bordure : Inférieure #333333 (0.5px)
- Contenu : Navigation globale

### Column 1 (Gemini)
- Position : x=554px, width=504px
- Accent : #626AE8
- Contenu : Flux de tokens Gemini

### Column 2 (DeepSeek)
- Position : x=1058px, width=504px
- Accent : #A58DE0
- Contenu : Flux de tokens DeepSeek

### Column 3 (Groq)
- Position : x=1562px, width=504px
- Accent : #8CC63F
- Contenu : Flux de tokens Groq / Llama

### Column 4 (Sullivan's Basket)
- Position : x=2066px, width=504px
- Fond : #FFFFFF / #F9F9F9
- Contenu : Pépites capturées et Cockpit de génération PRD

## 5. Composants atomiques
- **Boutons** : Rectangles de ~180x75px (#999999) ou ronds (radius 50%).
- **Insight Cards** : Blocs à bords francs (radius=0 dans le SVG), bordures subtiles.
- **Indicateurs de statut** : Cercles de ~25px de diamètre aux couleurs des accents providers.

## 6. Différenciateurs par provider
- **Couleur d'accent** : Indigo (#626AE8) pour Gemini, Mauve (#A58DE0) pour DeepSeek, Vert (#8CC63F) pour Groq.
- **Positionnement** : Ordre strict C1, C2, C3 de gauche à droite après la sidebar.

## 7. Barre de séquençage
Non identifiée explicitement comme barre horizontale, mais intégrée dans le cockpit Sullivan (Colonne 4, bas de page) avec des indicateurs circulaires pour chaque étape/provider.
