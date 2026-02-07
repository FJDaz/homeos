# MISSION : Sullivan Selecteur SET — Logique d'inférence

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Priorité** : HAUTE
**Prérequis** : Mission MONITORING terminée ✅

---

## Contexte

Tu as implémenté `select_component` qui trouve UN composant pour UN intent.
Maintenant il faut la logique pour **inférer un SET de composants** à partir de :

1. **Une Typologie** (Backend/Frontend/Deploy)
2. **Des Endpoints** (POST /users, GET /products...)
3. **Des Méthodes** (CRUD operations)

---

## Ce que tu dois créer

### 1. Nouveau fichier : `Backend/Prod/sullivan/agent/component_inference.py`

```python
"""
Sullivan Component Inference Engine
Infère un set de composants à partir d'endpoints et typologies.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from loguru import logger

@dataclass
class ComponentSelection:
    """Représente un composant sélectionné par Sullivan."""
    component_id: str
    category: str  # atoms, molecules, organisms
    typography: str  # Backend, Frontend, Deploy
    reason: str  # Explication de Sullivan
    selected: bool = True  # Sélectionné par défaut

@dataclass
class InferenceResult:
    """Résultat d'une inférence de composants."""
    typography: str
    components: List[ComponentSelection]
    endpoint: Optional[str] = None
    method: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════
# MAPPING METHOD → COMPOSANTS
# ══════════════════════════════════════════════════════════════════════

METHOD_TO_COMPONENTS = {
    "POST": {
        "primary": ["form", "input", "button"],
        "secondary": ["modal", "toast", "badge"],
        "explanation": "Création de ressource → Formulaire avec validation et feedback"
    },
    "GET": {
        "single": ["card", "badge", "button"],
        "list": ["card", "table", "pagination", "search", "badge"],
        "explanation": "Lecture → Affichage détail ou liste avec filtres"
    },
    "PUT": {
        "primary": ["form", "input", "button", "modal"],
        "secondary": ["toast", "badge"],
        "explanation": "Mise à jour complète → Formulaire pré-rempli avec confirmation"
    },
    "PATCH": {
        "primary": ["form", "input", "button"],
        "secondary": ["toast"],
        "explanation": "Mise à jour partielle → Champs modifiables inline"
    },
    "DELETE": {
        "primary": ["modal", "button"],
        "secondary": ["toast"],
        "explanation": "Suppression → Confirmation obligatoire avant action destructive"
    }
}


# ══════════════════════════════════════════════════════════════════════
# MAPPING RESOURCE → COMPOSANTS SPÉCIFIQUES
# ══════════════════════════════════════════════════════════════════════

RESOURCE_HINTS = {
    # Utilisateurs
    "user": ["card", "badge", "form", "input"],
    "users": ["card", "table", "pagination", "search"],
    "auth": ["form", "input", "button", "modal"],
    "login": ["form", "input", "button"],
    "profile": ["card", "badge", "button"],

    # Produits / E-commerce
    "product": ["card", "badge", "button"],
    "products": ["card", "table", "pagination", "search"],
    "cart": ["card", "button", "badge"],
    "order": ["card", "badge", "table"],

    # Fichiers
    "file": ["button", "card", "badge"],
    "upload": ["button", "card", "modal"],
    "image": ["card", "modal"],

    # Recherche
    "search": ["input", "button", "card"],
    "filter": ["input", "button", "badge"],

    # Générique
    "health": ["badge"],
    "status": ["badge", "card"],
    "config": ["form", "input", "button"],
}


# ══════════════════════════════════════════════════════════════════════
# MAPPING TYPOLOGIE → ZONE UI
# ══════════════════════════════════════════════════════════════════════

TYPOGRAPHY_ZONES = {
    "Brainstorm": {
        "allowed_categories": ["atoms", "molecules"],
        "focus": ["card", "badge", "button"],
    },
    "Backend": {
        "allowed_categories": ["atoms", "molecules"],
        "focus": ["badge", "card", "table"],
    },
    "Frontend": {
        "allowed_categories": ["atoms", "molecules", "organisms"],
        "focus": ["form", "card", "button", "input", "modal", "table"],
    },
    "Deploy": {
        "allowed_categories": ["atoms", "molecules"],
        "focus": ["badge", "button", "card"],
    },
}


# ══════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE : INFÉRENCE
# ══════════════════════════════════════════════════════════════════════

def infer_components_for_endpoint(
    endpoint: str,
    method: str = "GET",
    typography: str = "Frontend",
    library: Dict = None,
) -> InferenceResult:
    """
    Infère les composants nécessaires pour un endpoint donné.

    Args:
        endpoint: L'endpoint (ex: "/api/users", "/api/products/{id}")
        method: La méthode HTTP (GET, POST, PUT, DELETE, PATCH)
        typography: La typologie (Brainstorm, Backend, Frontend, Deploy)
        library: La library de composants (optionnel, charge depuis fichier sinon)

    Returns:
        InferenceResult avec les composants sélectionnés et explications

    Example:
        >>> result = infer_components_for_endpoint("/api/users", "POST", "Frontend")
        >>> print(result.components)
        [ComponentSelection(id="atoms_button", reason="Bouton de soumission pour POST"), ...]
    """
    method = method.upper()

    # 1. Extraire la ressource de l'endpoint
    resource = _extract_resource(endpoint)
    logger.debug(f"Resource extraite: {resource} depuis {endpoint}")

    # 2. Obtenir les composants suggérés par la méthode
    method_info = METHOD_TO_COMPONENTS.get(method, METHOD_TO_COMPONENTS["GET"])

    # 3. Déterminer si c'est une liste ou un item unique
    is_list = not _is_single_resource(endpoint)

    if method == "GET":
        base_components = method_info["list"] if is_list else method_info["single"]
    else:
        base_components = method_info.get("primary", [])

    # 4. Ajouter les composants spécifiques à la ressource
    resource_components = RESOURCE_HINTS.get(resource, [])

    # 5. Fusionner et dédupliquer
    all_suggested = list(dict.fromkeys(base_components + resource_components))

    # 6. Filtrer selon la typologie
    zone_info = TYPOGRAPHY_ZONES.get(typography, TYPOGRAPHY_ZONES["Frontend"])
    filtered = [c for c in all_suggested if c in zone_info["focus"]]

    # 7. Matcher avec la library réelle
    if library is None:
        library = _load_library()

    selections = []
    for comp_hint in filtered:
        matched = _find_component_in_library(library, comp_hint, zone_info["allowed_categories"])
        if matched:
            reason = _generate_reason(comp_hint, method, resource, typography)
            selections.append(ComponentSelection(
                component_id=matched["id"],
                category=matched.get("matched_category", "atoms"),
                typography=typography,
                reason=reason,
                selected=True,
            ))

    return InferenceResult(
        typography=typography,
        components=selections,
        endpoint=endpoint,
        method=method,
    )


def infer_components_for_typography(
    typography: str,
    endpoints: List[Dict] = None,
    library: Dict = None,
) -> List[InferenceResult]:
    """
    Infère les composants pour une typologie entière.

    Args:
        typography: "Backend", "Frontend", "Deploy"
        endpoints: Liste de {"path": "/api/...", "method": "GET/POST/..."}
        library: Library de composants

    Returns:
        Liste d'InferenceResult, un par endpoint
    """
    if endpoints is None:
        endpoints = []

    if library is None:
        library = _load_library()

    results = []
    for ep in endpoints:
        result = infer_components_for_endpoint(
            endpoint=ep.get("path", ep.get("endpoint", "")),
            method=ep.get("method", "GET"),
            typography=typography,
            library=library,
        )
        results.append(result)

    return results


# ══════════════════════════════════════════════════════════════════════
# FONCTIONS HELPER
# ══════════════════════════════════════════════════════════════════════

def _extract_resource(endpoint: str) -> str:
    """Extrait le nom de la ressource d'un endpoint."""
    # /api/users/{id} → users
    # /api/v1/products → products
    parts = endpoint.strip("/").split("/")

    # Ignorer les préfixes communs
    ignore = {"api", "v1", "v2", "v3"}

    for part in parts:
        if part not in ignore and not part.startswith("{"):
            return part.lower()

    return "resource"


def _is_single_resource(endpoint: str) -> bool:
    """Détecte si l'endpoint cible un item unique ou une liste."""
    # /api/users/{id} → True (single)
    # /api/users → False (list)
    return "{" in endpoint or endpoint.rstrip("/").split("/")[-1].isdigit()


def _load_library() -> Dict:
    """Charge la library de composants."""
    from pathlib import Path
    import json

    library_path = Path("/Users/francois-jeandazin/AETHERFLOW/output/components/library.json")

    if not library_path.exists():
        logger.warning(f"Library non trouvée: {library_path}")
        return {"categories": {}}

    try:
        return json.loads(library_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Erreur chargement library: {e}")
        return {"categories": {}}


def _find_component_in_library(
    library: Dict,
    hint: str,
    allowed_categories: List[str],
) -> Optional[Dict]:
    """Trouve un composant dans la library correspondant au hint."""
    if not library or "categories" not in library:
        return None

    hint_lower = hint.lower()

    for category in allowed_categories:
        if category not in library["categories"]:
            continue

        for name, comp in library["categories"][category].items():
            # Match sur le nom
            if hint_lower in name.lower():
                return {**comp, "matched_category": category}

            # Match sur les tags
            tags = [t.lower() for t in comp.get("tags", [])]
            if hint_lower in tags:
                return {**comp, "matched_category": category}

    return None


def _generate_reason(hint: str, method: str, resource: str, typography: str) -> str:
    """Génère une explication pour le choix du composant."""
    reasons = {
        ("button", "POST"): f"Bouton de soumission pour créer un {resource}",
        ("button", "DELETE"): f"Bouton de confirmation pour supprimer",
        ("button", "GET"): f"Bouton d'action contextuelle",
        ("form", "POST"): f"Formulaire de création de {resource}",
        ("form", "PUT"): f"Formulaire de modification de {resource}",
        ("input", "POST"): f"Champ de saisie pour les données du {resource}",
        ("input", "PUT"): f"Champ éditable pour modifier le {resource}",
        ("card", "GET"): f"Carte d'affichage pour {resource}",
        ("table", "GET"): f"Tableau pour lister les {resource}s",
        ("modal", "DELETE"): f"Fenêtre de confirmation avant suppression",
        ("modal", "POST"): f"Fenêtre modale pour formulaire de création",
        ("badge", "GET"): f"Badge de statut pour {resource}",
        ("search", "GET"): f"Barre de recherche pour filtrer les {resource}s",
        ("pagination", "GET"): f"Pagination pour naviguer dans la liste",
    }

    key = (hint.lower(), method.upper())
    return reasons.get(key, f"Composant {hint} pour {typography}")


# ══════════════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Testing Sullivan Component Inference Engine...")
    print("=" * 60)

    # Test 1: POST /api/users
    result = infer_components_for_endpoint("/api/users", "POST", "Frontend")
    print(f"\n📍 POST /api/users → Frontend")
    print(f"   Composants: {len(result.components)}")
    for comp in result.components:
        print(f"   - {comp.component_id}: {comp.reason}")

    # Test 2: GET /api/products
    result = infer_components_for_endpoint("/api/products", "GET", "Frontend")
    print(f"\n📍 GET /api/products → Frontend")
    print(f"   Composants: {len(result.components)}")
    for comp in result.components:
        print(f"   - {comp.component_id}: {comp.reason}")

    # Test 3: DELETE /api/users/{id}
    result = infer_components_for_endpoint("/api/users/{id}", "DELETE", "Frontend")
    print(f"\n📍 DELETE /api/users/{{id}} → Frontend")
    print(f"   Composants: {len(result.components)}")
    for comp in result.components:
        print(f"   - {comp.component_id}: {comp.reason}")

    # Test 4: Typography complète
    endpoints = [
        {"path": "/api/users", "method": "GET"},
        {"path": "/api/users", "method": "POST"},
        {"path": "/api/users/{id}", "method": "DELETE"},
    ]
    results = infer_components_for_typography("Frontend", endpoints)
    print(f"\n📍 Typography 'Frontend' avec {len(endpoints)} endpoints")
    print(f"   Total résultats: {len(results)}")

    print("\n✅ Tests terminés!")
```

