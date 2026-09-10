import pandas as pd
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
