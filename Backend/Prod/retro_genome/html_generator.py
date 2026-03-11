"""
HtmlGenerator — Retro-Genome Pipeline (Mission 35)
Génère du HTML/CSS sémantique à partir du PNG original et du JSON validé par l'utilisateur.
Utilise UN SEUL PNG de référence (pour économiser les tokens) + le JSON du SemanticMatcher.
"""
import json
import re
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
from loguru import logger
from dotenv import load_dotenv

# Backend imports
from Backend.Prod.models.gemini_client import GeminiClient
from Backend.Prod.retro_genome.analyzer import ImagePreprocessor, extract_json_robust

project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / "Backend/.env")

# --- PROMPTS MULTI-PASS ---

PASS_1_STRUCTURE_PROMPT = """Tu es un Architecte Frontend et Ingénieur Full-Stack. 
Ta mission : Analyser l'IMAGE et le JSON d'analyse pour générer la STRUCTURE HTML5 (et le script d'initialisation si nécessaire).

RÈGLES DE BASE :
- Utilise des balises sémantiques (<header>, <nav>, <main>, <section>, <article>, <footer>).
- Crée une hiérarchie de <div> cohérente avec la disposition visuelle.
- Assigne des noms de classes descriptifs (ex: .hero-section, .nav-item, .card-gallery).
- NE GÉNÈRE AUCUN CSS ICI.
- Intègre les corrections des GAPS identifiés dans l'audit du JSON.

TECH STACK AWARENESS (CRITIQUE) :
- Vérifie si le JSON d'analyse contient un champ "manifesto" stipulant des solutions techniques (ex: Roo Code, Monaco Editor, API VScode-like, iframe Jet Bridge...).
- Si OUI, ne génère pas de simples `<textarea>` ou structures passives. Implémente DIRECTEMENT les containers appropriés (ex: `<div id="monaco-editor">`) et le tag `<script>` d'initialisation via CDN (le wiring JS de base pour instancier l'outil). Anticipe le branchement technique.

CONTRAINTE : Réponds UNIQUEMENT avec le code HTML (incluant les balises scripts si justifiées par le manifeste), sans les balises <html>, <head> ni <body>."""

PASS_2_STYLING_PROMPT = """Contexte : Tu es un intégrateur HTML/CSS de luxe, expert en reproduction pixel-perfect.
Ta mission : Générer le CSS complet pour styliser la STRUCTURE HTML fournie afin qu'elle corresponde EXACTEMENT à la disposition, aux couleurs, aux bordures, et aux proportions de l'IMAGE. Prends tout le soin nécessaire pour produire un design de très haut niveau, élégant et soigné.

CONTRAINTES STYLISTIQUES IMPÉRATIVES (RÈGLES DE L'AGENCE) :
1. Reset Strict : *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
2. Flexbox est la reine pour les alignements 1D. Grid pour les grilles complexes 2D.
3. ESPACEMENT PAR GAP obligatoirement (pas de margins individuelles).
4. Responsive : Tailles fluides (%, fr, vw), max-width, min-width: 0. 
   - Media queries : Tablette (768px) et Mobile (480px) obligatoires.
5. Variables CSS : Utilise :root pour les couleurs (hex/rgba extrêmes du PNG), espacements et typo (clamp() pour fluidité).
6. Pas de tailles fixes en pixels sur les conteneurs.
7. Images/Icônes : img { max-width: 100%; height: auto; }. Utilise des emojis/Unicode pour les icônes simples.
8. TECH STACK AWARENESS : Si la structure HTML contient des classes/id liés à une librairie injectée (ex: #monaco-editor), NE CASSE PAS leur styling interne. Contente-toi de dimensionner le conteneur parent.

CONTRAINTE : Réponds UNIQUEMENT avec le bloc <style>...</style> complet."""

PASS_3_REVIEW_PROMPT = """Tu es le Directeur Artistique. 
Ta mission : Comparer le RENDU ACTUEL (HTML+CSS) avec l'IMAGE originale et corriger les erreurs de fidélité.

RÈGLE D'OR - COHÉRENCE STRUCTURELLE :
- Tu ne dois SOUS AUCUN PRÉTEXTE renommer les classes HTML existantes (ex: si le HTML a <div class="app-main">, n'écris pas .main_content dans le CSS).
- Maintiens la stricte liaison entre le bloc <style> et le bloc <body>.
- Contente-toi d'affiner les PRIX CSS (couleurs, grid-templates, gap, dimensions, typos) ou d'ajouter de légères divs de wrapper SI VRAIMENT NÉCESSAIRE.

ANALYSE :
- Vérifie les alignements, les couleurs exactes, les espacements, les arrondis (border-radius) et les ombres.
- Identifie ce qui "cloche" visuellement.

RETOUR :
- Applique les corrections nécessaires au code existant pour atteindre la perfection visuelle de l'image.

CONTRAINTE ABSOLUE : Réponds UNIQUEMENT avec le document HTML COMPLET définitif (DOCTYPE, head avec son bloc style, body). Aucun commentaire ou texte explicatif."""

OUTPUT_PATH = Path(__file__).parent.parent.parent.parent / "exports" / "retro_genome" / "reality.html"

from Backend.Prod.models.gemini_client import GeminiClient

