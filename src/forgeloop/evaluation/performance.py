import math


def unit_interval(value: float, name: str) -> float:
    """Reject invalid measurements instead of silently generating a score."""
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return float(value)


def calculate_performance_score(orbit: float, speed: float, integrity: float) -> float:
    """Local weighted score [0, 100]; not a verified competition evaluator."""
    orbit = unit_interval(orbit, "orbit")
    speed = unit_interval(speed, "speed")
    integrity = unit_interval(integrity, "integrity")
    return 100.0 * (0.70 * orbit + 0.20 * speed + 0.10 * integrity)
