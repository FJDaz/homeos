# MISSION : Implémenter le Design ARBITER Dynamique

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Priorité** : CRITIQUE
**Prérequis** : Missions SELECTEUR_SET et CONNECT_INFERENCE terminées ✅

---

## Le Contexte

Tu as créé un design statique ARBITER magnifique dans `Frontend/arbiter-interface.html`.
Tu as aussi créé le moteur d'inférence `component_inference.py`.

**PROBLÈME** : Ces deux ne sont pas connectés. Le design statique montre des "DROPDOWN" et "LARGE BUTTON" en placeholder, mais ne consomme pas les vrais composants inférés.

---

## Le Design ARBITER (Rappel Visuel)

```
┌──────────────────────────────────────┬─────────────────────────────────┐
│         PANNEAU GAUCHE (55%)         │     PANNEAU DROIT (45%)         │
│         Intent Revue (CLAIR)         │     Génome (SOMBRE)             │
│         #f0f0e8                      │     #252525                     │
├──────────────────────────────────────┼─────────────────────────────────┤
│                                      │                                 │
│  § Typologie déclarée                │  Génome de [Produit]            │
│  ┌────────┬─────────┬────────┐      │                                 │
│  │ Entry  │ Compos  │ Toggle │      │  ─── Corps ───                  │
│  ├────────┼─────────┼────────┤      │  Brainstorm │ Back │ Front     │
│  │Backend │ [...]   │ ✓ OFF  │      │  [dropdowns] [cards] [toggles] │
│  │Frontend│ [...]   │ ✓ ON   │      │                                 │
│  │Deploy  │ [...]   │ ✓ OFF  │      │  ─── Organes ───                │
│  └────────┴─────────┴────────┘      │  [icons grid]                   │
│                                      │                                 │
│  Pourquoi (explication Sullivan)     │  ─── Cellules ───               │
│                                      │  [mini items]                   │
│  § Endpoints (collapsible)           │                                 │
│  § Code IR (collapsible)             │                                 │
│                                      │                                 │
└──────────────────────────────────────┴─────────────────────────────────┘
```

---

## CE QUE TU DOIS IMPLÉMENTER

### LOGIQUE DU PANNEAU GAUCHE

Pour **chaque catégorie** (Typologie, Endpoints, Code IR), créer une **section à deux colonnes** :

```
┌─────────────────────────────────────────────────────────────────────┐
│ § TYPOLOGIE DÉCLARÉE                                     [↕ toggle] │
├──────────────────────────────┬──────────────────────────────────────┤
│                              │                                      │
│  COLONNE GAUCHE              │  COLONNE DROITE                      │
│  (Entrées par typologie)     │  (Composants choisis par Sullivan)   │
│                              │                                      │
│  ┌───────────────────────┐   │  ┌────────────────────────────────┐  │
│  │ H2: Backend           │   │  │ Composant 1 [checkbox ✓]      │  │
│  │                       │   │  │ Composant 2 [checkbox ✓]      │  │
│  │                       │   │  │ Composant 3 [checkbox ☐]      │  │
│  │                       │   │  ├────────────────────────────────┤  │
│  │                       │   │  │ 💡 Explication Sullivan:       │  │
│  │                       │   │  │ "J'ai choisi ces composants   │  │
│  │                       │   │  │  car le POST /users nécessite │  │
│  │                       │   │  │  un formulaire d'inscription" │  │
│  │                       │   │  ├────────────────────────────────┤  │
│  │                       │   │  │ [Valider Backend]             │  │
│  └───────────────────────┘   │  └────────────────────────────────┘  │
│                              │                                      │
│  ┌───────────────────────┐   │  ┌────────────────────────────────┐  │
│  │ H2: Frontend          │   │  │ Composant A [checkbox ✓]      │  │
│  │                       │   │  │ Composant B [checkbox ✓]      │  │
│  │                       │   │  ├────────────────────────────────┤  │
│  │                       │   │  │ 💡 Explication Sullivan:       │  │
│  │                       │   │  │ "Interface de dashboard..."   │  │
│  │                       │   │  ├────────────────────────────────┤  │
│  │                       │   │  │ [Valider Frontend]            │  │
│  └───────────────────────┘   │  └────────────────────────────────┘  │
│                              │                                      │
├──────────────────────────────┴──────────────────────────────────────┤
│                    [Valider tous les composants]                    │
└─────────────────────────────────────────────────────────────────────┘
```

