#!/usr/bin/env python3
"""
DeepSeek Code Assistant - Chat CLI avec accès à la codebase

Usage:
    python scripts/deepseek_code_assistant.py
    python scripts/deepseek_code_assistant.py --system "Tu es un expert Python"
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import argparse
import json
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Backend.Prod.models.deepseek_client import DeepSeekClient
from loguru import logger
import httpx

# Couleurs pour le terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


class CodebaseTools:
    """Outils pour interagir avec la codebase"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def read_file(self, file_path: str) -> str:
        """Lire un fichier"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.project_root / path

            if not path.exists():
                return f"❌ Fichier introuvable : {file_path}"

            content = path.read_text(encoding='utf-8')
            return f"📄 {path.name}\n```\n{content}\n```"
        except Exception as e:
            return f"❌ Erreur lecture : {e}"

    def grep(self, pattern: str, path: str = ".", file_type: str = None) -> str:
        """Rechercher un pattern dans les fichiers"""
        try:
            cmd = ["grep", "-r", "-n", "-i", pattern]

            if file_type:
                cmd.extend(["--include", f"*.{file_type}"])

            search_path = self.project_root / path if path != "." else self.project_root
            cmd.append(str(search_path))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 50:
                    lines = lines[:50] + [f"... ({len(lines) - 50} résultats supplémentaires)"]
                return "🔍 Résultats :\n" + "\n".join(lines)
            elif result.returncode == 1:
                return f"❌ Aucun résultat pour '{pattern}'"
            else:
                return f"❌ Erreur grep : {result.stderr}"

        except subprocess.TimeoutExpired:
            return "⏱️ Timeout (>10s)"
        except Exception as e:
            return f"❌ Erreur : {e}"

    def glob(self, pattern: str) -> str:
        """Trouver des fichiers par pattern"""
        try:
            matches = list(self.project_root.glob(pattern))
            if not matches:
                return f"❌ Aucun fichier trouvé : {pattern}"

            if len(matches) > 50:
                matches = matches[:50]
                suffix = f"\n... ({len(list(self.project_root.glob(pattern))) - 50} fichiers supplémentaires)"
            else:
                suffix = ""

            files = "\n".join(f"  - {m.relative_to(self.project_root)}" for m in matches)
            return f"📁 Fichiers trouvés ({len(matches)}) :\n{files}{suffix}"

        except Exception as e:
            return f"❌ Erreur glob : {e}"

    def tree(self, path: str = ".", max_depth: int = 3) -> str:
        """Afficher l'arborescence"""
        try:
            search_path = self.project_root / path if path != "." else self.project_root

            cmd = ["tree", "-L", str(max_depth), "-I", "venv|__pycache__|*.pyc|node_modules|.git"]
            cmd.append(str(search_path))

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return f"🌳 Arborescence :\n{result.stdout}"
            else:
                # Fallback si tree n'est pas installé
                return self._manual_tree(search_path, max_depth)

        except FileNotFoundError:
            return self._manual_tree(search_path, max_depth)
        except Exception as e:
            return f"❌ Erreur : {e}"

    def _manual_tree(self, path: Path, max_depth: int, _depth: int = 0, _prefix: str = "") -> str:
        """Arborescence manuelle si tree n'est pas installé"""
        if _depth >= max_depth:
            return ""

        result = []
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            items = [i for i in items if i.name not in {'.git', '__pycache__', 'venv', 'node_modules'}]

            for i, item in enumerate(items[:20]):  # Limite à 20 items
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                result.append(f"{_prefix}{current_prefix}{item.name}")

                if item.is_dir() and _depth < max_depth - 1:
                    next_prefix = _prefix + ("    " if is_last else "│   ")
                    result.append(self._manual_tree(item, max_depth, _depth + 1, next_prefix))

        except PermissionError:
            pass

        return "\n".join(filter(None, result))


