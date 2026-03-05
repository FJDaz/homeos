#!/usr/bin/env python3
import os
import json
import requests
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt
from rich.text import Text
from rich.spinner import Spinner

# CHARGEMENT DU .ENV
env_path = Path("/Users/francois-jeandazin/AETHERFLOW/.env")
load_dotenv(dotenv_path=env_path)

# CONFIGURATION
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-reasoner"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

console = Console()

def get_response(history):
    payload = {"model": MODEL, "messages": history, "stream": True}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    # On ajoute un timeout de 10s pour l'établissement de la connexion
    return requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=(10, None))

def chat():
    if not API_KEY or "votre_cle_ici" in API_KEY:
        console.print(Panel("[red]ERREUR : DEEPSEEK_API_KEY est manquante ou invalide dans le .env ![/red]", border_style="red"))
        sys.exit(1)

    console.print(Panel(
        Text.from_markup("[bold cyan]DS-R1 CLI (v2.1)[/bold cyan]\n[dim]Connecté à api.deepseek.com[/dim]"),
        border_style="bright_blue"
    ))
    
    history = []
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]❯[/bold cyan]")
            
            if not user_input.strip(): continue
            if user_input.lower() in ["exit", "quit"]: break
            if user_input.lower() == "clear":
                history = []
                console.print("[dim italic]Historique effacé.[/dim italic]")
                continue
            
            history.append({"role": "user", "content": user_input})
            
            reasoning = ""
            content = ""
            start_time = time.time()
            
            console.print()
            
            with Live(Spinner("dots", text="[magenta] Connexion à DeepSeek...[/magenta]"), console=console, refresh_per_second=10) as live:
                try:
                    response = get_response(history)
                    
                    if response.status_code != 200:
                        live.update(f"[red]Erreur API ({response.status_code}): {response.text}[/red]")
                        # On retire le dernier message car il a échoué
                        history.pop()
                        continue

                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_str = line_str[6:].strip()
                                if data_str == "[DONE]": break
                                try:
                                    data = json.loads(data_str)
                                    delta = data['choices'][0]['delta']
                                    
                                    if 'reasoning_content' in delta:
                                        reasoning += delta['reasoning_content']
                                    if 'content' in delta:
                                        content += delta['content']
                                    
                                    elapsed = time.time() - start_time
                                    display = []
                                    if reasoning:
                                        title = f"[magenta]Thinking... ({elapsed:.1f}s)[/magenta]"
                                        display.append(Panel(Text(reasoning, style="italic dim"), title=title, border_style="magenta"))
                                    if content:
                                        display.append(Markdown(content))
                                    
                                    if not reasoning and not content:
                                        live.update(Spinner("dots", text=f"[magenta] En attente de réponse... ({elapsed:.1f}s)[/magenta]"))
                                    else:
                                        live.update(console.render_group(display))
                                except: continue
                except Exception as e:
                    live.update(f"[red]Erreur de connexion : {e}[/red]")

            if content:
                history.append({"role": "assistant", "content": content})

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompu.[/yellow]")
            break

if __name__ == "__main__":
    chat()