### STRUCTURE POUR CHAQUE TYPOLOGIE (Backend/Frontend/Deploy)

```html
<div class="typography-entry" data-typography="Frontend">
    <!-- COLONNE GAUCHE : Titre + détails -->
    <div class="entry-info">
        <h2>Frontend</h2>
        <p class="entry-meta">3 endpoints • 5 composants suggérés</p>
    </div>

    <!-- COLONNE DROITE : Composants inférés -->
    <div class="inferred-components">
        <!-- Chargé dynamiquement via /studio/inference/Frontend -->
        <div class="component-item" data-id="atoms_input">
            <input type="checkbox" checked>
            <span class="component-name">atoms_input</span>
            <span class="component-reason">Formulaire utilisateur</span>
        </div>
        <!-- ... autres composants ... -->

        <!-- Explication Sullivan -->
        <div class="sullivan-explanation">
            <span class="icon">💡</span>
            <p>J'ai sélectionné ces composants car...</p>
        </div>

        <!-- Bouton Valider cette typologie -->
        <button class="validate-btn"
                hx-post="/studio/validate/Frontend"
                hx-swap="outerHTML">
            Valider Frontend
        </button>
    </div>
</div>
```

---

## FICHIERS À MODIFIER

### 1. `Backend/Prod/templates/studio_homeos.html`

Dans la section `#frontend-arbiter`, remplacer le contenu statique par :

```html
<div id="frontend-arbiter" class="arbiter-layout">
    <!-- PANNEAU GAUCHE (Intent Revue) -->
    <div class="panel-left">
        <div class="panel-header">
            <span class="panel-title">Intent Revue</span>
            <span class="arbiter-badge">Arbitrage Sullivan</span>
        </div>

        <!-- Section Typologies - DYNAMIQUE -->
        <div id="typologies-section"
             class="typology-section"
             hx-get="/studio/typologies/arbiter"
             hx-trigger="load"
             hx-swap="innerHTML">
            <span class="text-gray-400">Chargement des typologies...</span>
        </div>

        <!-- Section Endpoints - Collapsible -->
        <details class="expandable-section">
            <summary class="expandable-header">
                <span class="expand-icon">↕</span>
                <span class="expandable-title">§ Endpoints</span>
            </summary>
            <div id="endpoints-list"
                 hx-get="/studio/reports/endpoints"
                 hx-trigger="revealed"
                 hx-swap="innerHTML">
                Chargement...
            </div>
        </details>

        <!-- Section Code IR - Collapsible -->
        <details class="expandable-section">
            <summary class="expandable-header">
                <span class="expand-icon">↕</span>
                <span class="expandable-title">§ Code IR</span>
            </summary>
            <div id="code-ir-list"
                 hx-get="/studio/reports/code-ir"
                 hx-trigger="revealed"
                 hx-swap="innerHTML">
                Chargement...
            </div>
        </details>
    </div>

    <!-- PANNEAU DROIT (Génome) -->
    <div class="panel-right">
        <!-- Garde le contenu actuel du génome -->
    </div>
</div>
```

### 2. `Backend/Prod/sullivan/studio_routes.py`

Ajouter cette nouvelle route :

