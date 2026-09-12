import sys
from pathlib import Path
sys.path.insert(0, str(Path('src').absolute()))

from forgeloop.cli.dashboard import LeaderboardCLI
from forgeloop.experiments.registry import ExperimentRegistry
from forgeloop.experiments.experiment import Experiment
from forgeloop.experiments.result import ExperimentResult
from forgeloop.decisions.proposal import AIProposal
from forgeloop.decisions.decision import HumanDecision, DecisionStatus
from forgeloop.agents.compiler import AutopilotCompiler
from forgeloop.agents.scrubber import TranscriptScrubber

def run_showcase():
    print("Synthetic demonstration only. No game or AI provider is connected.")
    print("\n--- 1. DERIVED TRANSCRIPT DEMO ---")
    raw_transcript = "Here is the block payload: ```json\n{'block': 'wheel', 'x': 0, 'y': 10}\n``` We built it."
    scrubber = TranscriptScrubber()
    cleaned = scrubber.scrub(raw_transcript)
    print(f"RAW (Length: {len(raw_transcript)}):\n{raw_transcript}")
    print(f"\nSCRUBBED (Length: {len(cleaned)}):\n{cleaned}")
    
    print("\n--- 2. THE AUTOPILOT COMPILER ---")
    prop = AIProposal(id="AI-042", strategy="Quad-symmetry with staged decouplers and aerodynamic shielding.", expected_benefit="Perfect balance")
    dec = HumanDecision(status=DecisionStatus.ACCEPT, reason="Illustrative approval for this synthetic demo")
    best_exp = Experiment(id="EXP-042", build_mode="Copilot", hypothesis="Staging works", proposal=prop, human_decision=dec)
    
    # Illustrative fixture, not a measured flight result.
    best_exp.result = ExperimentResult(0.95, 0.88, 1.0, 94.1, 2.5, 93.6)
    compiler = AutopilotCompiler()
    mega_prompt = compiler.compile_megaprompt(best_exp)
    print("Candidate prompt from a synthetic example; eligibility is not established:")
    print(mega_prompt)
    
    print("\n--- 3. SYNTHETIC EXAMPLE LEADERBOARD ---")
    
    exp2 = Experiment(id="EXP-043", build_mode="Autopilot", hypothesis="Compiled Run", proposal=prop, human_decision=dec)
    exp2.result = ExperimentResult(0.95, 0.88, 1.0, 94.1, 0.5, 107.6) # x1.15 and lower penalty!
    
    registry = ExperimentRegistry()
    registry.register(best_exp)
    registry.register(exp2)
    
    cli = LeaderboardCLI(registry)
    cli.render()

if __name__ == "__main__":
    run_showcase()
