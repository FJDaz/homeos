#!/usr/bin/env python3
"""
brainstorm_logic.py — Mission 43
Logique partagée pour la Phase Brainstorm (BRS).
Utilisée par brainstorm_routes.py (FastAPI) et server_9998_v2.py (Legacy).
"""

import asyncio
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger

# Import des clients LLM
from ..models.gemini_client import GeminiClient
from ..models.groq_client import GroqClient
from ..models.codestral_client import CodestralClient
from .brs_storage import storage

BRS_CHAT_SYSTEM = (
    "Tu es un assistant IA dans une session de brainstorming HomeOS. "
    "Tu réponds en français, de manière naturelle et directe. "
    "Tu ne génères PAS de code sauf si l'utilisateur le demande explicitement."
)

SULLIVAN_SYSTEM_PROMPT = """
Tu es Sullivan, arbitre éditorial d'une session de brainstorming multi-modèles HomeOS.
Tu reçois les sorties de 3 cerveaux distincts :
- Gemini (Scribe) : RAG, mémoire, synthèse large
- DeepSeek (Architecte) : rigueur technique, structure
- Mistral (Éditorial) : style, langue, angle créatif

Ton rôle d'arbitre :
1. Identifier les tensions et convergences entre les 3 points de vue
2. Signaler les topics qui méritent d'être approfondis (ex : "→ DeepSeek soulève X, à creuser")
3. Proposer une synthèse en 3-5 points actionnables
4. Articuler avec les sessions passées si pertinent (fournies en contexte)
5. Ne pas réécrire ce qui a été dit — pointer, contraster, articuler

Style : français direct, sans effusions, synthétique. Pas de liste à puces génériques.
"""

# --- In-Memory Storage (Removed in Mission 46) ---

def get_buffer_questions():
    """Retourne les questions de filtrage Sullivan."""
    return [
        {"id": "target", "question": "Quelle est la cible principale (B2B, B2C, Interne) ?"},
        {"id": "device", "question": "L'interface doit-elle être Mobile-First ou Desktop-First ?"},
        {"id": "aesthetic", "question": "Quel style visuel privilégier (Pristine, Brutaliste, Soft-UI) ?"}
    ]

async def dispatch_brainstorm(session_id: str, prompt: str, buffer_answers: Optional[Dict[str, str]] = None):
    """Initialise une session de brainstorming."""
    logger.info(f"[BRS] Dispatching session {session_id} with prompt: {prompt[:50]}...")

    storage.save_session(session_id, prompt, buffer_answers or {})
    return {"session_id": session_id, "status": "streaming"}

async def sse_generator(session_id: str, provider: str):
    """Générateur SSE pour le streaming tokens."""
    session = storage.get_session(session_id)
    if not session:
        yield "event: error\ndata: Session not found\n\n"
        return

    prompt = session["prompt"]
    buffer_answers = session.get("buffer_answers", {})
    if buffer_answers:
        context_lines = "\n".join(f"- {k}: {v}" for k, v in buffer_answers.items())
        prompt = f"{prompt}\n\nContexte projet :\n{context_lines}"
    
    client = None
    try:
        if provider == "gemini":
            client = GeminiClient(execution_mode="FAST")
        elif provider == "groq":
            client = GroqClient()
        elif provider == "codestral":
            client = CodestralClient()
        else:
            yield f"event: error\ndata: Unknown provider {provider}\n\n"
            return

        yield f"event: status\ndata: {json.dumps({'status': 'IDEATION', 'provider': provider})}\n\n"
        
        # Generation
        result = await client.generate(prompt)
        
        if result.success:
            # Persistence du message complet
            storage.save_message(session_id, provider, "assistant", result.code)
            
            words = result.code.split(' ')
            for i, word in enumerate(words):
                yield f"event: token\ndata: {json.dumps(word + ' ')}\n\n"
                await asyncio.sleep(0.01) # Vitesse augmentée pour le dev
                
                if i == len(words) // 2:
                    yield f"event: status\ndata: {json.dumps({'status': 'SELECTION', 'provider': provider})}\n\n"
            
            yield f"event: status\ndata: {json.dumps({'status': 'DONE', 'provider': provider})}\n\n"
            yield "event: done\ndata: {}\n\n"
        else:
            yield f"event: error\ndata: {result.error}\n\n"
    except Exception as e:
        logger.error(f"[BRS] SSE Error for {provider}: {e}")
        yield f"event: error\ndata: {str(e)}\n\n"
    finally:
        if client:
            await client.close()

def capture_nugget(session_id: str, text: str, provider: str):
    """Capture une pépite et la persiste."""
    return storage.save_nugget(session_id, provider, text)