```python
@router.get("/typologies/arbiter", response_class=HTMLResponse)
async def get_typologies_arbiter(request: Request):
    """
    Retourne le HTML des typologies avec composants inférés
    pour le design ARBITER.
    """
    from Backend.Prod.sullivan.agent.component_inference import (
        infer_components_for_typography,
    )

    typologies = ["Backend", "Frontend", "Deploy"]

    # Charger les endpoints depuis l'IR
    ir_data = load_ir_data()
    endpoints = extract_endpoints_from_ir(ir_data)

    html_parts = []

    for typo in typologies:
        # Filtrer les endpoints par typologie
        typo_endpoints = [e for e in endpoints if e.get("typography") == typo]

        # Inférer les composants
        components = infer_components_for_typography(typo, typo_endpoints)

        # Générer le HTML pour cette typologie
        html_parts.append(f'''
        <div class="typography-entry" data-typography="{typo}">
            <div class="entry-row">
                <div class="entry-info">
                    <h2 class="entry-title">{typo}</h2>
                    <span class="entry-meta">{len(typo_endpoints)} endpoints</span>
                </div>
                <div class="inferred-components">
                    {"".join(_render_component(c) for c in components)}
                    <div class="sullivan-explanation">
                        <span class="icon">💡</span>
                        <p>{_generate_explanation(typo, components)}</p>
                    </div>
                    <button class="validate-btn"
                            hx-post="/studio/validate/{typo}"
                            hx-swap="outerHTML">
                        Valider {typo}
                    </button>
                </div>
            </div>
        </div>
        ''')

    # Bouton global
    html_parts.append('''
    <div class="validate-all-section">
        <button class="validate-all-btn"
                hx-post="/studio/validate/all"
                hx-swap="outerHTML">
            Valider tous les composants
        </button>
    </div>
    ''')

    return HTMLResponse("".join(html_parts))


def _render_component(comp) -> str:
    """Rend un composant en HTML."""
    checked = "checked" if comp.selected else ""
    return f'''
    <div class="component-item" data-id="{comp.component_id}">
        <input type="checkbox" {checked} name="components[]" value="{comp.component_id}">
        <span class="component-name">{comp.component_id}</span>
        <span class="component-reason">{comp.reason}</span>
    </div>
    '''


def _generate_explanation(typography: str, components) -> str:
    """Génère l'explication Sullivan."""
    selected = [c for c in components if c.selected]
    if not selected:
        return f"Aucun composant suggéré pour {typography}."

    return f"J'ai sélectionné {len(selected)} composants pour {typography} basés sur les endpoints détectés."
```

### 3. CSS À AJOUTER (dans `<style>` du template)

```css
/* Layout ARBITER 2 colonnes */
.arbiter-layout {
    display: flex;
    min-height: 100vh;
}

.panel-left {
    width: 55%;
    background: #f0f0e8;
    padding: 24px 32px;
}

.panel-right {
    width: 45%;
    background: #252525;
    padding: 24px 32px;
    color: #fff;
}

/* Typography entry avec 2 colonnes */
.typography-entry {
    margin-bottom: 24px;
    border-bottom: 1px solid #d0d0c8;
    padding-bottom: 16px;
}

.entry-row {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 24px;
}

.entry-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
}

.entry-meta {
    font-size: 11px;
    color: #888;
}

/* Composants inférés */
.inferred-components {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 12px;
}

.component-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid #f0f0f0;
}

.component-item:last-of-type {
    border-bottom: none;
}

.component-name {
    font-size: 12px;
    font-weight: 500;
    color: #333;
}

.component-reason {
    font-size: 10px;
    color: #666;
    margin-left: auto;
}

/* Explication Sullivan */
.sullivan-explanation {
    background: #f8f9fa;
    border-left: 3px solid #7cb342;
    padding: 10px;
    margin: 12px 0;
    font-size: 11px;
    color: #555;
}

.sullivan-explanation .icon {
    margin-right: 6px;
}

/* Boutons Valider */
.validate-btn {
    background: #7cb342;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    margin-top: 8px;
}

.validate-btn:hover {
    background: #689f38;
}

.validate-all-section {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 2px solid #7cb342;
}

.validate-all-btn {
    background: #5a8f2e;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
}

/* Sections collapsibles */
.expandable-section {
    margin-top: 20px;
    border-top: 1px solid #d0d0c8;
    padding-top: 12px;
}

.expandable-header {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 8px 0;
}

.expand-icon {
    color: #7cb342;
}

.expandable-title {
    font-size: 12px;
    font-weight: 600;
    color: #7cb342;
}
```

