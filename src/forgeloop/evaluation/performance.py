def calculate_performance_score(orbit: float, speed: float, integrity: float) -> float:
    """
    70% Orbit Progress, 20% Speed Score, 10% Structure Integrity
    Returns normalized score [0, 100].
    """
    return 100.0 * (0.70 * orbit + 0.20 * speed + 0.10 * integrity)
