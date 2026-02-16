# 🎯 MISSION KIMI : Bibliothèque de Composants Pré-générés (Tier 1)

**Date** : 10 février 2026
**Agent** : Kimi (Lead FRD)
**Mode** : Aetherflow Hybrid
**Priorité** : Haute
**Statut** : En attente
**Référence Plan** : [plan_tier1_pregenerated_components.json](../../../Backend/Notebooks/benchmark_tasks/plan_tier1_pregenerated_components.json)

---

## 📋 Contexte

D'après la **Stratégie Hybride de Pré-génération**, nous devons implémenter un système **3-Tiers** :

- **Tier 1 (0ms)** : Bibliothèque pré-générée d'atomes/molécules → **CETTE MISSION**
- **Tier 2 (<100ms)** : Cache sémantique avec adaptation légère → Futur
- **Tier 3 (1-5s)** : Génération à la volée avec LLM → Déjà existant

**Objectif** : Créer une bibliothèque de **48+ composants** (8 styles × 6 atomes) pour réduire la latence à **0ms** pour 60% des cas.

---

## 🎯 Objectifs de la Mission

### Résultats Attendus
- ✅ **Latence** : 0ms pour composants pré-générés (vs 1-5s LLM)
- ✅ **Cache Hit Rate** : 85%+
- ✅ **User Satisfaction** : 95%+
- ✅ **Avg Response Time** : < 150ms

### Livrables
1. **pregenerated_components.json** : 8 styles × 6 atomes = 48+ entrées
2. **component_library.py** : Classe de gestion du cache
3. **Intégration component_generator.py** : Check cache avant LLM
4. **API Endpoint** : `/api/components/library/{style}/{atom}`
5. **Interface 9998** : Preview des atomes après sélection style
6. **Tests TDD** : Validation cache hit rate > 80%

---

## 🏗️ Architecture (Génome N0-N3)

### N0 : Frontend
### N1 : Component Generation
### N2 : Pregenerated Library (Tier 1)
### N3 : Atomes (button, input, card, badge, avatar, divider)

---

## 💻 Implémentation - 6 Steps

---

### ✅ **STEP 1 : Créer pregenerated_components.json**

**Fichier** : `Backend/Prod/sullivan/pregenerated_components.json`

**Contenu** :
```json
{
  "styles": {
    "minimal": {
      "button": {
        "primary": {
          "html": "<button class='btn btn-minimal-primary' role='button' aria-label='Action principale'>{{text}}</button>",
          "css_classes": ["btn", "btn-minimal-primary"],
          "accessibility": {
            "role": "button",
            "aria-label": "Action principale"
          },
          "props": {
            "text": "string",
            "disabled": "boolean",
            "type": "submit|button|reset"
          }
        },
        "secondary": { /* ... */ },
        "danger": { /* ... */ }
      },
      "input": {
        "text": {
          "html": "<input type='text' class='input input-minimal' placeholder='{{placeholder}}' aria-label='{{label}}' />",
          "css_classes": ["input", "input-minimal"],
          "accessibility": {
            "role": "textbox",
            "aria-label": "Champ de texte"
          },
          "props": {
            "placeholder": "string",
            "label": "string",
            "required": "boolean"
          }
        },
        "email": { /* ... */ },
        "password": { /* ... */ }
      },
      "card": { /* ... */ },
      "badge": { /* ... */ },
      "avatar": { /* ... */ },
      "divider": { /* ... */ }
    },
    "corporate": { /* Répéter structure pour corporate */ },
    "creative": { /* ... */ },
    "tech": { /* ... */ },
    "elegant": { /* ... */ },
    "playful": { /* ... */ },
    "dark": { /* ... */ },
    "colorful": { /* ... */ }
  }
}
```

**Design Tokens** : Utiliser les couleurs/fonts de `Backend/Prod/sullivan/identity.py` lignes 114-172 (SULLIVAN_LAYOUT_PROPOSALS).

**Exemple pour style "minimal"** :
- Couleurs : `#000000` (primary), `#f5f5f5` (secondary)
- Font : `monospace`
- Spacing : `1.25` scale

