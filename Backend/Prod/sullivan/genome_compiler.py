"""
HOMEO_GENOME Compiler — Mission 189
Compile un HOMEO_GENOME.md unifié par projet à partir de :
- DESIGN.md (tokens)
- manifest.json (organes, intentions, wires)
- BRS sessions (pépites, arbitrage)

Aucun LLM — lecture + restructuration de données existantes uniquement.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class GenomeCompiler:
    """Compile HOMEO_GENOME.md pour un projet donné."""

    MAX_GENOME_SIZE_KB = 200
    MAX_BRS_PEPITES = 50

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.warnings: List[str] = []

    def compile(self) -> Dict[str, Any]:
        """Compile HOMEO_GENOME.md et retourne les métadonnées."""
        sections = {}
        sections_written = []

        # §1 Méta-Projet
        sections["§1"] = self._compile_meta()
        sections_written.append("§1 Méta-Projet")

        # §2 Design System
        sections["§2"] = self._compile_design_system()
        sections_written.append("§2 Design System (Tokens)")

        # §3 Intent Map
        sections["§3"] = self._compile_intent_map()
        sections_written.append("§3 Intent Map (Stitch)")

        # §4 UI Inventory
        sections["§4"] = self._compile_ui_inventory()
        sections_written.append("§4 UI Inventory (Organes)")

        # §5 Workflow BRS
        sections["§5"] = self._compile_brs_workflow()
        sections_written.append("§5 Workflow BRS")

        # §6 Wire Map
        sections["§6"] = self._compile_wire_map()
        sections_written.append("§6 Wire Map")

        # Assembler le document
        genome_md = self._assemble(sections)

        # Vérifier la taille
        size_kb = len(genome_md.encode('utf-8')) / 1024
        if size_kb > self.MAX_GENOME_SIZE_KB:
            self.warnings.append(f"HOMEO_GENOME.md dépasse {self.MAX_GENOME_SIZE_KB}Ko ({size_kb:.1f}Ko)")

        # Écrire le fichier
        genome_path = self.project_dir / "HOMEO_GENOME.md"
        genome_path.write_text(genome_md, encoding='utf-8')

        return {
            "path": str(genome_path),
            "sections_written": sections_written,
            "warnings": self.warnings,
            "size_kb": round(size_kb, 1)
        }

    def _compile_meta(self) -> str:
        """§1 Méta-Projet"""
        manifest = self._load_manifest()
        name = manifest.get("name", "Sans nom")
        archetype = manifest.get("archetype", "Non défini")
        version = manifest.get("version", "0.1.0")
        created = manifest.get("created_at", datetime.now().isoformat())

        return f"""## §1 Méta-Projet

| Clé | Valeur |
|---|---|
| Nom | {name} |
| Archétype | {archetype} |
| Version | {version} |
| Créé le | {created} |
| Dernière MAJ | {datetime.now().isoformat()} |
"""

    def _compile_design_system(self) -> str:
        """§2 Design System (Tokens)"""
        design_path = self.project_dir / "DESIGN.md"
        if not design_path.exists():
            self.warnings.append("DESIGN.md absent — §2 vide")
            return """## §2 Design System (Tokens)

> Aucune donnée disponible. Créez `DESIGN.md` dans le dossier projet.
"""

        content = design_path.read_text(encoding='utf-8')
        # Tronquer si trop long (max 4000 chars pour la section)
        if len(content) > 4000:
            content = content[:4000] + "\n\n> ... (tronqué, voir DESIGN.md complet)"
            self.warnings.append("DESIGN.md tronqué à 4000 chars dans §2")

        return f"""## §2 Design System (Tokens)

Source : `DESIGN.md`

{content}
"""

    def _compile_intent_map(self) -> str:
        """§3 Intent Map (Stitch)"""
        manifest = self._load_manifest()
        intents = manifest.get("stitch_intents", [])

        if not intents:
            # Fallback: chercher dans les screens
            screens = manifest.get("screens", [])
            for screen in screens:
                for corps in screen.get("corps", []):
                    for organe in corps.get("organes", []):
                        if organe.get("intention"):
                            intents.append({
                                "organe": organe.get("id", "?"),
                                "intention": organe.get("intention", ""),
                                "confiance": organe.get("confiance", 0.5)
                            })

        if not intents:
            self.warnings.append("Aucune intention Stitch trouvée — §3 vide")
            return """## §3 Intent Map (Stitch)

> Aucune donnée disponible. Importez un design.md Stitch ou définissez des intentions.
"""

        rows = "| organe | intention | confiance |\n|---|---|---|\n"
        for intent in intents[:50]:  # Max 50 intentions
            organe = intent.get("organe", "?")
            intention = intent.get("intention", "?")
            confiance = intent.get("confiance", 0.5)
            rows += f"| {organe} | {intention} | {confiance:.2f} |\n"

        return f"""## §3 Intent Map (Stitch)

