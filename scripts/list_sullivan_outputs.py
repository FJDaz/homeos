#!/usr/bin/env python3
"""
Script pour lister tous les outputs générés par Sullivan Kernel.
"""
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel

console = Console()


def find_sullivan_outputs():
    """Trouve tous les outputs Sullivan dans le projet."""
    project_root = Path(__file__).parent.parent
    
    outputs = {
        "temporary_outputs": [],
        "local_cache": [],
        "elite_library": [],
        "devmode_results": [],
        "designermode_results": [],
        "plans": [],
        "validation_outputs": []
    }
    
    # 1. Outputs temporaires dans /tmp
    tmp_sullivan = Path("/tmp/sullivan_outputs")
    if tmp_sullivan.exists():
        for plan_dir in tmp_sullivan.iterdir():
            if plan_dir.is_dir():
                outputs["temporary_outputs"].append({
                    "path": str(plan_dir),
                    "name": plan_dir.name,
                    "files": list(plan_dir.rglob("*.txt"))
                })
    
    # 2. Plans temporaires
    tmp_plans = Path("/tmp/sullivan_plans")
    if tmp_plans.exists():
        for plan_file in tmp_plans.glob("*.json"):
            outputs["plans"].append({
                "path": str(plan_file),
                "name": plan_file.name,
                "size": plan_file.stat().st_size
            })
    
    # 3. Cache local
    cache_dir = Path.home() / ".aetherflow" / "components"
    if cache_dir.exists():
        for user_dir in cache_dir.iterdir():
            if user_dir.is_dir():
                user_components = list(user_dir.glob("*.json"))
                if user_components:
                    outputs["local_cache"].append({
                        "user_id": user_dir.name,
                        "path": str(user_dir),
                        "count": len(user_components),
                        "components": [c.name for c in user_components[:5]]  # Top 5
                    })
    
    # 4. Elite Library
    elite_dir = project_root / "components" / "elite"
    if elite_dir.exists():
        elite_components = list(elite_dir.glob("*.json"))
        archived_components = list((elite_dir / "archived").glob("*.json")) if (elite_dir / "archived").exists() else []
        
        outputs["elite_library"] = {
            "path": str(elite_dir),
            "active_count": len(elite_components),
            "archived_count": len(archived_components),
            "components": [c.name for c in elite_components[:10]]  # Top 10
        }
    
    # 5. Résultats DevMode
    output_dir = project_root / "output"
    if output_dir.exists():
        for result_dir in output_dir.iterdir():
            if result_dir.is_dir():
                result_file = result_dir / "sullivan_result.json"
                if result_file.exists():
                    outputs["devmode_results"].append({
                        "path": str(result_file),
                        "name": result_dir.name,
                        "size": result_file.stat().st_size,
                        "modified": datetime.fromtimestamp(result_file.stat().st_mtime)
                    })
                
                designer_file = result_dir / "sullivan_designer_result.json"
                if designer_file.exists():
                    outputs["designermode_results"].append({
                        "path": str(designer_file),
                        "name": result_dir.name,
                        "size": designer_file.stat().st_size,
                        "modified": datetime.fromtimestamp(designer_file.stat().st_mtime)
                    })
    
    # 6. Plans JSON sources
    plans_dir = project_root / "Backend" / "Notebooks" / "benchmark_tasks"
    if plans_dir.exists():
        for plan_file in plans_dir.glob("sullivan*.json"):
            outputs["plans"].append({
                "path": str(plan_file),
                "name": plan_file.name,
                "size": plan_file.stat().st_size,
                "type": "source"
            })
    
    # 7. Outputs validation
    tmp_validation = Path("/tmp/sullivan_validation_outputs")
    if tmp_validation.exists():
        for validation_dir in tmp_validation.iterdir():
            if validation_dir.is_dir():
                outputs["validation_outputs"].append({
                    "path": str(validation_dir),
                    "name": validation_dir.name
                })
    
    return outputs


