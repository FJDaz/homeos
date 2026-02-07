# MISSION KIMI PADAWAN : Implémenter le KIMI Adapter

**De** : Claude-Code (Senior)
**Pour** : KIMI Padawan (Cursor)
**Date** : 4 février 2026
**Priorité** : HAUTE

---

## CONTEXTE

On a confirmé que **KIMI K2.5** est accessible via **HuggingFace Router**.
Ta mission : implémenter l'adapter qui permet à Sullivan d'utiliser KIMI pour analyser des templates PNG et en extraire des composants.

---

## API KIMI K2.5 - INFORMATIONS CONFIRMÉES

### Endpoint (TESTÉ ET FONCTIONNEL)
```
https://router.huggingface.co/v1/chat/completions
```

### Modèle
```
moonshotai/Kimi-K2.5:novita
```

### Authentification
```
Authorization: Bearer $HF_KEY
```
(La clé est dans `.env` sous le nom `HF_KEY`)

### Format de payload VISION (multimodal)
```json
{
  "model": "moonshotai/Kimi-K2.5:novita",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Analyse ce template PNG et extrais les composants UI..."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,{BASE64_IMAGE}"
          }
        }
      ]
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.1
}
```

---

## FICHIERS À CRÉER

### 1. `Backend/Prod/models/kimi_vision_client.py`

```python
"""
KIMI K2.5 Vision Client - Analyse de templates PNG via HuggingFace Router.
"""

import httpx
import base64
import json
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from ..config.settings import settings


class KimiVisionClient:
    """
    Client pour KIMI K2.5 via HuggingFace Router.
    Spécialisé dans l'analyse visuelle de templates PNG.
    """

    def __init__(self):
        self.api_key = settings.hf_key  # HF_KEY dans .env
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.model = "moonshotai/Kimi-K2.5:novita"
        self.timeout = 60  # Vision peut prendre plus de temps

        if not self.api_key:
            logger.warning("HF_KEY not configured - KIMI Vision unavailable")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def analyze_template(
        self,
        image_path: str,
        instructions: str = ""
    ) -> Dict:
        """
        Analyse un template PNG et extrait les composants UI.

        Args:
            image_path: Chemin vers le fichier PNG
            instructions: Instructions additionnelles

        Returns:
            dict avec layout, components, colors, etc.
        """
        if not self.available:
            return {"error": "KIMI Vision not available", "components": []}

        # Encoder l'image en base64
        image_base64 = self._encode_image(image_path)
        if not image_base64:
            return {"error": f"Cannot read image: {image_path}", "components": []}

        # Construire le prompt d'analyse
        prompt = self._build_analysis_prompt(instructions)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.1
                    }
                )

                if response.status_code != 200:
                    logger.error(f"KIMI API error: {response.status_code}")
                    return {"error": f"API error: {response.status_code}", "components": []}

                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return self._parse_analysis(content)

        except Exception as e:
            logger.error(f"KIMI Vision error: {e}")
            return {"error": str(e), "components": []}

    def _encode_image(self, image_path: str) -> Optional[str]:
        """Encode une image en base64."""
        try:
            path = Path(image_path)
            if not path.exists():
                return None
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return None

    def _build_analysis_prompt(self, instructions: str) -> str:
        """Construit le prompt d'analyse UI."""
        return f"""Tu es un expert UI/UX. Analyse ce template PNG et extrais les informations suivantes.

RETOURNE UN JSON VALIDE avec cette structure exacte:

{{
  "layout": {{
    "type": "sidebar-left|sidebar-right|full-width|centered|grid",
    "zones": ["header", "sidebar", "main", "footer"]
  }},
  "components": [
    {{
      "name": "nom_du_composant",
      "category": "atoms|molecules|organisms",
      "description": "Description courte",
      "html_estimate": "<div class='...'>...</div>",
      "css_classes": ["class1", "class2"],
      "position": "top-left|center|sidebar|etc"
    }}
  ],
  "colors": {{
    "primary": "#hex",
    "secondary": "#hex",
    "background": "#hex",
    "text": "#hex",
    "accent": "#hex"
  }},
  "typography": {{
    "headings": "font-family ou style",
    "body": "font-family ou style"
  }},
  "spacing": "compact|normal|spacious"
}}

Instructions additionnelles: {instructions or "Aucune"}

IMPORTANT: Retourne UNIQUEMENT le JSON, pas de texte autour."""

    def _parse_analysis(self, content: str) -> Dict:
        """Parse la réponse de KIMI."""
        try:
            # Nettoyer le markdown si présent
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())
        except json.JSONDecodeError:
            logger.warning(f"KIMI returned non-JSON: {content[:200]}")
            return {
                "error": "Invalid JSON response",
                "raw_content": content[:500],
                "components": []
            }


# Singleton pour usage global
_kimi_vision_client: Optional[KimiVisionClient] = None


def get_kimi_vision_client() -> KimiVisionClient:
    """Get or create the KIMI Vision client singleton."""
    global _kimi_vision_client
    if _kimi_vision_client is None:
        _kimi_vision_client = KimiVisionClient()
    return _kimi_vision_client
```

---

### 2. Ajouter `hf_key` dans `Backend/Prod/config/settings.py`

Trouve la classe `Settings` et ajoute :

```python
# HuggingFace API (pour KIMI K2.5 Vision)
hf_key: str = Field(default="", env="HF_KEY")
```

---

### 3. `Backend/Prod/sullivan/kimi_adapter.py`

