# Mission KIMI - Layout Final Genome Viewer

**Date** : 10 février 2026
**Priorité** : 🔴 ULTIME TENTATIVE
**Durée** : 30 min MAX

---

## 🎯 OBJECTIF SIMPLE

Refaire le layout du commit `5aa7b18` qui était **beau et fonctionnel**, mais cette fois avec la **vraie hiérarchie N0-N3**.

**Ce qui existe déjà et FONCTIONNE** :
- ✅ La structure HTML génère correctement les 4 Corps → 11 Organes → 11 Cellules → 39 Atomes
- ✅ Les données sont bonnes
- ❌ Le CSS est MOCHE et cassé

**Ce qu'il faut faire** :
- Copier le CSS du commit `5aa7b18`
- L'adapter pour fonctionner avec la nouvelle structure HTML

---

## 📋 LAYOUT ATTENDU (Référence : commit 5aa7b18)

### Structure visuelle claire :

```
┌─────────────────────────────────────────────────────────────┐
│  ROW CORPS (4 grandes cartes horizontales)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │Brainstorm│ │ Backend  │ │ Frontend │ │  Deploy  │      │
│  │ 2 org    │ │ 1 org    │ │ 7 org    │ │ 1 org    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘

Quand on clique sur "Brainstorm" ▼ :

┌─────────────────────────────────────────────────────────────┐
│  ROW ORGANES (dans Brainstorm)                              │
│  ┌────────────────────────┐ ┌────────────────────────┐     │
│  │ Intent Refactoring     │ │ Arbitrage              │     │
│  │ 1 cellule, 2 atomes    │ │ 1 cellule, 3 atomes    │     │
│  └────────────────────────┘ └────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘

Quand on clique sur "Intent Refactoring" ▼ :

┌─────────────────────────────────────────────────────────────┐
│  ROW CELLULES (dans Intent Refactoring)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Rapport IR (1 cellule)                                 │ │
│  │ 2 atomes                                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Quand on clique sur "Rapport IR" ▼ :

┌─────────────────────────────────────────────────────────────┐
│  GRID ATOMES (les 2 composants UI)                          │
│  ┌────────────┐ ┌────────────┐                             │
│  │ Vue Rapport│ │ Détail     │                             │
│  │ IR         │ │ Organe     │                             │
│  │ [wireframe]│ │ [wireframe]│                             │
│  └────────────┘ └────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📐 CSS À APPLIQUER (Inspiré commit 5aa7b18)

### Principes de base :

1. **ROW CORPS** : `display: flex; gap: 16px;` - 4 cartes côte à côte
2. **ROW ORGANES** : `display: flex; gap: 12px; flex-wrap: wrap;` - cartes flexibles
3. **ROW CELLULES** : `display: flex; gap: 12px; flex-wrap: wrap;` - cartes flexibles
4. **GRID ATOMES** : `display: grid; grid-template-columns: repeat(5, 1fr);` - grille 5 colonnes

### Carte de niveau (Corps/Organe/Cellule) :

```css
.level-card {
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.level-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.level-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.level-card-title {
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
}

.level-card-count {
    font-size: 12px;
    color: #64748b;
    background: #f1f5f9;
    padding: 2px 8px;
    border-radius: 8px;
}

.level-card-content {
    margin-top: 12px;
    display: none;
}

.level-card-content.open {
    display: block;
}
```

### Couleurs par niveau :

```css
/* N0 - Corps */
.level-n0 .level-card {
    border-left: 4px solid #7aca6a;
}

.level-n0 .level-card-title {
    color: #7aca6a;
}

/* N1 - Organes */
.level-n1 .level-card {
    border-left: 3px solid #5a9ac6;
}

.level-n1 .level-card-title {
    color: #5a9ac6;
}

/* N2 - Cellules */
.level-n2 .level-card {
    border-left: 2px solid #e4bb5a;
}

.level-n2 .level-card-title {
    color: #e4bb5a;
}
```

---

## 🔧 STRUCTURE HTML ATTENDUE

**IMPORTANTE** : Ne pas toucher aux fonctions Python ! Seulement adapter le HTML/CSS.

Les fonctions Python génèrent déjà cette structure :

```html
<div class="hierarchy-container">
    <!-- N0 - Corps -->
    <div class="level-section level-n0">
        <div class="level-header" onclick="toggleLevel('n0_brainstorm')">
            <span>📦 Corps: Brainstorm</span>
            <span>2 organes · 5 atomes</span>
        </div>
        <div class="level-content" id="content-n0_brainstorm">

            <!-- N1 - Organes -->
            <div class="level-subsection level-n1">
                <div class="level-subheader" onclick="toggleLevel('n1_ir')">
                    <span>🔧 Organe: Intent Refactoring</span>
                    <span>1 cellule · 2 atomes</span>
                </div>
                <div class="level-content" id="content-n1_ir">

                    <!-- N2 - Cellules -->
                    <div class="level-subsubsection level-n2">
                        <div class="level-subsubheader" onclick="toggleLevel('n2_rapport_ir')">
                            <span>⚙️ Cellule: Rapport IR</span>
                            <span>2 atomes</span>
                        </div>
                        <div class="level-content" id="content-n2_rapport_ir">

                            <!-- N3 - Atomes (component-grid déjà OK) -->
                            <div class="component-grid">
                                [Wireframes des composants]
                            </div>

                        </div>
                    </div>

                </div>
            </div>

        </div>
    </div>
</div>
```

**TON JOB** : Transformer les `.level-header`, `.level-subheader`, `.level-subsubheader` en **cartes élégantes** avec le CSS ci-dessus.

---

## ✅ CHECKLIST

- [ ] ROW CORPS : 4 cartes horizontales visibles par défaut
- [ ] Clic sur Corps → affiche ROW ORGANES en dessous
- [ ] Clic sur Organe → affiche ROW CELLULES en dessous
- [ ] Clic sur Cellule → affiche GRID ATOMES (déjà OK)
- [ ] Flèches ▼/▲ fonctionnelles
- [ ] Gradients et ombres comme commit 5aa7b18
- [ ] Hover states qui marchent
- [ ] Responsive (colonnes s'adaptent)
- [ ] Pas de régression : checkboxes fonctionnelles

---

## 🚫 INTERDICTIONS

1. **NE PAS** toucher aux fonctions Python (`render_n1_sections`, `render_n2_features`, `render_n3_components`)
2. **NE PAS** changer la structure HTML générée
3. **NE PAS** inventer de nouveaux wireframes
4. **SEULEMENT** modifier le CSS entre `<style>` et `</style>`

---

## 📦 FICHIER À MODIFIER

**1 seul fichier** :
```
/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py
```

**Section à modifier** : Lignes ~567-660 (le bloc `<style>`)

---

## 🎨 EXEMPLE CONCRET

**Avant (actuel - MOCHE)** :
```
▼ 🔧 Organe: Intent Refactoring  1 cellule · 2 atomes
   ▼ ⚙️ Cellule: Rapport IR  2 atomes
```

**Après (BEAU comme commit 5aa7b18)** :
```
┌────────────────────────────────────┐
│ 🔧 Intent Refactoring              │
│ 1 cellule · 2 atomes           ▼  │
│                                    │
│ ┌────────────────────────────────┐│
│ │ ⚙️ Rapport IR                  ││
│ │ 2 atomes                    ▼ ││
│ └────────────────────────────────┘│
└────────────────────────────────────┘
```

---

## 💡 CONSEIL

Va voir le commit `5aa7b18` pour t'inspirer du CSS :

```bash
git show 5aa7b18:docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py | grep -A 200 "<style>"
```

**Concentre-toi sur** :
- Les classes `.level-section`, `.level-header`, `.level-content`
- Les transitions et hover states
- Les gradients `linear-gradient(145deg, ...)`
- Les box-shadow

**Adapte-les pour** :
- `.level-n0` → Row Corps (flex horizontal)
- `.level-n1` → Row Organes (flex wrap)
- `.level-n2` → Row Cellules (flex wrap)
- `.level-n3` → Grid Atomes (déjà OK)

---

## 🎯 RÉSULTAT ATTENDU

Un layout **professionnel, élégant, hiérarchique** comme le commit `5aa7b18`, mais avec la vraie structure N0-N3.

**Tu es fatigué, on est tous fatigués. Mais c'est la dernière ligne droite.**

**Applique-toi. Fais un truc beau. Tu sais faire.**

---

**Bonne chance KIMI. C'est la dernière tentative. 🚀**
