import json
import re
from pathlib import Path
from typing import Dict, List, Optional

class StitchPromptBuilder:
    """Compile un brief Stitch depuis manifest + DESIGN.md + BRS."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def build(self, screen_intent: str) -> str:
        """Construit le prompt final structuré."""
        manifest = self._load_manifest()
        design_context = self._build_design_context()
        structure = self._build_structure(manifest)
        intentions = self._build_intentions(manifest)
        pepites = self._build_pepites()

        prompt = f"""DESIGN BRIEF FOR GOOGLE STITCH

CORE INTENT:
{screen_intent}

DESIGN CONTEXT & TOKENS:
{design_context}

EXISTING STRUCTURE (FOR CONSISTENCY):
{structure}

COMPONENT INTENTIONS:
{intentions}

USER INSIGHTS (BRS):
{pepites}

INSTRUCTIONS:
- Always use lowercase for UI labels (HoméOS style).
- Respect the design tokens strictly.
- Create a clean, Hard-Edge layout.
- No rounded corners unless specified in §Shape.
"""
        return prompt

    def _load_manifest(self) -> Dict:
        path = self.project_dir / "manifest.json"
        if path.exists():
            try: return json.loads(path.read_text('utf-8'))
            except: return {}
        return {}

    def _build_design_context(self) -> str:
        """Extrait les tokens du DESIGN.md."""
        path = self.project_dir / "DESIGN.md"
        if not path.exists():
            return "- No DESIGN.md found. Use standard HoméOS neutrals (#f7f6f2, #3d3d3c, #8cc63f)."
        
        content = path.read_text('utf-8')
        # Extraire uniquement §Colors + §Typography (les plus utiles pour la génération)
        sections = []
        for section in ['## Colors', '## Typography', '## Shape']:
            # Search for the section and take content until next ## or end of file
            match = re.search(rf'{re.escape(section)}\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
            if match:
                # Garder uniquement les lignes avec des tokens (lignes avec | ou `)
                lines = [l for l in match.group(1).split('\n') if '|' in l or '`' in l or ':' in l]
                sections.append(f"{section}\n" + '\n'.join(lines[:12]))  # max 12 lignes par section
        
        return '\n\n'.join(sections) if sections else "- Voir DESIGN.md"

    def _build_structure(self, manifest: Dict) -> str:
        """Construit la hiérarchie corps → organes."""
        screens = manifest.get("screens", [])
        if not screens:
            return "- (aucune structure définie — screen généré librement)"
        
        lines = []
        for screen in screens[:3]:  # Max 3 screens
            screen_name = screen.get("name", screen.get("id", "screen"))
            lines.append(f"Screen: {screen_name}")
            for corps in screen.get("corps", [])[:8]:  # Max 8 corps
                corps_id = corps.get("id", "corps")
                lines.append(f"  [{corps_id}]")
                for organe in corps.get("organes", [])[:6]:  # Max 6 organes par corps
                    o_id = organe.get("id", "organe")
                    o_type = organe.get("type", "element")
                    lines.append(f"    - {o_id} ({o_type})")
        
        return '\n'.join(lines) if lines else "- (aucune structure)"

    def _build_intentions(self, manifest: Dict) -> str:
        """Construit la liste intentions depuis stitch_intents ou organes."""
        intents = manifest.get("stitch_intents", [])
        
        if not intents:
            # Fallback: extraire depuis corps/organes
            for screen in manifest.get("screens", []):
                for corps in screen.get("corps", []):
                    for organe in corps.get("organes", []):
                        if organe.get("intention"):
                            intents.append({
                                "organe": organe.get("id", "?"),
                                "intention": organe.get("intention", "")
                            })
        
        if not intents:
            return "- (aucune intention définie)"
        
        return '\n'.join([f"- {i.get('organe', '?')}: {i.get('intention', '?')}" 
                          for i in intents[:30]])  # Max 30 intentions

    def _build_pepites(self) -> str:
        """Extrait les 5 meilleures pépites BRS."""
        # Find project root relative to this file
        # PROJECTS_DIR is ROOT_DIR / "projects"
        # project_dir is PROJECTS_DIR / id
        # exports/brs is ROOT_DIR / "exports/brs"
        brs_dir = self.project_dir.parent.parent / "exports" / "brs"
        if not brs_dir.exists():
            return "- (aucune session BRS)"
        
        sessions = sorted(brs_dir.glob("CAD-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not sessions:
            return "- (aucune session BRS)"
        
        try:
            data = json.loads(sessions[0].read_text('utf-8'))
            pepites = data.get("pepites", [])[:5]
            if not pepites:
                return "- (aucune pépite BRS)"
            return '\n'.join([f"- {p.get('text', '')}" for p in pepites])
        except:
            return "- (erreur lecture BRS)"
