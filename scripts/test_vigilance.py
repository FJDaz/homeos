"""Test Script for HOMEOS V2 Vigilance Foundations."""
import httpx
import asyncio
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

async def test_vigilance():
    base_url = "http://127.0.0.1:8001" # Port Aetherflow
    
    console.print(Panel.fit("[bold cyan]HOMEOS V2 - Vigilance System Test[/]", border_style="cyan"))
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Test Status
        console.print("\n[yellow]⏳ Testing /v1/admin/status...[/]")
        try:
            resp = await client.get(f"{base_url}/v1/admin/status")
            if resp.status_code == 200:
                data = resp.json()
                console.print("[green]✅ Status retrieved successfully.[/]")
                
                # Table de santé
                table = Table(title="Health Snapshot", show_header=True, header_style="bold magenta")
                table.add_column("Provider", style="dim")
                table.add_column("Status")
                table.add_column("Latency (ms)", justify="right")
                
                health = data.get("health", {})
                if not health:
                    table.add_row("N/A", "Waiting for first check", "-")
                else:
                    for p, info in health.items():
                        table.add_row(p, info["status"], str(info["latency_ms"]))
                console.print(table)
                
                # Empreinte énergétique
                env = data.get("environment", {})
                console.print(f"\n[bold green]🌱 Impact Environnemental:[/] {env.get('estimated_co2_g', 0)} gCO2")
                console.print(f"[bold green]📊 Score de Frugalité:[/] {env.get('frugality_score', 0)}/100")
                
            else:
                console.print(f"[red]❌ Error status: {resp.status_code}[/]")
        except Exception as e:
            console.print(f"[red]❌ Connection failed: {e}[/]")

        # 2. Test Costs
        console.print("\n[yellow]⏳ Testing /v1/admin/costs...[/]")
        try:
            resp = await client.get(f"{base_url}/v1/admin/costs")
            if resp.status_code == 200:
                data = resp.json()
                console.print("[green]✅ Costs report retrieved.[/]")
                # console.print(data.get("report", "No report content"))
            else:
                console.print(f"[red]❌ Error costs: {resp.status_code}[/]")
        except Exception as e:
            console.print(f"[red]❌ Connection failed: {e}[/]")

if __name__ == "__main__":
    asyncio.run(test_vigilance())
