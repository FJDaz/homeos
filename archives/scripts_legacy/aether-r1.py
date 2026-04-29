#!/usr/bin/env python3
import os
import json
import requests
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt
from rich.layout import Layout
from rich.table import Table

# CONFIGURATION DIRECTE DEEPSEEK (API OFFICIELLE)
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-reasoner"

# VOTRE CLÉ DEEPSEEK (Celle qui commence par sk-)
API_KEY = "sk-VOTRE_CLE_DEEPSEEK_ICI"

console = Console()

def get_response(history):
    payload = {
        "model": MODEL,
        "messages": history,
        "max_tokens": 8192,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    return requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=None)

def create_display(reasoning, content):
    """Crée un affichage combiné Pensée + Réponse."""
    table = Table.grid(expand=True)
    
    if reasoning:
        table.add_row(Panel(Markdown(reasoning), title="[bold magenta]Pensée Interne[/bold magenta]", border_style="dim"))
    
    if content:
        table.add_row(Panel(Markdown(content), title="[bold green]Réponse Finale[/bold green]", border_style="blue"))
    
    return table

def chat():
    console.print(Panel(
        "[bold cyan]AETHER-DEEPSEEK R1 (DEBUG MODE)[/bold cyan]\n"
        "[dim]Visualisation du Chain of Thought en temps réel[/dim]",
        border_style="blue",
        padding=(1, 2)
    ))
    
    history = []
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]AetherFlow[/bold green]")
            
            if user_input.lower() in ["exit", "quit", "bye", "clear"]:
                if user_input.lower() == "clear":
                    history = []
                    console.print("[yellow]Historique effacé.[/yellow]")
                    continue
                break
            
            history.append({"role": "user", "content": user_input})
            
            full_response = ""
            full_reasoning = ""
            
            with Live(create_display("", ""), console=console, refresh_per_second=10) as live:
                try:
                    response = get_response(history)

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
                                    delta = data['choices'][0]['delta']
                                    
                                    # Récupération de la pensée
                                    if 'reasoning_content' in delta:
                                        full_reasoning += delta['reasoning_content']
                                    
                                    # Récupération du contenu final
                                    if 'content' in delta:
                                        full_response += delta['content']
                                    
                                    live.update(create_display(full_reasoning, full_response))
                                except:
                                    continue
                except Exception as e:
                    live.update(f"[red]Erreur de connexion : {e}[/red]")

            history.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            console.print("\n[yellow]Interruption détectée.[/yellow]")
            break

if __name__ == "__main__":
    if API_KEY == "sk-VOTRE_CLE_DEEPSEEK_ICI":
        console.print("[red]ERREUR : Vous devez insérer votre clé API DeepSeek dans le script ![/red]")
        sys.exit(1)
    chat()