**Critères de Validation** :
- ✅ JSON valide (pas d'erreur de parsing)
- ✅ 8 styles présents (minimal, corporate, creative, tech, elegant, playful, dark, colorful)
- ✅ Chaque style a 6 atomes minimum
- ✅ Chaque composant a : `html`, `css_classes`, `accessibility`, `props`

---

### ✅ **STEP 2 : Créer component_library.py**

**Fichier** : `Backend/Prod/sullivan/component_library.py`

**Code** :
```python
import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger


class ComponentNotFoundError(Exception):
    """Raised when component not found in library."""
    pass


class ComponentLibrary:
    """
    Tier 1 Component Library - Instant retrieval (0ms latency).

    Manages pregenerated components for 8 styles:
    - minimal, corporate, creative, tech, elegant, playful, dark, colorful

    Each style contains 6+ atom types:
    - button, input, card, badge, avatar, divider
    """

    def __init__(self, json_path: Optional[Path] = None):
        """
        Load pregenerated components from JSON.

        Args:
            json_path: Path to pregenerated_components.json
        """
        if json_path is None:
            json_path = Path(__file__).parent / "pregenerated_components.json"

        self.json_path = json_path
        self._cache: Dict = {}
        self._load_library()

    def _load_library(self):
        """Load JSON into memory cache."""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache = data.get("styles", {})
                logger.info(f"✅ Loaded {len(self._cache)} styles from {self.json_path}")
        except FileNotFoundError:
            logger.error(f"❌ Component library not found: {self.json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in component library: {e}")
            raise

    def get_component(
        self,
        style_id: str,
        atom_type: str,
        variant: str = "primary"
    ) -> Dict:
        """
        Get component from cache.

        Args:
            style_id: Style ID (e.g., "minimal")
            atom_type: Atom type (e.g., "button")
            variant: Variant (e.g., "primary", "secondary")

        Returns:
            Component dict with html, css_classes, accessibility, props

        Raises:
            ComponentNotFoundError: If component not found
        """
        try:
            component = self._cache[style_id][atom_type][variant]
            logger.debug(f"⚡ Cache HIT: {style_id}/{atom_type}/{variant}")
            return component
        except KeyError:
            logger.warning(f"❌ Cache MISS: {style_id}/{atom_type}/{variant}")
            raise ComponentNotFoundError(
                f"Component not found: {style_id}/{atom_type}/{variant}"
            )

    def get_all_atoms(self, style_id: str) -> List[str]:
        """
        List all atom types for a style.

        Args:
            style_id: Style ID

        Returns:
            List of atom types (e.g., ["button", "input", "card"])
        """
        try:
            return list(self._cache[style_id].keys())
        except KeyError:
            raise ComponentNotFoundError(f"Style not found: {style_id}")

    def render_component(
        self,
        style_id: str,
        atom_type: str,
        variant: str,
        props: Dict
    ) -> str:
        """
        Render component HTML with props injection.

        Args:
            style_id: Style ID
            atom_type: Atom type
            variant: Variant
            props: Props to inject (e.g., {"text": "Click me"})

        Returns:
            Rendered HTML string
        """
        component = self.get_component(style_id, atom_type, variant)
        html = component["html"]

        # Inject props via placeholder replacement
        for key, value in props.items():
            placeholder = f"{{{{{key}}}}}"
            html = html.replace(placeholder, str(value))

        return html

    def get_css_classes(
        self,
        style_id: str,
        atom_type: str,
        variant: str
    ) -> List[str]:
        """
        Get CSS classes for component.

        Args:
            style_id: Style ID
            atom_type: Atom type
            variant: Variant

        Returns:
            List of CSS class names
        """
        component = self.get_component(style_id, atom_type, variant)
        return component.get("css_classes", [])
```

**Critères de Validation** :
- ✅ Classe `ComponentLibrary` définie
- ✅ Méthodes `get_component`, `get_all_atoms`, `render_component`, `get_css_classes`
- ✅ Exception `ComponentNotFoundError` custom
- ✅ Logs cache HIT/MISS avec logger
- ✅ Type hints complets

---

### ✅ **STEP 3 : Intégrer dans component_generator.py**

**Fichier** : `Backend/Prod/sullivan/generator/component_generator.py`

**Modifications** :
```python
# En haut du fichier
from Backend.Prod.sullivan.component_library import ComponentLibrary, ComponentNotFoundError

# Dans la classe ComponentGenerator (ou équivalent)
class ComponentGenerator:
    def __init__(self):
        self.library = ComponentLibrary()  # Charger la library
        # ... reste de l'init

    def generate_component(
        self,
        style_id: str,
        atom_type: str,
        variant: str = "primary",
        context: Optional[Dict] = None
    ):
        """
        Generate component - Check cache first (Tier 1), then LLM (Tier 3).
        """
        # Étape 1 : Vérifier cache Tier 1
        try:
            component = self.library.get_component(style_id, atom_type, variant)
            logger.info(f"⚡ TIER 1 (0ms): {style_id}/{atom_type}/{variant}")
            return component
        except ComponentNotFoundError:
            logger.info(f"🔄 TIER 3 (1-5s): Generating {style_id}/{atom_type}/{variant} with LLM")
            # Étape 2 : Fallback vers génération LLM (existante)
            return self._generate_with_llm(style_id, atom_type, variant, context)

    def _generate_with_llm(self, style_id, atom_type, variant, context):
        """Génération LLM existante (ne pas modifier)."""
        # Code existant de génération LLM
        pass
```

**Critères de Validation** :
- ✅ `ComponentLibrary` importée
- ✅ Check cache AVANT génération LLM
- ✅ Retour immédiat si trouvé (Tier 1)
- ✅ Fallback LLM si non trouvé (Tier 3)
- ✅ Logs différenciés TIER 1 vs TIER 3

---

### ✅ **STEP 4 : Créer l'endpoint API**

**Fichier** : `Backend/Prod/routes/studio_routes.py`

**Code** :
```python
from Backend.Prod.sullivan.component_library import ComponentLibrary, ComponentNotFoundError

# Instancier library (global ou dans dépendance FastAPI)
component_library = ComponentLibrary()

@router.get("/api/components/library/{style_id}/{atom_type}")
async def get_pregenerated_component(
    style_id: str,
    atom_type: str,
    variant: str = Query(default="primary"),
    props: Optional[str] = Query(default=None)
):
    """
    # Tier 1 Component Library - Instant component retrieval (0ms latency)

    Get a pregenerated component from the library.

    Args:
        style_id: Style ID (minimal, corporate, creative, etc.)
        atom_type: Atom type (button, input, card, etc.)
        variant: Variant (primary, secondary, danger, etc.)
        props: Optional JSON string for prop injection

    Returns:
        Component with html, css_classes, accessibility, cache_hit=true

    Example:
        GET /api/components/library/minimal/button?variant=primary&props={"text":"Click"}
    """
    try:
        component = component_library.get_component(style_id, atom_type, variant)

        # Inject props if provided
        if props:
            props_dict = json.loads(props)
            html = component_library.render_component(style_id, atom_type, variant, props_dict)
            component = {**component, "html": html}

        return {
            **component,
            "cache_hit": True,
            "tier": 1,
            "latency_ms": 0
        }

    except ComponentNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Component not found: {style_id}/{atom_type}/{variant}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid props JSON format"
        )


@router.get("/api/components/library/preview/{style_id}")
async def get_style_preview(style_id: str):
    """
    Get preview of 6 base atoms for a style.

    Returns HTML grid with examples of button, input, card, badge, avatar, divider.
    """
    try:
        atoms = component_library.get_all_atoms(style_id)

        previews = []
        for atom_type in atoms[:6]:  # Limiter à 6 atomes
            try:
                component = component_library.get_component(style_id, atom_type, "primary")
                previews.append({
                    "atom_type": atom_type,
                    "html": component["html"],
                    "css_classes": component["css_classes"]
                })
            except ComponentNotFoundError:
                continue

        return {
            "style_id": style_id,
            "previews": previews,
            "count": len(previews)
        }

    except ComponentNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Style not found: {style_id}"
        )
```

**Critères de Validation** :
- ✅ Endpoint `/api/components/library/{style_id}/{atom_type}` créé
- ✅ Query params `variant` et `props` fonctionnels
- ✅ Retour JSON avec `cache_hit: true`, `tier: 1`, `latency_ms: 0`
- ✅ Endpoint `/api/components/library/preview/{style_id}` pour grille
- ✅ Gestion d'erreurs 404/400
- ✅ Documentation OpenAPI (docstring)

---

### ✅ **STEP 5 : Connecter au serveur 9998**

**Fichier** : `server_9998_v2.py`

**Modification JavaScript** (après ligne 1067) :
```javascript
// Gestion sélection de style avec preview
document.querySelectorAll('.style-card').forEach(card => {
    card.addEventListener('click', async () => {
        // Désélectionner les autres
        document.querySelectorAll('.style-card').forEach(c => c.classList.remove('selected'));
        // Sélectionner celui-ci
        card.classList.add('selected');

        const styleId = card.dataset.style;
        console.log('Style sélectionné:', styleId);

        // Fetch preview des atomes
        try {
            const response = await fetch(`/api/components/library/preview/${styleId}`);
            const data = await response.json();

            // Afficher la section preview
            showStylePreview(data);
        } catch (error) {
            console.error('Erreur fetch preview:', error);
        }
    });
});

function showStylePreview(data) {
    // Créer ou récupérer section-style-preview
    let previewSection = document.getElementById('section-style-preview');

    if (!previewSection) {
        // Créer la section si elle n'existe pas
        previewSection = document.createElement('div');
        previewSection.id = 'section-style-preview';
        previewSection.className = 'section';
        previewSection.style.display = 'none';
        previewSection.style.marginTop = '40px';

        // Insérer après section-style-choice
        const styleChoice = document.getElementById('section-style-choice');
        styleChoice.parentNode.insertBefore(previewSection, styleChoice.nextSibling);
    }

    // Générer le HTML de preview (grille 3x2 des atomes)
    const previewsHTML = data.previews.map(p => `
        <div class="atom-preview">
            <div class="atom-label">${p.atom_type}</div>
            ${p.html}
        </div>
    `).join('');

    previewSection.innerHTML = `
        <div class="section-header" style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);">
            <span class="section-title">Aperçu du Style "${data.style_id}"</span>
        </div>
        <div class="section-content">
            <div class="atoms-grid">
                ${previewsHTML}
            </div>
            <div style="text-align: center; margin-top: 24px;">
                <button class="validate-btn" onclick="confirmStyle('${data.style_id}')">
                    Confirmer ce style
                </button>
            </div>
        </div>
    `;

    // Afficher avec animation
    previewSection.style.display = 'block';
    setTimeout(() => {
        previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

function confirmStyle(styleId) {
    console.log('Style confirmé:', styleId);
    alert(`Style "${styleId}" confirmé ! (Step suivant à implémenter)`);
    // TODO: Passer au step suivant
}
```

