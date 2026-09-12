"""Descriptive telemetry summaries and explicitly unverified test hypotheses."""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


class TelemetryStrategist:
    def analyze_flight(self, trajectory_df: "pd.DataFrame") -> str:
        if trajectory_df.empty:
            return "[STRATEGIST] No telemetry data available."

        required = ('z', 'angular_progress', 'vz')
        missing = [field for field in required if field not in trajectory_df.columns]
        if missing:
            return f"[STRATEGIST] Missing telemetry fields: {', '.join(missing)}."
        values = {}
        for field in required:
            try:
                column = [float(value) for value in trajectory_df[field]]
            except (TypeError, ValueError):
                return f"[STRATEGIST] Invalid telemetry: {field} must contain finite numbers."
            if not all(math.isfinite(value) for value in column):
                return f"[STRATEGIST] Invalid telemetry: {field} must contain finite numbers."
            values[field] = column

        z, angles, vz = (values[field] for field in required)
        mean_vz = sum(vz) / len(vz)
        spread_vz = math.sqrt(sum((value - mean_vz) ** 2 for value in vz) / len(vz))
        lines = [
            '[STRATEGIST OBSERVATIONS]',
            f'Samples: {len(z)}.',
            f'Z coordinate: min {min(z):.3f}, max {max(z):.3f}, final {z[-1]:.3f}.',
            f'Angular progress change (last minus first): {angles[-1] - angles[0]:.3f}.',
            f'Vz population standard deviation: {spread_vz:.3f} (recorded units).',
            'Coordinate frame and angular units must be confirmed before interpreting these measurements.',
            'These measurements alone do not establish altitude, tumbling, orbital insertion, or stability.',
        ]
        if len(z) < 2:
            lines.append('Only one sample: flight trends cannot be assessed.')
        else:
            lines.append(
                'Hypothesis for investigation: compare changes in position and velocity with '
                'control inputs and orientation telemetry before changing propulsion or mass distribution.'
            )
        return '\n'.join(lines)
