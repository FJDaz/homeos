"""
SullivanAgent - Agent conversationnel complet pour AetherFlow.

Capacités:
- Chat naturel avec mémoire de contexte
- Exécution d'outils (générer, analyser, modifier)
- Personnalité Sullivan (pédagogique, minimaliste)
- Intégration au parcours UX (9 étapes)
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
from loguru import logger

from .memory import ConversationMemory, create_session_id
from .tools import ToolRegistry, ToolResult, tool_registry
from ...models.gemini_client import GeminiClient
from ...models.groq_client import GroqClient


@dataclass
class AgentResponse:
    """Réponse de l'agent Sullivan."""
    content: str
    tool_calls: List[Dict[str, Any]]
    tool_results: List[ToolResult]
    session_id: str
    metadata: Dict[str, Any]


class SullivanAgent:
    """
    Agent conversationnel Sullivan.
    
    Usage:
        agent = SullivanAgent(session_id="abc123")
        
        # Réponse simple
        response = await agent.chat("Je veux créer une page de login")
        
        # Streaming
        async for chunk in agent.chat_stream("Génère un bouton"):
            print(chunk, end="")
    """
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        user_id: str = "anonymous",
        memory: Optional[ConversationMemory] = None,
        tools: Optional[ToolRegistry] = None,
        llm_provider: str = "groq",  # "groq" (rapide) ou "gemini" (capable)
    ):
        """
        Args:
            session_id: ID de session (créé si non fourni)
            user_id: ID utilisateur
            memory: Instance de mémoire (créée si non fournie)
            tools: Registre d'outils (défaut: global)
            llm_provider: Provider LLM principal
        """
        self.session_id = session_id or create_session_id(user_id)
        self.user_id = user_id
        self.memory = memory or ConversationMemory(
            session_id=self.session_id,
            user_id=user_id,
        )
        self.tools = tools or tool_registry
        self.llm_provider = llm_provider
        
        # Clients LLM
        self.groq = GroqClient()
        self.gemini = GeminiClient(execution_mode="BUILD")
        
        logger.info(f"SullivanAgent initialized: {self.session_id} (LLM: {llm_provider})")
    
    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        execute_tools: bool = True,
    ) -> AgentResponse:
        """
        Envoie un message à Sullivan et reçoit une réponse.
        
        Args:
            message: Message de l'utilisateur
            context: Contexte additionnel (optionnel)
            execute_tools: Si True, exécute les outils demandés
            
        Returns:
            Réponse complète de l'agent
        """
        # Ajouter le message utilisateur à l'historique
        self.memory.add_message("user", message, metadata=context)
        
        # Construire le contexte pour le LLM
        messages = self.memory.get_context_for_llm()
        tools_schemas = self.tools.get_schemas()
        
        # Appeler le LLM
        llm_response = await self._call_llm(
            messages=messages,
            tools=tools_schemas if execute_tools else None,
        )
        
        # Parser la réponse pour détecter les appels d'outils et actions
        content, tool_calls, dom_actions, code_actions = self._parse_response(llm_response)
        
        # Exécuter les outils si demandé
        tool_results = []
        if execute_tools and tool_calls:
            tool_results = await self._execute_tools(tool_calls)
            
            # Si des outils ont été exécutés, demander une réponse finale
            if tool_results:
                content = await self._generate_final_response(
                    original_message=message,
                    tool_results=tool_results,
                )
            
            # Extraire les dom_actions des tool_results (pour injection dans la sidebar, etc.)
            for result in tool_results:
                if result.success and result.data and "dom_action" in result.data:
                    dom_actions.append(result.data["dom_action"])
        
        # Ajouter la réponse à l'historique
        metadata = {"tool_calls": tool_calls}
        if dom_actions:
            metadata["dom_actions"] = dom_actions
        if code_actions:
            metadata["code_actions"] = code_actions
            
        self.memory.add_message(
            role="assistant",
            content=content,
            metadata=metadata,
        )
        
        return AgentResponse(
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            session_id=self.session_id,
            metadata={
                "step": self.memory.session_context.current_step,
                "tool_count": len(tool_calls),
                "dom_actions": dom_actions,
                "code_actions": code_actions,
            },
        )
    
    async def chat_stream(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Version streaming de chat pour réponses en temps réel.
        
        Args:
            message: Message de l'utilisateur
            context: Contexte additionnel
            
        Yields:
            Chunks de la réponse
        """
        self.memory.add_message("user", message, metadata=context)
        
        messages = self.memory.get_context_for_llm()
        
        # Utiliser Groq pour le streaming (plus rapide)
        full_response = ""
        
        try:
            # Simuler le streaming (Groq ne supporte pas vraiment le streaming async)
            response = await self.groq.generate(
                prompt=self._messages_to_prompt(messages),
                max_tokens=2048,
            )
            
            if response.success and response.code:
                full_response = response.code
                # Yield par phrases pour effet streaming
                for sentence in full_response.split(". "):
                    yield sentence + ". "
                    await asyncio.sleep(0.05)  # Petit délai pour l'effet
            else:
                yield "Désolé, je n'ai pas pu générer de réponse."
                
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"Erreur: {str(e)}"
        
        # Sauvegarder la réponse complète
        if full_response:
            self.memory.add_message("assistant", full_response)
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Appelle le LLM avec les messages et outils.
        Fallback: Groq → Gemini si rate limit.
        
        Args:
            messages: Messages formatés pour le LLM
            tools: Schemas des outils disponibles
            
        Returns:
            Réponse texte du LLM
        """
        prompt = self._messages_to_prompt(messages)
        
        # Essayer le provider configuré
        if self.llm_provider == "groq":
            result = await self.groq.generate(
                prompt=prompt,
                max_tokens=2048,
            )
            
            # Si Groq rate limited, fallback sur Gemini
            if not result.success and ("429" in str(result.error) or "rate_limit" in str(result.error).lower()):
                logger.warning(f"Groq rate limited, fallback to Gemini")
                result = await self.gemini.generate(
                    prompt=prompt,
                    max_tokens=2048,
                )
        else:
            result = await self.gemini.generate(
                prompt=prompt,
                max_tokens=2048,
            )
        
        if result.success and result.code:
            return result.code
        else:
            logger.error(f"LLM call failed: {result.error}")
            return f"Désolé, une erreur est survenue: {result.error}"
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convertit les messages en prompt texte simple."""
        lines = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                lines.append(f"[System]\n{content}\n")
            elif role == "user":
                lines.append(f"[User]\n{content}\n")
            elif role == "assistant":
                lines.append(f"[Assistant]\n{content}\n")
        
        lines.append("[Assistant]")
        return "\n".join(lines)
    
    def _parse_response(
        self,
        response: str,
    ) -> tuple[str, List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parse la réponse du LLM pour extraire:
        - Le contenu texte
        - Les appels d'outils (format: @tool_name({"param": "value"}))
        - Les actions DOM (@dom_action({...}))
        - Les actions code (@code_action({...}))
        - Les blocs HTML (```html ... ```)

        Returns:
            (content, tool_calls, dom_actions, code_actions)
        """
        import re

        tool_calls = []
        dom_actions = []
        code_actions = []
        content = response

        # 1. Extraire les blocs HTML ```html ... ``` et les convertir en code_actions
        html_pattern = r'```html\s*([\s\S]*?)\s*```'
        html_matches = re.findall(html_pattern, response)
        for html_code in html_matches:
            if html_code.strip():
                code_actions.append({
                    "type": "insert_html",
                    "html": html_code.strip(),
                    "target": "#studio-main-zone",  # Zone par défaut
                })
                logger.debug(f"Extracted HTML block: {len(html_code)} chars")

        # Retirer les blocs HTML du contenu
        content = re.sub(html_pattern, '', content)

        # 2. Parser les @tool_name({...}) avec support JSON multiline et triple quotes
        # On cherche @nom_outil( puis on balance les accolades pour trouver la fin
        tool_start_pattern = r'@(\w+)\('

        for match in re.finditer(tool_start_pattern, response):
            tool_name = match.group(1)
            start_pos = match.end()

            # Extraire le contenu entre parenthèses en balançant les accolades
            params_str = self._extract_balanced_json(response, start_pos)
            if not params_str:
                continue

            # Parser le JSON (avec support triple quotes)
            params = self._parse_tool_params(params_str)
            if params is None:
                logger.warning(f"Failed to parse tool params for {tool_name}: {params_str[:100]}...")
                continue

            # Reconstruire le texte complet pour le retirer du content
            full_call = f"@{tool_name}({params_str})"

            # Classifier selon le type
            if tool_name == 'dom_action':
                dom_actions.append(params)
                content = content.replace(full_call, "")
                logger.debug(f"Parsed DOM action: {params.get('type', 'unknown')}")
            elif tool_name == 'code_action':
                code_actions.append(params)
                content = content.replace(full_call, "")
                logger.debug(f"Parsed code action: {params.get('type', 'unknown')}")
            else:
                tool_calls.append({
                    "tool": tool_name,
                    "params": params,
                })
                content = content.replace(full_call, "")
                logger.debug(f"Parsed tool call: {tool_name}")

        return content.strip(), tool_calls, dom_actions, code_actions

    def _extract_balanced_json(self, text: str, start_pos: int) -> Optional[str]:
        """Extrait le JSON en balançant les accolades, avec support triple quotes."""
        if start_pos >= len(text) or text[start_pos] != '{':
            return None

        depth = 0
        in_string = False
        in_triple_quote = False
        escape_next = False
        i = start_pos

        while i < len(text):
            char = text[i]

            # Gérer les triple quotes """
            if not escape_next and text[i:i+3] == '"""':
                in_triple_quote = not in_triple_quote
                i += 3
                continue

            if escape_next:
                escape_next = False
                i += 1
                continue

            if char == '\\' and in_string:
                escape_next = True
                i += 1
                continue

            # Ignorer tout dans les triple quotes
            if in_triple_quote:
                i += 1
                continue

            if char == '"' and not in_triple_quote:
                in_string = not in_string
            elif not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start_pos:i+1]

            i += 1

        return None

    def _parse_tool_params(self, params_str: str) -> Optional[Dict[str, Any]]:
        """Parse les paramètres d'un outil, avec support triple quotes."""
        import re

        # 1. Essayer JSON standard d'abord
        try:
            return json.loads(params_str)
        except json.JSONDecodeError:
            pass

        # 2. Convertir les triple quotes en strings JSON valides
        # Pattern: """ ... """ -> "..."  (avec échappement des guillemets internes)
        def convert_triple_quotes(match):
            content = match.group(1)
            # Échapper les guillemets doubles internes
            escaped = content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'"{escaped}"'

        fixed_str = re.sub(r'"""([\s\S]*?)"""', convert_triple_quotes, params_str)

        try:
            return json.loads(fixed_str)
        except json.JSONDecodeError:
            pass

        # 3. Essayer avec guillemets simples convertis
        try:
            fixed_str = params_str.replace("'", '"')
            return json.loads(fixed_str)
        except json.JSONDecodeError:
            pass

        return None
    
    async def _execute_tools(
        self,
        tool_calls: List[Dict[str, Any]],
    ) -> List[ToolResult]:
        """
        Exécute les outils demandés.
        
        Args:
            tool_calls: Liste des appels d'outils
            
        Returns:
            Résultats des exécutions
        """
        results = []
        
        for call in tool_calls:
            tool_name = call["tool"]
            params = call["params"]
            
            tool = self.tools.get(tool_name)
            if tool:
                logger.info(f"Executing tool: {tool_name} with params {params}")
                try:
                    result = await tool.execute(**params)
                    if not result.success:
                        logger.warning(f"Tool {tool_name} failed: {result.error}")
                    else:
                        logger.info(f"Tool {tool_name} succeeded: {result.content[:100]}...")
                    results.append(result)
                except Exception as e:
                    logger.error(f"Tool {tool_name} exception: {e}")
                    results.append(ToolResult(
                        success=False,
                        content=f"Erreur lors de l'exécution de {tool_name}",
                        error=str(e),
                    ))
            else:
                logger.warning(f"Tool not found: {tool_name}")
                results.append(ToolResult(
                    success=False,
                    content=f"Outil '{tool_name}' non trouvé.",
                    error="Tool not found",
                ))
        
        return results
    
    async def _generate_final_response(
        self,
        original_message: str,
        tool_results: List[ToolResult],
    ) -> str:
        """
        Génère une réponse finale après exécution des outils.
        
        Args:
            original_message: Message original de l'utilisateur
            tool_results: Résultats des outils exécutés
            
        Returns:
            Réponse finale
        """
        # Construire un résumé des résultats
        results_summary = []
        for i, result in enumerate(tool_results, 1):
            status = "✓" if result.success else "✗"
            results_summary.append(f"{status} Résultat {i}: {result.content}")
        
        prompt = f"""
Tu as exécuté des actions pour l'utilisateur. Résume les résultats de manière concise et naturelle.

Message de l'utilisateur: {original_message}

Résultats des actions:
{chr(10).join(results_summary)}

Réponds en 2-3 phrases maximum, de manière conversationnelle.
"""
        
        # Utiliser Groq pour une réponse rapide
        result = await self.groq.generate(prompt, max_tokens=512)
        
        if result.success and result.code:
            return result.code.strip()
        else:
            return "J'ai exécuté les actions demandées. Voici les résultats:\n" + "\n".join(results_summary)
    
    def update_step(self, step: int) -> None:
        """Met à jour l'étape actuelle du parcours UX."""
        self.memory.update_context(current_step=step)
        logger.info(f"Step updated to {step}")
    
    def set_project(self, project_name: str) -> None:
        """Définit le projet courant."""
        self.memory.update_context(current_project=project_name)
    
    def export_session(self) -> Dict[str, Any]:
        """Exporte la session complète."""
        return self.memory.export_conversation()
    
    def clear_history(self) -> None:
        """Efface l'historique de conversation."""
        self.memory.clear()


# ===== UTILITAIRES =====

async def create_agent(
    user_id: str = "anonymous",
    session_id: Optional[str] = None,
    step: int = 1,
) -> SullivanAgent:
    """
    Factory pour créer un agent Sullivan configuré.
    
    Args:
        user_id: ID utilisateur
        session_id: ID de session existante (optionnel)
        step: Étape initiale du parcours UX
        
    Returns:
        Agent configuré
    """
    agent = SullivanAgent(
        session_id=session_id,
        user_id=user_id,
        llm_provider="gemini",  # Gemini par défaut (rate limit illimité)
    )
    
    agent.update_step(step)
    
    # Activer le mode AGENT pour avoir accès aux outils
    agent.memory.update_context(mode="agent")
    
    return agent


__all__ = [
    "SullivanAgent",
    "AgentResponse",
    "create_agent",
]
