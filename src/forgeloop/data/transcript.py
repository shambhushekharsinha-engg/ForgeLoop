from pathlib import Path


class ChatTranscript:
    def __init__(self, filepath: Path):
        self.filepath = Path(filepath)

    def read_text(self) -> str:
        # Missing evidence must not silently look like a zero-cost conversation.
        return self.filepath.read_text(encoding="utf-8")
