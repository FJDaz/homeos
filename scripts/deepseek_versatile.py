#!/usr/bin/env python3
import asyncio
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import argparse
import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.prompt import Prompt
from rich.panel import Panel
from rich.status import Status

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# --- Auto-resolve Virtualenv (Mission 308 - Environment Protection) ---
venv_python = project_root / "venv" / "bin" / "python3"
if os.name != "nt" and venv_python.exists() and sys.executable != str(venv_python):
    # If not running from venv, re-exec with venv python
    # This prevents 'ModuleNotFoundError: llama_index' when user runs 'python3 script.py' instead of './venv/bin/python3'
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)


from Backend.Prod.models.deepseek_client import DeepSeekClient

console = Console()

# --- Tool Definitions ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lit le contenu complet d'un fichier du projet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin relatif du fichier par rapport à la racine (ex: ROADMAP.md)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Liste les fichiers et dossiers dans un répertoire donné.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Répertoire à lister (ex: Backend/Prod)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "code_search",
            "description": "Effectue une recherche sémantique dans toute la codebase pour trouver des exemples ou de la logique.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "La question ou le concept à chercher"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Crée ou modifie un fichier dans le projet. ATTENTION: Écrase le contenu existant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Chemin relatif du fichier (ex: Backend/Prod/new_script.py)"},
                    "content": {"type": "string", "description": "Contenu complet à écrire dans le fichier"}
                },
                "required": ["path", "content"]
            }
        }
    }
]

# --- Tool Implementations ---

async def call_tool(name: str, args: Dict[str, Any], client: DeepSeekClient) -> str:
    try:
        if name == "read_file":
            path = args.get("path")
            p = project_root / path
            if p.exists() and p.is_file():
                return p.read_text(encoding='utf-8')
            return f"Erreur: Fichier '{path}' introuvable ou n'est pas un fichier."

        elif name == "list_files":
            path = args.get("path", ".")
            p = project_root / path
            if p.exists() and p.is_dir():
                items = [f"{'[DIR] ' if i.is_dir() else '[FILE]'} {i.name}" for i in p.iterdir() if not i.name.startswith('.')]
                return "\n".join(items)
            return f"Erreur: Dossier '{path}' introuvable."

        elif name == "code_search":
            query = args.get("query")
            # Utilise le RAG déjà présent dans le client
            return await client.retrieve_context(query, top_k=5)

        elif name == "write_file":
            path = args.get("path")
            content = args.get("content")
            p = project_root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
            return f"Succès: Fichier '{path}' écrit ({len(content)} caractères)."

    except Exception as e:
        return f"Erreur lors de l'exécution de {name}: {str(e)}"
    return f"Outil '{name}' inconnu."

# --- Main Logic ---

