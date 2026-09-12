import math


def calculate_final_score(
    performance_score: float, cost_penalty: float, build_mode: str = "Copilot"
) -> float:
    """Local score projection using the repository's unverified weighting."""
    if not math.isfinite(performance_score) or not 0 <= performance_score <= 100:
        raise ValueError("performance_score must be finite and between 0 and 100")
    if not math.isfinite(cost_penalty) or cost_penalty < 0:
        raise ValueError("cost_penalty must be finite and nonnegative")
    mode = build_mode.strip().upper()
    if mode not in {"AUTOPILOT", "COPILOT"}:
        raise ValueError("build_mode must be Autopilot or Copilot")
    coefficient = 1.15 if mode == "AUTOPILOT" else 1.00
    return max(0.0, performance_score - 0.20 * cost_penalty) * coefficient
