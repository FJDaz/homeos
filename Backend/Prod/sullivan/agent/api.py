"""
API - Endpoints FastAPI pour Sullivan Agent.

Routes:
- POST /sullivan/agent/chat : Chat simple
- POST /sullivan/agent/chat/stream : Chat streaming (SSE)
- GET  /sullivan/agent/session/{id} : Récupérer une session
- POST /sullivan/agent/session/{id}/clear : Effacer l'historique
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from loguru import logger

from .sullivan_agent import SullivanAgent, create_agent
from .memory import ConversationMemory


router = APIRouter(prefix="/sullivan/agent", tags=["agent"])


# ===== MODÈLES DE REQUÊTES/RÉPONSES =====

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: str = "anonymous"
    context: Optional[Dict[str, Any]] = None
    step: int = 1
    mode: str = "creation"  # "creation" | "agent" - agent = full capabilities


class ChatResponse(BaseModel):
    content: str
    session_id: str
    tool_calls: list
    dom_actions: list = []
    code_actions: list = []
    metadata: Dict[str, Any]


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    message_count: int
    current_step: int
    current_project: Optional[str]
    mode: str
    messages: list


# ===== ENDPOINTS =====

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat avec Sullivan Agent.
    
    Crée une nouvelle session ou continue une existante.
    """
    try:
        # Créer ou récupérer l'agent
        if request.session_id:
            # Récupérer session existante
            memory = ConversationMemory(
                session_id=request.session_id,
                user_id=request.user_id,
            )
            agent = SullivanAgent(
                session_id=request.session_id,
                user_id=request.user_id,
                memory=memory,
            )
        else:
            # Nouvelle session
            agent = await create_agent(
                user_id=request.user_id,
                step=request.step,
            )
        
        # Mettre à jour le mode dans la mémoire si fourni
        if request.mode:
            agent.memory.update_context(mode=request.mode)
        
        # Chat
        response = await agent.chat(
            message=request.message,
            context=request.context,
        )
        
        return ChatResponse(
            content=response.content,
            session_id=response.session_id,
            tool_calls=[
                {"tool": tc["tool"], "params": tc["params"]}
                for tc in response.tool_calls
            ],
            dom_actions=response.metadata.get("dom_actions", []),
            code_actions=response.metadata.get("code_actions", []),
            metadata=response.metadata,
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Chat avec Sullivan Agent en streaming (SSE).
    
    Retourne la réponse token par token.
    """
    async def event_generator():
        try:
            agent = await create_agent(
                user_id=request.user_id,
                session_id=request.session_id,
                step=request.step,
            )
            
            async for chunk in agent.chat_stream(
                message=request.message,
                context=request.context,
            ):
                yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Récupère les détails d'une session de conversation.
    """
    try:
        memory = ConversationMemory(session_id=session_id)
        ctx = memory.session_context
        
        return SessionResponse(
            session_id=session_id,
            user_id=ctx.user_id,
            message_count=len(memory.messages),
            current_step=ctx.current_step,
            current_project=ctx.current_project,
            mode=ctx.mode,
            messages=[
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in memory.messages[-20:]  # Derniers 20 messages
            ],
        )
        
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=404, detail="Session not found")


@router.post("/session/{session_id}/clear")
async def clear_session(session_id: str):
    """
    Efface l'historique d'une session (garde le contexte).
    """
    try:
        memory = ConversationMemory(session_id=session_id)
        memory.clear()
        
        return {"status": "cleared", "session_id": session_id}
        
    except Exception as e:
        logger.error(f"Clear session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def list_tools():
    """
    Liste les outils disponibles pour l'agent.
    """
    from .tools import tool_registry
    
    tools = []
    for tool in tool_registry.list_tools():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "requires_confirmation": tool.requires_confirmation,
        })
    
    return {"tools": tools}


# Pour inclusion dans api.py
__all__ = ["router"]
