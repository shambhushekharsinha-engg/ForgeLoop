import zipfile

import pytest

from forgeloop.agents.scrubber import TranscriptScrubber
from forgeloop.cli.packager import SubmissionPackager
from forgeloop.data.machine import BSGMachine
from forgeloop.data.transcript import ChatTranscript
from forgeloop.data.validators import (
    validate_bsg_structure,
    validate_no_geometry_changes,
)

BSG = b"""<?xml version="1.0" encoding="utf-8"?>
<Machine version="1" bsgVersion="1.4" name="test">
  <Global><Position x="0" y="5" z="0"/><Rotation x="0" y="0" z="0" w="1"/></Global>
  <Data/>
  <Blocks><Block id="0" guid="ec03d0f8-c5d8-42e6-83e9-b368f33d486a">
    <Transform><Position x="0" y="0" z="0"/><Rotation x="0" y="0" z="0" w="1"/><Scale x="1" y="1" z="1"/></Transform>
    <Data/>
  </Block></Blocks>
</Machine>"""


@pytest.fixture
def artifacts(tmp_path):
    source = tmp_path / "evidence"
    source.mkdir()
    contents = {
        "machine_raw.bsg": BSG,
        "machine_tuned.bsg": BSG,
        "build_history.json": b'[{"action": "build"}]',
        "build_history_full.json": b'{"events": [{"action": "build"}]}',
        "trajectory.csv": b"timestamp,x,y\n0,1,2\n1,3,4\n",
        "chat_transcript.md": b'Human:\r\n  Keep this instruction.\r\n```json\r\n{"x": 1}\r\n```\r\n',
    }
    for name, content in contents.items():
        (source / name).write_bytes(content)
    return source, contents


def test_missing_source_does_not_create_evidence(tmp_path):
    source = tmp_path / "missing"
    output = tmp_path / "submission.zip"
    assert not SubmissionPackager(source, output).package()
    assert not source.exists()
    assert not output.exists()


@pytest.mark.parametrize(
    "name,content",
    [
        ("machine_raw.bsg", b""),
        ("machine_tuned.bsg", b"not xml"),
        ("build_history.json", b"bad json"),
        ("build_history.json", b"null"),
        ("build_history_full.json", b"[]"),
        ("trajectory.csv", b"x,y\n"),
        ("trajectory.csv", b"x,y\n1\n"),
        ("trajectory.csv", b"x,x\n1,2\n"),
        ("chat_transcript.md", b"   \n"),
    ],
)
def test_invalid_evidence_preserves_previous_archive(
    artifacts, tmp_path, name, content
):
    source, _ = artifacts
    (source / name).write_bytes(content)
    output = tmp_path / "submission.zip"
    output.write_bytes(b"previous archive")
    assert not SubmissionPackager(source, output, overwrite=True).package()
    assert output.read_bytes() == b"previous archive"


def test_package_preserves_all_original_bytes(artifacts, tmp_path):
    source, contents = artifacts
    output = tmp_path / "submission.zip"
    assert SubmissionPackager(source, output).package()
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == set(contents)
        for name, content in contents.items():
            assert archive.read(name) == content
            assert (source / name).read_bytes() == content


def test_output_cannot_overwrite_evidence(artifacts):
    source, contents = artifacts
    assert not SubmissionPackager(source, source / "chat_transcript.md").package()
    assert (source / "chat_transcript.md").read_bytes() == contents[
        "chat_transcript.md"
    ]


def test_scrubber_preserves_instructions_and_formatting():
    transcript = 'Human:\n  Use this:\n```json\n{"action":"build"}\n```\n\nAI:\n```xml\n<instruction/>\n```\n'
    scrubber = TranscriptScrubber()
    assert scrubber.scrub(transcript) == transcript
    assert scrubber.scrub(transcript, redact_tool_outputs=True) == transcript


def test_scrubber_only_redacts_explicit_tool_output():
    transcript = "Human: keep me\n<!-- forgeloop:tool-output -->\nlarge payload\n<!-- /forgeloop:tool-output -->\nAI: decision\n"
    scrubber = TranscriptScrubber()
    assert scrubber.scrub(transcript) == transcript
    assert (
        scrubber.scrub(transcript, redact_tool_outputs=True)
        == "Human: keep me\n[TOOL_OUTPUT_REDACTED_IN_REVIEW_COPY]\nAI: decision\n"
    )


def test_missing_transcript_is_not_empty_conversation(tmp_path):
    with pytest.raises(FileNotFoundError):
        ChatTranscript(tmp_path / "missing.md").read_text()


