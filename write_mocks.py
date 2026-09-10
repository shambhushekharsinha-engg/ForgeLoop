import os
import numpy as np
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET

class ForgeLoopSimulator:
    """
    Since we do not have the Steam keys yet, this Simulator mathematically generates 
    synthetic Besiege artifacts (BSG XMLs, JSON histories, and realistic CSV flight telemetry) 
    so we can fully test our pipeline end-to-end.
    """
    
    @staticmethod
    def generate_orbital_trajectory(filepath: str, periods=2.5, noise=0.05):
        """Generates a trajectory.csv mimicking a spacecraft in orbit."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Simulate time and orbital math (1 period = 2*pi radians)
        t = np.linspace(0, periods * 2 * np.pi, 500)
        
        # Simulated physics (X/Y orbit, slightly unstable Z altitude)
        df = pd.DataFrame({
            'timestamp': np.linspace(0, 120, 500), # 120 seconds flight time
            'x': 500 * np.cos(t) + np.random.normal(0, noise*500, 500),
            'y': 500 * np.sin(t) + np.random.normal(0, noise*500, 500),
            'z': 1000 + np.sin(t/2)*50 + np.random.normal(0, noise*100, 500), # Altitude ~1000m
            'vx': -50 * np.sin(t),
            'vy': 50 * np.cos(t),
            'vz': np.random.normal(0, 1, 500),
            'angular_progress': t * (180/np.pi) # Convert radians to degrees
        })
        
        df.to_csv(filepath, index=False)
        print(f"[Simulator] Generated realistic flight telemetry: {filepath}")
        return df

    @staticmethod
    def generate_mock_bsg(filepath: str):
        """Generates a dummy .bsg (XML) machine file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        root = ET.Element("Machine", version="1", name="ForgeLoop_Mock")
        blocks = ET.SubElement(root, "Blocks")
        # Starting block
        ET.SubElement(blocks, "Block", id="0", guid="starting-block-123")
        # Add some thrusters
        for i in range(4):
            ET.SubElement(blocks, "Block", id="18", guid=f"thruster-{i}")
            
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
        print(f"[Simulator] Generated raw machine: {filepath}")
        
    @staticmethod
    def setup_mock_experiment(exp_id="MOCK-001"):
        """Packages an entire synthetic experiment run."""
        base_dir = Path(f"experiments/{exp_id}")
        
        ForgeLoopSimulator.generate_mock_bsg(base_dir / "machine_raw.bsg")
        ForgeLoopSimulator.generate_mock_bsg(base_dir / "machine_tuned.bsg")
        trajectory = ForgeLoopSimulator.generate_orbital_trajectory(base_dir / "trajectory.csv", periods=2.8)
        
        return base_dir, trajectory
'''
with open("src/forgeloop/simulation/mock_generator.py", "w") as f:
    pass # Wait, I'll write the script using run_command to avoid syntax issues.