**CSS à ajouter** (avant `</style>`) :
```css
/* Style Preview Section */
.atoms-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    padding: 24px;
}
.atom-preview {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s;
}
.atom-preview:hover {
    border-color: #7aca6a;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.atom-label {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
```

**Critères de Validation** :
- ✅ Fetch `/api/components/library/preview/{style_id}` au clic
- ✅ Section `section-style-preview` créée dynamiquement
- ✅ Grille 3×2 des atomes affichée
- ✅ Bouton "Confirmer ce style" fonctionnel
- ✅ Animation fade-in / scroll smooth

---

### ✅ **STEP 6 : Tests TDD**

**Tests Manuels** :

1. **Vérifier JSON** :
   ```bash
   python3 -c "import json; data=json.load(open('Backend/Prod/sullivan/pregenerated_components.json')); print(f'{len(data[\"styles\"])} styles loaded')"
   ```
   → Doit afficher "8 styles loaded"

2. **Tester API Endpoint** :
   ```bash
   curl http://localhost:8000/api/components/library/minimal/button?variant=primary
   ```
   → Doit retourner JSON avec `cache_hit: true`, `tier: 1`

3. **Tester Preview API** :
   ```bash
   curl http://localhost:8000/api/components/library/preview/minimal
   ```
   → Doit retourner `previews` avec 6 atomes