def test_machine_requires_nonempty_file(tmp_path):
    assert not BSGMachine(tmp_path, True).validate_exists()
    path = tmp_path / "machine.bsg"
    path.touch()
    assert not BSGMachine(path, True).validate_exists()


def test_unimplemented_geometry_check_is_explicit():
    with pytest.raises(NotImplementedError, match="verified BSG schema"):
        validate_no_geometry_changes(None, None)


@pytest.mark.parametrize(
    "content",
    [
        b"<unrelated/>",
        BSG.replace(b'<Block id="0"', b'<Block id="-1"'),
        BSG.replace(b"ec03d0f8-c5d8-42e6-83e9-b368f33d486a", b"invalid"),
        BSG.replace(b'x="0"', b'x="NaN"', 1),
        BSG.replace(b'w="1"', b'w="0"', 1),
        BSG.replace(b'<Scale x="1" y="1" z="1"/>', b""),
        BSG.replace(b"<Blocks>", b"<Blocks><Block/>"),
        BSG.replace(
            b"<Machine ", b'<!DOCTYPE Machine [<!ENTITY a "payload">]><Machine ', 1
        ),
    ],
)
def test_bsg_structure_rejects_arbitrary_or_broken_machine(content):
    with pytest.raises(ValueError):
        validate_bsg_structure(content)


def test_bsg_duplicate_guid_rejected():
    block = BSG.split(b"<Blocks>")[1].split(b"</Blocks>")[0]
    with pytest.raises(ValueError, match="GUIDs unique"):
        validate_bsg_structure(BSG.replace(b"</Blocks>", block + b"</Blocks>"))


@pytest.mark.parametrize(
    "name,content",
    [
        ("build_history.json", b'{"value":NaN}'),
        ("build_history.json", b'{"value":Infinity}'),
        ("build_history.json", b'{"value":1e999}'),
        ("build_history.json", b'{"value":1,"value":2}'),
        ("trajectory.csv", b"t,x\n0,NaN\n"),
        ("trajectory.csv", b"t,x\n0,1e999\n"),
        ("trajectory.csv", b"x, x\n0,1\n"),
        ("machine_raw.bsg", b"<unrelated/>"),
    ],
)
def test_package_rejects_structural_bypasses(artifacts, tmp_path, name, content):
    source, _ = artifacts
    (source / name).write_bytes(content)
    output = tmp_path / "submission.zip"
    assert not SubmissionPackager(source, output).package()
    assert not output.exists()


def test_archive_overwrite_requires_explicit_opt_in(artifacts, tmp_path):
    source, _ = artifacts
    output = tmp_path / "submission.zip"
    output.write_bytes(b"existing evidence")
    assert not SubmissionPackager(source, output).package()
    assert output.read_bytes() == b"existing evidence"
    assert SubmissionPackager(source, output, overwrite=True).package()
    assert zipfile.is_zipfile(output)


def test_archive_created_during_validation_is_not_clobbered(
    artifacts, tmp_path, monkeypatch
):
    source, _ = artifacts
    output = tmp_path / "submission.zip"
    packager = SubmissionPackager(source, output)
    read = packager._read_artifacts

    def create_racing_archive():
        data = read()
        output.write_bytes(b"concurrent evidence")
        return data

    monkeypatch.setattr(packager, "_read_artifacts", create_racing_archive)
    assert not packager.package()
    assert output.read_bytes() == b"concurrent evidence"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["evidence", "submission.zip"]


@pytest.mark.parametrize(
    "limits",
    [
        {"max_artifact_bytes": 10},
        {"max_total_bytes": len(BSG) + 1},
    ],
)
def test_artifact_size_limits(artifacts, tmp_path, limits):
    source, _ = artifacts
    output = tmp_path / "submission.zip"
    assert not SubmissionPackager(source, output, **limits).package()
    assert not output.exists()


def test_symlink_artifact_rejected(artifacts, tmp_path):
    source, contents = artifacts
    original = tmp_path / "original.bsg"
    original.write_bytes(contents["machine_raw.bsg"])
    (source / "machine_raw.bsg").unlink()
    try:
        (source / "machine_raw.bsg").symlink_to(original)
    except OSError as e:
        if getattr(e, "winerror", None) == 1314:
            pytest.skip("Symlink creation requires privileges on Windows")
        raise
    assert not SubmissionPackager(source, tmp_path / "submission.zip").package()
