"""
M282/M292: Manifest Analyzer — Background analysis of manifest content + design tokens.
Uses fast model (Groq/Gemini) to:
- If !manifest: infer from design tokens alone → propose draft manifest
- If manifest exists: analyze for gaps → prepare questions for Sullivan
"""
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("AetherFlowV3")

# --- PATHS ---
CWD = Path(__file__).parent.parent.resolve()
ROOT_DIR = CWD.parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"


async def analyze_manifest(project_id: str, manifest_data: Optional[Dict] = None, tokens: Optional[Dict] = None) -> Dict:
    """
    Analyze manifest + tokens. Returns:
    - proposed_content: markdown to inject in editor
    - questions: list of questions Sullivan should ask
    - inferred_from_tokens: bool
    """
    has_manifest = manifest_data and (manifest_data.get("raw_content") or manifest_data.get("description"))

    if not has_manifest:
        return await _infer_from_tokens(project_id, tokens)
    else:
        return await _analyze_existing_manifest(project_id, manifest_data, tokens)


async def _infer_from_tokens(project_id: str, tokens: Optional[Dict]) -> Dict:
    """No manifest — Groq/Gemini infers from design tokens alone."""
    palette = tokens.get("colors", {}).get("palette", []) if tokens else []
    primary = tokens.get("colors", {}).get("primary", "#8cc63f") if tokens else "#8cc63f"

    prompt = f"""Tu es un architecte UX senior. Un élève vient d'uploader des écrans dans HomeOS.
Tu as extrait ces tokens design de ses écrans :

Couleurs dominantes: {', '.join(palette) if palette else 'non détectées'}
Couleur principale: {primary}

À partir de ces seuls indices, propose un manifeste de projet structuré en markdown.
Le manifeste doit décrire :
- L'intention du projet (ce que tu pères que l'élève veut faire)
- Les écrans probables (d'après les dimensions moyennes des écrans uploadés)
- Les composants clés
- Les contraintes techniques potentielles

Commence par : "Voilà ce que je crois avoir compris de ce que tu veux faire. Ai-je raison ? Corrige-moi."

Réponds UNIQUEMENT en markdown."""

    result = await _call_ai(prompt)

    return {
        "proposed_content": result,
        "questions": [
            "Est-ce que ça correspond à ton intention ?",
            "Quels écrans comptes-tu ajouter ?",
            "Y a-t-il des contraintes particulières ?"
        ],
        "inferred_from_tokens": True
    }


async def _analyze_existing_manifest(project_id: str, manifest_data: Dict, tokens: Optional[Dict]) -> Dict:
    """Manifest exists — ask a few questions to better understand intent."""
    content = manifest_data.get("raw_content", "")[:3000]
    name = manifest_data.get("name", "Projet")

    prompt = f"""Tu es un mentor UX bienveillant. Un élève a rédigé ce manifeste pour son projet.

Projet: {name}

Manifeste:
{content}

Pose-lui 3-4 questions courtes pour mieux cerner son intention.
Sois concis, direct, encourageant.

Réponds avec UNIQUEMENT un objet JSON :
{{
  "questions": ["question 1", "question 2", "question 3"]
}}"""

    result = await _call_ai(prompt)

    try:
        data = json.loads(result)
        questions = data.get("questions", [])
    except:
        questions = ["Est-ce que le manifeste reflète bien ton intention ?"]

    return {
        "current_content": content,
        "questions": questions[:4],
        "inferred_from_tokens": False
    }


async def _call_ai(prompt: str) -> str:
    """Call AI model. Tries Groq first (fast), falls back to Gemini."""
    # Try Groq first (fastest)
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key:
        try:
            return await _call_groq(prompt, groq_key)
        except Exception as e:
            logger.warning(f"Groq failed, falling back to Gemini: {e}")

    # Fallback: Gemini
    try:
        from Backend.Prod.models.gemini_client import GeminiClient
        client = GeminiClient()
        result = await client.generate(
            prompt=prompt,
            output_constraint="Markdown or JSON",
            max_tokens=2000,
            temperature=0.3
        )
        if result.success:
            return result.code.strip()
    except Exception as e:
        logger.error(f"Gemini failed: {e}")

    return "Impossible d'analyser le manifeste pour le moment."


async def _call_groq(prompt: str, api_key: str) -> str:
    """Call Groq API (ultra-fast)."""
    import urllib.request
    import json

    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2000
    }).encode()

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
        return result["choices"][0]["message"]["content"].strip()