{rows}
"""

    def _compile_ui_inventory(self) -> str:
        """§4 UI Inventory (Organes)"""
        manifest = self._load_manifest()
        screens = manifest.get("screens", [])

        if not screens:
            self.warnings.append("Aucun screen dans le manifest — §4 vide")
            return """## §4 UI Inventory (Organes)

> Aucune donnée disponible. Ajoutez des screens au manifest.
"""

        rows = "| id | sélecteur | type | screen |\n|---|---|---|---|\n"
        count = 0
        for screen in screens:
            screen_name = screen.get("name", screen.get("id", "?"))
            for corps in screen.get("corps", []):
                for organe in corps.get("organes", []):
                    rows += f"| {organe.get('id', '?')} | {organe.get('selector', '?')} | {organe.get('type', '?')} | {screen_name} |\n"
                    count += 1
                    if count > 200:
                        rows += "\n> ... (tronqué à 200 organes)\n"
                        break
                if count > 200:
                    break
            if count > 200:
                break

        if count == 0:
            return """## §4 UI Inventory (Organes)

> Aucune donnée disponible.
"""

        return f"""## §4 UI Inventory (Organes)

Total : {count} organes

{rows}
"""

    def _compile_brs_workflow(self) -> str:
        """§5 Workflow BRS"""
        # Chercher les sessions BRS
        brs_dir = Path(__file__).parent.parent.parent.parent / "exports" / "brs"
        if not brs_dir.exists():
            self.warnings.append("Dossier BRS absent — §5 vide")
            return """## §5 Workflow BRS

> Aucune donnée disponible.
"""

        # Chercher la session active ou la plus récente
        sessions = sorted(brs_dir.glob("CAD-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not sessions:
            return """## §5 Workflow BRS

> Aucune session BRS trouvée.
"""

        latest = sessions[0]
        try:
            data = json.loads(latest.read_text(encoding='utf-8'))
        except:
            return """## §5 Workflow BRS

> Erreur de lecture de la session BRS.
"""

        pepites = data.get("pepites", [])
        arbitrage = data.get("arbitrage", "Non défini")
        session_id = data.get("session_id", latest.stem)

        # Tronquer les pépites
        if len(pepites) > self.MAX_BRS_PEPITES:
            pepites = pepites[:self.MAX_BRS_PEPITES]
            self.warnings.append(f"BRS pépites tronquées à {self.MAX_BRS_PEPITES}")

        rows = "| # | pépite | contexte |\n|---|---|---|\n"
        for i, pep in enumerate(pepites, 1):
            text = str(pep.get("text", ""))[:100]
            ctx = str(pep.get("context", ""))[:50]
            rows += f"| {i} | {text} | {ctx} |\n"

        return f"""## §5 Workflow BRS

Session : `{session_id}`
Arbitrage Sullivan : {arbitrage}

{rows}
"""

    def _compile_wire_map(self) -> str:
        """§6 Wire Map"""
        manifest = self._load_manifest()
        wires = manifest.get("wires", [])

        if not wires:
            return """## §6 Wire Map

> Aucune donnée disponible. Forgez des wires via le mode Wire.
"""

        rows = "| id | sélecteur | data-wire | intention forgée |\n|---|---|---|---|\n"
        for wire in wires[:100]:  # Max 100 wires
            w_id = wire.get("id", "?")
            selector = wire.get("selector", "?")
            data_wire = wire.get("data_wire", "?")
            intention = wire.get("intention", "?")
            rows += f"| {w_id} | {selector} | {data_wire} | {intention} |\n"

        return f"""## §6 Wire Map

{rows}
"""

    def _load_manifest(self) -> Dict[str, Any]:
        """Charge le manifest.json du projet."""
        manifest_path = self.project_dir / "manifest.json"
        if manifest_path.exists():
            try:
                return json.loads(manifest_path.read_text(encoding='utf-8'))
            except:
                pass
        return {}

    def _assemble(self, sections: Dict[str, str]) -> str:
        """Assemble les sections en un document Markdown."""
        manifest = self._load_manifest()
        project_name = manifest.get("name", "Projet sans nom")

        header = f"""# HOMEO_GENOME — {project_name}

> Généré automatiquement le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> Ce fichier est la source de vérité unifiée du projet.
> Ne pas éditer manuellement — utiliser le compiler via `POST /api/projects/{{id}}/genome-compile`.

"""
        body = "\n".join(sections.values())
        return header + body
