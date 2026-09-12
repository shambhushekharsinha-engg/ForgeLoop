from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from ..decisions.proposal import AIProposal
from ..decisions.decision import HumanDecision
from .result import ExperimentResult
from ..data.machine import BSGMachine
if TYPE_CHECKING:
    from ..data.trajectory import Trajectory

@dataclass
class Experiment:
    id: str
    build_mode: str  # 'Autopilot' or 'Copilot'
    hypothesis: str
    proposal: AIProposal
    human_decision: HumanDecision
    machine_raw: Optional[BSGMachine] = None
    machine_tuned: Optional[BSGMachine] = None
    trajectory: Optional[Trajectory] = None
    result: Optional[ExperimentResult] = None
    notes: str = ""
