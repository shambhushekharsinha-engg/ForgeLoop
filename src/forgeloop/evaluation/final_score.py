def calculate_final_score(performance_score: float, cost_penalty: float, build_mode: str = 'Copilot') -> float:
    """
    Formula: max(0, PerformanceScore - 0.20 * CostPenalty) * BuildModeCoefficient
    """
    coefficient = 1.15 if build_mode.upper() == 'AUTOPILOT' else 1.00
    base_score = max(0.0, performance_score - (0.20 * cost_penalty))
    return base_score * coefficient
