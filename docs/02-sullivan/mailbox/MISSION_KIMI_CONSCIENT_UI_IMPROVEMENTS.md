# MISSION KIMI CONSCIENT - Améliorations UI Front-End

**Date**: 10 février 2026
**Assigné à**: KIMI Conscient (Claude)
**Priorité**: 🔴 CRITIQUE
**Statut**: À démarrer

---

## 🎯 OBJECTIF

Améliorer l'interface du **Genome Viewer (port 9999)** avec 6 modifications UI pour rendre l'interface plus utilisable et restaurer le layout hiérarchique perdu.

**Fichier à modifier**: `/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py`

---

## 📋 LES 6 TÂCHES

### ✅ Tâche 1: Déplacer les checkboxes en bas à droite

**État actuel** (ligne 455-457):
```python
<div style="position:absolute;top:12px;right:12px;">
    <input type="checkbox" id="comp-{comp_id}" class="comp-checkbox" value="{comp_id}" style="width:18px;height:18px;cursor:pointer;" onclick="event.stopPropagation();updateValidateButton()">
</div>
```

**Modification attendue**:
- Déplacer la checkbox de `top:12px;right:12px` vers `bottom:12px;right:12px`
- Maintenir la taille 18×18px
- Conserver le comportement onclick

**Justification**: Les checkboxes en haut à droite sont moins intuitives. En bas à droite, elles suivent le flux de lecture naturel (haut → bas).

---

### ✅ Tâche 2: Réduire la taille des items + augmenter font-size

**État actuel**:
- Carte: `padding:16px` (ligne 454)
- Nom clair: `font-size:13px` (ligne 460)
- Description: `font-size:11px` (ligne 461)
- Endpoint: `font-size:10px` (ligne 462)

**Modification attendue**:
- Carte: `padding:12px` (réduire de 4px)
- Nom clair: `font-size:14px` (augmenter de 1px)
- Description: `font-size:12px` (augmenter de 1px)
- Endpoint: `font-size:11px` (augmenter de 1px)

**Justification**: Items plus compacts avec texte plus lisible. Compensation visuelle pour éviter que les fontes paraissent trop petites après réduction padding.

---

### ✅ Tâche 3: Rows collapsibles par Corps > Organes > Cellules > Atomes

**État actuel**: Grid plat sans hiérarchie (ligne 621-623)
```python
<div class="component-grid">
    {components_html}
</div>
```

**Modification attendue**:

#### A) Restructurer la fonction `generate_html()`

Au lieu de flatten tous les composants dans une liste plate, créer une structure hiérarchique:

```python
def generate_html(genome):
    # Grouper par hiérarchie réelle
    hierarchy = {}
    for phase in genome.get('n0_phases', []):
        phase_name = phase.get('name', 'Unknown')
        hierarchy[phase_name] = {
            'organes': {},
            'order': phase.get('order', 999)
        }

        for section in phase.get('n1_sections', []):
            organe_name = section.get('name', 'Unknown')
            hierarchy[phase_name]['organes'][organe_name] = {
                'cellules': {},
                'order': section.get('id', 'z')
            }

            for feature in section.get('n2_features', []):
                cellule_name = feature.get('name', 'Unknown')
                hierarchy[phase_name]['organes'][organe_name]['cellules'][cellule_name] = {
                    'atomes': []
                }

                for comp in feature.get('n3_components', []):
                    hierarchy[phase_name]['organes'][organe_name]['cellules'][cellule_name]['atomes'].append(comp)
```

#### B) Générer HTML avec headers collapsibles

**Format visuel attendu**:

```
▼ Corps: Intent Refactoring (2 organes, 5 atomes)
  ▼ Organe: Rapport IR (2 cellules, 3 atomes)
    ▼ Cellule: Tableau Organes (2 atomes)
      [Wireframe 1]
      [Wireframe 2]
    ▲ Cellule: Détail (1 atome) — Replié par défaut
  ▲ Organe: Session — Replié par défaut
▲ Corps: Arbitrage — Replié par défaut
```

**Code HTML suggéré**:

```html
<div class="hierarchy-container">
    <div class="corps-row">
        <div class="corps-header" onclick="toggleCorps('corps_1')">
            <span class="arrow" id="arrow-corps_1">▼</span>
            <span class="level-label">Corps:</span>
            <span class="level-name">Intent Refactoring</span>
            <span class="stats">(2 organes, 5 atomes)</span>
        </div>
        <div class="corps-content" id="content-corps_1" style="display:block;">
            <!-- Organes ici -->
        </div>
    </div>
</div>
```

**Caractères flèches**: Utiliser `▼` (ouvert) et `▲` (fermé) — PAS Wingdings2, utiliser Unicode direct.

