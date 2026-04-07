# 🎨 Bibliothèque de Styles Sullivan

Collection de 20 styles de rendu SVG pour les cartes organe AetherFlow.

## 📁 Fichiers

| Fichier | Description |
|---------|-------------|
| `style_prompts_library.json` | 20 prompts templates pour différents styles UI |

## 🎯 Styles Disponibles

| ID | Nom | Description | Use Case |
|----|-----|-------------|----------|
| `minimal` | Minimaliste | Épure totale, lignes fines | Dashboards pros |
| `brutalist` | Brutaliste | Bordures épaisses, contraste fort | Landing pages audacieuses |
| `kids` | Enfant / Jeunesse | Couleurs vives, formes arrondies | Apps éducatives |
| `neumorphism` | Neumorphisme | Effets relief doux | IoT, contrôles |
| `glassmorphism` | Glassmorphism | Transparence, flou | Apps modernes |
| `retro` | Rétro | Années 70-80, teintes sépia | Marques vintage |
| `cyberpunk` | Cyberpunk | Néon, noir profond | Gaming, tech |
| `swiss` | Swiss Design | Grille rigide, Helvetica | Éditorial, print |
| `material` | Material Design | Ombres portées, surfaces | Apps Android |
| `flat` | Flat Design | Couleurs plates, sans relief | Web moderne |
| `skeuomorphism` | Skeuomorphisme | Réalisme, textures | Apps legacy iOS |
| `art_nouveau` | Art Nouveau | Lignes organiques, Mucha | Luxe, beauté |
| `art_deco` | Art Déco | Géométrie chic, dorures | Événements, mode |
| `bauhaus` | Bauhaus | Forme suit fonction | Design éducatif |
| `dark_mode` | Dark Mode | Fond sombre, accents | Apps nuit |
| `pastel` | Pastel | Couleurs douces, ambiance | Lifestyle, bien-être |
| `high_contrast` | High Contrast | Accessibilité maximale | Usage accessible |
| `hand_drawn` | Hand Drawn | Style croquis, traits irréguliers | Créatifs, brainstorming |
| `isometric` | 3D Isométrique | Perspective 3D | Architecture, data |
| `memphis` | Memphis Design | Sottsass, motifs flashy | Créatifs, art |

## 🚀 Utilisation

### 1. Charger le style souhaité

```python
import json

with open('style_prompts_library.json') as f:
    library = json.load(f)

# Sélectionner un style
style = next(s for s in library['styles'] if s['id'] == 'glassmorphism')
prompt_template = style['prompt_template']
```

### 2. Injecter les variables

```python
prompt = prompt_template.format(
    organ={'id': 'auth_service', 'name': 'Auth Service'},
    N=4,
    components=['login', 'signup', 'oauth', 'reset']
)
```

### 3. Envoyer au LLM

Le prompt contient toutes les contraintes SVG et le format de sortie JSON attendu.

## 📝 Format de Sortie Attendu

Chaque prompt demande au LLM de répondre avec :

```json
{
  "h": 240,
  "svg": "<g>...</g>"
}
```

- `h`: Hauteur totale calculée de la carte
- `svg`: Contenu SVG brut (sans balise `<svg>` racine) à wrapper dans un `<svg viewBox="0 0 400 {h}">`

## 🛠 Personnalisation

Pour ajouter un nouveau style, ajouter une entrée au tableau `styles` avec :
- `id`: Identifiant unique (snake_case)
- `name`: Nom français
- `name_en`: Nom anglais
- `description`: Courte description
- `prompt_template`: Template avec variables `{organ.id}`, `{organ.name}`, `{N}`, `[liste]`

## 🎨 Palettes de Couleurs Récurrentes

### Couleurs AetherFlow (base)
- Fond: `#f7f6f2`
- Composant: `#ffffff`
- Bordure: `#d5d4d0`
- Texte: `#3d3d3c`
- Secondaire: `#9d9c98`
- Accent: `#a8c5fc`
- Chaud: `#f0c27f`

### Contraintes XML Communes
- Guillemets doubles UNIQUEMENT (`"`)
- Pas d'apostrophes dans les attributs
- Pas de `<style>`, `<script>`, `<svg>` racine
- `data-hint` en anglais uniquement
