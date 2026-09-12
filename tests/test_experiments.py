import pytest

from forgeloop.decisions.decision import DecisionStatus, HumanDecision
from forgeloop.decisions.proposal import AIProposal
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
        human_decision=dec,
    )

    assert exp.id == "EXP-999"
    assert exp.human_decision.status == DecisionStatus.REJECT


def test_experiment_runner_attaches_results():
    """Test that the runner correctly evaluates telemetry and attaches a result object."""
    prop = AIProposal(id="AI-001", strategy="Basic", expected_benefit="Orbit")
    dec = HumanDecision(status=DecisionStatus.ACCEPT, reason="Valid")
    exp = Experiment(
        id="EXP-001",
        build_mode="Autopilot",
        hypothesis="Test",
        proposal=prop,
        human_decision=dec,
    )

    runner = ExperimentRunner()
    # Provide synthetic flight telemetry and an offline transcript cost estimate.
    runner.evaluate_experiment(
        exp, orbit=0.5, speed=0.5, integrity=1.0, transcript="A" * 500
    )

    assert exp.result is not None
    # Perf = 100 * (0.7*0.5 + 0.2*0.5 + 0.1*1.0) = 55.0
    # 500 ASCII bytes estimate 125 tokens, a local penalty of 0.0125.
    assert exp.result.performance_score == pytest.approx(55.0)
    assert exp.result.final_score == pytest.approx((55 - 0.2 * 0.0125) * 1.15)


def test_registry_does_not_overwrite_or_reuse_sparse_ids():
    from types import SimpleNamespace

    from forgeloop.experiments.registry import ExperimentRegistry

    registry = ExperimentRegistry()
    experiment = SimpleNamespace(id="EXP-002")
    registry.register(experiment)
    assert registry.get_next_id() == "EXP-003"
    with pytest.raises(ValueError):
        registry.register(SimpleNamespace(id="EXP-002"))
    assert registry.experiments["EXP-002"] is experiment
    registry.register(SimpleNamespace(id="SIM-999"))
    assert registry.get_next_id() == "EXP-003"