class HtmlGenerator:
    def __init__(self):
        # On utilise une session persistante si possible ou on recrée pour chaque passe
        self.client = None

    async def _call_gemini(self, prompt: str, image_b64: Optional[str] = None, mime_type: Optional[str] = None) -> str:
        client = GeminiClient(execution_mode="FAST")
        try:
            if image_b64:
                result = await client.generate_with_image(
                    prompt=prompt,
                    image_base64=image_b64,
                    mime_type=mime_type,
                    output_constraint="Code only",
                    max_tokens=4096
                )
            else:
                result = await client.generate(
                    prompt=prompt,
                    output_constraint="Code only",
                    max_tokens=4096
                )
            
            if not result.success:
                raise ValueError(result.error)
            
            # Nettoyage des markdown fences et des balises <think> (Gemini 3.1 Pro Preview)
            content = result.code.strip()
            if '<think>' in content:
                content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
            
            # 1. Chercher en priorité un bloc markdown ```...```
            code_block = re.search(r'```(?:[a-z]*)\s*([\s\S]*?)\s*```', content)
            if code_block:
                return code_block.group(1).strip()

            # 2. Si pas de block markdown, on nettoie les fences orphelines
            content = re.sub(r'^```[a-z]*\s*', '', content, flags=re.MULTILINE)
            content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
            content = content.strip()
            
            # 3. Sécurité finale pour éliminer toute prose s'il n'y a pas eu de backticks:
            # On prend strictement du premier '<' au dernier '>'
            first = content.find('<')
            last = content.rfind('>')
            if first != -1 and last != -1 and last > first:
                return content[first:last+1].strip()

            return content
        finally:
            await client.close()

    async def generate(self, png_path: Path, matched_analysis: Dict, output_path: Optional[Path] = None, status_callback: Optional[callable] = None) -> str:
        logger.info(f"🏗️ Starting Multi-pass HTML Generation for {png_path.name}...")

        preprocessor = ImagePreprocessor()
        b64_image, mime_type = preprocessor.process(png_path)
        analysis_summary = json.dumps(matched_analysis, indent=2, ensure_ascii=False)

        # PASSE 1 : STRUCTURE
        msg = "Passe 1/3 : Analyse de la structure HTML sémantique..."
        if status_callback: status_callback(msg)
        logger.info(f"  {msg}")
        p1_prompt = f"{PASS_1_STRUCTURE_PROMPT}\n\nANALYSE SÉMANTIQUE :\n{analysis_summary}"
        structure = await self._call_gemini(p1_prompt, b64_image, mime_type)
        
        # PASSE 2 : STYLING
        msg = "Passe 2/3 : Génération du styling CSS (Pixel-Perfect)..."
        if status_callback: status_callback(msg)
        logger.info(f"  {msg}")
        p2_prompt = f"{PASS_2_STYLING_PROMPT}\n\nSTRUCTURE HTML À STYLISER :\n{structure}"
        styling = await self._call_gemini(p2_prompt, b64_image, mime_type)

        # PASSE 3 : REVIEW & POLISH
        msg = "Passe 3/3 : Revue de fidélité visuelle et finitions..."
        if status_callback: status_callback(msg)
        logger.info(f"  {msg}")
        current_code = f"<!DOCTYPE html><html><head><meta charset='UTF-8'>{styling}</head><body>{structure}</body></html>"
        p3_prompt = f"{PASS_3_REVIEW_PROMPT}\n\nCODE ACTUEL :\n{current_code}"
        final_html = await self._call_gemini(p3_prompt, b64_image, mime_type)

        # Sauvegarde
        save_path = output_path or OUTPUT_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(final_html, encoding='utf-8')
        logger.info(f"✅ Multi-pass generation complete. Saved to {save_path}")

        return final_html

    async def refine(self, current_html: str, feedback: str, png_path: Optional[Path] = None, output_path: Optional[Path] = None) -> str:
        """
        Mission 36 : Mode Conversationnel (Sullivan Refine).
        Prend le code courant, le feedback de l'utilisateur et amende le code en conservant la structure.
        """
        logger.info("🗣️ User prompted Sullivan to refine the HTML...")
        
        PASS_4_REFINE_PROMPT = f"""Tu es Sullivan, le Mentor technique de la Reality View.
L'utilisateur te demande de modifier le CODE HTML/CSS existant suite à une revue visuelle.

RÈGLES D'INTERVENTION CHIRURGICALE :
1. Tu ne dois PAS tout réécrire depuis zéro. Conserve la hiérarchie existante.
2. Modifie le composant visé PAR la demande de l'utilisateur (le feedback).
3. Continue de respecter les contraintes AetherFlow impératives : Flexbox, Grid, Gap, Clamp, pas de width absolue.
4. Si la demande concerne une couleur, intègre la modification proprement dans le <style> (ex: dans les variables :root ou sur la classe cible).

FEEDBACK UTILISATEUR :
"{feedback}"

CONTRAINTE ABSOLUE : Réponds UNIQUEMENT avec le document HTML COMPLET mis à jour (<!DOCTYPE html>...). Aucun texte, aucun Markdown."""

        b64_image = None
        mime_type = None
        if png_path and png_path.exists():
            from Backend.Prod.retro_genome.analyzer import ImagePreprocessor
            preprocessor = ImagePreprocessor()
            b64_image, mime_type = preprocessor.process(png_path)
            
        p4_prompt = f"{PASS_4_REFINE_PROMPT}\n\nCODE ACTUEL :\n{current_html}"
        
        refined_html = await self._call_gemini(p4_prompt, b64_image, mime_type)
        
        # Sauvegarde
        save_path = output_path or OUTPUT_PATH
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(refined_html, encoding='utf-8')
        logger.info(f"✅ HTML refined by Sullivan. Saved to {save_path}")
        
        return refined_html
