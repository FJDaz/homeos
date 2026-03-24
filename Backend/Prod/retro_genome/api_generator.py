#!/usr/bin/env python3
"""
api_generator.py — Mission 91 + 91-A
Générateur automatique de routes FastAPI à partir d'un manifest Retro-Genome.
M91-A : support multi-archetype (top-2) + résolution conventions AetherFlow.
"""

import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger

try:
    from .archetype_detector import ArchetypeDetector
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from archetype_detector import ArchetypeDetector


class APIGenerator:
    def __init__(self):
        self.detector = ArchetypeDetector()
        self.archetypes = self.detector.archetypes

    def _detect_top2(self, manifest: Dict) -> List[Dict]:
        """Retourne les 2 archetypes avec le score le plus élevé (si score2 > 50% score1)."""
        elements = manifest.get("elements", [])
        hints  = [e.get("visual_hint", "").lower() for e in elements if e.get("visual_hint")]
        roles  = [r.get("structural_role", "").lower() for r in manifest.get("regions", []) if r.get("structural_role")]
        ids    = [e.get("id", "").lower() for e in elements if e.get("id")]
        names  = [e.get("name", "").lower() for e in elements if e.get("name")]
        texts  = " ".join(e.get("text_content", "").lower() for e in elements if e.get("text_content"))

        scores: List[Tuple[int, Dict]] = []
        for arch in self.archetypes:
            score = 0
            for trigger in arch.get("visual_triggers", []):
                t = trigger.lower()
                if any(t in h for h in hints): score += 3
                if any(t in r for r in roles): score += 3
                if any(t in i for i in ids):   score += 2
                if any(t in n for n in names): score += 1
                if t in texts:                  score += 1
            if score > 0:
                scores.append((score, arch))

        scores.sort(key=lambda x: x[0], reverse=True)
        if not scores:
            return []

        top_score, top_arch = scores[0]
        result = [top_arch]

        if len(scores) > 1:
            second_score, second_arch = scores[1]
            if second_score >= top_score * 0.5:
                result.append(second_arch)
                logger.info(f"🎯 Composite: {top_arch['archetype_id']} ({top_score}) + {second_arch['archetype_id']} ({second_score})")

        return result

    def _apply_conventions(self, endpoint: str, slug: str, conventions: Dict) -> str:
        """Remplace les paths génériques par les conventions AetherFlow."""
        if endpoint in conventions:
            return conventions[endpoint].replace("{slug}", slug)
        # Fallback : substitue /api/ par /api/{slug}/
        method, path = endpoint.split(" ", 1)
        if path.startswith("/api/"):
            parts = path.split("/")  # ['', 'api', 'resource', 'action']
            if len(parts) >= 3:
                # /api/fs/tree → /api/{slug}/tree  (drop generic resource name)
                action = "/".join(parts[3:]) if len(parts) > 3 else parts[2]
                return f"{method} /api/{slug}/{action}"
        return endpoint

    def _path_to_handler(self, method: str, path: str) -> str:
        clean = re.sub(r'[^a-zA-Z0-9]', '_', path.replace('/api/', ''))
        clean = re.sub(r'_+', '_', clean).strip('_')
        return f"{method.lower()}_{clean}"

    def _path_to_model(self, path: str) -> str:
        parts = [p.capitalize() for p in re.sub(r'[^a-zA-Z0-9/]', '', path).replace('/api/', '').split('/') if p]
        return "".join(parts) + "Request"

    def generate(self, manifest_path: Path, output_path: Optional[Path] = None):
        if not manifest_path.exists():
            logger.error(f"Manifest not found: {manifest_path}")
            return

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        # 1. Détection multi-archetype
        archetypes = self._detect_top2(manifest)
        if not archetypes:
            logger.warning("No archetype detected — using generic scaffold")
            archetypes = [{"archetype_id": "generic", "label": "Generic", "suggested_endpoints": [], "aetherflow_conventions": {}}]

        slug = manifest_path.stem.replace("manifest_", "")
        output_file = output_path or Path("/tmp") / f"router_{slug}.py"

        # 2. Merger les endpoints des archetypes détectés (dedup)
        all_endpoints: List[Tuple[str, Dict]] = []
        seen = set()
        for arch in archetypes:
            conventions = arch.get("aetherflow_conventions", {})
            for ep in arch.get("suggested_endpoints", []):
                resolved = self._apply_conventions(ep, slug, conventions)
                if resolved not in seen:
                    seen.add(resolved)
                    all_endpoints.append((resolved, arch))

        # 3. Générer le contenu Python
        arch_ids = " + ".join(a["archetype_id"] for a in archetypes)
        arch_labels = " + ".join(a["label"] for a in archetypes)

        content = [
            "#!/usr/bin/env python3",
            "# [auto-generated] AetherFlow API Generator — M91-A",
            f"# Archetypes: {arch_ids}",
            "from fastapi import APIRouter, HTTPException, Query",
            "from pydantic import BaseModel",
            "from typing import List, Optional, Dict, Any",
            "",
            f"router = APIRouter(prefix='/api/{slug}', tags=['{slug}'])",
            f"# {arch_labels}",
            "",
        ]

        # Pydantic models
        generated_models = set()
        for resolved, arch in all_endpoints:
            method, path = resolved.split(" ", 1)
            if method in ("POST", "PUT", "PATCH"):
                model = self._path_to_model(path)
                if model not in generated_models:
                    generated_models.add(model)
                    content.append(f"class {model}(BaseModel):")
                    if "chat" in path:
                        content += ["    message: str", "    history: Optional[List[Dict[str, Any]]] = None"]
                    elif "file" in path or "save" in path:
                        content += ["    path: str", "    content: str"]
                    else:
                        content += ["    payload: Dict[str, Any] = {}"]
                    content.append("")

        # Routes
        for resolved, arch in all_endpoints:
            method, path = resolved.split(" ", 1)
            rel = path.replace(f"/api/{slug}", "") or "/"
            handler = self._path_to_handler(method, path)
            content.append(f"@router.{method.lower()}('{rel}')")
            if method in ("POST", "PUT", "PATCH"):
                model = self._path_to_model(path)
                content.append(f"async def {handler}(body: {model}):")
            else:
                content.append(f"async def {handler}():")
            content.append(f"    \"\"\"[auto] {method} {path} — {arch['archetype_id']}\"\"\"")
            content.append("    raise HTTPException(status_code=501, detail='Not implemented')")
            content.append("")

        output_file.write_text("\n".join(content), encoding='utf-8')
        logger.info(f"✅ Router generated: {output_file}")

        # Rapport
        print(f"\n--- GENERATION REPORT : {slug} ---")
        print(f"Archetypes : {arch_ids}")
        print(f"Endpoints  : {len(all_endpoints)}")
        for ep, arch in all_endpoints:
            print(f"  {ep}  [{arch['archetype_id']}]")
        print("------------------------------------------\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AetherFlow API Generator — M91-A")
    parser.add_argument("--manifest", required=True, help="Path to manifest.json")
    parser.add_argument("--output", help="Output Python file path")
    args = parser.parse_args()

    gen = APIGenerator()
    gen.generate(Path(args.manifest), Path(args.output) if args.output else None)
