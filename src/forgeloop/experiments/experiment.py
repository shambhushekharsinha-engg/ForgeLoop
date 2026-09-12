from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..data.machine import BSGMachine
from ..decisions.decision import HumanDecision
from ..decisions.proposal import AIProposal
from .result import ExperimentResult

if TYPE_CHECKING:
    from ..data.trajectory import Trajectory


@dataclass
class Experiment:
    id: str
    build_mode: str  # 'Autopilot' or 'Copilot'
    hypothesis: str
    proposal: AIProposal
    human_decision: HumanDecision
    machine_raw: BSGMachine | None = None
    machine_tuned: BSGMachine | None = None
    trajectory: Trajectory | None = None
    result: ExperimentResult | None = None
    notes: str = ""
