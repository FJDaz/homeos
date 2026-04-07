# DESIGN.md — HoméOS Design System
**Version :** 1.1.0
**Autorité :** FJD (Directeur Artistique) — seule personne habilitée à modifier ce fichier.
**Usage :** Loi esthétique pour tous les agents (Sullivan, Gemini, MIMO, Qwen). Parsé par `parse_design_md()`. Injecté dans HOMEO_GENOME.md §2. Prévaut sur tout autre document de style.

> Ce fichier couvre l'**UI système HoméOS** (l'outil lui-même).
> Pour les screens générés dans les projets élèves → `projects/{uuid}/DESIGN.md` (distinct).
> Pour les interactions FEE (GSAP, Lenis) → `DESIGN_FEE.md`.

---

## Colors

### Palette de base
| Token | Valeur | Usage |
|---|---|---|
| `--bg-primary` | `#f7f6f2` | fond global — crème chaud |
| `--bg-secondary` | `#efefeb` | fond panneau secondaire, hover subtil |
| `--text-primary` | `#3d3d3c` | texte principal — jamais noir pur |
| `--text-muted` | `#9a9a98` | labels secondaires, placeholders |
| `--separator` | `#e5e5e5` | bordures, dividers |
| `--homeos-green` | `#8cc63f` | nudge uniquement — voir §Tone |

### Accents désaturés
| Token | Valeur | Rôle sémantique |
|---|---|---|
| `--accent-bleu` | `#a8c5fc` | focus, sélection active |
| `--accent-vert` | `#a8dcc9` | succès, confirmé |
| `--accent-rose` | `#d4b2bc` | alerte douce, attention |
| `--accent-orange` | `#edd0b0` | avertissement |
| `--accent-mauve` | `#c4b5d4` | info, neutre |
| `--accent-rouge` | `#ddb0b0` | erreur — jamais rouge vif |

### Règles absolues
- Noir pur `#000` interdit → utiliser `--text-primary`
- Rouge vif (`#ff0000`, `#ef4444`) interdit → utiliser `--accent-rouge`
- Blanc pur `#ffffff` déconseillé → utiliser `--bg-primary`
- Dégradés interdits sans validation FJD explicite

---

## Typography

### Polices système
```
UI :    'Geist', -apple-system, BlinkMacSystemFont, sans-serif
Code :  'Geist Mono', 'Fira Code', monospace
```

> **Direction typographique long terme (FJD) :** Univers LT Std — tradition suisse, Frutiger, design-friendly. Geist est un refuge provisoire jusqu'à la mise en place d'un générateur `@font-face` robuste. Quand Univers sera disponible, il remplace Geist sur toute la stack. Ne pas hardcoder Geist dans les nouveaux composants critiques — utiliser `font-family: inherit` pour faciliter la migration.

### Échelle
| Rôle | Taille | Weight | Usage |
|---|---|---|---|
| `micro` | 9px | 400 | timestamps, badges discrets |
| `caption` | 10px | 400 | labels secondaires, métadonnées |
| `label` | 11px | 400 | nav items, labels interface |
| `body` | 12px | 400 | **base** — texte courant |
| `body-md` | 13px | 400 | corps légèrement aéré |
| `title-sm` | 14px | 500 | titres de section, drawers |
| `title` | 16px | 600 | titres principaux |
| `display` | 20px | 600 | titres de page, états vides |

### Règles absolues
- Minimum : **9px** — en dessous interdit
- Maximum sans validation FJD : **20px**
- Weights autorisés : 400, 500, 600 — pas de 700/bold
- `text-transform: uppercase` interdit
- `letter-spacing` > `0.05em` interdit
- Line-height minimum : `1.2` — défaut `1.4`

---

## Shape

| Token | Valeur | Usage |
|---|---|---|
| `--radius-sm` | `2px` | inputs, tableaux dense |
| `--radius` | `4px` | **défaut** — boutons, badges |
| `--radius-md` | `6px` | cards de contenu |
| `--radius-lg` | `12px` | modals, panels flottants |
| `--radius-max` | `20px` | **maximum absolu** — pills, overlays |

### Règles absolues
- `border-radius` > `20px` interdit
- `border-radius: 50%` interdit sauf avatars utilisateur
- Classes Tailwind `rounded-2xl`, `rounded-3xl`, `rounded-full` interdites
- Contextes Hard-Edge (Wire, tableaux de données) : `0px` — respecter le contexte de la mission

---

## Effects

