from enum import Enum
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
