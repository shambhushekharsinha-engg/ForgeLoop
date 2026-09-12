from types import SimpleNamespace

from forgeloop.cli.export_web import export_dashboard


def test_empty_export_does_not_fabricate_results_or_flight_evidence(tmp_path):
    output = export_dashboard(
        output_dir=tmp_path / "site", plots_dir=tmp_path / "missing"
    )
    page = output.read_text()
    assert "No evaluated experiments supplied" in page
    assert "EXP-142" not in page
    assert "114.7" not in page
    assert "VIDEO EVIDENCE PENDING" in page
    assert "No verified flight recording" not in page
    assert "No live MCP connection" in page


def test_export_renders_only_supplied_results_sorted_and_escaped(tmp_path):
    def experiment(name, score):
        return SimpleNamespace(
            id=name,
            hypothesis="<script>alert(1)</script>",
            build_mode="Copilot",
            result=SimpleNamespace(
                final_score=score, orbit_progress=0.5, cost_penalty=2
            ),
        )

    registry = SimpleNamespace(
        experiments={
            "low": experiment("LOW", 10),
            "high": experiment("HIGH", 20),
            "pending": SimpleNamespace(result=None),
        }
    )
    page = export_dashboard(registry, tmp_path / "site").read_text()
    assert page.index("HIGH") < page.index("LOW")
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "<script>alert(1)</script>" not in page
    assert "50.0%" in page


def test_export_can_copy_plots_from_output_directory(tmp_path):
    plots = tmp_path / "site" / "plots"
    plots.mkdir(parents=True)
    (plots / "local.png").write_bytes(b"plot fixture")
    export_dashboard(output_dir=tmp_path / "site", plots_dir=plots)
    assert (plots / "local.png").read_bytes() == b"plot fixture"


def test_writeup_marks_unknown_details_and_preserves_prompt_fence(tmp_path):
    from forgeloop.reporting.writeup import WriteupGenerator

    experiment = SimpleNamespace(
        id="EXP-001",
        hypothesis="Balance",
        build_mode="Copilot",
        notes="",
        result=None,
    )
    target = tmp_path / "nested" / "writeup.md"
    prompt = "Build this\n```\nuntrusted fence"
    assert (
        WriteupGenerator(target).generate("Test machine", experiment, prompt) == target
    )
    draft = target.read_text()
    assert "Not evaluated" in draft
    assert "Gemini" not in draft
    assert "RECORD WHAT WAS ACTUALLY USED" in draft
    assert "````text\n" + prompt + "\n````" in draft
