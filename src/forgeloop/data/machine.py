from dataclasses import dataclass
from pathlib import Path

@dataclass
class BSGMachine:
    filepath: Path
    is_raw: bool

    def validate_exists(self) -> bool:
        path = Path(self.filepath)
        return path.is_file() and path.stat().st_size > 0