---

### 2. Nouveau tool : `select_component_set`

**Fichier** : `Backend/Prod/sullivan/agent/tools.py`

Ajoute ce tool après `select_component` :

```python
# Tool: select_component_set (SULLIVAN SELECTEUR SET)
self.register(Tool(
    name="select_component_set",
    description="Sélectionne un SET de composants pour une typologie entière basé sur les endpoints. Utilise l'inférence pour choisir automatiquement les composants appropriés.",
    parameters={
        "type": "object",
        "properties": {
            "typography": {
                "type": "string",
                "enum": ["Brainstorm", "Backend", "Frontend", "Deploy"],
                "description": "La typologie cible",
            },
            "endpoints": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                    },
                },
                "description": "Liste des endpoints à couvrir",
            },
        },
        "required": ["typography"],
    },
    handler=self._select_component_set,
))

async def _select_component_set(
    self,
    typography: str,
    endpoints: List[Dict] = None,
    **kwargs,
) -> ToolResult:
    """
    Sélectionne un set de composants pour une typologie.

    Args:
        typography: Backend, Frontend, Deploy
        endpoints: Liste d'endpoints [{path, method}, ...]

    Returns:
        ToolResult avec les composants par endpoint
    """
    from Backend.Prod.sullivan.agent.component_inference import (
        infer_components_for_typography,
        infer_components_for_endpoint,
    )

    try:
        if endpoints:
            results = infer_components_for_typography(typography, endpoints)
        else:
            # Pas d'endpoints fournis, utiliser des defaults selon typography
            default_endpoints = {
                "Backend": [
                    {"path": "/api/health", "method": "GET"},
                    {"path": "/api/config", "method": "GET"},
                ],
                "Frontend": [
                    {"path": "/api/users", "method": "GET"},
                    {"path": "/api/users", "method": "POST"},
                ],
                "Deploy": [
                    {"path": "/api/status", "method": "GET"},
                ],
            }
            results = infer_components_for_typography(
                typography,
                default_endpoints.get(typography, []),
            )

        # Formater la réponse
        output = []
        all_components = []

        for result in results:
            endpoint_info = {
                "endpoint": result.endpoint,
                "method": result.method,
                "components": [],
            }

            for comp in result.components:
                comp_info = {
                    "id": comp.component_id,
                    "category": comp.category,
                    "reason": comp.reason,
                    "selected": comp.selected,
                }
                endpoint_info["components"].append(comp_info)
                all_components.append(comp_info)

            output.append(endpoint_info)

        # Dédupliquer les composants
        seen = set()
        unique_components = []
        for c in all_components:
            if c["id"] not in seen:
                seen.add(c["id"])
                unique_components.append(c)

        return ToolResult(
            success=True,
            content=f"✅ {len(unique_components)} composants sélectionnés pour {typography}",
            data={
                "typography": typography,
                "total_components": len(unique_components),
                "by_endpoint": output,
                "unique_components": unique_components,
            },
        )

    except Exception as e:
        logger.error(f"Erreur select_component_set: {e}")
        return ToolResult(
            success=False,
            content=f"❌ Erreur: {str(e)}",
            data={"error": str(e)},
        )
```

