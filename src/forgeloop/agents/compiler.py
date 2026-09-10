from ..experiments.experiment import Experiment

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
