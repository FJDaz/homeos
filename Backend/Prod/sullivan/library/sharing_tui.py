"""SharingTUI - Interface TUI pour confirmation de partage."""
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.text import Text
from loguru import logger

from ..models.component import Component
from ..models.categories import classify_component
from .elite_library import EliteLibrary


class SharingTUI:
    """
    Interface TUI (Text User Interface) pour confirmation de partage de composants.
    
    Utilise Rich pour affichage clair et confirmation utilisateur.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialise l'interface TUI de partage.

        Args:
            console: Instance Rich Console (optionnel)
        """
        self.console = console or Console()
        logger.info("SharingTUI initialized")

    def confirm_sharing(
        self,
        library: EliteLibrary,
        component: Component
    ) -> Optional[Component]:
        """
        Affiche les détails d'un composant et demande confirmation de partage.

        Args:
            library: Instance EliteLibrary
            component: Composant à partager

        Returns:
            Component si confirmé et ajouté, None sinon
        """
        logger.info(f"Showing sharing confirmation for component: {component.name}")
        
        # Classifier le composant si pas déjà fait
        if not component.category:
            component.category = classify_component(component).value
        
        self.console.print(Panel(
            Text("Confirmation de Partage de Composant", style="bold magenta"),
            title="[bold blue]Elite Library Sharing[/bold blue]",
            border_style="cyan"
        ))

        # Afficher détails du composant
        component_info = Text()
        component_info.append("Détails du composant à partager:\n", style="bold white")
        component_info.append(f"  Nom: [green]{component.name}[/green]\n")
        component_info.append(f"  Taille: [yellow]{component.size_kb} KB[/yellow]\n")
        component_info.append(f"  Score Sullivan: [blue]{component.sullivan_score:.1f}[/blue]\n")
        component_info.append(f"  Performance: [cyan]{component.performance_score}[/cyan]\n")
        component_info.append(f"  Accessibilité: [cyan]{component.accessibility_score}[/cyan]\n")
        component_info.append(f"  Validation: [cyan]{component.validation_score}[/cyan]\n")
        component_info.append(f"  Catégorie: [purple]{component.category}[/purple]\n")

        self.console.print(Panel(component_info, border_style="green"))

        try:
            # Demander confirmation
            confirmed = Confirm.ask(
                "[bold yellow]Voulez-vous ajouter ce composant à la Elite Library ?[/bold yellow]",
                default=False
            )

            if confirmed:
                success = library.add(component)
                if success:
                    self.console.print(f"\n[bold green]Composant '{component.name}' ajouté à la bibliothèque.[/bold green]")
                    logger.info(f"Component '{component.name}' shared successfully")
                    return component
                else:
                    self.console.print("\n[bold red]Le composant n'a pas pu être ajouté (score insuffisant).[/bold red]")
                    logger.warning(f"Component '{component.name}' could not be added (score too low)")
                    return None
            else:
                self.console.print("\n[bold yellow]Partage du composant annulé par l'utilisateur.[/bold yellow]")
                logger.info(f"Sharing cancelled by user for component: {component.name}")
                return None
                
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Opération annulée par l'utilisateur (Ctrl+C).[/bold red]")
            logger.info("Sharing cancelled by user (Ctrl+C)")
            return None
        except Exception as e:
            self.console.print(f"\n[bold red]Erreur lors de la confirmation : {e}[/bold red]")
            logger.error(f"Error in sharing confirmation: {e}", exc_info=True)
            return None


# Exemple d'utilisation
if __name__ == "__main__":
    from datetime import datetime
    
    library = EliteLibrary()
    tui = SharingTUI()
    
    component = Component(
        name="Test Component",
        sullivan_score=90.0,
        performance_score=95,
        accessibility_score=90,
        ecology_score=85,
        popularity_score=80,
        validation_score=95,
        size_kb=50,
        created_at=datetime.now(),
        user_id="test_user",
        category=None,
        last_used=None
    )
    
    result = tui.confirm_sharing(library, component)
    if result:
        print(f"Component shared: {result.name}")