---

## Tests à effectuer

```bash
# 1. Tester le module d'inférence
python Backend/Prod/sullivan/agent/component_inference.py

# Attendu:
# 📍 POST /api/users → Frontend
#    Composants: 3+
#    - atoms_button: Bouton de soumission...
#    - atoms_input: Champ de saisie...

# 2. Tester le tool via CLI
./aetherflow-chat "Sélectionne les composants pour Frontend avec POST /api/users"

# Attendu: Liste des composants avec explications
```

---

## Rappel : Format de sortie pour l'UI

Sullivan retourne pour chaque Typography :

```json
{
  "typography": "Frontend",
  "by_endpoint": [
    {
      "endpoint": "/api/users",
      "method": "POST",
      "components": [
        {"id": "atoms_button", "reason": "Bouton de soumission...", "selected": true},
        {"id": "atoms_input", "reason": "Champ de saisie...", "selected": true}
      ]
    }
  ],
  "unique_components": [...]
}
```

L'UI affichera ça en colonnes (Backend | Frontend | Deploy) avec les composants sous chaque entrée.

---

## Quand tu as terminé

1. **Teste** le module standalone
2. **Intègre** le tool dans tools.py
3. **Mets à jour** ton rapport avec les résultats des tests
4. **Log** tes actions avec le système de monitoring

---

**Tu vas adorer cette mission, Padawan. C'est le CŒUR de Sullivan.**

*— Claude-Code Senior*