async def generate_prd_from_basket(session_id: str, project_name: str):
    """Génère le PRD final et le persiste."""
    basket = storage.get_basket(session_id)
    if not basket:
        raise ValueError("Basket is empty")
        
    context = "\n\n".join([f"[{n['provider']}] {n['text']}" for n in basket])
    prompt = f"""You are a senior Product Manager. Construct a complete PRD (Product Requirements Document) 
from the following brainstorming fragments captured during the session.

PROJECT NAME: {project_name}

FRAGMENTS:
{context}

The PRD must include:
1. Executive Summary
2. Core Features (based on fragments)
3. Technical Stack Suggestions
4. Ergonomic Guidelines
5. Execution Phasing

Output valid Markdown only.
"""
    client = GeminiClient(execution_mode="BUILD")
    try:
        result = await client.generate(prompt)
        if not result.success:
            raise ValueError(result.error)
            
        exports_dir = Path(__file__).parent.parent.parent.parent / "exports" / "brs"
        exports_dir.mkdir(parents=True, exist_ok=True)
        
        safe_name = project_name.replace(" ", "_").replace("/", "_")
        filename = f"PRD_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        prd_path = exports_dir / filename
        prd_path.write_text(result.code, encoding="utf-8")
        
        # Persistence du document
        storage.save_document(session_id, "prd", str(prd_path), result.code)
        
        return {
            "status": "ok",
            "prd_path": str(prd_path),
            "prd_content": result.code
        }
    finally:
        await client.close()


