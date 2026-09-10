from dataclasses import dataclass
from .machine import BSGMachine
from .trajectory import Trajectory
from .history import BuildHistory
from .transcript import ChatTranscript

@dataclass
class SubmissionPackage:
    machine_raw: BSGMachine
    machine_tuned: BSGMachine
    trajectory: Trajectory
    history: BuildHistory
    transcript: ChatTranscript
