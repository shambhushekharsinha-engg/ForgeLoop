from dataclasses import dataclass
from pathlib import Path

@dataclass
class BSGMachine:
    filepath: Path
    is_raw: bool

    def validate_exists(self) -> bool:
        return self.filepath.exists()
