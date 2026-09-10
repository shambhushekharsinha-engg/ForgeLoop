from .experiment import Experiment
from ..evaluation.performance import calculate_performance_score
from ..evaluation.final_score import calculate_final_score
from ..evaluation.cost import estimate_token_cost
from .result import ExperimentResult

class ExperimentRunner:
    def evaluate_experiment(self, exp: Experiment, orbit: float, speed: float, integrity: float, transcript: str):
        performance = calculate_performance_score(orbit, speed, integrity)
        cost = estimate_token_cost(transcript)
        final = calculate_final_score(performance, cost, exp.build_mode)
        
        exp.result = ExperimentResult(
            orbit_progress=orbit,
            speed_score=speed,
            integrity=integrity,
            performance_score=performance,
            cost_penalty=cost,
            final_score=final
        )
        return exp.result
