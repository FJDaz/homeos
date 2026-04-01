"""
React to Tailwind Direct — Mission 119 (AetherFlow)

Convertit le code source React (TSX/JSX) d'une archive ZIP en HTML5+Tailwind sémantique.
Priorise l'éditabilité (Intent-to-Code) sur la fidélité brute du build exporté.
"""
import re
import json
import zipfile
import io
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

class ReactToTailwindConverter:
    def __init__(self):
        self._client = None
        self._default_tokens = {
            "colors": {"primary": "#8cc63f", "neutral": "#ffffff", "text": "#3d3d3c"},
            "typography": {"body": "Geist Sans"},
            "shape": {"border_radius": "6px"}
        }

    @property
    def client(self):
        if self._client is None:
            from Backend.Prod.models.gemini_client import GeminiClient
            self._client = GeminiClient(execution_mode="BUILD")
        return self._client

    def _load_project_tokens(self) -> dict:
        try:
            from bkd_service import get_active_project_path
            token_path = get_active_project_path() / "exports" / "design_tokens.json"
            if token_path.exists():
                return json.loads(token_path.read_text())
        except Exception as e:
            logger.warning(f"[ReactToTailwind] Failed to load tokens: {e}")
        return self._default_tokens

    def _clean_jsx(self, code: str) -> str:
        """Nettoyage agressif pour réduire le bruit (tokens) et faciliter la traduction."""
        # Supprimer les imports
        code = re.sub(r'^import\s+[\s\S]*?;', '', code, flags=re.MULTILINE)
        # Supprimer les types TypeScript (interfaces, types)
        code = re.sub(r'interface\b[\s\S]*?\}', '', code)
        code = re.sub(r'type\b[\s\S]*?=', '', code)
        # Supprimer les annotations de type (ex: :string, :any)
        code = re.sub(r':\s*[A-Z][a-zA-Z<>\[\]]+', '', code)
        # Supprimer les hooks (simplification)
        code = re.sub(r'const\s+\[.*?,.*?\]\s*=\s*useState\([\s\S]*?\);?', '', code)
        code = re.sub(r'useEffect\(\(\)\s*=>\s*\{[\s\S]*?\}\s*,\s*\[.*?\]\);?', '', code)
        # Supprimer les commentaires
        code = re.sub(r'/\*\*[\s\S]*?\*/', '', code)
        code = re.sub(r'//.*', '', code)
        return code.strip()

    async def convert(self, zip_path: Path, import_name: str) -> str:
        logger.info(f"[ReactToTailwind] Extracting source from '{import_name}'...")
        
        source_code = ""
        files_found = []
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            file_list = z.namelist()
            # 1. Identifier App.tsx, App.jsx ou index.tsx (entry points)
            entry_points = [f for f in file_list if f.endswith(('App.tsx', 'App.jsx', 'page.tsx', 'index.tsx')) and not f.startswith('__MACOSX')]
            
            if not entry_points:
                # Fallback : prendre le plus gros .tsx/.jsx
                source_files = [f for f in file_list if f.endswith(('.tsx', '.jsx')) and not f.startswith('__MACOSX')]
                if not source_files:
                    raise Exception("Aucun code source React (.tsx, .jsx) trouvé dans l'archive.")
                entry_points = sorted(source_files, key=lambda f: z.getinfo(f).file_size, reverse=True)[:1]

            # 2. Lire et nettoyer le code
            for entry in entry_points:
                code = z.read(entry).decode('utf-8', errors='replace')
                clean = self._clean_jsx(code)
                source_code += f"// FILE: {entry}\n{clean}\n\n"
                files_found.append(entry)

        # 3. Limitation de taille (tokens approximatifs)
        if len(source_code) > 25000:
            source_code = source_code[:25000] + "\n... [TRUNCATED]"

        # 4. Chargement des tokens
        tokens = self._load_project_tokens()

        # 5. Prompt LLM
        prompt = f"""Tu es un Expert Intégrateur Frontend AetherFlow (Sullivan AI).
MISSION : Traduis ce code source React (JSX/TSX) en un document HTML5 complet utilisant Tailwind CSS.

NOM DE L'IMPORT : {import_name}
COMPOSANTS DÉTECTÉS : {", ".join(files_found)}

CODE SOURCE (NETTOYÉ) :
{source_code}

TOKENS DE DESIGN (DÉDUITS DU PROJET) :
- Background : `{tokens['colors']['neutral']}`
- Texte : `{tokens['colors']['text']}`
- Primaire / Accent : `{tokens['colors']['primary']}`
- Typographie : {tokens['typography']['body']}
- Border-radius : {tokens['shape'].get('border_radius', '20px')}

CONSIGNES DE TRADUCTION :
1. Produis un fichier HTML5 AUTONOME (<!DOCTYPE html>).
2. Utilise UNIQUEMENT Tailwind CSS via CDN (https://cdn.tailwindcss.com).
3. TRADUCTION DE L'INTENTION : Ne cherche pas à simuler une application React. Transforme les composants, les boucles (.map) et les conditions en structures HTML/Tailwind statiques fidèles au design.
4. SÉMANTIQUE : Utilise les balises <header>, <main>, <section>, <nav>.
5. TYPOGRAPHIE : Injecte Google Fonts pour {tokens['typography']['body']}.
6. CLASSES EXISTANTES : Si le code source utilise déjà des classes Tailwind (className="..."), GARDE-LES PRÉCISÉMENT.

Réponds UNIQUEMENT avec le code HTML complet. Pas de prose, pas de markdown.
"""

        result = await self.client.generate(
            prompt=prompt,
            max_tokens=16000,
            temperature=0.1,
            output_constraint="No prose"
        )

        if not result.success:
            logger.error(f"[ReactToTailwind] LLM Error: {result.error}")
            raise RuntimeError(f"React to Tailwind conversion failed: {result.error}")

        code = result.code
        if "```html" in code:
            code = code.split("```html")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
            
        return code.strip()

