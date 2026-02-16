"""Simulation of Strategic Vigilance (BERT)."""
import httpx
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

async def simulate_veille():
    base_url = "http://127.0.0.1:8001"
    
    console.print(Panel.fit("[bold magenta]HOMEOS V2 - Strategic Vigilance (BERT)[/]", border_style="magenta"))
    console.print("\n[yellow]⏳ Requesting Strategic Veille Report from Aetherflow...[/]")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(f"{base_url}/v1/admin/veille/report")
            if resp.status_code == 200:
                data = resp.json()
                console.print("[green]✅ Veille Intelligence Report received.[/]\n")
                
                table = Table(title="Signal Analysis (BERT)", show_header=True, header_style="bold cyan")
                table.add_column("Signal Text", style="dim", width=50)
                table.add_column("BERT Label")
                table.add_column("Confidence", justify="right")
                
                for item in data.get("report", []):
                    analysis = item.get("analysis", {})
                    label = analysis.get("label", "N/A")
                    conf = analysis.get("confidence", 0)
                    
                    # Color coordination for labels
                    style = "white"
                    if label == "PRICE_ALERT": style = "bold red"
                    elif label == "PERFORMANCE_LEAP": style = "bold green"
                    elif label == "OPPORTUNITY": style = "bold yellow"
                    
                    table.add_row(item["text"], f"[{style}]{label}[/]", f"{conf:.2f}")
                
                console.print(table)
            else:
                console.print(f"[red]❌ Error: {resp.status_code} - {resp.text}[/]")
        except Exception as e:
            console.print(f"[red]❌ Connection failed: {e}[/]")

if __name__ == "__main__":
    asyncio.run(simulate_veille())


{
  "operations": [
    {
      "type": "add_function",
      "target": "scripts/simulate_veille.py",
      "position": "end",
      "code": """
async def simulate_veille_with_agent():
    base_url = "http://127.0.0.1:8001"
    
    console.print(Panel.fit("[bold magenta]HOMEOS V2 - Strategic Vigilance (BERT) with Agent[/]", border_style="magenta"))
    console.print("\n[yellow]⏳ Requesting Strategic Veille Report from Aetherflow with Agent...[/]")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(f"{base_url}/v1/admin/veille/report")
            if resp.status_code == 200:
                data = resp.json()
                console.print("[green]✅ Veille Intelligence Report received with Agent.[/]\n")
                
                table = Table(title="Signal Analysis (BERT) with Agent", show_header=True, header_style="bold cyan")
                table.add_column("Signal Text", style="dim", width=50)
                table.add_column("BERT Label")
                table.add_column("Confidence", justify="right")
                
                for item in data.get("report", []):
                    analysis = item.get("analysis", {})
                    label = analysis.get("label", "N/A")
                    conf = analysis.get("confidence", 0)
                    
                    # Color coordination for labels
                    style = "white"
                    if label == "PRICE_ALERT": style = "bold red"
                    elif label == "PERFORMANCE_LEAP": style = "bold green"
                    elif label == "OPPORTUNITY": style = "bold yellow"
                    
                    table.add_row(item["text"], f"[{style}]{label}[/]", f"{conf:.2f}")
                
                console.print(table)
            else:
                console.print(f"[red]❌ Error: {resp.status_code} - {resp.text}[/]")
        except Exception as e:
            console.print(f"[red]❌ Connection failed: {e}[/]")
"""
    },
    {
      "type": "add_function",
      "target": "scripts/simulate_veille.py",
      "position": "end",
      "code": """
def main():
    asyncio.run(simulate_veille())
    asyncio.run(simulate_veille_with_agent())

if __name__ == "__main__":
    main()
"""
    }
  ]
}