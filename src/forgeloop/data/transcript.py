from pathlib import Path

class ChatTranscript:
    def __init__(self, filepath: Path):
        self.filepath = filepath

    def read_text(self) -> str:
        if self.filepath.exists():
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ''
