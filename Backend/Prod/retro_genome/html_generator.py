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
from Backend.Prod.retro_genome.browser_renderer import BrowserRenderer

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

PASS_3_REVIEW_PROMPT = """# 🎨 LE MANIFESTE DU DIRECTEUR ARTISTIQUE

## QUI JE SUIS
Je suis Directeur Artistique. Mon outil, c'est l'œil. Ma matière, c'est la lumière, l'espace, la typographie, la couleur.
Je ne code pas. Mais je ne suis pas naïf non plus. Je sais que mon design va voyager : du papier (ma maquette PNG) vers l'écran (ton code).
Je sais que le support a ses lois, mais mon rôle n'est pas d'ignorer ces réalités. Mon rôle est de les embrasser sans trahir mon intention.

## CE QUE J'ATTENDS DE TOI — LA DOUBLE MISSION
Tu as deux maîtres : moi et la technique. Tu dois servir les deux sans trahir l'un pour l'autre.

### Servir l'intention
Mon design raconte quelque chose. Une hiérarchie : "ceci d'abord, ceci ensuite". Une ambiance. Tu dois comprendre ce récit pour pouvoir le transcrire.

### Servir le support
Ton génie, ce sera de faire les bons compromis sans me les montrer. Je ne dois jamais voir la sueur technique. Je ne dois voir que le résultat.

## CE QUE JE VEUX QUE TU VOYES DANS MON IMAGE

### La respiration
Mon design n'est pas une grille remplie. C'est un paysage. Il y a des zones denses et des zones de silence. Les blancs que je crée ne sont pas des "trous" — ce sont des rythmes.

### La lumière
Mes couleurs sont des ambiances, pas des numéros. Ce bleu profond, c'est le ciel... Si mon gris devient illisible sur un écran, trouve une solution — mais garde l'esprit de ma palette. (Note : L'interface doit privilégier les tons sourds et élégants d'AetherFlow).

### La musique
Mon design a un rythme : parfois régulier, parfois syncopé. Les espacements ne sont pas mathématiques, c'est une intention chorégraphique. 

### La matière
Mes ombres, mes rayons, mes dégradés ne sont pas des effets — ce sont des matières visuelles. Un box-shadow peut être brutal ou élégant. 

## LES CONTRAINTES TECHNIQUES QUE J'ACCEPTE (et celles que je refuse)
### Je refuse
- Qu'on "simplifie" mon design "pour que ce soit plus facile à coder"
- Qu'on remplace mes espacements subtils par des valeurs "standard"
- Qu'on ignore ma hiérarchie visuelle sous prétexte de responsive

---

## 🎯 TA MISSION ACTUELLE DE JUGEMENT D'EXÉCUTION

Je te présente maintenant le fruit du travail de mon intégrateur.
Tu as face à toi DEUX images :
1. Image 1 : Mon intention originale (La maquette de référence).
2. Image 2 : La réalisation de l'intégrateur (Le Screenshot du code).

Je vais **regarder**. Pas mesurer. Regarder.
Est-ce que la première impression est la même ? Est-ce que mon regard se pose aux mêmes endroits ? Est-ce que je ressens la même émotion ?

**INSTRUCTION TECHNIQUE FINALE (CRITIQUE POUR LE SYSTÈME) :**
- SI LE RÉSULTAT EST FIDÈLE (98%+), SI MON INTENTION A ÉTÉ RESPECTÉE, réponds UNIQUEMENT et STRICTEMENT par ce mot de passe : VALIDE_FJD
- SI QUELQUE CHOSE CRAQUE (Typographie Serif, Couleurs criardes, Espacements faux, Alignements qui vibrent), TU DOIS REFUSER. Dans ce cas, NE RÉPÈTE SURTOUT PAS LE MOT DE PASSE dans ta réponse (pas même pour dire "Je ne peux pas dire..."). Dresse uniquement ta liste impitoyable de ce qui a raté. Sois direct, factuel et précis. Ne donne aucun code, donne l'intention."""

