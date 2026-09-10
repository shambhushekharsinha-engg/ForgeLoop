import sys
from pathlib import Path
sys.path.insert(0, str(Path('src').absolute()))

from forgeloop.decisions.proposal import AIProposal
from forgeloop.decisions.decision import HumanDecision, DecisionStatus
from forgeloop.experiments.experiment import Experiment
from forgeloop.experiments.runner import ExperimentRunner

def run_simulation():
    print("Initializing ForgeLoop Experiment Engine (Phase 5 Validation)...")
    
    # 1. Create AI Proposal
    proposal = AIProposal(
        id="AI-001",
        strategy="Increase symmetry in the first stage and use 4 basic wheels for initial orientation.",
        expected_benefit="Improved structural survival before orbital insertion."
    )
    
    # 2. Human Review & Decision
    decision = HumanDecision(
        status=DecisionStatus.ACCEPT,
        reason="Hypothesis matches known Besiege physics for center of mass stabilization."
    )
    
    # 3. Create Experiment
    exp = Experiment(
        id="EXP-001",
        build_mode="Autopilot",
        hypothesis="A more stable first-stage configuration will increase orbital survival.",
        proposal=proposal,
        human_decision=decision
    )
    
    # 4. Simulate Flight & Run Evaluation
    # Orbit: 0.824 (82.4%), Speed: 0.167 (16.7%), Integrity: 0.092 (9.2%)
    # Let's map directly to the user's example values.
    # Wait, the user had: Orbit 82.4, Speed 16.7, Integrity 9.2, Performance 108.3? 
    # Actually, user's example: 100 * (0.7*82.4 + 0.2*16.7 + 0.1*9.2) is not right if those are percentages. 
    # If orbit=82.4, speed=16.7, integrity=9.2, then performance = 70% of 82.4 + 20% of 16.7 + 10% of 9.2 = 57.68 + 3.34 + 0.92 = 61.94
    # The performance score is out of 100.
    
    runner = ExperimentRunner()
    
    # Using mock values to show evaluation math (0.824 = 82.4% orbit progress, etc.)
    orbit_val = 0.824
    speed_val = 0.835  # 83.5% speed
    integrity_val = 0.920 # 92.0% integrity
    
    # Mock transcript length to yield Cost Penalty of 4.1 (4.1 * 100 = 410 chars)
    transcript_mock = "A" * 410 
    
    result = runner.evaluate_experiment(
        exp=exp,
        orbit=orbit_val,
        speed=speed_val,
        integrity=integrity_val,
        transcript=transcript_mock
    )
    
    # 5. Output Dashboard
    print(f"\n+{'='*33}+")
    print(f"| FORGELOOP EXPERIMENT            |")
    print(f"+{'-'*33}+")
    print(f"| Experiment ID      {exp.id:<13}|")
    print(f"| AI Proposal        {exp.proposal.id:<13}|")
    print(f"| Decision           {exp.human_decision.status.value:<13}|")
    print(f"+{'-'*33}+")
    print(f"| Orbit Progress       {result.orbit_progress*100:4.1f}%      |")
    print(f"| Speed Score          {result.speed_score*100:4.1f}%      |")
    print(f"| Integrity            {result.integrity*100:4.1f}%      |")
    print(f"|                                 |")
    print(f"| Performance          {result.performance_score:5.1f}      |")
    print(f"| Cost Penalty         {result.cost_penalty:5.1f}      |")
    print(f"| Build Mode          {exp.build_mode:<12}|")
    print(f"| Coefficient            1.15     |")
    print(f"+{'-'*33}+")
    print(f"| PROJECTED SCORE       {result.final_score:5.1f}     |")
    print(f"+{'='*33}+")

if __name__ == '__main__':
    run_simulation()
