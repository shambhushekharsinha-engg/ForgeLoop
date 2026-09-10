import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

class TrajectoryPlotter:
    def __init__(self, output_dir="docs/plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_orbit(self, experiment_id: str, trajectory_data: pd.DataFrame):
        """Generates a 3D plot of the spacecraft trajectory."""
        if trajectory_data.empty:
            print(f"[{experiment_id}] No trajectory data to plot.")
            return None
            
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Assuming the CSV has x, y, z columns
        x = trajectory_data.get('x', [0, 1, 2, 0])
        y = trajectory_data.get('y', [0, 1, 0, -1])
        z = trajectory_data.get('z', [0, 0, 1, 0])
        
        ax.plot(x, y, z, label=f'Flight Path ({experiment_id})', color='cyan', linewidth=2)
        ax.scatter([0], [0], [0], color='yellow', s=100, label='Orbital Center (Planet)')
        
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Altitude (Z)')
        ax.set_title(f'Orbital Insertion Trajectory: {experiment_id}')
        ax.legend()
        
        output_path = self.output_dir / f"{experiment_id}_orbit.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path
