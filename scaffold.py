import os

data_dir = "src/forgeloop/data"
eval_dir = "src/forgeloop/evaluation"

data_files = {
    "__init__.py": "",
    "machine.py": """from dataclasses import dataclass
from pathlib import Path

@dataclass
class BSGMachine:
    filepath: Path
    is_raw: bool

    def validate_exists(self) -> bool:
        return self.filepath.exists()
""",
    "trajectory.py": """import pandas as pd
from pathlib import Path

class Trajectory:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        if self.filepath.exists():
            self.data = pd.read_csv(filepath)
        else:
            self.data = pd.DataFrame()

    @property
    def is_valid(self):
        return not self.data.empty
""",
    "history.py": """from pathlib import Path

class BuildHistory:
    def __init__(self, history_path: Path, history_full_path: Path):
        self.history_path = history_path
        self.history_full_path = history_full_path
""",
    "transcript.py": """from pathlib import Path

class ChatTranscript:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def read_text(self) -> str:
        if self.filepath.exists():
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ''
""",
    "submission.py": """from dataclasses import dataclass
from .machine import BSGMachine
from .trajectory import Trajectory
from .history import BuildHistory
from .transcript import ChatTranscript

@dataclass
class SubmissionPackage:
    machine_raw: BSGMachine
    machine_tuned: BSGMachine
    trajectory: Trajectory
    history: BuildHistory
    transcript: ChatTranscript
""",
    "validators.py": """def validate_no_geometry_changes(machine_raw, machine_tuned):
    # TODO: Implement strict checking that block positions/types didn't change
    pass
""",
}

eval_files = {
    "__init__.py": "",
    "orbit.py": '''def calculate_orbit_progress(trajectory) -> float:
    """Calculates Orbit Progress (max 1.0 for 3 full periods/1080 degrees)."""
    return 0.0
''',
    "speed.py": '''def calculate_speed_score(trajectory, orbit_progress) -> float:
    """Rewards entries that achieve valid orbital progress faster. [0, 1]"""
    return 0.0
''',
    "integrity.py": '''def calculate_integrity(trajectory) -> float:
    """Fraction of original tracked blocks still connected to the Starting Block."""
    return 0.0
''',
    "performance.py": '''def calculate_performance_score(orbit: float, speed: float, integrity: float) -> float:
    """
    70% Orbit Progress, 20% Speed Score, 10% Structure Integrity
    Returns normalized score [0, 100].
    """
    return 100.0 * (0.70 * orbit + 0.20 * speed + 0.10 * integrity)
''',
    "cost.py": '''def estimate_token_cost(transcript_text: str) -> float:
    """Estimates the cost penalty using tiktoken cl100k_base (simulated)."""
    return 0.0
''',
    "final_score.py": '''def calculate_final_score(performance_score: float, cost_penalty: float, build_mode: str = 'Copilot') -> float:
    """
    Formula: max(0, PerformanceScore - 0.20 * CostPenalty) * BuildModeCoefficient
    """
    coefficient = 1.15 if build_mode.upper() == 'AUTOPILOT' else 1.00
    base_score = max(0.0, performance_score - (0.20 * cost_penalty))
    return base_score * coefficient
''',
}

for d, files in [(data_dir, data_files), (eval_dir, eval_files)]:
    os.makedirs(d, exist_ok=True)
    for fname, content in files.items():
        with open(os.path.join(d, fname), "w", encoding="utf-8") as f:
            f.write(content)
