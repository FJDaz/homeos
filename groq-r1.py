#!/usr/bin/env python3
import os
import json
import requests
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt
from rich.text import Text

# CHARGEMENT DU .ENV
env_path = Path("/Users/francois-jeandazin/AETHERFLOW/.env")
load_dotenv(dotenv_path=env_path)

# CONFIGURATION GROQ
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "deepseek-r1-distill-llama-70b"
API_KEY = os.getenv("GROQ_API_KEY")

console = Console()

def chat():
    if not API_KEY:
        console.print("[red]ERREUR : GROQ_API_KEY manquante dans le .env ![/red]")
        sys.exit(1)

    console.print(Panel(
        Text.from_markup(f"[bold green]GROQ R1-DISTILL[/bold green]\n[dim]Modèle: {MODEL}[/dim]"),
        border_style="green"
    ))
    
    history = []
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]❯[/bold green]")
            if not user_input.strip(): continue
            if user_input.lower() in ["exit", "quit"]: break
            
            history.append({"role": "user", "content": user_input})
            
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": MODEL,
                "messages": history,
                "stream": True
            }

            full_response = ""
            console.print()
            
            with Live(Text("Réflexion...", style="italic dim"), console=console, refresh_per_second=10) as live:
                response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=20)
                
                if response.status_code != 200:
                    live.update(f"[red]Erreur Groq: {response.text}[/red]")
                    continue

                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:].strip()
                            if data_str == "[DONE]": break
                            try:
                                data = json.loads(data_str)
                                delta = data['choices'][0]['delta'].get('content', '')
                                full_response += delta
                                live.update(Markdown(full_response))
                            except: continue

            history.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    chat()
