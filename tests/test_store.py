from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3

import pytest

from forgeloop.cli.main import main
from forgeloop.decisions.decision import HumanDecision, DecisionStatus
from forgeloop.decisions.proposal import AIProposal
from forgeloop.experiments.experiment import Experiment
from forgeloop.experiments.runner import ExperimentRunner
from forgeloop.experiments.store import ExperimentStore


def experiment(name='EXP-001'):
    exp = Experiment(name, 'Copilot', '<script>hypothesis</script>', AIProposal('P1', 'Test', 'Test'),
                     HumanDecision(DecisionStatus.ACCEPT, 'Test only'))
    ExperimentRunner().evaluate_experiment(exp, .5, .5, 1, 'test transcript')
    return exp


def save(store, exp=None, kind='synthetic'):
    return store.save(exp or experiment(), b'original csv', b'test transcript',
                      evidence_kind=kind, assumptions={'local': True})


def test_saved_experiments_survive_reopening_and_keep_evidence(tmp_path):
    path = tmp_path / 'runs' / 'experiments.sqlite3'
    original = save(ExperimentStore(path))
    reopened = ExperimentStore(path)
    assert reopened.records() == [original]
    assert reopened.registry('synthetic').experiments['EXP-001'].result.final_score > 0
    assert reopened.records('measured') == []
    with sqlite3.connect(path) as connection:
        assert connection.execute('SELECT transcript FROM experiments').fetchone()[0] == b'test transcript'


def test_concurrent_duplicate_inserts_do_not_overwrite(tmp_path):
    path = tmp_path / 'experiments.sqlite3'
    def attempt(_):
        try:
            save(ExperimentStore(path))
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert results.count(True) == 1
    assert len(ExperimentStore(path).records()) == 1


def test_corrupted_evidence_is_not_exported(tmp_path):
    path = tmp_path / 'experiments.sqlite3'
    save(ExperimentStore(path))
    with sqlite3.connect(path) as connection:
        connection.execute('UPDATE experiments SET transcript=?', (b'changed',))
    with pytest.raises(ValueError, match='checksum mismatch'):
        ExperimentStore(path).registry('synthetic')


def test_no_database_created_by_list(tmp_path, capsys):
    path = tmp_path / 'missing.sqlite3'
    with pytest.raises(SystemExit) as error:
        main(['list', '--store', str(path)])
    assert error.value.code == 2
    assert not path.exists()


def test_dashboard_separates_synthetic_and_measured_records(tmp_path):
    path = tmp_path / 'experiments.sqlite3'
    save(ExperimentStore(path), experiment('SYNTHETIC-001'))
    save(ExperimentStore(path), experiment('MEASURED-001'), kind='measured')
    out = tmp_path / 'site'
    main(['dashboard', '--store', str(path), '--evidence-kind', 'measured', '--output', str(out)])
    page = (out / 'index.html').read_text()
    assert 'MEASURED-001' in page and 'SYNTHETIC-001' not in page
    assert 'Measured Inputs' in page
    assert '<script>hypothesis</script>' not in page


@pytest.mark.parametrize('name', ['../escape', '', 'a' * 65])
def test_invalid_id_rejected(tmp_path, name):
    with pytest.raises(ValueError, match='Experiment ID'):
        save(ExperimentStore(tmp_path / 'db'), experiment(name))


def test_inconsistent_scores_rejected(tmp_path):
    exp = experiment()
    exp.result.final_score = 999
    with pytest.raises(ValueError, match='component scores'):
        save(ExperimentStore(tmp_path / 'db'), exp)


def test_analyze_real_pipeline_and_duplicate_protection(tmp_path, capsys):
    pytest.importorskip('pandas')
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    database = tmp_path / 'runs.sqlite3'
    args = ['analyze', str(root / 'examples/synthetic-flight.csv'),
            '--transcript', str(root / 'examples/synthetic-transcript.md'), '--id', 'EXP-001',
            '--hypothesis', 'Pipeline', '--strategy', 'Fixture', '--reason', 'Test',
            '--decision', 'ACCEPT', '--build-mode', 'Copilot', '--evidence-kind', 'synthetic',
            '--reference-duration', '120', '--store', str(database)]
    main(args)
    record = json.loads(capsys.readouterr().out)
    assert record['result']['orbit_progress'] == 1
    assert record['result']['integrity'] == .9
    assert record['official_scoring'] is False
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert len(ExperimentStore(database).records()) == 1
