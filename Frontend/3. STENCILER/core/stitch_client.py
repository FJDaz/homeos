"""
Stitch Client — Mission 201-A-FIX + 201-B
Client MCP JSON-RPC pour Google Stitch (StreamableHTTP).
Protocol: POST https://stitch.googleapis.com/mcp avec JSON-RPC 2.0
Auth: X-Goog-Api-Key header (pas Bearer)

Réponse MCP tools/call : {"result": {"content": [{"type": "text", "text": "<json>"}]}}
→ _mcp_call parse content[0].text et retourne directement les données Stitch.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Optional, Any

logger = logging.getLogger("AetherFlowV3")

STITCH_MCP_URL = "https://stitch.googleapis.com/mcp"
STITCH_API_KEY = os.getenv("STITCH_API_KEY", "")


def _mcp_call(method: str, params: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
    """Appel JSON-RPC MCP vers Stitch. Retourne les données Stitch parsées."""
    key = api_key or STITCH_API_KEY
    if not key:
        raise ValueError("STITCH_API_KEY non configurée")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": method,
            "arguments": params
        }
    }

    req = urllib.request.Request(
        STITCH_MCP_URL,
        data=json.dumps(payload).encode(),
        headers={
            "X-Goog-Api-Key": key,
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise ConnectionError(f"Stitch MCP HTTP {e.code}: {body}")

    # Le protocole MCP tools/call encapsule la réponse dans content[0].text
    # Format: {"result": {"content": [{"type": "text", "text": "<json_string>"}]}}
    mcp_result = raw.get("result", {})
    content = mcp_result.get("content", [])
    if content and isinstance(content, list) and content[0].get("type") == "text":
        try:
            return json.loads(content[0]["text"])
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback : résultat direct (Stitch sans encapsulation content)
    return mcp_result


def _fetch_url(url: str) -> str:
    """Télécharge le contenu d'une URL (pour les downloadUrl Stitch)."""
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8')


class StitchClient:
    """Client MCP pour Stitch — récupère écrans et Design DNA via JSON-RPC."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or STITCH_API_KEY
        if not self.api_key:
            raise ValueError("STITCH_API_KEY non configurée")

    def get_project_data(self, project_id: str) -> Dict[str, Any]:
        """Liste les écrans d'un projet Stitch via get_project."""
        return _mcp_call("get_project", {"name": f"projects/{project_id}"}, self.api_key)

    def get_screen_code(self, project_id: str, screen_name: str) -> Dict[str, Any]:
        """Récupère le HTML d'un écran via get_screen → fetch downloadUrl."""
        screen_data = _mcp_call(
            "get_screen",
            {"name": f"projects/{project_id}/screens/{screen_name}"},
            self.api_key
        )

        # LOG: dump ALL keys for debugging
        logger.info(f"Stitch get_screen FULL KEYS: {list(screen_data.keys()) if isinstance(screen_data, dict) else type(screen_data)}")
        if isinstance(screen_data, dict):
            for k, v in screen_data.items():
                logger.info(f"Stitch get_screen key={k} type={type(v).__name__} val={str(v)[:300]}")

        html_code = screen_data.get("htmlCode", {})
        download_url = html_code.get("downloadUrl")

        if not download_url:
            inline = html_code.get("content", "")
            return {"html": inline, "screen_data": screen_data}

        html = _fetch_url(download_url)
        return {"html": html, "screen_data": screen_data}

    def get_design_dna(self, project_id: str) -> Dict[str, Any]:
        """Récupère le Design DNA via list_design_systems."""
        return _mcp_call(
            "list_design_systems",
            {"parent": f"projects/{project_id}"},
            self.api_key
        )

    def generate_screen_from_text(self, prompt: str, project_id: str) -> Dict[str, Any]:
        """Génère un nouvel écran Stitch depuis un prompt textuel."""
        return _mcp_call(
            "generate_screen_from_text",
            {
                "parent": f"projects/{project_id}",
                "text": prompt
            },
            self.api_key
        )

    def edit_screen(self, project_id: str, screen_id: str, instructions: str) -> Dict[str, Any]:
        """Modifie un écran Stitch existant via des instructions textuelles."""
        return _mcp_call(
            "edit_screen",
            {
                "name": f"projects/{project_id}/screens/{screen_id}",
                "instructions": instructions
            },
            self.api_key
        )

    def is_available(self) -> bool:
        """Vérifie que la clé API est présente."""
        return bool(self.api_key)
