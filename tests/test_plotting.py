"""Full analysis CI installs these dependencies; lightweight installs may skip."""

import pytest


@pytest.fixture
def plot_modules():
    pd = pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    from forgeloop.reporting.plotter import TrajectoryPlotter

    return pd, TrajectoryPlotter


def test_headless_png_uses_measured_coordinates_without_invented_planet(
    tmp_path, plot_modules, monkeypatch
):
    pd, Plotter = plot_modules
    from matplotlib.figure import Figure

    seen = {}
    original = Figure.savefig

    def inspect(fig, *args, **kwargs):
        seen["collections"] = len(fig.axes[0].collections)
        seen["title"] = fig.axes[0].get_title()
        return original(fig, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", inspect)
    result = Plotter(tmp_path).plot_orbit(
        "EXP-001", pd.DataFrame({"x": [1, 2], "y": [3, 4], "z": [5, 6]})
    )
    assert result.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert seen["collections"] == 0
    assert seen["title"] == "Recorded trajectory: EXP-001"


def test_explicit_center_and_save_failure_cleanup(tmp_path, plot_modules, monkeypatch):
    pd, Plotter = plot_modules
    from matplotlib.figure import Figure

    captured = []

    def fail(fig, *args, **kwargs):
        assert len(fig.axes[0].collections) == 1
        captured.append(fig)
        raise OSError("disk full")

    monkeypatch.setattr(Figure, "savefig", fail)
    with pytest.raises(OSError, match="disk full"):
        Plotter(tmp_path).plot_orbit(
            "EXP-001",
            pd.DataFrame({"x": [1, 2], "y": [3, 4], "z": [5, 6]}),
            center=(10, 20, 30),
        )
    assert captured[0].axes == []


@pytest.mark.parametrize(
    "identifier", ["../escape", "/absolute", "a/b", "a\\b", "", ".", ".."]
)
def test_plot_path_traversal_rejected(tmp_path, plot_modules, identifier):
    pd, Plotter = plot_modules
    with pytest.raises(ValueError):
        Plotter(tmp_path).plot_orbit(
            identifier, pd.DataFrame({"x": [1], "y": [2], "z": [3]})
        )


@pytest.mark.parametrize(
    "data",
    [
        {"x": [1], "y": [2]},
        {"x": [float("nan")], "y": [2], "z": [3]},
        {"x": [float("inf")], "y": [2], "z": [3]},
        {"x": ["bad"], "y": [2], "z": [3]},
    ],
)
def test_invalid_plot_coordinates_rejected(tmp_path, plot_modules, data):
    pd, Plotter = plot_modules
    with pytest.raises(ValueError):
        Plotter(tmp_path).plot_orbit("EXP-001", pd.DataFrame(data))
    assert not list(tmp_path.glob("*.png"))


def test_empty_trajectory_has_no_plot(tmp_path, plot_modules):
    pd, Plotter = plot_modules
    assert Plotter(tmp_path).plot_orbit("EXP-001", pd.DataFrame()) is None
