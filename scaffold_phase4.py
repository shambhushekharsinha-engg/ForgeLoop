import os

# Ensure directories exist
os.makedirs("src/forgeloop/decisions", exist_ok=True)
os.makedirs("src/forgeloop/experiments", exist_ok=True)

decisions_files = {
    "__init__.py": "",
    "proposal.py": """from dataclasses import dataclass

@dataclass
class AIProposal:
    id: str
    strategy: str
    expected_benefit: str
""",
    "decision.py": """from enum import Enum
from dataclasses import dataclass

class DecisionStatus(Enum):
    ACCEPT = "ACCEPT"
    MODIFY = "MODIFY"
    REJECT = "REJECT"

@dataclass
class HumanDecision:
    status: DecisionStatus
    reason: str
    modified_strategy: str = None
""",
    "ledger.py": """import json
from pathlib import Path
from .proposal import AIProposal
from .decision import HumanDecision

class DecisionLedger:
    def __init__(self, log_path="docs/DECISIONS.md"):
        self.log_path = Path(log_path)
    
    def log_decision(self, exp_id: str, problem: str, proposal: AIProposal, decision: HumanDecision):
        # Implementation to append to markdown log
        pass
""",
}

experiments_files = {
    "__init__.py": "",
    "result.py": """from dataclasses import dataclass

@dataclass
class ExperimentResult:
    orbit_progress: float
    speed_score: float
    integrity: float
    performance_score: float
    cost_penalty: float
    final_score: float
""",
    "experiment.py": """from dataclasses import dataclass
from typing import Optional
from ..decisions.proposal import AIProposal
from ..decisions.decision import HumanDecision
from .result import ExperimentResult
from ..data.machine import BSGMachine
from ..data.trajectory import Trajectory

@dataclass
class Experiment:
    id: str
    build_mode: str  # 'Autopilot' or 'Copilot'
    hypothesis: str
    proposal: AIProposal
    human_decision: HumanDecision
    machine_raw: Optional[BSGMachine] = None
    machine_tuned: Optional[BSGMachine] = None
    trajectory: Optional[Trajectory] = None
    result: Optional[ExperimentResult] = None
    notes: str = ""
""",
    "registry.py": """class ExperimentRegistry:
    def __init__(self):
        self.experiments = {}
    
    def register(self, experiment):
        self.experiments[experiment.id] = experiment
        
    def get_next_id(self):
        return f"EXP-{len(self.experiments) + 1:03d}"
""",
    "runner.py": """from .experiment import Experiment
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
""",
}

for fname, content in decisions_files.items():
    with open(f"src/forgeloop/decisions/{fname}", "w", encoding="utf-8") as f:
        f.write(content)

for fname, content in experiments_files.items():
    with open(f"src/forgeloop/experiments/{fname}", "w", encoding="utf-8") as f:
        f.write(content)

# Update evaluation stub for the synthetic run
eval_cost_stub = """def estimate_token_cost(transcript_text: str) -> float:
    # Stub: returns length / 100 as dummy token cost for phase 5 validation
    return len(transcript_text) / 100.0
"""
with open("src/forgeloop/evaluation/cost.py", "w", encoding="utf-8") as f:
    f.write(eval_cost_stub)