class DeepSeekCodeAssistant:
    """Chat CLI DeepSeek avec accès codebase"""

    def __init__(self, system_prompt: Optional[str] = None, model: str = "deepseek-chat"):
        self.client = DeepSeekClient(model=model)
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = system_prompt or (
            "Tu es un assistant code expert. Tu as accès à la codebase via des outils. "
            "Réponds de manière concise et précise."
        )

        self.http_client = httpx.AsyncClient(
            timeout=120,
            headers={
                "Authorization": f"Bearer {self.client.api_key}",
                "Content-Type": "application/json"
            }
        )

        self.tools = CodebaseTools(project_root)

    async def close(self):
        await self.client.close()
        await self.http_client.aclose()

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def execute_tool(self, tool_name: str, args: str) -> str:
        """Exécuter un outil"""
        parts = args.split(maxsplit=1)

        if tool_name == "read":
            if len(parts) < 1:
                return "❌ Usage : /read <file_path>"
            return self.tools.read_file(parts[0])

        elif tool_name == "grep":
            if len(parts) < 1:
                return "❌ Usage : /grep <pattern> [path] [type]"
            pattern = parts[0]
            path = parts[1] if len(parts) > 1 else "."
            return self.tools.grep(pattern, path)

        elif tool_name == "glob":
            if len(parts) < 1:
                return "❌ Usage : /glob <pattern>"
            return self.tools.glob(parts[0])

        elif tool_name == "tree":
            path = parts[0] if len(parts) > 0 else "."
            return self.tools.tree(path)

        else:
            return f"❌ Outil inconnu : {tool_name}"

    async def send_message(self, user_message: str) -> str:
        """Envoyer un message"""
        self.add_message("user", user_message)

        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        try:
            response = await self.http_client.post(
                self.client.api_url,
                json={
                    "model": self.client.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
            )
            response.raise_for_status()

            data = response.json()
            assistant_message = data["choices"][0]["message"]["content"]

            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            self.add_message("assistant", assistant_message)

            cost = (input_tokens / 1_000_000 * 0.27) + (output_tokens / 1_000_000 * 1.10)
            footer = f"\n{DIM}[{input_tokens + output_tokens} tokens | ${cost:.4f}]{RESET}"

            return assistant_message + footer

        except Exception as e:
            logger.error(f"Error: {e}")
            return f"❌ Erreur : {str(e)}"

    def print_welcome(self):
        print(f"\n{MAGENTA}{BOLD}╔═══════════════════════════════════════╗{RESET}")
        print(f"{MAGENTA}{BOLD}║   DeepSeek Code Assistant v1.0        ║{RESET}")
        print(f"{MAGENTA}{BOLD}╚═══════════════════════════════════════╝{RESET}")
        print(f"\n{GREEN}Modèle : {self.client.model}{RESET}")
        print(f"{GREEN}Projet : {project_root.name}{RESET}")
        print(f"{DIM}Système : {self.system_prompt[:60]}...{RESET}\n")
        print(f"{YELLOW}Commandes Chat :{RESET}")
        print(f"  {CYAN}/clear{RESET}        - Effacer l'historique")
        print(f"  {CYAN}/system <text>{RESET} - Changer prompt système")
        print(f"  {CYAN}/exit{RESET}         - Quitter")
        print(f"\n{YELLOW}Outils Codebase :{RESET}")
        print(f"  {CYAN}/read <file>{RESET}   - Lire un fichier")
        print(f"  {CYAN}/grep <pattern>{RESET} - Chercher dans les fichiers")
        print(f"  {CYAN}/glob <pattern>{RESET} - Trouver fichiers par pattern")
        print(f"  {CYAN}/tree [path]{RESET}  - Afficher arborescence")
        print(f"\n{DIM}{'─' * 50}{RESET}\n")


async def main():
    parser = argparse.ArgumentParser(description="DeepSeek Code Assistant")
    parser.add_argument("--system", "-s", help="Prompt système")
    parser.add_argument("--model", "-m", default="deepseek-chat",
                       choices=["deepseek-chat", "deepseek-coder"])
    args = parser.parse_args()

    assistant = DeepSeekCodeAssistant(
        system_prompt=args.system,
        model=args.model
    )

    assistant.print_welcome()

    try:
        while True:
            try:
                user_input = input(f"{GREEN}Toi >{RESET} ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            # Commandes spéciales
            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()

                if cmd == "/exit":
                    print(f"\n{YELLOW}Au revoir !{RESET}")
                    break

                elif cmd == "/clear":
                    assistant.conversation_history = []
                    print(f"{GREEN}✓ Historique effacé{RESET}\n")
                    continue

                elif cmd == "/system":
                    if len(cmd_parts) > 1:
                        assistant.system_prompt = cmd_parts[1]
                        print(f"{GREEN}✓ Prompt système mis à jour{RESET}\n")
                    else:
                        print(f"{RED}Usage : /system <texte>{RESET}\n")
                    continue

                # Outils codebase
                elif cmd in ["/read", "/grep", "/glob", "/tree"]:
                    tool_name = cmd[1:]
                    tool_args = cmd_parts[1] if len(cmd_parts) > 1 else ""
                    result = assistant.execute_tool(tool_name, tool_args)
                    print(f"\n{CYAN}{result}{RESET}\n")

                    # Ajouter au contexte pour que DeepSeek puisse analyser
                    if not result.startswith("❌"):
                        user_input = f"Voici le résultat de {cmd} :\n\n{result}"
                    else:
                        continue
                else:
                    print(f"{RED}Commande inconnue : {cmd}{RESET}\n")
                    continue

            # Envoyer le message
            print(f"\n{MAGENTA}DeepSeek >{RESET}")
            response = await assistant.send_message(user_input)
            print(response)
            print(f"\n{DIM}{'─' * 50}{RESET}\n")

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interruption (Ctrl+C){RESET}")

    finally:
        await assistant.close()


if __name__ == "__main__":
    asyncio.run(main())
