def calculate_integrity(trajectory) -> float:
    """Local survival fraction using explicitly measured original block counts.

    connected_blocks must count only original tracked blocks still connected
    to the starting block. tracked_blocks is the initial tracked population.
    Position data alone cannot establish structural integrity.
    """
    trajectory.validate()
    required = {'connected_blocks', 'tracked_blocks'}
    if not required.issubset(trajectory.data.columns):
        raise ValueError("Integrity requires connected_blocks and tracked_blocks measurements")
    initial = float(trajectory.data['tracked_blocks'].iloc[0])
    tracked = trajectory.data['tracked_blocks']
    connected = trajectory.data['connected_blocks']
    if initial <= 0 or not initial.is_integer() or not (tracked == initial).all():
        raise ValueError("tracked_blocks must be a constant positive integer")
    if not ((connected >= 0) & (connected <= initial)).all() or not connected.map(lambda v: float(v).is_integer()).all():
        raise ValueError("connected_blocks must be integer counts within the initial population")
    return float(connected.iloc[-1]) / initial