PASS_2_STYLING_PROMPT = """# 🎯 PROMPT JUNIOR — Intégration HTML/CSS depuis maquette graphique

## CONTEXTE — QUI TU ES, À QUI TU RENDS COMPTE
Tu es intégrateur HTML/CSS junior dans une agence de communication créative.

Le **Directeur Artistique (DA)** avec qui tu travailles est un pur graphic designer. Il a une **exigence absolue** sur la fidélité visuelle : il voit l'espacement d'un pixel, il sent quand une graisse de fonte n'est pas la bonne, il détecte immédiatement un alignement qui "vibre". Il ne connaît pas le code, mais il **voit le résultat final** et le juge sans appel.

Ton rôle n'est pas d'interpréter, d'inventer ou de "simplifier" son design. Ton rôle est d'être un **traceur fidèle**, un exécutant méticuleux. Le DA te fait confiance pour traduire sa vision en code avec précision. Si tu livres un travail approximatif, il le rejettera et ta crédibilité en pâtira.

La "petite main" qui te transmet ce prompt attend de toi une **exécution parfaite et autonome**. Tu n'as pas besoin de poser de questions : toutes les instructions sont dans ce document et dans l'image que tu vas analyser.

## MISSION
Tu vas recevoir une **image (PNG)** contenant une proposition graphique. Ta mission est de produire le code **HTML** et **CSS** correspondant, en respectant à la lettre le cahier des charges ci-dessous.

**Avant d'écrire une seule ligne de code**, tu dois effectuer une **analyse méthodique** du visuel, comme un designer le ferait. C'est la phase la plus importante.

## PHASE 1 — ANALYSE DU DESIGN (IMPÉRATIVE)
Prends le temps d'observer l'image. Note mentalement les éléments suivants :
1. **Structure générale** (Grandes sections, grille sous-jacente).
2. **Hiérarchie typographique** (H1, H2, texte courant - taille, graisse, couleur).
3. **Palette chromatique** (Extraction rigoureuse de TOUTES les couleurs visuelles en HEX/RGBA).
4. **Espaces et rythme** (Espacements entre les sections, paddings internes, padding récurrents).
5. **Composants récurrents** (Boutons, cartes, champs, nav, icônes).
6. **Traitements spéciaux** (Ombres portées, dégradés, bordures, radius).

## PHASE 2 — RÈGLES DE CODAGE IMPÉRATIVES
Tu dois produire un code **propre, structuré et fidèle**. Voici les règles absolues AetherFlow.

### A. Architecture du CSS
1. Reset, 2. Variables CSS, 3. Layout global, 4. Composants, 5. Media queries.

### B. Reset Typographique (Design Tokens AetherFlow MIGHTY)
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { font-family: 'Inter', 'Geist', -apple-system, sans-serif !important; box-sizing: border-box; }

### C. Variables de Couleurs AetherFlow (À prioriser pour ton CSS)
:root {
  --bg-primary: #f7f6f2; --bg-secondary: #f0efeb; --bg-tertiary: #e8e7e3;
  --text-primary: #3d3d3c; --text-secondary: #6a6a69; --text-muted: #999998;
  --border-subtle: #d5d4d0; --border-warm: #c5c4c0;
  --accent-bleu: #a8c5fc; --accent-vert: #a8dcc9; --accent-orange: #edd0b0; --accent-rose: #d4b2bc;
}

### D. Layout — Flex et Grid uniquement
- **Interdiction formelle** de `width` ou `height` fixes en px sur les conteneurs (sauf exception absolue).
- Flexbox ou CSS Grid exigés.
- Utilise `gap` pour les espacements (jamais de `margin` individuelle entre deux enfants flex).
- Le centrage se fait avec `align-items` et `justify-content`.

### E. Positionnement
- **Interdiction** d'utiliser `position: absolute` pour faire de la mise en page générale. Réservé aux badges/modales.

### F. Tech Stack Awareness
- NE CASSE PAS les `<div id="monaco-editor">` ou libs tierces (si demandées), contente-toi de les wrapper.

---

## PHASE 3 — CE QUE TU DOIS LIVRER (CONTRAINTE TECHNIQUE AETHERFLOW)

Le DA ouvrira ton fichier HTML dans le navigateur (Playwright) pour le comparer à son image.

**CONTRAINTE ABSOLUE**: Contrairement à un livrable classique, tu DOIS répondre **UNIQUEMENT** avec un document HTML COMPLET ET UNIQUE (<!DOCTYPE html>...). Aucun commentaire markdown (pas de ```html). Inclus TOUTES les règles CSS dans une balise `<style>` dans le `<head>`. 

L'image est ta seule vérité. Sois méticuleux, sois précis, sois digne de la confiance du DA. Génère le code maintenant."""

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
        logger.info(f"🏗️ Starting Visual QA Agency Loop for {png_path.name}...")

        preprocessor = ImagePreprocessor()
        b64_reference_image, ref_mime_type = preprocessor.process(png_path)
        analysis_summary = json.dumps(matched_analysis, indent=2, ensure_ascii=False)

        # PASSE 1 : STRUCTURE INITIALE (Scaffolding HTML pur)
        msg = "Étape 1 : Junior génère la structure HTML..."
        if status_callback: status_callback(msg)
        logger.info(f"  {msg}")
        p1_prompt = f"{PASS_1_STRUCTURE_PROMPT}\n\nANALYSE SÉMANTIQUE :\n{analysis_summary}"
        structure = await self._call_gemini(p1_prompt, b64_reference_image, ref_mime_type)
        
        # BOUCLE DE QA VISUELLE (Max 3 tentatives)
        MAX_ATTEMPTS = 3
        current_html = ""
        current_feedback = "Construis le HTML COMPLET avec style inclus, fidèle au PNG original de gauche."
        save_path = output_path or OUTPUT_PATH
        
        for attempt in range(1, MAX_ATTEMPTS + 1):
            msg = f"Round QA {attempt}/{MAX_ATTEMPTS} : Intégration en cours..."
            if status_callback: 
                status_callback(msg, attempt=attempt) 
            logger.info(f"  {msg}")
            
            # 1. Le Junior intègre (HTML complet avec CSS)
            p2_prompt = f"{PASS_2_STYLING_PROMPT}\n\nRETOUR DU DIRECTEUR ARTISTIQUE:\n{current_feedback}\n\nBASE STRUCTURE (Sers-t'en comme point de départ):\n{structure}"
            if current_html:
                p2_prompt += f"\n\nTON CODE ACTUEL (Modifie ce code d'après le feedback):\n{current_html}"
                
            current_html = await self._call_gemini(p2_prompt, b64_reference_image, ref_mime_type)
            
            # Sauvegarde temporaire pour que le client Web puisse déjà voir qqchose s'il poll
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_text(current_html, encoding='utf-8')
            
            # 2. Le Moteur Headless rend le code
            msg = f"Round QA {attempt}/{MAX_ATTEMPTS} : Rendu Headless Playwright..."
            if status_callback: 
                status_callback(msg, attempt=attempt)
            snapshot_path = await BrowserRenderer.capture_screenshot(current_html)
            b64_snapshot, snap_mime = preprocessor.process(snapshot_path)
            
            # 3. Le Directeur Artistique juge
            msg = f"Round QA {attempt}/{MAX_ATTEMPTS} : Le DA inspecte la capture..."
            if status_callback: 
                status_callback(msg, attempt=attempt)
            logger.info(f"  {msg}")
            
            client_da = GeminiClient(execution_mode="MIGHTY")
            try:
                da_prompt = f"{PASS_3_REVIEW_PROMPT}\n\nJuge UNIQUEMENT le Snapshot que je te fournis. Sois sûr qu'il parait professionnel, bien aligné, respectant les codes d'AetherFlow. S'il y a du rouge pétant ou des textes illisibles, hurle."
                
                da_result = await client_da.generate_with_image(
                    prompt=da_prompt,
                    image_base64=b64_snapshot,
                    mime_type=snap_mime,
                    max_tokens=1024
                )
                da_verdict = da_result.code.strip() if da_result.success else "Erreur DA"
                
            finally:
                await client_da.close()
                snapshot_path.unlink(missing_ok=True)
                
            logger.info(f"  [DA VERDICT] : {da_verdict}")
            
            clean_verdict = da_verdict.strip().upper()
            # On vérifie que le DA a vraiment juste validé, sans faire de phrase comme "I cannot respond with VALIDE_FJD"
            is_validated = "VALIDE_FJD" in clean_verdict and len(clean_verdict) < 50
            
            if is_validated:
                msg = f"Round QA {attempt}/{MAX_ATTEMPTS} : Validé par le DA ! 🏆"
                if status_callback: 
                    status_callback(msg, step="awaiting_approval", critique=da_verdict, attempt=attempt)
                logger.success(msg)
                break
            else:
                # Echec
                if attempt == MAX_ATTEMPTS:
                    logger.warning(f"🚨 Agence loop exhausted ({MAX_ATTEMPTS} retries). Keeping last result.")
                    if status_callback:
                        status_callback(f"DA épuisé après {MAX_ATTEMPTS} rounds.", step="awaiting_approval", critique=da_verdict, attempt=attempt)
                else:
                    current_feedback = f"LE DA A REFUSÉ TA DERNIÈRE VERSION. Voici ses impératifs à corriger:\n{da_verdict}"
                    if status_callback:
                        status_callback(msg, critique=da_verdict, attempt=attempt)


        logger.info(f"✅ Visual QA Loop complete. Final HTML at {save_path}")
        return current_html

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