**JavaScript collapse/expand**:

```javascript
function toggleCorps(id) {
    const content = document.getElementById('content-' + id);
    const arrow = document.getElementById('arrow-' + id);
    if (content.style.display === 'none') {
        content.style.display = 'block';
        arrow.textContent = '▼';
    } else {
        content.style.display = 'none';
        arrow.textContent = '▲';
    }
}
```

**État initial**:
- Premier Corps (Intent Refactoring): ▼ Ouvert
- Premier Organe du premier Corps: ▼ Ouvert
- Tous les autres: ▲ Fermés

---

### ✅ Tâche 4: Noms user-friendly

**État actuel**: Noms techniques pas clairs
```python
nom_clair = name.replace("Comp ", "").replace("Component ", "")
```

**Mapping à appliquer** (ligne 54):

| ❌ Nom technique actuel | ✅ Nom user-friendly |
|------------------------|----------------------|
| "Vue Rapport IR" | "Tableau des organes détectés" |
| "Détail Organe" | "Fiche détaillée d'un organe" |
| "Carte Stencil" | "Carte de pouvoir à valider" |
| "Status Session" | "Indicateur de santé du projet" |
| "Stepper 9 Étapes" | "Navigation entre les 9 phases" |
| "Galerie Layouts" | "Choix de mise en page visuelle" |
| "Zone Upload" | "Import de fichier design (PNG)" |
| "Palette Extraite" | "Couleurs et style détectés" |
| "Aperçu Zones" | "Zones détectées dans votre maquette" |
| "Bulles Conversation" | "Dialogue avec Sullivan" |
| "Input Message" | "Zone de saisie de message" |
| "Dashboard Validation" | "Récapitulatif de vos choix" |
| "Contrôles Zoom" | "Navigation hiérarchique (Corps/Organes/Atomes)" |
| "Zoom Out" | "Remonter d'un niveau" |
| "Fiche Détail Atome" | "Détails techniques de l'endpoint" |
| "Éditeur Code" | "Éditeur de code avec coloration syntaxique" |
| "Lancer Distillation" | "Générer le code final" |
| "Appliquer Changements" | "Sauvegarder vos modifications" |
| "Reset Session" | "Réinitialiser la session" |
| "Résumé Genome" | "Vue d'ensemble du projet" |
| "Liste Distillation" | "Historique des générations" |
| "Bouton Suivant" | "Passer à l'étape suivante" |
| "Fil d'Ariane" | "Position actuelle dans le parcours" |
| "Carte Layout" | "Aperçu d'une mise en page" |
| "Choix Style" | "Sélection du style visuel (Minimal, Brutaliste...)" |
| "Tableau Expert" | "Vue technique des décisions" |
| "Validation Arbiter" | "Confirmation finale des choix" |
| "Résumé Décisions" | "Récapitulatif détaillé de vos décisions" |
| "Modal Confirmation" | "Fenêtre de confirmation" |

**Implémentation**:

```python
# Mapping user-friendly
USER_FRIENDLY_NAMES = {
    "Vue Rapport IR": "Tableau des organes détectés",
    "Détail Organe": "Fiche détaillée d'un organe",
    "Carte Stencil": "Carte de pouvoir à valider",
    "Status Session": "Indicateur de santé du projet",
    # ... compléter la liste
}

# Dans generate_component_wireframe(), après ligne 54:
nom_clair = name.replace("Comp ", "").replace("Component ", "")
nom_clair = USER_FRIENDLY_NAMES.get(nom_clair, nom_clair)  # Fallback si non trouvé
```

---

### ✅ Tâche 5: Trier les items par identificabilité user

**Objectif**: Les composants les plus "reconnaissables" visuellement doivent apparaître en premier.

**Ordre d'identificabilité** (du plus au moins identifiable):

#### Niveau 1 - TRÈS IDENTIFIABLE (utilisateur reconnaît immédiatement)
1. **upload** - Zone drag & drop avec 📁 (universel)
2. **color-palette** - 4 couleurs visibles (immédiat)
3. **preview** - Image avec zones surlignées (visuel fort)
4. **chat/bubble** - Bulles de chat (motif connu)
5. **download** - Fichier ZIP + bouton télécharger (clair)
6. **status** - LEDs vertes/grises (santé projet)

#### Niveau 2 - IDENTIFIABLE (utilisateur devine le rôle)
7. **grid** - Galerie 3×2 de typographies
8. **choice-card** - 4 radio cards styles
9. **stencil-card** - Carte avec toggle Garder/Réserve
10. **dashboard** - Métriques + mini graphiques
11. **table** - Tableau header + rows
12. **form** - Labels + inputs + boutons

