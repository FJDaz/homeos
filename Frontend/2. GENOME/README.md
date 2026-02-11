# GENOME — Structure de Référence

**Fichiers** :
- `genome_reference.json` (25KB) — Structure hiérarchique complète
- `elite_components/` (65 composants) — Elite Library Tier 1
- `pregenerated_components.json` (6.5KB) — Composants pré-générés
- `design_principles.json` (4.2KB) — Principes graphiques de référence

**Source** : `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent_v2.json`
**Dernière mise à jour** : 11 février 2026 — 12:18 — **GENOME CORRIGÉ (4 Corps)**

---

## 🚨 IMPORTANT — Genome Valide

Le genome contient **exactement 4 Corps** (n0_phases) comme spécifié dans le Stenciler :

| ID | Nom | Rôle | Organes (n1) |
|----|-----|------|--------------|
| n0_brainstorm | Brainstorm | discovery | 2 |
| n0_backend | Backend | infrastructure | 1 |
| n0_frontend | Frontend | interface | 7 |
| n0_deploy | Deploy | delivery | 1 |

**Total : 4 Corps → 11 Organes → 11 Cellules → 39 Atomes**

**Ancien genome (9 corps)** : REMPLACÉ — Incompatible avec le CORPS_MAPPING du Stenciler.

---

## 📋 Qu'est-ce que le Genome ?

Le Genome est la structure hiérarchique qui représente une interface web complète.

**Hiérarchie** :
```
N0 (Corps) → Sections majeures (Header, Hero, Content, Footer)
    ↓
N1 (Organes) → Groupes fonctionnels au sein d'un Corps
    ↓
N2 (Cells) → Éléments composites au sein d'un Organe
    ↓
N3 (Atomset) → Primitives (bouton, texte, icône)
```

**Exemple** :
```json
{
  "n0": [
    {
      "name": "Frontend",
      "visual_hint": "design",
      "color": "#ec4899",
      "n1": [
        {
          "name": "Layout & Navigation",
          "role": "navigation",
          "n2": [
            {
              "name": "Header",
              "type": "component",
              "n3": [...]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 🎯 Utilisation dans le Stenciler

### Phase 1 : Preview (20%)
- Afficher les 4 Corps (N0) en miniature
- Bande horizontale draggable

### Phase 2 : Tarmac (33%)
- Drop d'un Corps sur le canvas
- Affichage des Organes (N1)

### Phase 3 : Drill-down
- Double-clic sur Organe → Affiche Cells (N2)
- Double-clic sur Cell → Affiche Atomsets (N3)

---

## 🔧 Génération

**Générateur** : `Backend/Prod/core/genome_generator.py` (probablement)

**Commande** :
```bash
# À compléter selon le générateur existant
python Backend/Prod/core/genome_generator.py --input [spec] --output genome_reference.json
```

---

## 📖 Attributs Sémantiques (Conforme Constitution)

Le Genome contient **uniquement** des attributs sémantiques :

| Attribut | Type | Exemples |
|----------|------|----------|
| `name` | string | "Frontend", "Layout & Navigation" |
| `visual_hint` | string | "design", "backend", "api" |
| `color` | hex | "#ec4899" (interprété par KIMI) |
| `role` | string | "navigation", "content", "action" |
| `confidence` | float | 0.87 |

**Aucun CSS** n'est stocké dans le Genome.

---

## 🚫 Ce que le Genome NE contient PAS

- ❌ Classes Tailwind (`bg-blue-500`)
- ❌ Propriétés CSS (`padding: 16px`)
- ❌ HTML (`<div>`, `<button>`)
- ❌ Layout (`flex`, `grid`)

**Règle d'or** : Si ça contient du CSS, ce n'est pas dans le Genome.

---

## 📚 Elite Library (Tier 1)

**Localisation** : `elite_components/` (65 composants pré-générés)

La Elite Library contient les composants Tier 1 (cache) pour une réutilisation instantanée (0ms).

**Organisation** :
- **Corps** (4) : Frontend, Backend, Brainstorm, Deploy
- **Organes** (11) : Analyse_Projet, Choix_Fonctions, Discussion_Assistant, etc.
- **Cellules** (10) : Cartes_Fonctions, Choix_Look, Ma_Conversation, etc.
- **Atomes** (40) : Apercu_Zones, Bouton_Analyser, Carte_Layout, etc.

**Chaque composant** :
- Format JSON avec structure sémantique
- Attributs conformes à la Constitution (aucun CSS)
- Prêt pour intégration dans le Stenciler

---

## 🎨 Design Principles

**Fichier** : `design_principles.json`

Contient les principes graphiques extraits de la maquette de référence :
- Palette de couleurs (Vert primaire #4CAF50, arrière-plans clair/sombre)
- Typographie (hiérarchie des titres, police sans-serif)
- Composants UI (boutons, champs de saisie, icônes)
- Disposition et espacement (layout 2 colonnes)
- Cohérence visuelle générale

**Note** : Ces principes sont **sémantiques** et interprétés librement par KIMI pour le rendu.

---

## ⚙️ Pregenerated Components

**Fichier** : `pregenerated_components.json`

Composants pré-générés avec templates HTML/CSS pour les styles :
- `minimal`, `elegant`, `modern`, etc.
- Boutons (primary, secondary, danger)
- Inputs (text, email, password)
- Cards, navbars, modals

**Usage** : Stratégie hybride Tier 1/2/3 (cache → adaptation → génération)

---

## 🔗 Liens

- **Constitution** : `../1. CONSTITUTION/CONSTITUTION_AETHERFLOW.md`
- **API Schema** : `../1. CONSTITUTION/API_CONTRACT_SCHEMA.json`
- **Stenciler** : `../3. STENCILER/server_9998_v2.py`
- **Communication** : `../4. COMMUNICATION/CANAL_CLAUDE_KIMI.md`

---

*Document technique — Version 1.1.0 — Elite Library intégrée*
