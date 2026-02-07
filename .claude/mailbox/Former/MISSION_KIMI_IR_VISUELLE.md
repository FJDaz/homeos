# MISSION KIMI : Enrichir l'IR avec couche visuelle Gemini

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 5 fevrier 2026
**Priorite** : MOYENNE (apres DaisyUI)

---

## Contexte

L'IR actuelle traduit des endpoints en composants de facon purement textuelle.
On veut ajouter un "visual_hint" a chaque entree de l'IR pour que l'Arbiter
ait un indice visuel des le depart.

## API Gemini deja configuree

- Modele : `gemini-2.5-flash` (dans settings.py)
- Capacite : multimodal (vision + texte)
- Client existant : `Backend/Prod/models/gemini_client.py`

## Ce que tu dois faire

### 1. Modifier le genome_generator ou section_generator

Quand l'IR analyse un endpoint, ajouter un appel Gemini pour inferer :

```json
{
  "endpoint": "GET /api/users",
  "method": "GET",
  "summary": "Liste des utilisateurs",
  "visual_hint": "table",
  "visual_category": "data_display",
  "inferred_daisy_component": "daisy_table",
  "wireframe_sketch": "Header row + data rows + pagination"
}
```

### 2. Logique d'inference (PAS besoin de Gemini pour ca)

Mapping simple par heuristiques (pas de LLM necessaire) :

```python
ENDPOINT_TO_VISUAL = {
    # GET + liste → table
    ("GET", ["list", "all", "users", "items"]): {
        "visual_hint": "table",
        "visual_category": "data_display",
        "inferred_daisy_component": "daisy_table"
    },
    # POST + create → form
    ("POST", ["create", "new", "add", "register"]): {
        "visual_hint": "form",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_fieldset"
    },
    # GET + detail/id → card
    ("GET", ["detail", "profile", "info", "{id}"]): {
        "visual_hint": "card",
        "visual_category": "data_display",
        "inferred_daisy_component": "daisy_card"
    },
    # DELETE → modal confirmation
    ("DELETE", ["delete", "remove"]): {
        "visual_hint": "modal",
        "visual_category": "actions",
        "inferred_daisy_component": "daisy_modal"
    },
    # GET + status/health → stat
    ("GET", ["health", "status", "metrics"]): {
        "visual_hint": "stat",
        "visual_category": "data_display",
        "inferred_daisy_component": "daisy_stat"
    },
    # PUT/PATCH → form (edition)
    ("PUT", []): {
        "visual_hint": "form",
        "visual_category": "data_input",
        "inferred_daisy_component": "daisy_fieldset"
    }
}
```

### 3. Ou l'injecter

Dans le genome JSON, chaque endpoint doit porter ces champs supplementaires.
Le champ `inferred_daisy_component` pointe vers un ID de la library.json.

### 4. Gemini multimodal (V2 seulement)

En V2, si un PNG de maquette est disponible, on peut envoyer l'image
a Gemini pour qu'il infere le type de composant visuellement.
Pour l'instant, les heuristiques ci-dessus suffisent.

## Fichiers concernes

- `Backend/Prod/core/genome_generator.py` — enrichir les endpoints
- `Backend/Prod/models/section_generator.py` — si c'est la que les endpoints sont traites

## Important

- PAS d'appel API Gemini en V1, juste des heuristiques
- Le mapping doit pointer vers des composants DaisyUI de la library
- Faire ca APRES la mission DaisyUI (pour que les refs existent)

---

*— Claude-Code Senior*
