#!/usr/bin/env python3
import os, json, requests, sys, subprocess, time
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# --- CONFIG ---
ROOT = "/Users/francois-jeandazin/AETHERFLOW"
load_dotenv(dotenv_path=Path(ROOT) / ".env")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"
API_KEY = os.getenv("GROQ_API_KEY")
console = Console()

# --- TOOLS (MINIFIED) ---
def list_dir(d="."):
    try:
        p = Path(d) if Path(d).is_absolute() else Path(ROOT)/d
        return "\n".join([f"{'[D]' if i.is_dir() else '[F]'} {i.name}" for i in p.iterdir() if not i.name.startswith('.')])
    except Exception as e: return str(e)

def read_f(f):
    try:
        p = Path(f) if Path(f).is_absolute() else Path(ROOT)/f
        return p.read_text(encoding='utf-8')[:3000] # Cap à 3k pour sauver le TPM
    except Exception as e: return str(e)

def grep(pat, d="."):
    try:
        p = Path(d) if Path(d).is_absolute() else Path(ROOT)/d
        r = subprocess.run(["grep", "-rnE", pat, str(p), "--exclude-dir=.git", "--max-count=10"], capture_output=True, text=True)
        return r.stdout or "Rien."
    except Exception as e: return str(e)

def write_f(f, c):
    try:
        p = Path(f) if Path(f).is_absolute() else Path(ROOT)/f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(c, encoding='utf-8')
        return f"Ok: {f}"
    except Exception as e: return str(e)

TOOLS_MAP = {"list_dir": list_dir, "read_f": read_f, "grep": grep, "write_f": write_f}
TOOLS_DEF = [
    {"type":"function","function":{"name":"list_dir","parameters":{"type":"object","properties":{"d":{"type":"string"}}}}},
    {"type":"function","function":{"name":"read_f","parameters":{"type":"object","properties":{"f":{"type":"string"}},"required":["f"]}}},
    {"type":"function","function":{"name":"grep","parameters":{"type":"object","properties":{"pat":{"type":"string"},"d":{"type":"string"}},"required":["pat"]}}},
    {"type":"function","function":{"name":"write_f","parameters":{"type":"object","properties":{"f":{"type":"string"},"c":{"type":"string"}},"required":["f","c"]}}}
]

def call(msgs):
    payload = {
        "model": MODEL,
        "messages": msgs,
        "tools": TOOLS_DEF,
        "tool_choice": "auto",
        "temperature": 0.0 # Plus de précision, moins d'hallucinations de format
    }
    for _ in range(3):
        res = requests.post(API_URL, headers={"Authorization":f"Bearer {API_KEY}"}, json=payload)
        if res.status_code == 429:
            time.sleep(10); continue
        if res.status_code != 200: raise Exception(f"Err {res.status_code}: {res.text}")
        return res.json()

def chat():
    # Instruction de formatage stricte pour Llama 3.3
    sys_p = f"Archi AetherFlow. Root: {ROOT}. CALL TOOLS ONLY IN JSON FORMAT. BE CONCISE."
    hist = [{"role": "system", "content": sys_p}]
    console.print(Panel(f"[bold cyan]GA-70B[/bold cyan] | TPM: 12K | Context: 128K\nRoot: {ROOT}"))

    while True:
        try:
            u = Prompt.ask("\n[bold cyan]ARCHI ❯[/bold cyan]")
            if u.lower() in ["exit","quit"]: break
            hist.append({"role":"user", "content":u})
            if len(hist) > 6: hist = [hist[0]] + hist[-5:] # Garde l'historique très court
            
            run = True
            while run:
                with console.status("[yellow]...[/yellow]"):
                    ans = call(hist)
                    msg = ans['choices'][0]['message']
                if msg.get("tool_calls"):
                    hist.append(msg)
                    for tc in msg["tool_calls"]:
                        fn = tc['function']['name']
                        args = json.loads(tc['function']['arguments'])
                        console.print(f"[dim]🛠 {fn}({args})[/dim]")
                        res = TOOLS_MAP.get(fn, lambda **x: "Err")(**args)
                        hist.append({"role":"tool", "tool_call_id":tc['id'], "name":fn, "content":str(res)})
                else:
                    if msg.get("content"):
                        console.print(Panel(msg["content"], border_style="green"))
                        hist.append({"role":"assistant", "content":msg["content"]})
                    run = False
        except Exception as e: console.print(f"[red]{e}[/red]")

if __name__ == "__main__": chat()
