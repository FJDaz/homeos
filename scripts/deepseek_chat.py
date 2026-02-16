#!/usr/bin/env python3
"""
Chat CLI DeepSeek - Alternative rapide à Gemini pour QA et discussions

Usage:
    python scripts/deepseek_chat.py
    python scripts/deepseek_chat.py --system "Tu es un expert QA Python"
    python scripts/deepseek_chat.py --file rapport.md
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import argparse

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
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


class DeepSeekChat:
    """Chat CLI avec DeepSeek"""

    def __init__(self, system_prompt: Optional[str] = None, model: str = "deepseek-chat"):
        """
        Args:
            system_prompt: Prompt système optionnel
            model: Modèle à utiliser (deepseek-chat ou deepseek-coder)
        """
        self.client = DeepSeekClient(model=model)
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = system_prompt or "Tu es un assistant IA expert et concis."

        # HTTP client pour appel direct
        self.http_client = httpx.AsyncClient(
            timeout=120,
            headers={
                "Authorization": f"Bearer {self.client.api_key}",
                "Content-Type": "application/json"
            }
        )

    async def close(self):
        """Fermer les clients"""
        await self.client.close()
        await self.http_client.aclose()

    def add_message(self, role: str, content: str):
        """Ajouter un message à l'historique"""
        self.conversation_history.append({"role": role, "content": content})

    def load_file(self, file_path: str) -> str:
        """Charger un fichier et l'ajouter au contexte"""
        path = Path(file_path).expanduser()
        if not path.exists():
            return f"❌ Fichier introuvable : {file_path}"

        try:
            content = path.read_text(encoding='utf-8')
            return f"📄 Fichier chargé : {path.name}\n\n```\n{content}\n```"
        except Exception as e:
            return f"❌ Erreur lecture : {e}"

    async def send_message(self, user_message: str) -> str:
        """Envoyer un message et obtenir la réponse"""

        # Ajouter le message utilisateur
        self.add_message("user", user_message)

        # Construire les messages avec système
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        try:
            # Appel API direct
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

            # Usage tokens
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # Ajouter à l'historique
            self.add_message("assistant", assistant_message)

            # Calculer coût
            cost = (input_tokens / 1_000_000 * 0.27) + (output_tokens / 1_000_000 * 1.10)

            # Footer avec stats
            footer = f"\n{DIM}[{input_tokens + output_tokens} tokens | ${cost:.4f}]{RESET}"

            return assistant_message + footer

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"API error: {error_msg}")
            return f"❌ Erreur API : {error_msg}"

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"❌ Erreur : {str(e)}"

    def print_welcome(self):
        """Afficher le message de bienvenue"""
        print(f"\n{CYAN}{BOLD}╔═══════════════════════════════════════╗{RESET}")
        print(f"{CYAN}{BOLD}║   DeepSeek Chat CLI v1.0              ║{RESET}")
        print(f"{CYAN}{BOLD}╚═══════════════════════════════════════╝{RESET}")
        print(f"\n{GREEN}Modèle : {self.client.model}{RESET}")
        print(f"{DIM}Système : {self.system_prompt[:60]}...{RESET}\n")
        print(f"{YELLOW}Commandes :{RESET}")
        print(f"  {CYAN}/file <path>{RESET}  - Charger un fichier")
        print(f"  {CYAN}/clear{RESET}        - Effacer l'historique")
        print(f"  {CYAN}/system <text>{RESET} - Changer prompt système")
        print(f"  {CYAN}/exit{RESET}         - Quitter")
        print(f"\n{DIM}{'─' * 50}{RESET}\n")


async def main():
    parser = argparse.ArgumentParser(description="Chat CLI avec DeepSeek")
    parser.add_argument("--system", "-s", help="Prompt système personnalisé")
    parser.add_argument("--file", "-f", help="Charger un fichier au démarrage")
    parser.add_argument("--model", "-m", default="deepseek-chat",
                       choices=["deepseek-chat", "deepseek-coder"],
                       help="Modèle DeepSeek à utiliser")
    args = parser.parse_args()

    # Créer le chat
    chat = DeepSeekChat(
        system_prompt=args.system,
        model=args.model
    )

    chat.print_welcome()

    # Charger fichier si spécifié
    if args.file:
        file_content = chat.load_file(args.file)
        print(f"{GREEN}{file_content}{RESET}\n")
        # Ajouter au contexte
        chat.add_message("user", f"Voici le fichier à analyser :\n\n{file_content}")
        response = await chat.send_message("Résume ce fichier en 3 points clés.")
        print(f"{CYAN}Assistant :{RESET}\n{response}\n")

    # Boucle interactive
    try:
        while True:
            # Prompt utilisateur
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
                    chat.conversation_history = []
                    print(f"{GREEN}✓ Historique effacé{RESET}\n")
                    continue

                elif cmd == "/system":
                    if len(cmd_parts) > 1:
                        chat.system_prompt = cmd_parts[1]
                        print(f"{GREEN}✓ Prompt système mis à jour{RESET}\n")
                    else:
                        print(f"{RED}Usage : /system <texte>{RESET}\n")
                    continue

                elif cmd == "/file":
                    if len(cmd_parts) > 1:
                        file_content = chat.load_file(cmd_parts[1])
                        print(f"{GREEN}{file_content}{RESET}\n")
                        user_input = f"Voici le fichier :\n\n{file_content}"
                    else:
                        print(f"{RED}Usage : /file <path>{RESET}\n")
                        continue
                else:
                    print(f"{RED}Commande inconnue : {cmd}{RESET}\n")
                    continue

            # Envoyer le message
            print(f"\n{CYAN}DeepSeek :{RESET}")
            response = await chat.send_message(user_input)
            print(response)
            print(f"\n{DIM}{'─' * 50}{RESET}\n")

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Interruption (Ctrl+C){RESET}")

    finally:
        await chat.close()


if __name__ == "__main__":
    asyncio.run(main())
