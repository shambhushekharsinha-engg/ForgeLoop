import re
from pathlib import Path

from ..experiments.experiment import Experiment


class WriteupGenerator:
    def __init__(self, output_path="docs/KAGGLE_WRITEUP.md"):
        self.output_path = output_path

    def generate(self, machine_name: str, best_exp: Experiment, megaprompt: str):
        """Write an evidence-based draft; unknown run details remain explicit."""
        score = (
            best_exp.result.performance_score if best_exp.result else "Not evaluated"
        )
        fence = "`" * max(
            3, max((len(part) for part in re.findall(r"`+", megaprompt)), default=0) + 1
        )
        template = f"""# {machine_name}

## Track
- Intended track: Build with Agent
- Recorded build mode: {best_exp.build_mode}
- Eligibility: verify against the current competition rules and actual run history.

## Run Summary
- Experiment: {best_exp.id}
- Hypothesis: {best_exp.hypothesis}
- Local estimated performance score: {score}
- Notes: {best_exp.notes or "No run evidence recorded."}

Local scores and synthetic telemetry do not establish in-game flight performance.
Attach real flight evidence before making stability or orbit claims.

## Video
[ADD THE ACTUAL FLIGHT RECORDING LINK]

## LLM / Agent Setup
- Model and provider: [RECORD WHAT WAS ACTUALLY USED]
- Agent tools and game integration: [RECORD WHAT WAS ACTUALLY USED]
- Single-agent or multi-agent: [RECORD THE ACTUAL WORKFLOW]
- Visual feedback: [RECORD WHETHER IT WAS USED]

## Prompts and Workflow
Candidate prompt (not evidence of an executed run):
{fence}text
{megaprompt}
{fence}

Document the actual initial prompt, human interventions, and build history.
Compiling a prompt from a Copilot experiment does not establish Autopilot eligibility.

## Code and Tools
Repository: https://github.com/shambhushekharsinha-engg/ForgeLoop

## Notes
Preserve the complete original transcript. Verify allowed token exclusions against
the current competition rules before producing any derived counting copy.
"""
        output_path = Path(self.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(template, encoding="utf-8")
        print(f"[SUCCESS] Writeup draft generated at {output_path}")
        return output_path
