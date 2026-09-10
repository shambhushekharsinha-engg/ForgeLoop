import json
from pathlib import Path
from .proposal import AIProposal
from .decision import HumanDecision

class DecisionLedger:
    def __init__(self, log_path="docs/DECISIONS.md"):
        self.log_path = Path(log_path)
    
    def log_decision(self, exp_id: str, problem: str, proposal: AIProposal, decision: HumanDecision):
        # Implementation to append to markdown log
        pass