```
allowShadow:   ambient
allowGradient: false
allowBlur:     false
allowAnimation: open (UI: transitions légères / FEE: GSAP sans restriction)
```

### Ombres
Trois niveaux :
- **Ambiance** (paper on the desk) : `box-shadow: 0 4px 16px rgba(0,0,0,0.06)` — panels, cards, drawers flottants ✓
- **Focus ring** : `0 0 0 2px var(--bg-primary), 0 0 0 3px var(--text-primary)` ✓
- **Ombre portée dure** (Material Design) : ✗ interdit

> **Intention FJD :** L'effet "paper on the desk" fait partie de l'identité HoméOS. Piste : encapsuler toute l'UI dans une boîte avec cet effet, l'intérieur restant VS Code-like.

- `drop-shadow` sur images/SVG : parcimonie autorisée
- `filter: drop-shadow()` agressif : interdit

### Transitions UI
- Autorisées : `opacity`, `transform`, `background-color` — durée max `200ms`
- `transition-duration` > `200ms` interdit dans l'UI système
- Animations GSAP réservées aux screens projets en mode FEE → voir `DESIGN_FEE.md`

### Filtres
- `backdrop-filter: blur()` interdit
- `filter: blur()` interdit

---

## Spacing

Grille de base : **8px** — tout espacement multiple de 4px minimum.
> Les interprétations Sullivan ont été trop libres sur ce point. Le respect de la grille est non-négociable.

| Token | Valeur |
|---|---|
| `--space-1` | `4px` |
| `--space-2` | `8px` (unité de base) |
| `--space-3` | `12px` |
| `--space-4` | `16px` |
| `--space-6` | `24px` |
| `--space-8` | `32px` |

### Références layout
```
--sidebar-width:  200px
--header-height:  48px
```

- Valeurs arbitraires (`padding: 7px`, `margin: 13px`) interdites
- Classes Tailwind `p-5`, `p-7`, `gap-5`, `gap-7` à éviter

---

## Tone

- **Majuscules : rares et justifiées** — pas la propension anglo-saxonne systématique. Autorisées pour les éléments "got to see" (étape critique, alerte, titre de section structurant). Interdites sur les boutons courants, labels, nav items. Règle : si tu te demandes si c'est justifié, c'est que ça ne l'est pas.
- **Pas d'emojis** dans l'UI système — ni dans les labels, ni dans les boutons, ni dans les messages Sullivan
- **Pas de points d'exclamation** sauf toast de succès sobre
- Langue UI : français — anglais accepté dans le code et les variables

### Icons
- Privilégier les **icônes SVG inline sobres** — trait fin, monochrome, style minimaliste
- Taille recommandée : 14×14px (nav), 16×16px (actions), 20×20px (states)
- Stroke width : 1 à 1.5px — jamais gras
- Couleur : `currentColor` — hérite du contexte, pas de couleur hardcodée
- Bibliothèques autorisées : Lucide, Phosphor (style `thin` ou `regular`) — pas de Font Awesome, pas de Material Icons
- Emojis comme icônes fonctionnelles : **interdit**

### Le vert HoméOS `#8cc63f`
Nudge uniquement — jamais en fond large :
- ✓ bordure active, dot d'état, icône active, underline de nav, fond CTA < 160px
- ✗ fond de section, fond de sidebar, fond de card entière

---

## Forbidden

### Classes Tailwind interdites
```
rounded-2xl  rounded-3xl  rounded-full
shadow  shadow-sm  shadow-md  shadow-lg  shadow-xl  shadow-2xl
drop-shadow-*
text-4xl  text-5xl  text-6xl
font-bold  font-black
uppercase  tracking-widest  tracking-wider
bg-gradient-*  from-*  via-*  to-*
backdrop-blur-*  blur-*
animate-bounce  animate-spin  animate-pulse
```

### CSS interdit
```css
color: black;  color: #000;
background: white;
border-radius: > 20px;
box-shadow: (tout sauf focus ring);
font-weight: 700 | 800 | 900;
text-transform: uppercase;
font-size: < 9px ou > 20px (sans validation FJD);
```

### JS généré interdit
- `document.write()`, `alert()`, `confirm()`, `prompt()`
- `localhost` hardcodé → utiliser `window.location.origin`
- Scripts inline non-CDN dans les screens

---

## parse_design_md()

Format attendu par `core/design_parser.py` :
- Sections : `## NomSection`
- Tokens : tableaux Markdown 3 colonnes (Token | Valeur | Usage)
- Valeurs multi-lignes : blocs `code`
- Contraintes Sullivan : sections `### Règles absolues`
