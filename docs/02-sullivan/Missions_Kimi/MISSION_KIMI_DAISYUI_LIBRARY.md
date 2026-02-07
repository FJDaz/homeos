# MISSION KIMI : Integrer DaisyUI dans library.json

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 5 fevrier 2026
**Priorite** : HAUTE

---

## Objectif

Ajouter les 65 composants DaisyUI dans `output/components/library.json`.
Ce sont des composants Tailwind pre-valides, tagges par categorie.

## Source

Site officiel : https://daisyui.com/components/
Documentation de chaque composant : https://daisyui.com/components/{nom}/

## Ce que tu dois faire

Pour CHAQUE composant DaisyUI (65 au total) :

1. Va sur la page du composant
2. Recupere :
   - Nom
   - Categorie DaisyUI (Actions, Data Display, Navigation, Feedback, Data Input, Layout)
   - Classes CSS principales
   - HTML minimal (le plus court exemple fonctionnel)
   - Variants disponibles (primary, secondary, outline, etc.)

3. Mappe vers Atomic Design :
   - Actions (Button, Swap, Theme Controller) → atoms
   - Data Input (Input, Checkbox, Toggle, Select, etc.) → atoms
   - Feedback (Alert, Loading, Toast, Tooltip) → atoms
   - Data Display (Card, Table, Badge, Avatar, Stat) → molecules
   - Navigation (Navbar, Menu, Breadcrumbs, Tabs, Steps) → organisms
   - Layout (Drawer, Footer, Hero) → organisms
   - Actions complexes (Modal, Dropdown) → organisms

4. Ajoute dans library.json avec ce format :

```json
{
  "id": "{category}_daisy_{name}",
  "category": "{atoms|molecules|organisms}",
  "name": "daisy_{name}",
  "html": "<le HTML minimal>",
  "css": "/* DaisyUI - classes Tailwind, pas de CSS custom */",
  "description": "DaisyUI {name} - {description courte}",
  "tags": ["daisyui", "{categorie_daisy}", "{nom}", ...mots cles],
  "params": ["data:variant", "data:size"],
  "defaults": {"data:variant": "default", "data:size": "md"},
  "examples": [{"name": "basic", "description": "Usage basique", "params": {}}],
  "complexity": "low|medium|high",
  "source": "daisyui",
  "figma_type": "COMPONENT|INSTANCE"
}
```

## Liste des 65 composants

### Actions (→ atoms sauf Modal/Dropdown → organisms)
Button, Dropdown, FAB, Modal, Swap, Theme Controller

### Data Display (→ molecules)
Accordion, Avatar, Badge, Card, Carousel, Chat Bubble, Collapse,
Countdown, Diff, Kbd, List, Stat, Status, Table, Timeline

### Navigation (→ organisms)
Breadcrumbs, Dock, Link, Menu, Navbar, Pagination, Steps, Tab

### Feedback (→ atoms)
Alert, Loading, Progress, Radial Progress, Skeleton, Toast, Tooltip

### Data Input (→ atoms)
Calendar, Checkbox, Fieldset, File Input, Filter, Label, Radio,
Range, Rating, Select, Input, Textarea, Toggle, Validator

### Layout (→ organisms)
Divider, Drawer, Footer, Hero, Indicator, Join, Mask, Stack

## Fichier a modifier

`output/components/library.json` — ajouter dans les categories existantes.
Mettre a jour les stats a la fin.

## Important

- NE SUPPRIME PAS les composants existants
- Ajoute les DaisyUI EN PLUS
- Prefixe tous les noms avec `daisy_` pour les distinguer
- Le tag `daisyui` doit etre present sur chaque composant

---

*— Claude-Code Senior*