def display_outputs(outputs):
    """Affiche les outputs de manière organisée."""
    console.print(Panel.fit(
        "[bold cyan]📁 Répertoire des Outputs Sullivan Kernel[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    # Tree structure
    tree = Tree("📦 Outputs Sullivan Kernel")
    
    # 1. Outputs temporaires
    if outputs["temporary_outputs"]:
        tmp_branch = tree.add("🔧 [yellow]Outputs Temporaires[/yellow] (/tmp/sullivan_outputs/)")
        for output in outputs["temporary_outputs"][:5]:  # Top 5
            tmp_branch.add(f"📄 {output['name']} ({len(output['files'])} fichiers)")
    else:
        tree.add("🔧 [dim]Aucun output temporaire[/dim]")
    
    # 2. Plans
    if outputs["plans"]:
        plans_branch = tree.add("📋 [blue]Plans JSON[/blue]")
        source_plans = [p for p in outputs["plans"] if p.get("type") == "source"]
        temp_plans = [p for p in outputs["plans"] if p.get("type") != "source"]
        
        if source_plans:
            source_sub = plans_branch.add("📚 Sources (Backend/Notebooks/benchmark_tasks/)")
            for plan in source_plans[:5]:
                source_sub.add(f"📄 {plan['name']}")
        
        if temp_plans:
            temp_sub = plans_branch.add("🔧 Temporaires (/tmp/sullivan_plans/)")
            for plan in temp_plans[:5]:
                temp_sub.add(f"📄 {plan['name']}")
    else:
        tree.add("📋 [dim]Aucun plan trouvé[/dim]")
    
    # 3. Cache local
    if outputs["local_cache"]:
        cache_branch = tree.add("💾 [green]Cache Local[/green] (~/.aetherflow/components/)")
        for cache in outputs["local_cache"]:
            cache_branch.add(f"👤 {cache['user_id']}: {cache['count']} composants")
    else:
        tree.add("💾 [dim]Cache local vide[/dim]")
    
    # 4. Elite Library
    if outputs["elite_library"]:
        elite = outputs["elite_library"]
        elite_branch = tree.add(f"⭐ [magenta]Elite Library[/magenta] ({elite['path']})")
        elite_branch.add(f"✅ Actifs: {elite['active_count']} composants")
        elite_branch.add(f"📦 Archivés: {elite['archived_count']} composants")
    else:
        tree.add("⭐ [dim]Elite Library vide[/dim]")
    
    # 5. Résultats DevMode
    if outputs["devmode_results"]:
        devmode_branch = tree.add("🔍 [cyan]Résultats DevMode[/cyan] (output/)")
        for result in sorted(outputs["devmode_results"], key=lambda x: x["modified"], reverse=True)[:5]:
            devmode_branch.add(f"📄 {result['name']}/sullivan_result.json")
    else:
        tree.add("🔍 [dim]Aucun résultat DevMode[/dim]")
    
    # 6. Résultats DesignerMode
    if outputs["designermode_results"]:
        designer_branch = tree.add("🎨 [yellow]Résultats DesignerMode[/yellow] (output/)")
        for result in sorted(outputs["designermode_results"], key=lambda x: x["modified"], reverse=True)[:5]:
            designer_branch.add(f"📄 {result['name']}/sullivan_designer_result.json")
    else:
        tree.add("🎨 [dim]Aucun résultat DesignerMode[/dim]")
    
    # 7. Outputs validation
    if outputs["validation_outputs"]:
        validation_branch = tree.add("✅ [green]Outputs Validation[/green] (/tmp/sullivan_validation_outputs/)")
        for validation in outputs["validation_outputs"][:5]:
            validation_branch.add(f"📄 {validation['name']}")
    else:
        tree.add("✅ [dim]Aucun output validation[/dim]")
    
    console.print(tree)
    console.print()
    
    # Tableau récapitulatif
    table = Table(title="📊 Statistiques", show_header=True, header_style="bold magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Nombre", justify="right", style="green")
    table.add_column("Emplacement", style="dim")
    
    table.add_row(
        "Outputs temporaires",
        str(len(outputs["temporary_outputs"])),
        "/tmp/sullivan_outputs/"
    )
    table.add_row(
        "Plans JSON",
        str(len(outputs["plans"])),
        "/tmp/sullivan_plans/ + Backend/Notebooks/"
    )
    table.add_row(
        "Cache local (utilisateurs)",
        str(len(outputs["local_cache"])),
        "~/.aetherflow/components/"
    )
    table.add_row(
        "Elite Library",
        f"{outputs['elite_library'].get('active_count', 0)} actifs, {outputs['elite_library'].get('archived_count', 0)} archivés" if outputs['elite_library'] else "0",
        "components/elite/"
    )
    table.add_row(
        "Résultats DevMode",
        str(len(outputs["devmode_results"])),
        "output/*/sullivan_result.json"
    )
    table.add_row(
        "Résultats DesignerMode",
        str(len(outputs["designermode_results"])),
        "output/*/sullivan_designer_result.json"
    )
    table.add_row(
        "Outputs validation",
        str(len(outputs["validation_outputs"])),
        "/tmp/sullivan_validation_outputs/"
    )
    
    console.print(table)
    console.print()


def main():
    """Fonction principale."""
    console.print("[yellow]Recherche des outputs Sullivan...[/yellow]")
    outputs = find_sullivan_outputs()
    display_outputs(outputs)
    
    # Sauvegarder dans un fichier JSON
    output_file = Path(__file__).parent.parent / "docs" / "references" / "sullivan_outputs_inventory.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convertir datetime en string pour JSON
    def serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(outputs, f, indent=2, default=serialize, ensure_ascii=False)
    
    console.print(f"[green]✓ Inventaire sauvegardé:[/green] {output_file}")


if __name__ == "__main__":
    main()
