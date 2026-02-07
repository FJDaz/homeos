# MISSION : Connecter l'Inférence à l'UI

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Priorité** : CRITIQUE
**Prérequis** : Mission SELECTEUR_SET terminée ✅

---

## Le problème

Tu as créé le moteur d'inférence (`component_inference.py`) et le tool (`select_component_set`).

**MAIS** : Personne ne l'appelle. C'est une fonction dormante.

Quand l'utilisateur arrive sur `/studio?step=4`, il devrait voir les composants inférés automatiquement. Actuellement, rien ne se passe.

---

## Ce que tu dois faire

### 1. Créer une route API pour l'inférence

**Fichier** : `Backend/Prod/sullivan/studio_routes.py`

Ajoute cette route :

```python
@router.get("/inference/{typography}", response_class=JSONResponse)
async def get_inference_for_typography(
    request: Request,
    typography: str,
):
    """
    Retourne les composants inférés pour une typologie.

    Lit l'IR (Intent Revue) pour extraire les endpoints,
    puis appelle select_component_set pour inférer les composants.
    """
    from Backend.Prod.sullivan.agent.component_inference import (
        infer_components_for_typography,
    )

    # 1. Charger l'IR depuis le genome ou la session
    ir_data = load_ir_data()  # À implémenter

    # 2. Extraire les endpoints de l'IR
    endpoints = extract_endpoints_from_ir(ir_data)  # À implémenter

    # 3. Inférer les composants
    results = infer_components_for_typography(typography, endpoints)

    # 4. Formater la réponse
    output = {
        "typography": typography,
        "endpoints_count": len(endpoints),
        "components": [],
    }

    for result in results:
        for comp in result.components:
            output["components"].append({
                "id": comp.component_id,
                "category": comp.category,
                "reason": comp.reason,
                "selected": comp.selected,
                "endpoint": result.endpoint,
                "method": result.method,
            })

    return JSONResponse(content=output)
```

### 2. Créer les fonctions helper

```python
def load_ir_data() -> Dict:
    """Charge l'IR depuis le genome ou la session."""
    genome_path = Path("output/genome.json")

    if genome_path.exists():
        data = json.loads(genome_path.read_text())
        return data.get("ir", {})

    # Fallback : IR par défaut pour test
    return {
        "endpoints": [
            {"path": "/api/users", "method": "GET"},
            {"path": "/api/users", "method": "POST"},
            {"path": "/api/users/{id}", "method": "DELETE"},
        ]
    }


def extract_endpoints_from_ir(ir_data: Dict) -> List[Dict]:
    """Extrait les endpoints de l'IR."""
    endpoints = ir_data.get("endpoints", [])

    # Si pas d'endpoints explicites, essayer de les extraire du code IR
    if not endpoints:
        code_ir = ir_data.get("code_ir", "")
        # Parser le code IR pour trouver les endpoints
        # ...

    return endpoints
```

### 3. Modifier le template pour appeler l'inférence

**Fichier** : `Backend/Prod/templates/studio_homeos.html`

Dans la section `tab-frontend`, ajoute un appel HTMX ou JS pour charger les composants :

```html
<!-- Zone pour les composants inférés -->
<div id="inferred-components"
     hx-get="/studio/inference/Frontend"
     hx-trigger="load"
     hx-swap="innerHTML">
    <p class="text-gray-400">Chargement des composants...</p>
</div>
```

Ou en JavaScript :

```javascript
// Au chargement du tab Frontend
async function loadInferredComponents() {
    const response = await fetch('/studio/inference/Frontend');
    const data = await response.json();

    renderComponents(data.components);
}

function renderComponents(components) {
    const container = document.getElementById('inferred-components');

    let html = '<div class="components-grid">';

    components.forEach(comp => {
        html += `
            <div class="component-card" data-id="${comp.id}">
                <input type="checkbox" ${comp.selected ? 'checked' : ''}>
                <h4>${comp.id}</h4>
                <p class="reason">${comp.reason}</p>
                <span class="badge">${comp.method} ${comp.endpoint}</span>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

// Appeler au chargement
document.addEventListener('DOMContentLoaded', () => {
    if (currentStep >= 4) {
        loadInferredComponents();
    }
});
```

### 4. Ajouter le style CSS pour les composants

```css
.components-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
}

.component-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    transition: border-color 0.2s;
}

.component-card:hover {
    border-color: #7cb342;
}

.component-card input[type="checkbox"] {
    float: right;
}

.component-card h4 {
    margin: 0 0 0.5rem;
    font-size: 14px;
    font-weight: 600;
}

.component-card .reason {
    font-size: 12px;
    color: #666;
    margin: 0.5rem 0;
}

.component-card .badge {
    display: inline-block;
    background: #f0f0f0;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    color: #333;
}
```

---

## Flow complet attendu

```
1. User arrive sur /studio?step=4
   ↓
2. Tab Frontend s'active
   ↓
3. HTMX/JS appelle GET /studio/inference/Frontend
   ↓
4. Route charge l'IR depuis genome.json
   ↓
5. Route extrait les endpoints (POST /users, GET /products, etc.)
   ↓
6. Route appelle infer_components_for_typography()
   ↓
7. Route retourne JSON avec composants inférés
   ↓
8. Frontend affiche les composants avec checkboxes
   ↓
9. User peut décocher/cocher les composants
   ↓
10. Bouton "Valider" envoie la sélection finale
```

---

## Tests

```bash
# 1. Tester la route directement
curl http://localhost:8000/studio/inference/Frontend | jq

# Attendu:
# {
#   "typography": "Frontend",
#   "endpoints_count": 3,
#   "components": [
#     {"id": "atoms_input", "reason": "...", "selected": true, ...},
#     ...
#   ]
# }

# 2. Tester dans le navigateur
# Ouvrir http://localhost:8000/studio?step=4
# Les composants doivent apparaître automatiquement
```

---

## Quand tu as terminé

1. Teste la route `/studio/inference/Frontend`
2. Vérifie l'affichage dans le template
3. Mets à jour ton rapport
4. Log tes actions avec le monitoring

---

**C'est cette mission qui fait que Sullivan MONTRE ce qu'il pense.**

*— Claude-Code Senior*
