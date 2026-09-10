import pytest
from forgeloop.evaluation.performance import calculate_performance_score
from forgeloop.evaluation.final_score import calculate_final_score

def test_performance_score_perfect():
    """Test a perfect run: 100% orbit, speed, and integrity."""
    score = calculate_performance_score(orbit=1.0, speed=1.0, integrity=1.0)
    assert score == pytest.approx(100.0)

def test_performance_score_realistic():
    """Test realistic partial flight telemetry."""
    # 82.4% orbit, 83.5% speed, 92.0% integrity
    # 100 * (0.7*0.824 + 0.2*0.835 + 0.1*0.920) = 83.58
    score = calculate_performance_score(orbit=0.824, speed=0.835, integrity=0.920)
    assert round(score, 2) == 83.58

def test_performance_score_zero():
    """Test an exploding machine on the pad."""
    score = calculate_performance_score(orbit=0.0, speed=0.0, integrity=0.0)
    assert score == 0.0

def test_final_score_autopilot_multiplier():
    """Test that Autopilot correctly applies the x1.15 multiplier."""
    perf = 80.0
    cost = 10.0
    # Base: 80 - (0.2 * 10) = 78
    # Final: 78 * 1.15 = 89.7
    final = calculate_final_score(perf, cost, build_mode='Autopilot')
    assert round(final, 2) == 89.7

def test_final_score_copilot_multiplier():
    """Test that Copilot correctly applies the x1.00 multiplier."""
    perf = 80.0
    cost = 10.0
    # Base: 80 - (0.2 * 10) = 78
    # Final: 78 * 1.0 = 78.0
    final = calculate_final_score(perf, cost, build_mode='Copilot')
    assert final == 78.0

def test_final_score_floor():
    """Test that the base score cannot go below 0 due to heavy cost penalties."""
    perf = 10.0
    cost = 100.0 # 10 - 20 = -10
    final = calculate_final_score(perf, cost, build_mode='Copilot')
    assert final == 0.0
