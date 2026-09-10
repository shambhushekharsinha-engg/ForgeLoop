import pytest
from forgeloop.decisions.proposal import AIProposal
from forgeloop.decisions.decision import HumanDecision, DecisionStatus
from forgeloop.experiments.experiment import Experiment
from forgeloop.experiments.runner import ExperimentRunner

def test_experiment_creation():
    """Test that an experiment successfully binds AI proposals to Human decisions."""
    prop = AIProposal(id="AI-999", strategy="Add thrusters", expected_benefit="Speed")
    dec = HumanDecision(status=DecisionStatus.REJECT, reason="Too heavy")
    
    exp = Experiment(
        id="EXP-999",
        build_mode="Copilot",
        hypothesis="Thrusters make go fast",
        proposal=prop,
        human_decision=dec
    )
    
    assert exp.id == "EXP-999"
    assert exp.human_decision.status == DecisionStatus.REJECT

def test_experiment_runner_attaches_results():
    """Test that the runner correctly evaluates telemetry and attaches a result object."""
    prop = AIProposal(id="AI-001", strategy="Basic", expected_benefit="Orbit")
    dec = HumanDecision(status=DecisionStatus.ACCEPT, reason="Valid")
    exp = Experiment(id="EXP-001", build_mode="Autopilot", hypothesis="Test", proposal=prop, human_decision=dec)
    
    runner = ExperimentRunner()
    # Provide synthetic flight telemetry and a transcript of 500 chars (penalty = 5.0 in our stub)
    result = runner.evaluate_experiment(exp, orbit=0.5, speed=0.5, integrity=1.0, transcript="A"*500)
    
    assert exp.result is not None
    # Perf = 100 * (0.7*0.5 + 0.2*0.5 + 0.1*1.0) = 55.0
    # Cost = 5.0. Base = 55 - (0.2 * 5) = 54.0. Autopilot = 54.0 * 1.15 = 62.1
    assert exp.result.performance_score == pytest.approx(55.0)
    assert exp.result.final_score == pytest.approx(62.1)
