from rich.console import Console
from rich.table import Table
from ..experiments.registry import ExperimentRegistry

class LeaderboardCLI:
    def __init__(self, registry: ExperimentRegistry):
        self.registry = registry
        self.console = Console()
        
    def render(self):
        table = Table(title="ForgeLoop AI - Global Experiment Leaderboard", show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Exp ID", style="cyan")
        table.add_column("Mode", justify="center")
        table.add_column("Orbit %", justify="right")
        table.add_column("Speed %", justify="right")
        table.add_column("Cost Penalty", justify="right", style="red")
        table.add_column("Final Score", justify="right", style="green bold")
        
        # Sort experiments by final score descending
        sorted_exps = sorted(
            [e for e in self.registry.experiments.values() if e.result], 
            key=lambda x: x.result.final_score, 
            reverse=True
        )
        
        for rank, exp in enumerate(sorted_exps, 1):
            table.add_row(
                f"#{rank}",
                exp.id,
                exp.build_mode,
                f"{exp.result.orbit_progress * 100:.1f}%",
                f"{exp.result.speed_score * 100:.1f}%",
                f"-{exp.result.cost_penalty:.1f}",
                f"{exp.result.final_score:.1f}"
            )
            
        self.console.print(table)
