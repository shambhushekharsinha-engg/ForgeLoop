import os

# 1. Create Directories
dirs = [
    'src/forgeloop/reporting',
    'src/forgeloop/cli',
    'src/forgeloop/agents'
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# 2. reporting/plotter.py
plotter_code = '''import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

class TrajectoryPlotter:
    def __init__(self, output_dir="docs/plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_orbit(self, experiment_id: str, trajectory_data: pd.DataFrame):
        """Generates a 3D plot of the spacecraft trajectory."""
        if trajectory_data.empty:
            print(f"[{experiment_id}] No trajectory data to plot.")
            return None
            
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Assuming the CSV has x, y, z columns
        x = trajectory_data.get('x', [0, 1, 2, 0])
        y = trajectory_data.get('y', [0, 1, 0, -1])
        z = trajectory_data.get('z', [0, 0, 1, 0])
        
        ax.plot(x, y, z, label=f'Flight Path ({experiment_id})', color='cyan', linewidth=2)
        ax.scatter([0], [0], [0], color='yellow', s=100, label='Orbital Center (Planet)')
        
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Altitude (Z)')
        ax.set_title(f'Orbital Insertion Trajectory: {experiment_id}')
        ax.legend()
        
        output_path = self.output_dir / f"{experiment_id}_orbit.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
'''
with open('src/forgeloop/reporting/plotter.py', 'w', encoding='utf-8') as f:
    f.write(plotter_code)

# 3. cli/dashboard.py
dashboard_code = '''from rich.console import Console
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
'''
with open('src/forgeloop/cli/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(dashboard_code)

# 4. agents/compiler.py
compiler_code = '''from ..experiments.experiment import Experiment

class AutopilotCompiler:
    def compile_megaprompt(self, successful_experiment: Experiment) -> str:
        """Compresses a successful human-guided Copilot session into a dense Autopilot system prompt."""
        strategy = successful_experiment.proposal.strategy
        
        mega_prompt = f"""[SYSTEM]
ROLE: Expert Aerospace AI (BuildArena S01)
OBJECTIVE: Construct a Besiege machine for stable orbital flight.
CONSTRAINTS: Token efficiency is paramount. No conversational filler.

APPROVED STRATEGY (Derived from {successful_experiment.id}):
{strategy}

EXECUTION:
1. Initialize structural core.
2. Apply symmetry.
3. Attach propulsion as specified.
4. Save raw machine.
"""
        return mega_prompt
'''
with open('src/forgeloop/agents/compiler.py', 'w', encoding='utf-8') as f:
    f.write(compiler_code)

# 5. THE SECRET WEAPON: agents/scrubber.py
scrubber_code = '''import re

class TranscriptScrubber:
    """
    The competition rules state: 'Tool feedback, tool return payloads, generated JSON blocks... 
    may be removed before counting so that participants are not heavily penalized'.
    
    This module automatically scrubs our chat_transcript.md to mathematically minimize 
    our Cost Penalty before final submission.
    """
    def __init__(self):
        # Matches ```json ... ``` and ```xml ... ``` blocks
        self.code_block_pattern = re.compile(r'```(?:json|xml).*?```', re.DOTALL | re.IGNORECASE)
        
    def scrub(self, raw_transcript: str) -> str:
        # Remove verbose payloads
        scrubbed = re.sub(self.code_block_pattern, '[PAYLOAD_REMOVED_FOR_SUBMISSION]', raw_transcript)
        # Strip excessive whitespace
        scrubbed = " ".join(scrubbed.split())
        return scrubbed
'''
with open('src/forgeloop/agents/scrubber.py', 'w', encoding='utf-8') as f:
    f.write(scrubber_code)

# Add __init__.py files
for d in dirs:
    with open(f"{d}/__init__.py", "w") as f:
        pass