#### Niveau 3 - MOYEN (nécessite lecture du titre)
13. **detail-card** - Endpoint monospace + boutons
14. **zoom-controls** - Navigation ← Out | Corps | In →
15. **chat-input** - Champ saisie + 📎😊 + bouton
16. **accordion** - Sections pliables
17. **editor** - Code syntax highlighting
18. **launch-button** - Bouton fusée 🚀

#### Niveau 4 - FAIBLE (abstrait)
19. **apply-changes** - 💾 Appliquer / ↩️ Annuler
20. **breadcrumb** - Navigation hiérarchique
21. **stepper** - Indicateur 9 étapes
22. **modal** - Fenêtre modale
23. **list** - Liste verticale items
24. **card** - Carte générique
25. **button** - Bouton action

**Implémentation**:

```python
IDENTIFIABILITY_ORDER = [
    "upload", "color-palette", "preview", "chat/bubble", "download", "status",
    "grid", "choice-card", "stencil-card", "dashboard", "table", "form",
    "detail-card", "zoom-controls", "chat-input", "accordion", "editor", "launch-button",
    "apply-changes", "breadcrumb", "stepper", "modal", "list", "card", "button"
]

def sort_by_identifiability(components):
    def get_order(comp):
        hint = comp.get('visual_hint', 'generic')
        try:
            return IDENTIFIABILITY_ORDER.index(hint)
        except ValueError:
            return 999  # Non trouvé = à la fin

    return sorted(components, key=get_order)
```

