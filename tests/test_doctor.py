import json

from forgeloop import public_sources
from forgeloop.cli import doctor


def test_doctor_is_offline_and_does_not_claim_game_readiness(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("Doctor must not access the network")

    monkeypatch.setattr(public_sources, "urlopen", fail)
    report = doctor.check_environment()
    assert report["core_ready"] is True
    assert len(report["checks"]) == 6
    assert "game connectivity" in report["limitations"]
    assert "not verified" in report["limitations"]
    json.dumps(report)


def test_doctor_reports_invalid_catalog_with_failure_status(tmp_path, capsys):
    assert doctor.main(["--json", "--catalog", str(tmp_path / "missing.json")]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["core_ready"] is False
    assert (
        next(check for check in report["checks"] if check["name"] == "catalog")[
            "status"
        ]
        == "invalid"
    )


def test_analysis_dependencies_are_optional_unless_requested(monkeypatch, capsys):
    monkeypatch.setattr(doctor.importlib.util, "find_spec", lambda name: None)
    assert doctor.main(["--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["core_ready"] is True
    assert report["analysis_available"] is False
    assert doctor.main(["--require-analysis"]) == 1
    assert "pip install" in capsys.readouterr().out


def test_detected_dependencies_are_not_treated_as_import_verified(monkeypatch):
    monkeypatch.setattr(doctor.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setattr(doctor.importlib.metadata, "version", lambda name: "1.2.3")
    report = doctor.check_environment()
    assert report["analysis_available"] is True
    assert all(
        "runtime import not tested" in check["detail"]
        for check in report["checks"]
        if not check["required"]
    )
