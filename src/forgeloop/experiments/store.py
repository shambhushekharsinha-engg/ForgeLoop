"""Transactional experiment snapshots; hashes detect accidental evidence changes.

This is an application-level append-only store, not a cryptographic attestation
against someone who can rewrite the database and all its hashes.
"""

import hashlib
import json
import re
import sqlite3
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ..decisions.decision import DecisionStatus, HumanDecision
from ..decisions.proposal import AIProposal
from ..evaluation.final_score import calculate_final_score
from ..evaluation.performance import calculate_performance_score
from .experiment import Experiment
from .registry import ExperimentRegistry
from .result import ExperimentResult

MAX_ARTIFACT_BYTES = 20 * 1024 * 1024


def read_input(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Input must be a regular file: {path}")
    with path.open("rb") as stream:
        content = stream.read(MAX_ARTIFACT_BYTES + 1)
    if not content.strip() or len(content) > MAX_ARTIFACT_BYTES:
        raise ValueError(
            f"Input must be nonempty and at most {MAX_ARTIFACT_BYTES} bytes: {path}"
        )
    return content


class ExperimentStore:
    def __init__(self, path="runs/experiments.sqlite3"):
        self.path = Path(path).resolve()

    def _connect(self, create=False):
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        elif not self.path.is_file():
            raise ValueError(
                f"No experiment database at {self.path}; analyze a flight first"
            )
        # URI mode=rw prevents read commands from silently creating empty databases.
        connection = sqlite3.connect(
            self.path.as_uri() + "?mode=" + ("rwc" if create else "ro"),
            uri=True,
            timeout=15,
        )
        return connection

    def save(
        self,
        experiment,
        trajectory_bytes,
        transcript_bytes,
        *,
        evidence_kind,
        assumptions,
    ):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", experiment.id):
            raise ValueError(
                "Experiment ID must be 1-64 letters, digits, underscores or hyphens"
            )
        if evidence_kind not in ("measured", "synthetic"):
            raise ValueError(
                "Evidence kind must be measured or synthetic (user-declared)"
            )
        for content in (trajectory_bytes, transcript_bytes):
            if (
                not isinstance(content, bytes)
                or not content.strip()
                or len(content) > MAX_ARTIFACT_BYTES
            ):
                raise ValueError(
                    "Evidence must be nonempty bytes within the size limit"
                )
        if experiment.result is None:
            raise ValueError("An evaluated experiment is required")
        result = experiment.result
        performance = calculate_performance_score(
            result.orbit_progress, result.speed_score, result.integrity
        )
        expected = calculate_final_score(
            performance, result.cost_penalty, experiment.build_mode
        )
        if (
            abs(performance - result.performance_score) > 1e-9
            or abs(expected - result.final_score) > 1e-9
        ):
            raise ValueError("Result does not match its component scores")
        record = {
            "schema_version": 1,
            "id": experiment.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "hypothesis": experiment.hypothesis,
            "build_mode": experiment.build_mode,
            "proposal": asdict(experiment.proposal),
            "human_decision": {
                **asdict(experiment.human_decision),
                "status": experiment.human_decision.status.value,
            },
            "result": asdict(result),
            "notes": experiment.notes,
            "evidence_kind": evidence_kind,
            "official_scoring": False,
            "assumptions": assumptions,
            "sha256": {
                "trajectory.csv": hashlib.sha256(trajectory_bytes).hexdigest(),
                "chat_transcript.md": hashlib.sha256(transcript_bytes).hexdigest(),
            },
        }
        payload = json.dumps(record, allow_nan=False, sort_keys=True)
        with closing(self._connect(create=True)) as connection:
            try:
                with connection:
                    connection.execute(
                        "CREATE TABLE IF NOT EXISTS experiments (id TEXT PRIMARY KEY, payload TEXT NOT NULL, trajectory BLOB NOT NULL, transcript BLOB NOT NULL)"
                    )
                    connection.execute(
                        "INSERT INTO experiments VALUES (?, ?, ?, ?)",
                        (experiment.id, payload, trajectory_bytes, transcript_bytes),
                    )
            except sqlite3.IntegrityError as error:
                raise ValueError(
                    f"Experiment {experiment.id} already exists; choose a new ID"
                ) from error
        return record

    def records(self, evidence_kind=None):
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT id, payload, trajectory, transcript FROM experiments ORDER BY id"
            ).fetchall()
        finally:
            connection.close()
        result = []
        for exp_id, payload, trajectory, transcript in rows:
            record = json.loads(payload)
            if record.get("schema_version") != 1 or record.get("id") != exp_id:
                raise ValueError(f"Invalid stored record: {exp_id}")
            expected_hashes = {
                "trajectory.csv": hashlib.sha256(trajectory).hexdigest(),
                "chat_transcript.md": hashlib.sha256(transcript).hexdigest(),
            }
            if record.get("sha256") != expected_hashes:
                raise ValueError(f"Evidence checksum mismatch: {exp_id}")
            if evidence_kind is None or record["evidence_kind"] == evidence_kind:
                result.append(record)
        return result

    def registry(self, evidence_kind):
        registry = ExperimentRegistry()
        for record in self.records(evidence_kind):
            decision = dict(record["human_decision"])
            decision["status"] = DecisionStatus(decision["status"])
            registry.register(
                Experiment(
                    id=record["id"],
                    build_mode=record["build_mode"],
                    hypothesis=record["hypothesis"],
                    proposal=AIProposal(**record["proposal"]),
                    human_decision=HumanDecision(**decision),
                    result=ExperimentResult(**record["result"]),
                    notes=record["notes"],
                )
            )
        return registry
