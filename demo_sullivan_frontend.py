#!/usr/bin/env python3
"""
Démonstration Sullivan Kernel - Génération de frontend
Affiche le résultat HTML/CSS/JS généré par Sullivan
"""
import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

# Ajouter le chemin du projet
sys.path.insert(0, str(Path(__file__).parent))

from Backend.Prod.sullivan.registry import ComponentRegistry

console = Console()


async def demo_generate_frontend():
    """Démonstration de génération de frontend avec Sullivan."""
    
    console.print(Panel.fit(
        "[bold cyan]Sullivan Kernel[/] - Démonstration Frontend\n"
        "[dim]Génération de composant frontend via AETHERFLOW[/]",
        border_style="cyan"
    ))
    console.print()
    
    # Créer ComponentRegistry
    console.print("[yellow]Initialisation ComponentRegistry...[/yellow]")
    registry = ComponentRegistry()
    console.print("[green]✓ ComponentRegistry initialisé[/green]")
    console.print()
    
    # Intentions de test
    test_intents = [
        "Bouton d'appel à l'action pour landing page SaaS",
        "Formulaire de contact avec validation",
        "Barre de navigation responsive",
    ]
    
    console.print("[bold]Intents de test disponibles:[/bold]")
    for i, intent in enumerate(test_intents, 1):
        console.print(f"  {i}. {intent}")
    console.print()
    
    # Demander choix utilisateur
    try:
        choice = console.input("[bold cyan]Choisissez un intent (1-3) ou entrez votre propre intent: [/bold cyan]")
        
        if choice.isdigit() and 1 <= int(choice) <= len(test_intents):
            intent = test_intents[int(choice) - 1]
        else:
            intent = choice if choice else test_intents[0]
        
        console.print(f"\n[bold]Intent sélectionné:[/bold] {intent}")
        console.print()
        
        # Générer composant
        console.print("[yellow]Génération du composant frontend...[/yellow]")
        console.print("[dim](Cela peut prendre quelques secondes via AETHERFLOW)[/dim]")
        console.print()
        
        component = await registry.get_or_generate(
            intent=intent,
            user_id="demo_user"
        )
        
        console.print("[green]✓ Composant généré avec succès![/green]")
        console.print()
        
        # Afficher métadonnées
        console.print(Panel(
            f"[bold]Nom:[/bold] {component.name}\n"
            f"[bold]Score Sullivan:[/bold] {component.sullivan_score:.1f}/100\n"
            f"[bold]Performance:[/bold] {component.performance_score}/100\n"
            f"[bold]Accessibilité:[/bold] {component.accessibility_score}/100\n"
            f"[bold]Écologie:[/bold] {component.ecology_score}/100\n"
            f"[bold]Validation:[/bold] {component.validation_score}/100\n"
            f"[bold]Taille:[/bold] {component.size_kb} KB\n"
            f"[bold]Catégorie:[/bold] {component.category or 'Non classifié'}",
            title="[bold blue]Métadonnées du Composant[/bold blue]",
            border_style="blue"
        ))
        console.print()
        
        # Chercher le code généré dans les outputs AETHERFLOW
        # Le ComponentGenerator sauvegarde dans output_dir
        output_base = Path("output")
        component_outputs = list(output_base.rglob(f"*{component.name}*"))
        
        if component_outputs:
            console.print("[yellow]Recherche du code généré...[/yellow]")
            # Chercher fichiers HTML/CSS/JS dans les outputs
            for output_dir in component_outputs:
                html_files = list(output_dir.rglob("*.html"))
                css_files = list(output_dir.rglob("*.css"))
                js_files = list(output_dir.rglob("*.js"))
                
                if html_files or css_files or js_files:
                    console.print(f"[green]✓ Code trouvé dans: {output_dir}[/green]")
                    console.print()
                    
                    # Afficher HTML
                    if html_files:
                        html_file = html_files[0]
                        with open(html_file, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        console.print(Panel(
                            Syntax(html_content, "html", theme="monokai", line_numbers=True),
                            title="[bold green]HTML Généré[/bold green]",
                            border_style="green"
                        ))
                        console.print()
                    
                    # Afficher CSS
                    if css_files:
                        css_file = css_files[0]
                        with open(css_file, 'r', encoding='utf-8') as f:
                            css_content = f.read()
                        console.print(Panel(
                            Syntax(css_content, "css", theme="monokai", line_numbers=True),
                            title="[bold blue]CSS Généré[/bold blue]",
                            border_style="blue"
                        ))
                        console.print()
                    
                    # Afficher JS
                    if js_files:
                        js_file = js_files[0]
                        with open(js_file, 'r', encoding='utf-8') as f:
                            js_content = f.read()
                        console.print(Panel(
                            Syntax(js_content, "javascript", theme="monokai", line_numbers=True),
                            title="[bold yellow]JavaScript Généré[/bold yellow]",
                            border_style="yellow"
                        ))
                        console.print()
                    
                    # Créer fichier HTML complet pour visualisation
                    if html_files:
                        html_file = html_files[0]
                        demo_html = output_dir / "demo_preview.html"
                        
                        # Créer HTML complet avec CSS et JS intégrés
                        html_preview = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component.name} - Sullivan Demo</title>
    <style>
"""
                        if css_files:
                            with open(css_files[0], 'r', encoding='utf-8') as f:
                                html_preview += f.read()
                        html_preview += """
    </style>
</head>
<body>
"""
                        with open(html_file, 'r', encoding='utf-8') as f:
                            html_preview += f.read()
                        
                        if js_files:
                            html_preview += "\n    <script>\n"
                            with open(js_files[0], 'r', encoding='utf-8') as f:
                                html_preview += f.read()
                            html_preview += "\n    </script>\n"
                        
                        html_preview += """
</body>
</html>
"""
                        with open(demo_html, 'w', encoding='utf-8') as f:
                            f.write(html_preview)
                        
                        console.print(Panel(
                            f"[bold green]✓ Fichier HTML de prévisualisation créé:[/bold green]\n"
                            f"[cyan]{demo_html}[/cyan]\n\n"
                            f"Ouvrez ce fichier dans votre navigateur pour voir le résultat!",
                            border_style="green"
                        ))
                    
                    break
        else:
            console.print("[yellow]⚠ Code généré non trouvé dans les outputs[/yellow]")
            console.print("[dim]Le composant a peut-être été trouvé dans le cache ou la bibliothèque[/dim]")
            console.print()
            console.print("[bold]Pour voir le code généré, utilisez:[/bold]")
            console.print("  - Mode DEV: python -m Backend.Prod.cli sullivan dev --backend-path <path>")
            console.print("  - API: POST /sullivan/search avec intent")
            console.print()
        
        # Afficher où le composant a été trouvé
        console.print(Panel(
            f"[bold]Composant trouvé/généré:[/bold] {component.name}\n"
            f"[bold]Source:[/bold] {'Généré via AETHERFLOW' if component.sullivan_score < 90 else 'Trouvé dans EliteLibrary'}\n"
            f"[bold]Prêt pour utilisation![/bold]",
            title="[bold green]Résultat[/bold green]",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[red]Démonstration annulée par l'utilisateur[/red]")
    except Exception as e:
        console.print(f"\n[red]Erreur: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    asyncio.run(demo_generate_frontend())
