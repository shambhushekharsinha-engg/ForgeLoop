import math

from ..decisions.decision import DecisionStatus
from ..experiments.experiment import Experiment


class AutopilotCompiler:
    def compile_megaprompt(self, successful_experiment: Experiment) -> str:
        """Prepare a candidate prompt from a reviewed, evaluated experiment.

        The caller selects the experiment; this does not certify success or eligibility.
        """
        decision = successful_experiment.human_decision
        if decision.status not in (DecisionStatus.ACCEPT, DecisionStatus.MODIFY):
            raise ValueError("A rejected or unreviewed experiment cannot be compiled")
        result = successful_experiment.result
        if result is None or not math.isfinite(result.final_score):
            raise ValueError("An evaluated experiment with a finite result is required")
        strategy = (
            decision.modified_strategy
            if decision.status == DecisionStatus.MODIFY
            else successful_experiment.proposal.strategy
        )
        if not isinstance(strategy, str) or not strategy.strip():
            raise ValueError(
                "An approved strategy is required; MODIFY needs modified_strategy"
            )

        mega_prompt = f"""[SYSTEM]
ROLE: Expert Aerospace AI (BuildArena S01)
OBJECTIVE: Construct a Besiege machine for stable orbital flight.
CONSTRAINTS: Preserve complete build history and conversation evidence.
STATUS: Candidate prompt only. Flight success and competition eligibility require verification.

REVIEWED STRATEGY (Derived from {successful_experiment.id}):
{strategy}

EXECUTION:
1. Initialize structural core.
2. Apply symmetry.
3. Attach propulsion as specified.
4. Save raw machine.
"""
        return mega_prompt
