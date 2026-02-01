#!/usr/bin/env python3
"""
Démonstration Sullivan Kernel - Génération Frontend pour Homeos
Analyse le backend Homeos (AETHERFLOW) et génère le frontend correspondant
"""
import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
import json

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

from Backend.Prod.sullivan.modes.dev_mode import DevMode

console = Console()


async def demo_homeos_frontend():
    """Démonstration de génération de frontend pour Homeos."""
    
    console.print(Panel.fit(
        "[bold cyan]Sullivan Kernel[/] - Frontend pour Homeos\n"
        "[dim]Analyse du backend Homeos et génération du frontend correspondant[/]",
        border_style="cyan"
    ))
    console.print()
    
    # Chemin vers le backend Homeos (AETHERFLOW)
    backend_path = Path("Backend/Prod")
    output_path = Path("output/homeos_frontend")
    
    if not backend_path.exists():
        console.print(f"[red]✗ Backend path not found: {backend_path}[/red]")
        console.print("[yellow]Utilisation du chemin par défaut: Backend/Prod[/yellow]")
        backend_path = Path("Backend")
    
    console.print(f"[bold]Backend à analyser:[/bold] {backend_path.absolute()}")
    console.print(f"[bold]Sortie frontend:[/bold] {output_path.absolute()}")
    console.print()
    
    # Créer DevMode
    console.print("[yellow]Initialisation Sullivan DevMode...[/yellow]")
    dev_mode = DevMode(
        backend_path=backend_path,
        output_path=output_path,
        analyze_only=False,  # Générer le frontend
        non_interactive=True  # Mode non-interactif pour la démo
    )
    console.print("[green]✓ DevMode initialisé[/green]")
    console.print()
    
    # Exécuter workflow
    console.print("[yellow]Exécution du workflow 'Collaboration Heureuse'...[/yellow]")
    console.print("[dim](Analyse backend → Inférence fonction globale → Génération frontend)[/dim]")
    console.print()
    
    try:
        result = await dev_mode.run()
        
        if result["success"]:
            console.print("[green]✓ Workflow complété avec succès![/green]")
            console.print()
            
            # Afficher fonction globale
            if result.get("global_function"):
                gf = result["global_function"]
                console.print(Panel(
                    f"[bold]Type de produit:[/bold] {gf.get('product_type', 'N/A')}\n"
                    f"[bold]Acteurs:[/bold] {', '.join(gf.get('actors', []))}\n"
                    f"[bold]Flux métier:[/bold] {', '.join(gf.get('business_flows', []))}\n"
                    f"[bold]Cas d'usage:[/bold] {', '.join(gf.get('use_cases', []))}",
                    title="[bold blue]Fonction Globale Inférée[/bold blue]",
                    border_style="blue"
                ))
                console.print()
            
            # Afficher structure frontend
            if result.get("frontend_structure"):
                fs = result["frontend_structure"]
                console.print(Panel(
                    f"[bold]Structure frontend générée:[/bold]\n"
                    f"{json.dumps(fs, indent=2, ensure_ascii=False)[:500]}...",
                    title="[bold green]Structure Frontend[/bold green]",
                    border_style="green"
                ))
                console.print()
            
            # Afficher fichier résultat
            result_file = output_path / "sullivan_result.json"
            if result_file.exists():
                console.print(Panel(
                    f"[bold green]✓ Résultats sauvegardés:[/bold green]\n"
                    f"[cyan]{result_file.absolute()}[/cyan]\n\n"
                    f"Ce fichier contient:\n"
                    f"  • Fonction globale inférée\n"
                    f"  • Structure d'intention (étapes)\n"
                    f"  • Structure frontend complète (Corps → Organes → Molécules → Atomes)",
                    border_style="green"
                ))
                console.print()
            
            # Générer composants frontend réels via ComponentRegistry
            console.print("[yellow]Génération de composants frontend réels...[/yellow]")
            from Backend.Prod.sullivan.registry import ComponentRegistry
            
            registry = ComponentRegistry()
            
            # Générer quelques composants clés basés sur la fonction globale
            if result.get("ui_intent"):
                ui_intent = result["ui_intent"]
                proposed_steps = ui_intent.get("proposed_steps", [])
                
                if proposed_steps:
                    console.print(f"[cyan]Étapes proposées:[/cyan] {', '.join(proposed_steps[:3])}")
                    console.print()
                    
                    # Générer composant pour la première étape
                    if proposed_steps:
                        first_step = proposed_steps[0]
                        intent = f"Interface pour étape: {first_step}"
                        
                        console.print(f"[yellow]Génération composant: {intent}[/yellow]")
                        component = await registry.get_or_generate(
                            intent=intent,
                            user_id="homeos_demo"
                        )
                        
                        console.print(f"[green]✓ Composant généré: {component.name}[/green]")
                        console.print(f"  Score Sullivan: {component.sullivan_score:.1f}")
                        console.print(f"  Catégorie: {component.category or 'Non classifié'}")
                        console.print()
                        
                        # Chercher le code HTML/CSS/JS généré
                        output_base = Path("/tmp/sullivan_outputs")
                        if not output_base.exists():
                            output_base = Path("output")
                        
                        component_outputs = list(output_base.rglob("*component*"))
                        
                        if component_outputs:
                            for output_dir in component_outputs[:1]:  # Premier résultat
                                html_files = list(output_dir.rglob("*.html"))
                                css_files = list(output_dir.rglob("*.css"))
                                js_files = list(output_dir.rglob("*.js"))
                                
                                if html_files:
                                    html_file = html_files[0]
                                    console.print(f"[cyan]Code HTML trouvé: {html_file}[/cyan]")
                                    
                                    # Créer fichier de prévisualisation
                                    preview_file = output_path / "homeos_frontend_preview.html"
                                    
                                    html_content = html_file.read_text(encoding='utf-8')
                                    css_content = ""
                                    js_content = ""
                                    
                                    if css_files:
                                        css_content = css_files[0].read_text(encoding='utf-8')
                                    if js_files:
                                        js_content = js_files[0].read_text(encoding='utf-8')
                                    
                                    # Créer HTML complet
                                    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homeos - Frontend Généré par Sullivan</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <header>
        <h1>Homeos - Agence de Design Numérique</h1>
        <p>Frontend généré par Sullivan Kernel</p>
    </header>
    <main>
{html_content}
    </main>
    <footer>
        <p>Généré via AETHERFLOW + Sullivan Kernel</p>
    </footer>
    <script>
{js_content}
    </script>
</body>
</html>
"""
                                    preview_file.write_text(full_html, encoding='utf-8')
                                    
                                    console.print(Panel(
                                        f"[bold green]✓ Frontend Homeos généré![/bold green]\n\n"
                                        f"[cyan]Fichier HTML:[/cyan] {preview_file.absolute()}\n\n"
                                        f"[bold]Ouvrez ce fichier dans votre navigateur pour voir le résultat![/bold]",
                                        border_style="green"
                                    ))
                                    break
            
            console.print()
            console.print(Panel(
                "[bold]Résumé:[/bold]\n"
                f"  • Backend analysé: {backend_path}\n"
                f"  • Fonction globale: {gf.get('product_type', 'N/A') if result.get('global_function') else 'N/A'}\n"
                f"  • Structure frontend: Générée\n"
                f"  • Composants: Générés via ComponentRegistry\n"
                f"  • Résultats: {result_file if result_file.exists() else 'N/A'}",
                title="[bold cyan]Démonstration Complète[/bold cyan]",
                border_style="cyan"
            ))
        else:
            console.print(f"[red]✗ Erreur: {result.get('message', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]Erreur: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    asyncio.run(demo_homeos_frontend())