class DeepSeekAgent:
    def __init__(self, model: str = "deepseek-chat"):
        try:
            self.client = DeepSeekClient(model=model)
        except Exception as e:
            console.print(f"[bold red]Erreur d'initialisation : {e}[/bold red]")
            sys.exit(1)
        self.history = []
        self._load_context()

    def _load_context(self):
        try:
            identity = Path(project_root / "DEEPSEEK.md").read_text(encoding='utf-8')
            repo_map = Path(project_root / "REPO_MAP.md").read_text(encoding='utf-8')
        except:
            identity, repo_map = "Agent AetherFlow", "Repo Map indisponible"
            
        self.history.append({
            "role": "system", 
            "content": f"{identity}\n\n"
                       "IMPORTANT: You are an agent with DIRECT ACCESS to tools. "
                       "If you need to read a file or search the codebase to answer, DO NOT ask permission. "
                       "Use 'read_file', 'list_files', or 'code_search' IMMEDIATELY. "
                       "Always use tools before admitting you don't know something.\n\n"
                       f"STRUCTURE DU PROJET:\n{repo_map}"
        })

    async def run(self, initial_files: List[str] = None):
        if initial_files:
            for f in initial_files:
                p = project_root / f
                if p.exists():
                    self.history.append({"role": "user", "content": f"Voici le contenu de {f} :\n{p.read_text()}"})

        console.print(Panel(f"[bold cyan]DeepSeek Architect Agent[/bold cyan] v4.0\nMode: Agentic Tool Use\nCapacités: Lecture, Navigation, RAG Search", title="AETHERFLOW"))

        while True:
            try:
                user_msg = Prompt.ask("\n[bold magenta]USER ❯[/bold magenta]")
                if user_msg.lower() in ["exit", "quit"]: break
                if not user_msg.strip(): continue
                
                self.history.append({"role": "user", "content": user_msg})
                
                # Agent loop
                while True:
                    full_response = ""
                    tool_calls = []
                    
                    with Live(console=console, refresh_per_second=10) as live:
                        try:
                            async with httpx.AsyncClient(timeout=180) as http:
                                async with http.stream("POST", self.client.api_url, 
                                    headers={"Authorization": f"Bearer {self.client.api_key}"},
                                    json={
                                        "model": self.client.model,
                                        "messages": self.history,
                                        "tools": TOOLS,
                                        "tool_choice": "auto",
                                        "stream": True
                                    }) as response:
                                    
                                    if response.status_code != 200:
                                        err = await response.aread()
                                        live.update(f"[red]Erreur API: {response.status_code}\n{err.decode()}[/red]")
                                        break

                                    id_to_tool = {}
                                    async for line in response.aiter_lines():
                                        if not line.startswith("data: "): continue
                                        data_str = line[6:].strip()
                                        if data_str == "[DONE]": break
                                        
                                        data = json.loads(data_str)
                                        delta = data['choices'][0]['delta']
                                        
                                        # Handle Text
                                        if "content" in delta and delta["content"]:
                                            full_response += delta["content"]
                                            live.update(Markdown(full_response))
                                        
                                        # Handle Tool Calls (streaming)
                                        if "tool_calls" in delta:
                                            for tc in delta["tool_calls"]:
                                                idx = tc.get("index", 0)
                                                if idx not in id_to_tool:
                                                    id_to_tool[idx] = {"id": tc.get("id"), "name": "", "args": ""}
                                                
                                                if "function" in tc:
                                                    f = tc["function"]
                                                    if "name" in f: id_to_tool[idx]["name"] += f["name"]
                                                    if "arguments" in f: id_to_tool[idx]["args"] += f["arguments"]
                        
                        except Exception as e:
                            live.update(f"[red]Erreur fatale: {e}[/red]")
                            break

                    # Any tools to call?
                    if id_to_tool:
                        tool_calls = list(id_to_tool.values())
                        # Need to add the assistant message containing the tool calls to history
                        self.history.append({
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": t["id"],
                                    "type": "function",
                                    "function": {"name": t["name"], "arguments": t["args"]}
                                } for t in tool_calls
                            ]
                        })

                        # Execute tools
                        for t in tool_calls:
                            try:
                                args = json.loads(t["args"])
                            except: args = {}
                            
                            with console.status(f"[bold yellow]🔧 Action: {t['name']}({t['args']})...[/bold yellow]"):
                                result = await call_tool(t["name"], args, self.client)
                                self.history.append({
                                    "role": "tool",
                                    "tool_call_id": t["id"],
                                    "name": t["name"],
                                    "content": result
                                })
                        
                        # Continue to next iteration of Agent Loop to get response based on tool results
                        continue 
                    
                    else:
                        # Final response received
                        if full_response:
                            self.history.append({"role": "assistant", "content": full_response})
                        break

            except KeyboardInterrupt:
                break
        
        await self.client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Fichiers initiaux")
    args = parser.parse_args()

    agent = DeepSeekAgent()
    try:
        asyncio.run(agent.run(args.files))
    except (KeyboardInterrupt, SystemExit):
        pass
