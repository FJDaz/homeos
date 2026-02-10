# Mission Aetherflow - Correction Hiérarchie Genome Viewer

**Date** : 10 février 2026
**Agent** : Aetherflow (mode quick)
**Priorité** : 🔴 CRITIQUE
**Durée estimée** : 15-20 min

---

## 🎯 OBJECTIF

Réécrire la fonction `generate_hierarchy_html()` du serveur port 9999 pour qu'elle affiche la **vraie hiérarchie N0-N3 du genome** au lieu de classifier arbitrairement par visual_hint.

---

## 📋 PROBLÈME ACTUEL

**Fichier** : `/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py`

**Fonction problématique** : `generate_hierarchy_html()` (lignes ~423-547)

### Ce qu'elle fait actuellement (INCORRECT)

```python
# Classification arbitraire par visual_hint
corps_items = []      # visual_hint in ['preview', 'table', 'dashboard', ...]
organes_items = []    # visual_hint in ['stepper', 'breadcrumb', 'status', ...]
cellules_items = []   # visual_hint in ['upload', 'color-palette', ...]
atomes_items = []     # Tout le reste
```

**Résultat** : Affiche 4 sections plates (Corps/Organes/Cellules/Atomes) avec composants mélangés, **ignore la vraie hiérarchie du genome**.

### Ce qu'elle DEVRAIT faire (CORRECT)

Respecter la structure N0→N1→N2→N3 du genome JSON :

```
N0 (Corps) = 4 phases
├─ Brainstorm (BRS)
│  ├─ N1 (Organe) = Intent Refactoring
│  │  └─ N2 (Cellule) = Rapport IR
│  │     └─ N3 (Atomes) = 2 composants
│  └─ N1 (Organe) = Arbitrage
│     └─ N2 (Cellule) = Stencils HCI
│        └─ N3 (Atomes) = 3 composants
├─ Backend (BKD)
│  └─ N1 (Organe) = Session Management
│     └─ N2 (Cellule) = Configuration Sessions
│        └─ N3 (Atomes) = 4 composants
├─ Frontend (FRD)
│  ├─ N1 (Organe) = Navigation
│  ├─ N1 (Organe) = Layout Selection
│  ├─ N1 (Organe) = Upload Design
│  ├─ N1 (Organe) = Analyse PNG
│  ├─ N1 (Organe) = Dialogue Utilisateur
│  ├─ N1 (Organe) = Validation Composants
│  └─ N1 (Organe) = Adaptation / Zoom Atome
└─ Deploy (DPL)
   └─ N1 (Organe) = Export / Téléchargement
      └─ N2 (Cellule) = Génération ZIP
         └─ N3 (Atomes) = 3 composants
```

**Total** : 4 Corps → 11 Organes → 11 Cellules → 39 Atomes

---

## 🔧 TÂCHES À RÉALISER

### 1. Analyser la structure actuelle du genome v2

```bash
cat genome_inferred_kimi_innocent_v2.json | jq '.n0_phases[] | {name, sections: .n1_sections | length}'
```

**Attendu** :
```json
{"name": "Brainstorm", "sections": 2}
{"name": "Backend", "sections": 1}
{"name": "Frontend", "sections": 7}
{"name": "Deploy", "sections": 1}
```

### 2. Réécrire `generate_hierarchy_html(genome)`

**Nouvelle logique** :

```python
def generate_hierarchy_html(genome):
    """Generate TRUE N0→N1→N2→N3 hierarchy from genome structure"""

    html_sections = []

    # N0 = Corps (Phases)
    for phase in genome.get('n0_phases', []):
        phase_name = phase.get('name', 'Unknown')
        phase_id = phase.get('id', '')

        # Compter les organes (N1) dans ce corps
        n1_sections = phase.get('n1_sections', [])

        html_sections.append(f'''
        <div class="level-section level-n0">
            <div class="level-header" onclick="toggleLevel('{phase_id}')">
                <span class="level-arrow" id="arrow-{phase_id}">▼</span>
                <span class="level-title">Corps: {phase_name}</span>
                <span class="level-count">{len(n1_sections)} organes</span>
            </div>
            <div class="level-content open" id="content-{phase_id}">
                {render_n1_sections(n1_sections, phase_name)}
            </div>
        </div>
        ''')

    return ''.join(html_sections)

def render_n1_sections(sections, phase_name):
    """Render N1 (Organes) within a Corps"""
    html = []
    for section in sections:
        section_name = section.get('name', 'Unknown')
        section_id = section.get('id', '')
        features = section.get('n2_features', [])

        html.append(f'''
        <div class="level-subsection level-n1">
            <div class="level-subheader" onclick="toggleLevel('{section_id}')">
                <span class="level-arrow" id="arrow-{section_id}">▼</span>
                <span class="level-subtitle">Organe: {section_name}</span>
                <span class="level-count">{len(features)} cellules</span>
            </div>
            <div class="level-content open" id="content-{section_id}">
                {render_n2_features(features, phase_name)}
            </div>
        </div>
        ''')
    return ''.join(html)

def render_n2_features(features, phase_name):
    """Render N2 (Cellules) within an Organe"""
    html = []
    for feature in features:
        feature_name = feature.get('name', 'Unknown')
        feature_id = feature.get('id', '')
        components = feature.get('n3_components', [])

        html.append(f'''
        <div class="level-subsubsection level-n2">
            <div class="level-subsubheader" onclick="toggleLevel('{feature_id}')">
                <span class="level-arrow" id="arrow-{feature_id}">▼</span>
                <span class="level-subsubtitle">Cellule: {feature_name}</span>
                <span class="level-count">{len(components)} atomes</span>
            </div>
            <div class="level-content open" id="content-{feature_id}">
                <div class="component-grid">
                    {render_n3_components(components, phase_name)}
                </div>
            </div>
        </div>
        ''')
    return ''.join(html)

def render_n3_components(components, phase_name):
    """Render N3 (Atomes) - the actual component cards"""
    html = []
    for comp in components:
        comp['_phase'] = phase_name
        html.append(generate_component_wireframe(comp, phase_name, comp.get('description_ui', '')))
    return ''.join(html)
```