```python
"""
KIMI Adapter - Orchestre KIMI Vision → Sullivan pour PNG → Composants.
"""

import json
from pathlib import Path
from typing import Dict, List
from loguru import logger

from ..models.kimi_vision_client import get_kimi_vision_client


class KimiAdapter:
    """
    Adapter qui traduit l'analyse KIMI en composants pour la library Sullivan.
    """

    def __init__(self):
        self.kimi = get_kimi_vision_client()
        self.library_path = Path("output/components/library.json")

    async def process_template_to_library(
        self,
        image_path: str,
        instructions: str = ""
    ) -> Dict:
        """
        Workflow complet : PNG → KIMI analyse → Composants → Library.

        Returns:
            dict avec status, components ajoutés, erreurs
        """
        # 1. Analyse KIMI
        logger.info(f"Analyzing template: {image_path}")
        analysis = await self.kimi.analyze_template(image_path, instructions)

        if "error" in analysis:
            return {"status": "error", "error": analysis["error"]}

        # 2. Convertir en format library
        components = self._convert_to_library_format(analysis)

        # 3. Ajouter à la library
        added = self._add_to_library(components)

        return {
            "status": "success",
            "analysis": analysis,
            "components_added": len(added),
            "component_ids": added
        }

    def _convert_to_library_format(self, analysis: Dict) -> List[Dict]:
        """Convertit l'analyse KIMI en format library.json."""
        components = []

        for comp in analysis.get("components", []):
            category = comp.get("category", "molecules")
            name = comp.get("name", "unknown").lower().replace(" ", "_")

            component = {
                "id": f"{category}_{name}",
                "category": category,
                "name": name,
                "html": comp.get("html_estimate", "<div>TODO</div>"),
                "css": "",  # À remplir manuellement ou par génération
                "description": comp.get("description", ""),
                "tags": [name] + comp.get("css_classes", []),
                "params": [],
                "defaults": {},
                "examples": [{"name": "basic", "description": "Usage basique", "params": {}}],
                "complexity": "medium",
                "source": "kimi_vision"
            }
            components.append(component)

        return components

    def _add_to_library(self, components: List[Dict]) -> List[str]:
        """Ajoute les composants à library.json."""
        added_ids = []

        try:
            # Charger la library existante
            if self.library_path.exists():
                with open(self.library_path, "r") as f:
                    library = json.load(f)
            else:
                library = {"version": "1.0", "categories": {}, "stats": {}}

            # Ajouter chaque composant
            for comp in components:
                category = comp["category"]
                name = comp["name"]

                if category not in library["categories"]:
                    library["categories"][category] = {}

                # Éviter les doublons
                if name not in library["categories"][category]:
                    library["categories"][category][name] = comp
                    added_ids.append(comp["id"])
                    logger.info(f"Added component: {comp['id']}")

            # Mettre à jour les stats
            total = sum(len(cat) for cat in library["categories"].values())
            library["stats"] = {
                "total": total,
                "by_category": {k: len(v) for k, v in library["categories"].items()}
            }

            # Sauvegarder
            with open(self.library_path, "w") as f:
                json.dump(library, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error updating library: {e}")

        return added_ids


# Singleton
_kimi_adapter: KimiAdapter = None


def get_kimi_adapter() -> KimiAdapter:
    global _kimi_adapter
    if _kimi_adapter is None:
        _kimi_adapter = KimiAdapter()
    return _kimi_adapter
```

---

### 4. Endpoint API dans `Backend/Prod/sullivan/studio_routes.py`

Ajoute ces routes dans le fichier existant :

```python
from ..sullivan.kimi_adapter import get_kimi_adapter
from fastapi import UploadFile, File, Form
import tempfile
import os


@router.post("/kimi/analyze-template")
async def analyze_template_with_kimi(
    image: UploadFile = File(...),
    instructions: str = Form("")
):
    """
    Upload un PNG → KIMI l'analyse → Retourne les composants détectés.
    """
    # Sauvegarder temporairement
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        content = await image.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        adapter = get_kimi_adapter()
        result = await adapter.process_template_to_library(tmp_path, instructions)
        return result
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/kimi/test")
async def test_kimi_connection():
    """Test la connexion à KIMI K2.5."""
    from ..models.kimi_vision_client import get_kimi_vision_client

    client = get_kimi_vision_client()
    return {
        "available": client.available,
        "model": client.model,
        "endpoint": client.api_url
    }
```

---

## TEST APRÈS IMPLÉMENTATION

```bash
# 1. Test connexion
curl http://localhost:8000/sullivan/kimi/test

# 2. Test analyse (avec un PNG)
curl -X POST http://localhost:8000/sullivan/kimi/analyze-template \
  -F "image=@Frontend/arbiter-interface.png" \
  -F "instructions=Extrais tous les composants UI de cette interface"
```

---

## CHECKLIST

- [ ] Créer `Backend/Prod/models/kimi_vision_client.py`
- [ ] Ajouter `hf_key` dans `settings.py`
- [ ] Créer `Backend/Prod/sullivan/kimi_adapter.py`
- [ ] Ajouter les routes dans `studio_routes.py`
- [ ] Tester avec `/kimi/test`
- [ ] Tester avec une vraie image

---

## NOTES IMPORTANTES

1. **NE PAS** utiliser l'ancien `kimi_client.py` (il utilise Moonshot, pas HF Router)
2. **UTILISER** `HF_KEY` pas `KIMI_KEY`
3. **L'endpoint est** `https://router.huggingface.co/v1/chat/completions`
4. **Le modèle est** `moonshotai/Kimi-K2.5:novita`

---

*— Claude-Code Senior*
