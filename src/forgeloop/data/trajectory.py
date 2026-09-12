import csv
import io
from pathlib import Path
from collections.abc import Mapping

import numpy as np
import pandas as pd


class Trajectory:
    """A validated CSV in ForgeLoop's local telemetry format.

    timestamp is in seconds, positions are x/y/z, and optional
    angular_progress is signed cumulative degrees (not a wrapped angle).
    column_map explicitly maps local names to source CSV names; it does not
    convert units or certify an official tracker schema. The source CSV is
    never rewritten. The caller must supply seconds and cumulative degrees.
    """

    REQUIRED_COLUMNS = ('timestamp', 'x', 'y', 'z')

    def __init__(self, filepath: Path | str, *, column_map: Mapping[str, str] | None = None):
        self.filepath = Path(filepath)
        self._load_bytes(self.filepath.read_bytes(), column_map=column_map)

    @classmethod
    def from_bytes(cls, payload: bytes, *, source: str = "<memory>",
                   column_map: Mapping[str, str] | None = None):
        """Validate one immutable CSV snapshot without reopening its source."""
        trajectory = cls.__new__(cls)
        trajectory.filepath = Path(source)
        trajectory._load_bytes(payload, column_map=column_map)
        return trajectory

    def _load_bytes(self, payload: bytes, *, column_map=None):
        # pandas silently renames duplicate CSV headers; reject that ambiguity.
        header = next(csv.reader(io.StringIO(payload.decode("utf-8-sig"))), [])
        if not header or any(not name.strip() for name in header):
            raise ValueError("Trajectory requires nonempty CSV column names")
        if len(header) != len(set(header)):
            raise ValueError("Trajectory CSV column names must be unique")
        self.source_columns = tuple(header)
        self.column_map = dict(column_map or {})
        if any(not isinstance(k, str) or not isinstance(v, str) for k, v in self.column_map.items()):
            raise ValueError("column_map must map local column names to source column names")
        if len(set(self.column_map.values())) != len(self.column_map):
            raise ValueError("Each mapped local column must use a distinct source column")
        if set(self.column_map.values()) - set(header):
            raise ValueError("Mapped trajectory source columns are missing")
        self.data = pd.read_csv(io.BytesIO(payload))
        self.data = self.data.rename(columns={source: local for local, source in self.column_map.items()})
        self.validate()

    def validate(self):
        if not self.data.columns.is_unique:
            raise ValueError("Mapped trajectory columns must be unique")
        missing = set(self.REQUIRED_COLUMNS) - set(self.data.columns)
        if missing:
            raise ValueError(f"Missing trajectory columns: {', '.join(sorted(missing))}")
        if len(self.data) < 2:
            raise ValueError("Trajectory requires at least two samples")
        numeric = list(self.REQUIRED_COLUMNS) + [name for name in
            ('angular_progress', 'vx', 'vy', 'vz', 'connected_blocks', 'tracked_blocks')
            if name in self.data.columns]
        for name in numeric:
            if pd.api.types.is_bool_dtype(self.data[name]):
                raise ValueError(f"Trajectory {name} must be numeric, not boolean")
            values = pd.to_numeric(self.data[name], errors='raise')
            if pd.api.types.is_complex_dtype(values):
                raise ValueError(f"Trajectory {name} must contain real numbers")
            if not np.isfinite(values.to_numpy(dtype=float)).all():
                raise ValueError(f"Trajectory {name} must contain finite numbers")
            # Float arithmetic avoids unsigned subtraction wraparound.
            self.data[name] = values.astype(float)
        intervals = self.data['timestamp'].diff().iloc[1:]
        if not np.isfinite(intervals.to_numpy(dtype=float)).all() or not (intervals > 0).all():
            raise ValueError("Trajectory timestamps must be strictly increasing")

    @property
    def is_valid(self):
        try:
            self.validate()
        except (ValueError, TypeError):
            return False
        return True