### 3. Ajouter le CSS pour les niveaux hiérarchiques

```css
/* N0 - Corps */
.level-n0 {
    border: 2px solid #7aca6a;
    border-radius: 12px;
    margin-bottom: 20px;
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
}

/* N1 - Organes */
.level-n1 {
    margin-left: 20px;
    padding: 10px;
    border-left: 3px solid #5a9ac6;
    background: #fafafa;
}

/* N2 - Cellules */
.level-n2 {
    margin-left: 40px;
    padding: 8px;
    border-left: 2px solid #e4bb5a;
    background: #ffffff;
}

/* Headers pour chaque niveau */
.level-header {
    font-size: 18px;
    font-weight: 700;
    color: #7aca6a;
}

.level-subheader {
    font-size: 16px;
    font-weight: 600;
    color: #5a9ac6;
}

.level-subsubheader {
    font-size: 14px;
    font-weight: 500;
    color: #e4bb5a;
}
```

### 4. Tester le résultat

```bash
# Redémarrer le serveur
kill -9 $(lsof -ti:9999) 2>/dev/null
cd /Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06
python3 server_9999_v2.py &

# Ouvrir dans le navigateur
open http://localhost:9999

# Vérifier visuellement :
# - 4 Corps (Brainstorm, Backend, Frontend, Deploy)
# - Chaque Corps contient ses Organes (11 au total)
# - Chaque Organe contient ses Cellules (11 au total)
# - Chaque Cellule contient ses Atomes (39 au total)
```

---

## ✅ CRITÈRES DE VALIDATION

- [ ] La page affiche **4 Corps** (phases) au niveau racine
- [ ] Chaque Corps est **collapsible** (▼/▲)
- [ ] Les **11 Organes** sont répartis dans les 4 Corps
- [ ] Les **11 Cellules** sont réparties dans les 11 Organes
- [ ] Les **39 Atomes** sont affichés dans les 11 Cellules
- [ ] La hiérarchie est **visuellement claire** (indentation, couleurs)
- [ ] Le JSON `genome_inferred_kimi_innocent_v2.json` n'est **PAS modifié**
- [ ] Aucune erreur Python au démarrage du serveur

---

## 🚫 CONTRAINTES

1. **NE PAS modifier le genome JSON** - seulement le serveur Python
2. **Préserver les wireframes existants** - réutiliser `generate_component_wireframe()`
3. **Garder les checkboxes** - fonctionnalité de validation
4. **Responsive** - doit rester lisible sur écran 1440×900

---

## 📦 FICHIERS À MODIFIER

**1 seul fichier** :
- `/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py`

**Fonctions à réécrire** :
- `generate_hierarchy_html(genome)` (lignes ~423-547)

**Fonctions à créer** :
- `render_n1_sections(sections, phase_name)`
- `render_n2_features(features, phase_name)`
- `render_n3_components(components, phase_name)`

**CSS à ajouter** :
- Styles pour `.level-n0`, `.level-n1`, `.level-n2`
- Headers différenciés par niveau

---

## 🎯 RÉSULTAT ATTENDU

**Avant** (actuel) :
```
Corps (11 composants) ▼
Organes (5 composants) ▼
Cellules (13 composants) ▼
Atomes (10 composants) ▼
```
→ Classification plate par visual_hint

**Après** (correct) :
```
Corps: Brainstorm (2 organes) ▼
  ├─ Organe: Intent Refactoring (1 cellule) ▼
  │  └─ Cellule: Rapport IR (2 atomes) ▼
  │     ├─ Vue Rapport IR
  │     └─ Détail Organe
  └─ Organe: Arbitrage (1 cellule) ▼
     └─ Cellule: Stencils HCI (3 atomes) ▼
        ├─ Carte Stencil
        ├─ Validation Arbitrage
        └─ Tableau Expert

Corps: Backend (1 organe) ▼
  └─ Organe: Session Management (1 cellule) ▼
     └─ Cellule: Configuration Sessions (4 atomes) ▼
        ├─ Dashboard Config
        ├─ Choix Architecture
        ├─ Test Session
        └─ Nouvelle Session

Corps: Frontend (7 organes) ▼
  ├─ Organe: Navigation (1 cellule) ▼
  ├─ Organe: Layout Selection (1 cellule) ▼
  ├─ Organe: Upload Design (1 cellule) ▼
  └─ ...

Corps: Deploy (1 organe) ▼
  └─ Organe: Export / Téléchargement (1 cellule) ▼
     └─ Cellule: Génération ZIP (3 atomes) ▼
        ├─ Navigation Arborescence
        ├─ Téléchargement ZIP
        └─ Remonter d'un niveau
```
→ Hiérarchie complète et fidèle au genome

---

## 📝 COMMIT MESSAGE

```
feat(genome): Hiérarchie N0-N3 fidèle au genome v2

- Réécriture generate_hierarchy_html() pour respecter structure JSON
- Affichage 4 Corps → 11 Organes → 11 Cellules → 39 Atomes
- Indentation visuelle et couleurs par niveau
- Préservation wireframes et checkboxes
- Hiérarchie collapsible à tous les niveaux

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

**Bonne chance Aetherflow ! 🚀**
