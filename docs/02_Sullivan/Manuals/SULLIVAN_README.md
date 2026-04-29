# 🎨 Sullivan — Générateur SVG avec Layout Intelligent

Interface ultra-simple pour convertir le Genome AetherFlow en SVG organisé en zones UI réalistes.

## 🚀 Démarrage rapide

```bash
# 1. Générer un SVG basique (rapide)
./sullivan build

# 2. Générer un SVG organisé en zones (Header/Sidebar/Main/Footer)
./sullivan zones

# 3. Générer un SVG stylisé avec KIMI
./sullivan fancy --style glass

# 4. Le meilleur des deux mondes : Zones + Style KIMI
./sullivan fancy-zones --style swiss
```

## 📋 Commandes

| Commande | Description | Temps | Usage |
|----------|-------------|-------|-------|
| `build` | SVG simple, layout linéaire | 2s | Aperçu rapide |
| `zones` | **SVG organisé en zones UI** | 3s | **Recommandé sans KIMI** |
| `fancy` | Style visuel KIMI | 30-60s | Design spécifique |
| `fancy-zones` | **Zones + Style KIMI** | 30-60s | **Meilleur rendu** |
| `list-styles` | Liste les 20 styles disponibles | instant | Découverte |

## 🎯 Organisation en Zones

Le mode `zones` (et `fancy-zones`) analyse automatiquement les composants et les répartit :

```
┌─────────────────────────────────────┐
│  HEADER                             │  ← breadcrumb, nav, tabs, stepper
│  [Logo] [Search] [Actions]          │
├──────────┬──────────────────────────┤
│ SIDEBAR  │     MAIN CONTENT         │  ← sidebar: menu, tree, filters
│ [Menu]   │  ┌────────────────────┐  │  ← main: editor, preview, forms
│ [Tree]   │  │  EDITOR / PREVIEW  │  │
│ [Filters]│  └────────────────────┘  │
├──────────┴──────────────────────────┤
│  FOOTER                             │  ← status, pagination, actions
│  [Status] [Info] [Save]             │
└─────────────────────────────────────┘

        ╭─────────────────────╮
        │  FLOATING           │  ← modal, chat, dialog (z-index)
        │  [Chat Assistant]   │     position absolute
        ╰─────────────────────╯
```

### Classification automatique

| Zone | Composants détectés | Exemples |
|------|---------------------|----------|
| **Header** | breadcrumb, nav, tabs, stepper, toolbar | `breadcrumb`, `nav`, `tabs` |
| **Sidebar** | menu-tree, filters, settings, layers | `sidebar`, `file-tree`, `filters` |
| **Main** | editor, preview, form, table, canvas | `code-editor`, `preview`, `upload` |
| **Footer** | status-bar, pagination, actions | `status`, `pagination` |
| **Floating** | modal, chat, dialog, overlay | `chat-bubble`, `modal`, `ai-panel` |

## 🎨 Styles disponibles

### Populaires
```bash
./sullivan fancy-zones --style minimal      # Épuré, pro (défaut)
./sullivan fancy-zones --style glass        # Verre dépoli (moderne)
./sullivan fancy-zones --style cyber        # Néon, futuriste
./sullivan fancy-zones --style dark         # Mode sombre
./sullivan fancy-zones --style swiss        # Grille typographique
./sullivan fancy-zones --style brutal       # Brutaliste (audacieux)
./sullivan fancy-zones --style kids         # Ludique, couleurs vives
```

### Tous les styles (20)
```bash
./sullivan list-styles
```

**Liste complète :** minimal, brutalist, kids, neumorphism, glassmorphism, retro, cyberpunk, swiss, material, flat, skeuomorphism, art_nouveau, art_deco, bauhaus, dark_mode, pastel, high_contrast, hand_drawn, isometric, memphis

## 📁 Fichiers générés

Les SVG sont créés dans `exports/` :
- `genome_zones_20240302_142530.svg` → Layout zones
- `genome_glass_20240302_142530.svg` → Style KIMI seul
- `genome_zones_glass_20240302_142530.svg` → Zones + Style

## ⚙️ Prérequis

1. **Python** : Le venv doit exister (`.venv/`)
2. **KIMI** : Pour `fancy` et `fancy-zones`, ajoute ta clé dans `.env` :
   ```bash
   KIMI_KEY=sk-xxxxx
   ```

## 🐛 Problèmes courants

| Problème | Solution |
|----------|----------|
| "command not found" | `chmod +x sullivan` |
| "KIMI_KEY not found" | Vérifier `.env` ligne `KIMI_KEY=` |
| "genome not found" | Vérifier `Frontend/2. GENOME/genome_reference.json` |
| Résultat vide | Vérifier que le genome contient des `n3_components` |

## 🔄 Comparaison des modes

### Mode `build` (ancien)
```
[Organe Name]
├── Feature 1
│   ├── Component A
│   └── Component B
└── Feature 2
    └── Component C
```

### Mode `zones` (nouveau)
```
[Organe Name]
┌─────────────────────┐
│ [Header Zone]       │ ← Nav, Breadcrumb
├──────────┬──────────┤
│ [Sidebar]│ [Main]   │ ← Menu-tree | Editor
├──────────┴──────────┤
│ [Footer Zone]       │ ← Status, Actions
└─────────────────────┘
      [Floating]      │ ← Chat (z-index)
```

## 💡 Conseils d'utilisation

1. **Sans KIMI** : Utilise `./sullivan zones` → Rapide et bien structuré
2. **Avec KIMI** : Utilise `./sullivan fancy-zones --style <style>` → Meilleur rendu visuel
3. **Itération rapide** : Teste d'abord en `zones`, puis ajoute le style
4. **Pour Figma** : Importe le SVG, les calques sont nommés `af-organ`, `af-component`

## 📝 Exemple complet

```bash
# 1. Voir les styles disponibles
./sullivan list-styles

# 2. Générer avec zones (rapide)
./sullivan zones
# → exports/genome_zones_20240302_142530.svg

# 3. Même chose mais avec style Cyberpunk
./sullivan fancy-zones --style cyber
# → exports/genome_zones_cyber_20240302_142530.svg
```
