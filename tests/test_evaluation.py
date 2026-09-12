import pytest
from forgeloop.evaluation.performance import calculate_performance_score
from forgeloop.evaluation.final_score import calculate_final_score

def test_performance_score_perfect():
    """Test a perfect run: 100% orbit, speed, and integrity."""
    score = calculate_performance_score(orbit=1.0, speed=1.0, integrity=1.0)
    assert score == pytest.approx(100.0)

def test_performance_score_realistic():
    """Test realistic partial flight telemetry."""
    # 82.4% orbit, 83.5% speed, 92.0% integrity
    # 100 * (0.7*0.824 + 0.2*0.835 + 0.1*0.920) = 83.58
    score = calculate_performance_score(orbit=0.824, speed=0.835, integrity=0.920)
    assert round(score, 2) == 83.58

def test_performance_score_zero():
    """Test an exploding machine on the pad."""
    score = calculate_performance_score(orbit=0.0, speed=0.0, integrity=0.0)
    assert score == 0.0

def test_final_score_autopilot_multiplier():
    """Test that Autopilot correctly applies the x1.15 multiplier."""
    perf = 80.0
    cost = 10.0
    # Base: 80 - (0.2 * 10) = 78
    # Final: 78 * 1.15 = 89.7
    final = calculate_final_score(perf, cost, build_mode='Autopilot')
    assert round(final, 2) == 89.7

def test_final_score_copilot_multiplier():
    """Test that Copilot correctly applies the x1.00 multiplier."""
    perf = 80.0
    cost = 10.0
    # Base: 80 - (0.2 * 10) = 78
    # Final: 78 * 1.0 = 78.0
    final = calculate_final_score(perf, cost, build_mode='Copilot')
    assert final == 78.0

def test_final_score_floor():
    """Test that the base score cannot go below 0 due to heavy cost penalties."""
    perf = 10.0
    cost = 100.0 # 10 - 20 = -10
    final = calculate_final_score(perf, cost, build_mode='Copilot')
    assert final == 0.0


@pytest.mark.parametrize('value', [-0.1, 1.1, float('nan'), float('inf')])
def test_rejects_invalid_component(value):
    with pytest.raises(ValueError):
        calculate_performance_score(value, 0.5, 1.0)


@pytest.mark.parametrize('performance,cost,mode', [
    (101, 0, 'Copilot'), (50, -1, 'Copilot'),
    (float('nan'), 0, 'Copilot'), (50, float('inf'), 'Copilot'),
    (50, 0, 'Autopliot'),
])
def test_rejects_invalid_final_score_inputs(performance, cost, mode):
    with pytest.raises(ValueError):
        calculate_final_score(performance, cost, mode)


def test_cost_estimate_is_consistent_and_offline():
    from forgeloop.evaluation.cost import estimate_token_cost
    from forgeloop.evaluation.tokenizer import TokenAnalyzer
    result = TokenAnalyzer().calculate_penalty('A' * 500)
    assert result['tokens'] == 125
    assert result['is_estimate']
    assert not result['official_scoring']
    assert result['cost_penalty'] == estimate_token_cost('A' * 500)
    assert estimate_token_cost('') == 0


def write_trajectory(tmp_path, text):
    pytest.importorskip("pandas")
    from forgeloop.data.trajectory import Trajectory
    path = tmp_path / 'trajectory.csv'
    path.write_text(text)
    return Trajectory(str(path))


@pytest.mark.parametrize('angles', ['100,640,1180', '100,-440,-980'])
def test_orbit_accounts_for_start_angle_and_direction(tmp_path, angles):
    from forgeloop.evaluation.orbit import calculate_orbit_progress
    a, b, c = angles.split(',')
    trajectory = write_trajectory(tmp_path, f'timestamp,x,y,z,angular_progress\n0,1,0,1,{a}\n60,0,1,1,{b}\n120,1,0,1,{c}\n')
    assert calculate_orbit_progress(trajectory) == 1


def test_oscillation_does_not_accumulate_orbits(tmp_path):
    from forgeloop.evaluation.orbit import calculate_orbit_progress
    trajectory = write_trajectory(tmp_path, 'timestamp,x,y,z,angular_progress\n0,1,0,1,0\n1,0,1,1,180\n2,1,0,1,0\n3,0,1,1,180\n')
    assert calculate_orbit_progress(trajectory) == pytest.approx(1 / 6)


@pytest.mark.parametrize('text', [
    'timestamp,x,y\n0,1,2\n1,2,3\n',
    'timestamp,x,y,z\n0,1,2,3\n',
    'timestamp,x,y,z\n0,1,2,3\n0,2,3,4\n',
    'timestamp,x,y,z\n0,1,2,3\n1,nan,3,4\n',
    'timestamp,x,y,z\n1,1,2,3\n0,2,3,4\n',
])
def test_invalid_trajectory_is_rejected(tmp_path, text):
    with pytest.raises(ValueError):
        write_trajectory(tmp_path, text)


