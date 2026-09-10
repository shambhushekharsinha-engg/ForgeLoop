from pathlib import Path

class BuildHistory:
    def __init__(self, history_path: Path, history_full_path: Path):
        self.history_path = history_path
        self.history_full_path = history_full_path
