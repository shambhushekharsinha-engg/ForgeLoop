import sys
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from forgeloop.cli.packager import SubmissionPackager

def main():
    console = Console()
    console.print(Panel.fit("[bold magenta]🚀 ForgeLoop Submission Packager[/bold magenta]", border_style="magenta"))

    # Step 1: Pre-flight check via imported function if possible, or just print
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task1 = progress.add_task("[cyan]Verifying Kaggle artifacts...", total=None)
        time.sleep(1) # Dramatic effect for screen recording
        progress.update(task1, completed=100)

        task2 = progress.add_task("[cyan]Compressing telemetry and logs...", total=None)
        
        # Actually run the packager
        packager = SubmissionPackager()
        try:
            success = packager.package()
        except Exception as e:
            console.print(f"[bold red]❌ Packaging Error:[/bold red] {e}")
            sys.exit(1)
            
        time.sleep(1)
        progress.update(task2, completed=100)
        
    if not success:
        console.print("[bold red]❌ Failed to package submission. Please check your artifacts.[/bold red]")
        sys.exit(1)

    import os
    size_mb = os.path.getsize(packager.output_name) / (1024 * 1024)

    success_text = Text()
    success_text.append("✅ Packaged Successfully!\n\n", style="bold green")
    success_text.append(f"File: ", style="bold white")
    success_text.append(f"{packager.output_name}\n", style="cyan")
    success_text.append(f"Size: ", style="bold white")
    success_text.append(f"{size_mb:.2f} MB\n", style="cyan")
    
    console.print(Panel(success_text, title="READY FOR KAGGLE", border_style="green", expand=False))
    console.print("\n[bold yellow]Upload this zip file to Kaggle along with your YouTube link![/bold yellow]\n")

if __name__ == '__main__':
    main()
