import math

from .performance import unit_interval


def calculate_speed_score(trajectory, orbit_progress, *, reference_duration=None) -> float:
    """Local progress-per-duration proxy with a required user-supplied baseline.

    score = min(1, orbit_progress * reference_duration / elapsed_seconds).
    The reference duration and formula are not official competition rules.
    """
    trajectory.validate()
    progress = unit_interval(orbit_progress, 'orbit_progress')
    if reference_duration is None or not math.isfinite(reference_duration) or reference_duration <= 0:
        raise ValueError("Speed estimation requires a finite positive reference_duration in seconds")
    times = trajectory.data['timestamp']
    elapsed = float(times.iloc[-1] - times.iloc[0])
    return min(1.0, progress * reference_duration / elapsed)
