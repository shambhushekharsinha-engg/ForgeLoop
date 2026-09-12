import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

def main():
    console = Console()
    source_dir = Path("submissions/latest")
    
    console.print(Panel.fit("[bold cyan]🚀 ForgeLoop Kaggle Pre-Flight Checklist[/bold cyan]", border_style="cyan"))
    
    if not source_dir.exists():
        console.print(f"[bold red]❌ Error: Submission directory '{source_dir}' does not exist.[/bold red]")
        console.print("   [yellow]Make sure you save your game artifacts there before packaging.[/yellow]")
        sys.exit(1)
        
    console.print(f"[green]Found submission directory:[/green] [bold]{source_dir}[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="dim", width=10)
    table.add_column("Artifact Required", min_width=30)
    table.add_column("Description", min_width=40)
    
    expected_files = [
        ("machine_raw.bsg", "Base unmodified machine from BuildArena"),
        ("machine_tuned.bsg", "Final optimized machine"),
        ("trajectory.csv", "Flight telemetry from official tracker"),
        ("build_history.json", "History of LLM/Human build steps"),
        ("build_history_full.json", "Full extended build history log"),
        ("chat_transcript.md", "Autopilot prompt compilation and thoughts")
    ]
    
    missing = False
    for file, desc in expected_files:
        if (source_dir / file).exists():
            table.add_row("[bold green]✅ OK", file, desc)
        else:
            table.add_row("[bold red]❌ MISSING", f"[red]{file}[/red]", f"[red]{desc}[/red]")
            missing = True
            
    console.print(table)
    
    if missing:
        console.print("\n[bold red]❌ Cannot package submission. Please add the missing artifacts.[/bold red]")
        sys.exit(1)
        
    console.print("\n[bold green]✅ All required artifacts are present and accounted for.[/bold green]")
    console.print(Panel.fit("Run [bold cyan]make package[/bold cyan] to securely zip your submission!", border_style="green"))
    
if __name__ == '__main__':
    main()
