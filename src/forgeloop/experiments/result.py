from dataclasses import dataclass

@dataclass
class ExperimentResult:
    orbit_progress: float
    speed_score: float
    integrity: float
    performance_score: float
    cost_penalty: float
    final_score: float
