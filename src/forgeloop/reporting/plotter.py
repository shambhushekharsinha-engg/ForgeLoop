import re
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure


class TrajectoryPlotter:
    """Render telemetry on Linux/headless machines without opening a GUI."""

    def __init__(self, output_dir="docs/plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_orbit(
        self, experiment_id: str, trajectory_data: pd.DataFrame, *, center=None
    ):
        """Plot measured x/y/z; mark an orbital center only if explicitly supplied."""
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", experiment_id):
            raise ValueError("Experiment ID must be a plain filename component")
        if trajectory_data.empty:
            return None
        if not trajectory_data.columns.is_unique:
            raise ValueError("Trajectory columns must be unique")
        missing = {"x", "y", "z"}.difference(trajectory_data.columns)
        if missing:
            raise ValueError(
                f"Trajectory coordinates missing: {', '.join(sorted(missing))}"
            )
        coordinates = trajectory_data[["x", "y", "z"]].apply(
            pd.to_numeric, errors="raise"
        )
        if not np.isfinite(coordinates.to_numpy(dtype=float)).all():
            raise ValueError("Trajectory coordinates must be finite")
        if center is not None:
            center = np.asarray(center, dtype=float)
            if center.shape != (3,) or not np.isfinite(center).all():
                raise ValueError("center must contain three finite coordinates")

        import matplotlib.pyplot as plt
        plt.style.use("dark_background")
        
        fig = Figure(figsize=(10, 8), facecolor="#0a0a0a")
        FigureCanvasAgg(fig)
        try:
            ax = fig.add_subplot(111, projection="3d")
            ax.set_facecolor("#0a0a0a")
            # Enhance axis grid
            ax.grid(color='#333333', linestyle=':', linewidth=0.5)
            ax.xaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
            ax.yaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
            ax.zaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
            
            ax.plot(
                *(coordinates[column] for column in ("x", "y", "z")),
                label=f"Flight path ({experiment_id})",
                color="cyan",
                linewidth=2.5,
                alpha=0.8
            )
            if center is not None:
                ax.scatter(
                    *center, color="orange", s=100, label="Supplied orbital center"
                )
            ax.set_xlabel("X coordinate")
            ax.set_ylabel("Y coordinate")
            ax.set_zlabel("Z coordinate")
            ax.set_title(f"Recorded trajectory: {experiment_id}")
            ax.legend()
            output_path = self.output_dir / f"{experiment_id}_orbit.png"
            fig.savefig(output_path, dpi=150, bbox_inches="tight")
            return output_path
        finally:
            fig.clear()
