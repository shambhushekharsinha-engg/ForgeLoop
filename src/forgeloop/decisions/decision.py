from dataclasses import dataclass
from enum import Enum


class DecisionStatus(Enum):
    ACCEPT = "ACCEPT"
    MODIFY = "MODIFY"
    REJECT = "REJECT"


@dataclass
class HumanDecision:
    status: DecisionStatus
    reason: str
    modified_strategy: str = None
