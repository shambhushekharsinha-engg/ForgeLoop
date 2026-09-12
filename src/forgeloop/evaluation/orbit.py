import math


def calculate_orbit_progress(trajectory, target_degrees=1080.0) -> float:
    """Local net angular excursion proxy, capped at the requested target.

    Requires signed cumulative angular_progress in degrees. Oscillation does
    not count as repeated orbits. No altitude or game-validity claim is made.
    """
    trajectory.validate()
    if not math.isfinite(target_degrees) or target_degrees <= 0:
        raise ValueError("target_degrees must be finite and positive")
    if "angular_progress" not in trajectory.data:
        raise ValueError(
            "Orbit progress requires cumulative angular_progress in degrees"
        )
    angles = trajectory.data["angular_progress"]
    excursion = (angles - angles.iloc[0]).abs().max()
    if not math.isfinite(float(excursion)):
        raise ValueError("Angular excursion exceeds the finite numeric range")
    return min(1.0, float(excursion) / target_degrees)
