import io
import json
from urllib.error import URLError

import pytest

from forgeloop import public_sources
from forgeloop.cli.catalog import main


PAYLOAD = b'[roles.59]\nblock_name="Rocket"\ntype="pointer"\npointer_axis=[0,1,0]\n'


def test_bundled_catalog_is_searchable_offline():
    catalog = public_sources.load_catalog()
    assert catalog['revision'] == public_sources.REVISION
    assert catalog['license'] == 'CC-BY-NC-4.0'
    assert len(catalog['source_sha256']) == 64
    rocket = public_sources.search_blocks(catalog, 'rocket', 'pointer')
    assert any(block['id'] == 59 and block['name'] == 'Rocket' for block in rocket)
    assert public_sources.search_blocks(catalog, 'rocket', 'connection') == []


@pytest.mark.parametrize('payload', [b'', b'roles=[]', b'[roles.x]\nblock_name="X"\ntype="basic"', b'[roles.1]\nblock_name=1\ntype="basic"'])
def test_malformed_source_is_rejected(payload):
    with pytest.raises(ValueError):
        public_sources.parse_roles(payload)


def test_refresh_records_provenance_and_preserves_cache_on_failure(tmp_path, monkeypatch):
    destination = tmp_path / 'catalog.json'
    monkeypatch.setattr(public_sources, 'urlopen', lambda *args, **kwargs: io.BytesIO(PAYLOAD))
    catalog = public_sources.refresh_catalog(destination)
    assert public_sources.load_catalog(destination) == catalog
    assert catalog['blocks'][0]['id'] == 59
    before = destination.read_bytes()
    monkeypatch.setattr(public_sources, 'urlopen', lambda *args, **kwargs: io.BytesIO(b'bad TOML'))
    with pytest.raises(ValueError):
        public_sources.refresh_catalog(destination)
    assert destination.read_bytes() == before


def test_offline_cli_emits_source_and_results(capsys):
    main(['rocket', '--json'])
    output = json.loads(capsys.readouterr().out)
    assert output['source'] == public_sources.SOURCE_URL
    assert all('rocket' in block['name'].casefold() for block in output['blocks'])


def test_cli_network_error_is_actionable(tmp_path, monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise URLError('offline')
    monkeypatch.setattr(public_sources, 'urlopen', fail)
    with pytest.raises(SystemExit) as error:
        main(['--refresh', str(tmp_path / 'cache.json')])
    assert error.value.code == 2
    assert 'offline' in capsys.readouterr().err


@pytest.mark.parametrize('field,value', [
    ('source', 'https://example.com/untrusted'), ('revision', 'bad'), ('license', 'MIT'),
    ('source_sha256', 'not-a-hash'), ('retrieved_at', '2026-09-12'),
    ('schema_version', True), ('schema_version', 2), ('attribution', ''),
])
def test_load_rejects_invalid_provenance(tmp_path, field, value):
    catalog = public_sources.load_catalog()
    catalog[field] = value
    target = tmp_path / 'bad.json'
    target.write_text(json.dumps(catalog))
    with pytest.raises(ValueError):
        public_sources.load_catalog(target)


@pytest.mark.parametrize('block', [
    {'id': -1, 'name': 'X', 'type': 'basic'},
    {'id': True, 'name': 'X', 'type': 'basic'},
    {'id': 1, 'name': '', 'type': 'basic'},
    {'id': 1, 'name': 'X\x1b[2J', 'type': 'basic'},
    {'id': 1, 'name': 'X', 'type': 'basic', 'pointer_axis': [0, 1]},
    {'id': 1, 'name': 'X', 'type': 'basic', 'pointer_axis': [0, float('nan'), 0]},
    {'id': 1, 'name': 'X', 'type': 'basic', 'pointer_axis': [0, 10**400, 0]},
])
def test_catalog_rejects_invalid_blocks(block):
    catalog = public_sources.load_catalog()
    catalog['blocks'] = [block]
    with pytest.raises(ValueError):
        public_sources.validate_catalog(catalog)


def test_rejects_duplicate_ids_and_json_keys(tmp_path):
    catalog = public_sources.load_catalog()
    catalog['blocks'].append(catalog['blocks'][0])
    with pytest.raises(ValueError, match='unique'):
        public_sources.validate_catalog(catalog)
    target = tmp_path / 'duplicate.json'
    target.write_text('{"blocks":[],"blocks":[]}')
    with pytest.raises(ValueError, match='Duplicate'):
        public_sources.load_catalog(target)
    with pytest.raises(ValueError, match='unique'):
        public_sources.parse_roles(b'[roles.1]\nblock_name="One"\ntype="basic"\n[roles.01]\nblock_name="Alias"\ntype="basic"')


def test_size_limits_apply_to_cache_source_and_search(tmp_path, monkeypatch):
    catalog = public_sources.load_catalog()
    with pytest.raises(ValueError, match='query'):
        public_sources.search_blocks(catalog, 'a' * 1025)
    monkeypatch.setattr(public_sources, 'MAX_BYTES', 16)
    target = tmp_path / 'large.json'
    target.write_bytes(b' ' * 17)
    with pytest.raises(ValueError, match='size limit'):
        public_sources.load_catalog(target)
    with pytest.raises(ValueError, match='size limit'):
        public_sources.parse_roles(PAYLOAD)
    monkeypatch.setattr(public_sources, 'urlopen', lambda *args, **kwargs: io.BytesIO(PAYLOAD))
    with pytest.raises(ValueError, match='size limit'):
        public_sources.refresh_catalog(target)
    assert target.read_bytes() == b' ' * 17


def test_concurrent_refreshes_use_independent_atomic_temporary_files(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    destination = tmp_path / 'catalog.json'
    monkeypatch.setattr(public_sources, 'urlopen', lambda *args, **kwargs: io.BytesIO(PAYLOAD))
    barrier = Barrier(2)
    replace = public_sources.os.replace
    temporary_paths = []

    def overlapping_replace(source, target):
        temporary_paths.append(source)
        barrier.wait(timeout=5)
        replace(source, target)

    monkeypatch.setattr(public_sources.os, 'replace', overlapping_replace)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(public_sources.refresh_catalog, destination) for _ in range(2)]
        results = [future.result(timeout=10) for future in futures]
    assert len(set(temporary_paths)) == 2
    assert public_sources.load_catalog(destination) in results
    assert not list(tmp_path.glob('*.tmp'))


def test_failed_replace_cleans_temporary_file_and_preserves_cache(tmp_path, monkeypatch):
    destination = tmp_path / 'catalog.json'
    destination.write_text('previous contents')
    monkeypatch.setattr(public_sources, 'urlopen', lambda *args, **kwargs: io.BytesIO(PAYLOAD))

    def fail(source, target):
        raise OSError('cannot replace')

    monkeypatch.setattr(public_sources.os, 'replace', fail)
    with pytest.raises(OSError, match='cannot replace'):
        public_sources.refresh_catalog(destination)
    assert destination.read_text() == 'previous contents'
    assert list(tmp_path.iterdir()) == [destination]