---

## ZONE DES COMPOSANTS EN BAS (BONUS)

En bas de page, ajoute une zone collapsible avec TOUS les composants par section :

```html
<div id="all-components-zone" class="all-components-zone">
    <h3>Tous les composants disponibles</h3>

    <!-- Navigation par section -->
    <div class="section-nav">
        <button class="nav-arrow" onclick="scrollToSection('atoms')">← Atoms</button>
        <button class="nav-arrow" onclick="scrollToSection('molecules')">Molecules</button>
        <button class="nav-arrow" onclick="scrollToSection('organisms')">Organisms →</button>
    </div>

    <!-- Sections collapsibles -->
    <details id="section-atoms" class="component-section">
        <summary>Atoms (5 composants)</summary>
        <div class="components-grid" hx-get="/studio/components/atoms" hx-trigger="revealed">
            Chargement...
        </div>
    </details>

    <details id="section-molecules" class="component-section">
        <summary>Molecules (4 composants)</summary>
        <div class="components-grid" hx-get="/studio/components/molecules" hx-trigger="revealed">
            Chargement...
        </div>
    </details>

    <!-- etc. -->
</div>
```

---

## FLOW ATTENDU

```
1. User arrive sur /studio?step=4
   ↓
2. Design ARBITER s'affiche (2 panneaux)
   ↓
3. HTMX charge /studio/typologies/arbiter
   ↓
4. Pour chaque typologie (Backend/Frontend/Deploy):
   - Affiche le H2 titre
   - Affiche les composants inférés avec checkboxes
   - Affiche l'explication Sullivan
   - Affiche bouton "Valider [Typography]"
   ↓
5. User peut cocher/décocher les composants
   ↓
6. User clique "Valider Frontend"
   ↓
7. Composants validés passent dans le Génome (panneau droit)
   ↓
8. User clique "Valider tous les composants" pour finaliser
```

---

## TESTS

```bash
# 1. Vérifier que la route typologies existe
curl http://localhost:8000/studio/typologies/arbiter

# 2. Vérifier le rendu dans le navigateur
# Ouvrir http://localhost:8000/studio?step=4
# → Design ARBITER visible
# → Typologies avec composants
# → Boutons Valider fonctionnels

# 3. Tester la validation
# Cliquer sur "Valider Frontend"
# → Les composants doivent passer dans le Génome
```

---

## IMPORTANT

1. **NE SUPPRIME PAS** le design ARBITER existant
2. **NE CRÉE PAS** une nouvelle vue qui le remplace
3. **INTÈGRE** le contenu dynamique DANS la structure ARBITER existante
4. **UTILISE** HTMX pour charger les composants sans recharger la page

---

## Fichiers de référence

- **Design statique ARBITER** : `Frontend/arbiter-interface.html`
  - **URL pour visualiser** : http://localhost:8765/Frontend/arbiter-interface.html
  - C'est TON design. Regarde-le avec ton multimodal pour comprendre la structure.
- Moteur d'inférence : `Backend/Prod/sullivan/agent/component_inference.py`
- Routes studio : `Backend/Prod/sullivan/studio_routes.py`
- Template principal : `Backend/Prod/templates/studio_homeos.html`

---

**Le but : Que l'utilisateur VOIE les composants que Sullivan a choisis, avec une explication, et puisse les valider.**

*— Claude-Code Senior*