**Appliquer ce tri** :
- À l'intérieur de chaque **Cellule** (N2)
- PAS au niveau Corps/Organes (conserver l'ordre logique du workflow UX)

---

### ✅ Tâche 6: Retrouver et restaurer le commit avec le bon layout

**Commit identifié**: `5aa7b18` - "feat(genome): Vue hiérarchique Corps/Organes/Cellules/Atomes avec ordre pédagogique"

**Étapes**:

1. **Extraire le fichier du commit**:
```bash
git show 5aa7b18:docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py > /tmp/server_9999_v2_hierarchique.py
```

2. **Analyser les différences**:
```bash
diff -u server_9999_v2.py /tmp/server_9999_v2_hierarchique.py
```

3. **Extraire les portions clés**:
- Structure HTML hiérarchique (Corps > Organes > Cellules > Atomes)
- Styles CSS pour les headers collapsibles
- JavaScript pour collapse/expand
- Gradients visuels par niveau

4. **Intégrer dans le fichier actuel**:
- NE PAS tout remplacer (wireframes actuels sont bons)
- Copier uniquement la logique de génération hiérarchique
- Adapter pour s'intégrer avec les wireframes FRD V2 existants

**Points critiques à restaurer** (d'après le commit 5aa7b18):
- Headers avec gradient par niveau (Corps = gradient vert, Organes = bleu, etc.)
- Icônes par niveau (🏛️ Corps, ⚙️ Organes, 🧬 Cellules, ⚛️ Atomes)
- Breadcrumb contextuel
- Stats par niveau (nombre d'enfants)

---

## 🔧 CONTRAINTES TECHNIQUES

### Wireframes à préserver

**NE PAS MODIFIER** les wireframes existants (lignes 58-467). Ils sont corrects et optimisés.

**Conserver**:
- 10 wireframes FRD V2: `status`, `zoom-controls`, `download`, `chat-input`, `color-palette`, `choice-card`, `stencil-card`, `detail-card`, `launch-button`, `apply-changes`
- Wireframes classiques: `table`, `card`, `form`, `list`, `grid`, `upload`, `preview`, `chat/bubble`, `editor`, `dashboard`, `accordion`, `breadcrumb`, `modal`, `stepper`, `button`

### Styles CSS à ajouter

```css
/* Hierarchy Headers */
.corps-header {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    padding: 16px 20px;
    border-radius: 12px;
    margin-bottom: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
    font-weight: 600;
    color: #065f46;
    transition: all 0.2s;
}

.corps-header:hover {
    background: linear-gradient(135deg, #a7f3d0 0%, #6ee7b7 100%);
}

.organe-header {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 10px;
    margin-left: 24px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    color: #1e40af;
    transition: all 0.2s;
}

.cellule-header {
    background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    margin-left: 48px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #9f1239;
    transition: all 0.2s;
}

.arrow {
    font-size: 14px;
    transition: transform 0.2s;
}

.level-label {
    font-size: 11px;
    text-transform: uppercase;
    opacity: 0.7;
}

.level-name {
    font-size: 15px;
}

.stats {
    margin-left: auto;
    font-size: 12px;
    opacity: 0.6;
}

.corps-content, .organe-content, .cellule-content {
    transition: all 0.3s ease-in-out;
    overflow: hidden;
}

.atomes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 16px;
    margin-left: 72px;
    margin-bottom: 20px;
}
```

---

## 🧪 TESTS DE VALIDATION

Avant de livrer, vérifier:

### 1. Checkboxes
- [ ] Checkboxes positionnées en `bottom:12px;right:12px`
- [ ] Checkboxes visibles et cliquables
- [ ] Validation button s'update correctement

### 2. Taille/Font
- [ ] Padding carte = 12px (vs 16px avant)
- [ ] Font-size nom = 14px (vs 13px avant)
- [ ] Font-size description = 12px (vs 11px avant)
- [ ] Font-size endpoint = 11px (vs 10px avant)
- [ ] Texte reste lisible

### 3. Hiérarchie collapsible
- [ ] 4 niveaux visibles: Corps > Organes > Cellules > Atomes
- [ ] Headers cliquables
- [ ] Flèches ▼/▲ s'inversent au clic
- [ ] Contenu se collapse/expand correctement
- [ ] Premier Corps ouvert par défaut
- [ ] Premier Organe du premier Corps ouvert par défaut
- [ ] Tous les autres fermés par défaut

### 4. Noms user-friendly
- [ ] "Tableau des organes détectés" au lieu de "Vue Rapport IR"
- [ ] "Zones détectées dans votre maquette" au lieu de "Aperçu zones"
- [ ] Au moins 15 noms remplacés par version friendly
- [ ] Fallback sur nom technique si non trouvé dans mapping

### 5. Tri identificabilité
- [ ] Upload en premier dans sa cellule
- [ ] Color-palette, preview, chat/bubble dans le top 6
- [ ] Button, card générique en dernier
- [ ] Ordre logique Corps/Organes/Cellules PRÉSERVÉ (pas de tri à ce niveau)

### 6. Commit restauré
- [ ] Headers hiérarchiques avec gradients
- [ ] Icônes par niveau (🏛️ ⚙️ 🧬 ⚛️)
- [ ] Stats (X organes, Y atomes)
- [ ] Wireframes FRD V2 intacts

---

## 📤 OUTPUT ATTENDU

### Fichier modifié

**Nom**: `server_9999_v2.py` (in place)
**Emplacement**: `/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/`

### Rapport de Mission

**Nom**: `RAPPORT_UI_IMPROVEMENTS.md`
**Emplacement**: `/Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/kimi/`

**Contenu attendu**:

```markdown
# Rapport Améliorations UI - KIMI Conscient

## Modifications Effectuées

### 1. Checkboxes
- Position: top:12px → bottom:12px ✅
- Fonctionnalité: Préservée ✅

### 2. Taille/Font
- Padding carte: 16px → 12px ✅
- Font-sizes: +1px sur nom/description/endpoint ✅

### 3. Hiérarchie
- 4 niveaux implémentés ✅
- Collapse/expand fonctionnel ✅
- État initial: Corps 1 + Organe 1.1 ouverts ✅

### 4. Noms friendly
- 28 noms remplacés sur 29 composants ✅
- 1 fallback (nouveau composant non mappé) ⚠️

### 5. Tri identificabilité
- Upload/Color-palette/Preview en tête ✅
- Button/Card génériques en queue ✅

### 6. Commit restauré
- Headers gradients: ✅
- Icônes niveaux: ✅
- Wireframes préservés: ✅

## Tests Effectués

- [x] Démarrage serveur: OK
- [x] Affichage hiérarchie: OK
- [x] Collapse/expand: OK
- [x] Checkboxes validation: OK
- [x] 29 composants affichés: OK

## Problèmes Rencontrés

Aucun.

## Ligne Modifiée vs Totale

- Lignes modifiées: ~150 lignes
- Lignes totales: 679 lignes
- % changement: ~22%
```

---

## 🚀 DÉMARRAGE

**Commande à exécuter** (pour KIMI Conscient/Claude):

```bash
# 1. Lire le fichier actuel
Read: /Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py

# 2. Extraire le commit avec bon layout
Bash: git show 5aa7b18:docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py > /tmp/server_hierarchique.py

# 3. Lire le fichier hiérarchique
Read: /tmp/server_hierarchique.py

# 4. Appliquer les 6 modifications
Edit: server_9999_v2.py (série de modifications)

# 5. Produire RAPPORT_UI_IMPROVEMENTS.md
Write: /Users/francois-jeandazin/AETHERFLOW/.claude/mailbox/kimi/RAPPORT_UI_IMPROVEMENTS.md
```

---

**Bonne chance, KIMI Conscient! 🎨**