4. **Tester UI (serveur 9998)** :
   - Lancer `python3 server_9998_v2.py`
   - Ouvrir http://localhost:9998
   - Cliquer sur un style-card (ex: "Minimal")
   - Vérifier que la section preview s'affiche avec 6 atomes
   - Cliquer sur "Confirmer ce style" → console.log visible

5. **Vérifier Accessibility** :
   - Inspecter HTML généré
   - Vérifier présence de `role` et `aria-label` sur chaque composant

6. **Vérifier Cache Hit Rate** :
   - Appeler 10x l'API pour le même composant
   - Vérifier les logs : doit afficher "Cache HIT" 10 fois
   - Cache hit rate = 100% (car même composant)

**Critères de Validation** :
- ✅ 48+ entrées dans pregenerated_components.json
- ✅ API retourne JSON valide avec `cache_hit: true`
- ✅ Preview s'affiche au clic sur style-card
- ✅ Bouton confirmation fonctionne
- ✅ `aria-labels` présents
- ✅ Cache hit rate > 80%

---

## 📦 Checklist Finale

- [ ] pregenerated_components.json créé (8 styles × 6 atomes)
- [ ] component_library.py créé avec classe ComponentLibrary
- [ ] Intégration dans component_generator.py (check cache avant LLM)
- [ ] Endpoint API `/api/components/library/{style}/{atom}` créé
- [ ] Endpoint API `/api/components/library/preview/{style}` créé
- [ ] Modification server_9998_v2.py (fetch + affichage preview)
- [ ] CSS ajouté pour atoms-grid et atom-preview
- [ ] Tests manuels validés (6/6)

---

## 🎯 Bénéfices Attendus

| Métrique | Avant (Tier 3 seul) | Après (Tier 1 + 3) |
|----------|---------------------|---------------------|
| **Latence moyenne** | 2.1s | < 150ms |
| **Cache hit rate** | 0% | 85%+ |
| **User satisfaction** | 90% | 95%+ |
| **Composants/seconde** | ~0.5 | ~400 |

---

**Mission créée par** : Claude (Architecte)
**À exécuter par** : Kimi (Lead FRD) + DeepSeek (TDD/QA)
**Mode d'exécution** : Aetherflow Hybrid
