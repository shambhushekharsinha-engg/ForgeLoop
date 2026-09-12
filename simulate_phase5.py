import sys
from pathlib import Path

sys.path.insert(0, str(Path("src").absolute()))

from forgeloop.decisions.decision import DecisionStatus, HumanDecision
from forgeloop.decisions.proposal import AIProposal
from forgeloop.experiments.experiment import Experiment
from forgeloop.experiments.runner import ExperimentRunner


def run_simulation():
    # 1. Create AI Proposal
    proposal = AIProposal(
        id="AI-001",
        strategy="Increase symmetry in the first stage and use 4 basic wheels for initial orientation.",
        expected_benefit="Improved structural survival before orbital insertion.",
    )

    # 2. Human Review & Decision
    decision = HumanDecision(
        status=DecisionStatus.ACCEPT,
        reason="Hypothesis matches known Besiege physics for center of mass stabilization.",
    )

    # 3. Create Experiment
    exp = Experiment(
        id="EXP-001",
        build_mode="Autopilot",
        hypothesis="A more stable first-stage configuration will increase orbital survival.",
        proposal=proposal,
        human_decision=decision,
    )

    # Synthetic component scores demonstrate the local estimator.
    runner = ExperimentRunner()

    # Using mock values to show evaluation math (0.824 = 82.4% orbit progress, etc.)
    orbit_val = 0.824
    speed_val = 0.835  # 83.5% speed
    integrity_val = 0.920  # 92.0% integrity

    # Synthetic transcript for the offline token estimate.
    transcript_mock = "A" * 410

    result = runner.evaluate_experiment(
        exp=exp,
        orbit=orbit_val,
        speed=speed_val,
        integrity=integrity_val,
        transcript=transcript_mock,
    )

    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    console.print("[bold cyan]ForgeLoop synthetic score example — no game flight or official score[/bold cyan]\n")

    table = Table(title="FORGELOOP EXPERIMENT", show_header=False, title_style="bold magenta", border_style="cyan")
    table.add_row("Experiment ID", exp.id)
    table.add_row("AI Proposal", exp.proposal.id)
    table.add_row("Decision", exp.human_decision.status.value)
    table.add_section()
    table.add_row("Orbit Progress", f"[green]{result.orbit_progress*100:.1f}%[/green]")
    table.add_row("Speed Score", f"[green]{result.speed_score*100:.1f}%[/green]")
    table.add_row("Integrity", f"[green]{result.integrity*100:.1f}%[/green]")
    table.add_row("Performance", f"[bold white]{result.performance_score:.1f}[/bold white]")
    table.add_row("Cost Penalty", f"[red]{result.cost_penalty:.4f}[/red]")
    table.add_row("Build Mode", exp.build_mode)
    table.add_row("Coefficient", "1.15")
    table.add_section()
    table.add_row("[bold yellow]PROJECTED SCORE[/bold yellow]", f"[bold yellow]{result.final_score:.1f}[/bold yellow]")

    console.print(Panel(table, border_style="blue", expand=False))


if __name__ == "__main__":
    run_simulation()
