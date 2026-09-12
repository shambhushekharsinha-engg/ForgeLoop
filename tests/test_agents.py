from types import SimpleNamespace

import pytest

from forgeloop.agents.compiler import AutopilotCompiler
from forgeloop.agents.strategist import TelemetryStrategist
from forgeloop.decisions.decision import DecisionStatus, HumanDecision


def experiment(status=DecisionStatus.ACCEPT, modified=None, result=True):
    return SimpleNamespace(
        id='EXP-001', proposal=SimpleNamespace(strategy='Original strategy'),
        human_decision=HumanDecision(status, 'Reviewed', modified),
        result=SimpleNamespace(final_score=0) if result else None,
    )


def test_compiler_requires_evaluation_and_review():
    compiler = AutopilotCompiler()
    with pytest.raises(ValueError, match='evaluated'):
        compiler.compile_megaprompt(experiment(result=False))
    with pytest.raises(ValueError, match='rejected'):
        compiler.compile_megaprompt(experiment(DecisionStatus.REJECT))
    exp = experiment()
    exp.result.final_score = float('nan')
    with pytest.raises(ValueError, match='finite'):
        compiler.compile_megaprompt(exp)


def test_compiler_uses_reviewed_modification_and_does_not_claim_success():
    compiler = AutopilotCompiler()
    with pytest.raises(ValueError, match='modified_strategy'):
        compiler.compile_megaprompt(experiment(DecisionStatus.MODIFY))
    prompt = compiler.compile_megaprompt(experiment(DecisionStatus.MODIFY, 'Corrected strategy'))
    assert 'Corrected strategy' in prompt
    assert 'Original strategy' not in prompt
    assert 'Candidate prompt only' in prompt
    assert 'Original strategy' in compiler.compile_megaprompt(experiment())


def test_strategist_describes_measurements_without_diagnosing_physics():
    pd = pytest.importorskip('pandas')
    frame = pd.DataFrame({'z': [100, 0], 'angular_progress': [500, 550], 'vz': [-50, 50]})
    summary = TelemetryStrategist().analyze_flight(frame)
    assert 'last minus first): 50.000' in summary
    assert 'population standard deviation: 50.000' in summary
    assert 'Hypothesis for investigation' in summary
    assert 'do not establish altitude' in summary
    assert 'Severe altitude loss detected' not in summary
    assert 'tumbling detected' not in summary
    assert 'SUCCESS' not in summary


def test_strategist_reports_missing_and_invalid_data():
    pd = pytest.importorskip('pandas')
    strategist = TelemetryStrategist()
    assert 'No telemetry' in strategist.analyze_flight(pd.DataFrame())
    assert 'Missing telemetry fields' in strategist.analyze_flight(pd.DataFrame({'z': [1]}))
    for invalid in [float('nan'), float('inf'), 'bad']:
        frame = pd.DataFrame({'z': [invalid], 'angular_progress': [1], 'vz': [1]})
        assert 'Invalid telemetry: z' in strategist.analyze_flight(frame)
    frame = pd.DataFrame({'z': [1], 'angular_progress': [1], 'vz': [1]})
    assert 'Only one sample' in strategist.analyze_flight(frame)
