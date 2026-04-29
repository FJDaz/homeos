#!/usr/bin/env python3
import os
import json
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt

# CONFIGURATION DIRECTE NVIDIA (SANS PROXY)
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Modèle 2026 : DeepSeek V4 (le successeur du R1)
# Si V4 n'est pas encore dispo sur votre compte, essayez deepseek-ai/deepseek-v3.2
MODEL = "deepseek-ai/deepseek-v4"
API_KEY = "nvapi-VOTRE_CLE_ICI"

console = Console()

def chat():
    console.print(Panel("[bold cyan]AETHER-DEEPSEEK V4 (2026)[/bold cyan]\n[dim]Connexion au successeur du R1 (MODEL1)[/dim]", border_style="magenta"))
    
    history = []
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]Vous[/bold green]")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("[yellow]Au revoir ![/yellow]")
                break
            
            history.append({"role": "user", "content": user_input})
            
            payload = {
                "model": MODEL,
                "messages": history,
                "max_tokens": 8192,  # V4 supporte des sorties très longues
                "stream": True,
                "temperature": 0.6
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }

            console.print("\n[bold magenta]DeepSeek V4[/bold magenta] [dim](raisonnement...)[/dim]")
            
            full_response = ""
            with Live(Markdown(""), console=console, refresh_per_second=10) as live:
                try:
                    response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=None)
                    
                    if response.status_code != 200:
                        # Si V4 échoue, on tente automatiquement le V3.2 qui est la valeur sûre
                        if response.status_code == 404 or response.status_code == 400:
                            live.update("[yellow]V4 non trouvé, bascule sur V3.2...[/yellow]")
                            payload["model"] = "deepseek-ai/deepseek-v3.2"
                            response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=None)
                        
                        if response.status_code != 200:
                            live.update(f"[red]Erreur API ({response.status_code}): {response.text}[/red]")
                            continue

                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_str = line_str[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    chunk = data['choices'][0]['delta'].get('content', '')
                                    full_response += chunk
                                    live.update(Markdown(full_response))
                                except:
                                    continue
                except Exception as e:
                    live.update(f"[red]Erreur de connexion : {e}[/red]")

            history.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrompue.[/yellow]")
            break

if __name__ == "__main__":
    chat()