def test_missing_measurements_are_not_zero_scores(tmp_path):
    from forgeloop.evaluation.orbit import calculate_orbit_progress
    from forgeloop.evaluation.speed import calculate_speed_score
    from forgeloop.evaluation.integrity import calculate_integrity
    trajectory = write_trajectory(tmp_path, 'timestamp,x,y,z\n0,1,2,3\n120,2,3,4\n')
    with pytest.raises(ValueError):
        calculate_orbit_progress(trajectory)
    with pytest.raises(ValueError):
        calculate_integrity(trajectory)
    with pytest.raises(ValueError):
        calculate_speed_score(trajectory, 0.5)
    assert calculate_speed_score(trajectory, 0.5, reference_duration=60) == 0.25


def test_integrity_uses_original_population(tmp_path):
    from forgeloop.evaluation.integrity import calculate_integrity
    trajectory = write_trajectory(tmp_path, 'timestamp,x,y,z,tracked_blocks,connected_blocks\n0,1,2,3,10,10\n1,2,3,4,10,7\n')
    assert calculate_integrity(trajectory) == 0.7
    trajectory.data.loc[1, 'connected_blocks'] = 11
    with pytest.raises(ValueError):
        calculate_integrity(trajectory)


def test_column_mapping_preserves_source_and_rejects_collisions(tmp_path):
    pytest.importorskip('pandas')
    from forgeloop.data.trajectory import Trajectory
    path = tmp_path / 'external.csv'
    original = 'time,px,py,pz\n0,1,2,3\n1,2,3,4\n'
    path.write_text(original)
    mapping = {'timestamp': 'time', 'x': 'px', 'y': 'py', 'z': 'pz'}
    trajectory = Trajectory(path, column_map=mapping)
    assert list(trajectory.data.columns) == ['timestamp', 'x', 'y', 'z']
    assert trajectory.source_columns == ('time', 'px', 'py', 'pz')
    assert path.read_text() == original
    with pytest.raises(ValueError, match='distinct'):
        Trajectory(path, column_map={'x': 'px', 'y': 'px'})
    with pytest.raises(ValueError, match='missing'):
        Trajectory(path, column_map={'timestamp': 'absent'})
    with pytest.raises(ValueError, match='unique'):
        Trajectory(path, column_map={'px': 'py'})


@pytest.mark.parametrize('header', ['timestamp,x,y,z,x', 'timestamp,x,y,z,', ''])
def test_ambiguous_csv_headers_rejected(tmp_path, header):
    with pytest.raises(ValueError):
        write_trajectory(tmp_path, header + '\n0,1,2,3,4\n1,2,3,4,5\n')


def test_mutated_invalid_trajectory_is_rejected_by_evaluators(tmp_path):
    from forgeloop.evaluation.orbit import calculate_orbit_progress
    trajectory = write_trajectory(tmp_path, 'timestamp,x,y,z,angular_progress\n0,1,0,1,0\n1,0,1,1,360\n')
    trajectory.data.loc[1, 'timestamp'] = 0
    assert not trajectory.is_valid
    with pytest.raises(ValueError):
        calculate_orbit_progress(trajectory)


@pytest.mark.parametrize('tracked,connected', [(0,0), (10,10.5), (10,-1), (9.5,5)])
def test_invalid_integrity_counts_rejected(tmp_path, tracked, connected):
    from forgeloop.evaluation.integrity import calculate_integrity
    trajectory = write_trajectory(tmp_path, f'timestamp,x,y,z,tracked_blocks,connected_blocks\n0,1,2,3,{tracked},{tracked}\n1,2,3,4,{tracked},{connected}\n')
    with pytest.raises(ValueError):
        calculate_integrity(trajectory)


@pytest.mark.parametrize('duration', [0, -1, float('nan'), float('inf')])
def test_invalid_speed_reference_rejected(tmp_path, duration):
    from forgeloop.evaluation.speed import calculate_speed_score
    trajectory = write_trajectory(tmp_path, 'timestamp,x,y,z\n0,1,2,3\n1,2,3,4\n')
    with pytest.raises(ValueError):
        calculate_speed_score(trajectory, 0.5, reference_duration=duration)


def test_trajectory_from_bytes_never_reopens_source(tmp_path):
    pytest.importorskip('pandas')
    from forgeloop.data.trajectory import Trajectory
    payload = b'timestamp,x,y,z\n0,1,2,3\n1,2,3,4\n'
    source = tmp_path / 'does-not-exist.csv'
    trajectory = Trajectory.from_bytes(payload, source=str(source))
    assert trajectory.filepath == source
    assert trajectory.is_valid
    assert not source.exists()
    assert trajectory.data['x'].tolist() == [1, 2]
    with pytest.raises(ValueError, match='unique'):
        Trajectory.from_bytes(b'timestamp,x,y,z,x\n0,1,2,3,4\n1,2,3,4,5\n')


def test_large_unsigned_timestamps_cannot_wrap_into_valid_order(tmp_path):
    # Values force pandas into uint64; diff previously wrapped a descending pair.
    with pytest.raises(ValueError):
        write_trajectory(tmp_path, 'timestamp,x,y,z\n18446744073709551615,1,2,3\n0,2,3,4\n')


def test_negative_direction_does_not_underflow_unsigned_angles(tmp_path):
    from forgeloop.evaluation.orbit import calculate_orbit_progress
    trajectory = write_trajectory(tmp_path, 'timestamp,x,y,z,angular_progress\n0,1,2,3,1000\n1,2,3,4,460\n')
    assert calculate_orbit_progress(trajectory) == pytest.approx(0.5)