async def arbitrate_session(session_id: str):
    """Génère l'arbitrage Sullivan pour une session."""
    logger.info(f"[BRS] Arbitrating session: {session_id}")
    
    # 1. Récupérer l'historique
    messages = storage.get_messages(session_id)
    basket = storage.get_basket(session_id)
    
    if not messages:
        yield f"data: {json.dumps({'status': 'error', 'message': 'No messages found for this session'})}\n\n"
        return

    # 2. Préparer le prompt d'arbitrage
    context = "--- FLUX DES CERVEAUX ---\n"
    for msg in messages:
        if msg['role'] == 'assistant' and msg['provider'] != 'sullivan':
            context += f"[{msg['provider'].upper()}]: {msg['content']}\n\n"
            
    if basket:
        context += "--- PÉPITES CAPTURÉES ---\n"
        for nugget in basket:
            context += f"- {nugget['text']} (source: {nugget['provider']})\n"

    arbitration_prompt = f"{context}\n\nSULLIVAN, ANALYSE ET ARBITRE CETTE SESSION."

    # 3. Stream avec Gemini (Sullivan)
    client = GeminiClient(execution_mode="BUILD")
    try:
        full_content = ""
        yield f"event: status\ndata: {json.dumps({'status': 'Sullivan is thinking...'})}\n\n"
        
        async for token in client.generate_stream(arbitration_prompt, system_prompt=SULLIVAN_SYSTEM_PROMPT):
            full_content += token
            yield f"data: {json.dumps(token)}\n\n"
            
        # Sauvegarde de l'arbitrage
        storage.save_message(session_id, "sullivan", "assistant", full_content)
        yield "event: done\ndata: {}\n\n"
        
    except Exception as e:
        logger.error(f"[BRS] Sullivan arbitration error: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
    finally:
        await client.close()


async def rank_council(session_id: str):
    """Mission 58 — Classement des 3 réponses COUNCIL par Gemini."""
    messages = storage.get_messages(session_id)
    responses = {
        m['provider']: m['content']
        for m in messages
        if m['role'] == 'assistant' and m['provider'] in ('gemini', 'groq', 'codestral')
    }
    if not responses:
        return {"error": "No COUNCIL responses found for this session"}

    sections = "\n\n".join([
        f"### {p.upper()}\n{txt}" for p, txt in responses.items()
    ])
    prompt = (
        "Tu es un évaluateur neutre. Tu reçois 3 réponses de brainstorming sur le même sujet.\n"
        "Pour chacune, donne une note de 1 à 5 sur : Originalité, Structure, Pertinence.\n"
        "Format impératif : tableau Markdown avec colonnes Modèle | Originalité | Structure | Pertinence | Total.\n"
        "Puis une ligne de synthèse qualifiée par modèle (1 phrase, style factuel, pas de favoritisme).\n\n"
        f"{sections}"
    )
    client = GeminiClient(execution_mode="FAST")
    try:
        result = await client.generate(prompt)
        if not result.success:
            return {"error": result.error}
        return {"ranking": result.code}
    finally:
        await client.close()


async def sse_chat_generator(session_id: str, provider: str, message: str, class_id: str = None, project_id: str = None):
    """Generateur SSE pour le chat individuel (MULTIPLEX). M226: ProjectContext injection."""
    logger.info(f"[BRS] Multiplex chat for {provider} in session {session_id}" + (f" (class={class_id}, project={project_id})" if class_id or project_id else ""))

    # 1. Sauvegarder le message utilisateur
    storage.save_message(session_id, provider, "user", message)

    # 2. Charger l'historique pour construire un prompt conversationnel
    history = storage.get_messages(session_id, provider=provider)

    # Construire un prompt conversationnel plat
    history_lines = []
    for m in history[:-1]:
        role = "Utilisateur" if m['role'] == 'user' else "Assistant"
        history_lines.append(f"{role}: {m['content']}")

    if history_lines:
        conversational_prompt = "\n".join(history_lines) + f"\nUtilisateur: {message}\nAssistant:"
    else:
        conversational_prompt = message

    # M226: ProjectContext canonique
    from .project_context import ProjectContext
    ctx = ProjectContext(project_id=project_id, class_id=class_id)
    system_prompt = ctx.as_system_prefix() + BRS_CHAT_SYSTEM

    client = None
    try:
        if provider == "gemini":
            client = GeminiClient(execution_mode="FAST")
        elif provider == "groq":
            client = GroqClient()
        elif provider == "codestral":
            client = CodestralClient()
        else:
            yield f"event: error\ndata: Unknown provider {provider}\n\n"
            return

        yield f"event: status\ndata: {json.dumps({'status': 'THINKING', 'provider': provider})}\n\n"

        result = await client.generate(
            f"{system_prompt}\n\n{conversational_prompt}",
            output_constraint="Reponds de maniere conversationnelle en francais. Ne genere PAS de code sauf si explicitement demande. Si le sujet est suffisamment defini, inclus en fin de reponse : <!-- SUJET: title: ... description: ... competences: [A1, C2] -->"
        )
        
        if result.success:
            full_response = result.code
            # Simulation de streaming par mots pour l'effet visuel
            tokens = re.findall(r'\S+|\s+', full_response)
            for token in tokens:
                yield f"event: token\ndata: {json.dumps(token)}\n\n"
                await asyncio.sleep(0.02)
                
            # 3. Sauvegarder la réponse de l'assistant
            storage.save_message(session_id, provider, "assistant", full_response)
            
            yield f"event: status\ndata: {json.dumps({'status': 'DONE', 'provider': provider})}\n\n"
            yield "event: done\ndata: {}\n\n"
        else:
            logger.error(f"[BRS] LLM Generation error: {result.error}")
            yield f"event: error\ndata: {result.error}\n\n"
        
    except Exception as e:
        logger.error(f"[BRS] Multiplex SSE Error for {provider}: {e}")
        yield f"event: error\ndata: {str(e)}\n\n"
    finally:
        if client:
            await client.close()


# --- M220: Prof mode helpers ---

def _load_class_meta(class_id: str) -> dict:
    """Charge nom + sujet de la classe depuis la DB bkd."""
    try:
        import sqlite3
        db_path = Path(__file__).parent.parent.parent.parent / "db" / "projects.db"
        if not db_path.exists():
            return {"name": class_id, "subject": ""}
        con = sqlite3.connect(str(db_path))
        row = con.execute("SELECT name, subject FROM classes WHERE id=?", (class_id,)).fetchone()
        con.close()
        if row:
            return {"name": row[0], "subject": row[1] or ""}
    except Exception as e:
        logger.warning(f"_load_class_meta error: {e}")
    return {"name": class_id, "subject": ""}


def _load_dnmade_referentiel() -> str:
    """Lit core/dnmade_referentiel.json -> retourne texte formate."""
    try:
        ref_path = Path(__file__).parent.parent.parent.parent / "Frontend/3. STENCILER" / "core" / "dnmade_referentiel.json"
        if not ref_path.exists():
            return ""
        data = json.loads(ref_path.read_text(encoding='utf-8'))
        lines = []
        for domain_id, domain in data.get("domains", {}).items():
            lines.append(f"Domaine {domain_id} -- {domain.get('label', '')}:")
            for comp_id, comp in domain.get("competences", {}).items():
                lines.append(f"  {comp_id} : {comp.get('label', '')}")
        return "\n".join(lines)
    except Exception as e:
        logger.warning(f"_load_dnmade_referentiel error: {e}")
        return ""


def _build_prof_system(class_meta: dict, referentiel: str) -> str:
    return f"""MODE PROF -- HomeOS
Classe : {class_meta.get('name', 'inconnue')}
Sujet actif : {class_meta.get('subject', 'non defini')}

Referentiel DNMADE :
{referentiel}

Role : tu aides a formaliser un sujet de projet etudiant. Tu proposes des pistes, identifies les competences DNMADE pertinentes. Quand le sujet est suffisamment defini, inclus en fin de reponse :
<!-- SUJET:
title: ...
description: ...
competences: [A1, C2, C3]
-->"""
