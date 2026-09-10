import os
import numpy as np
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET

class ForgeLoopSimulator:
    @staticmethod
    def generate_orbital_trajectory(filepath: str, periods=2.5, noise=0.05):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        t = np.linspace(0, periods * 2 * np.pi, 500)
        df = pd.DataFrame({
            'timestamp': np.linspace(0, 120, 500),
            'x': 500 * np.cos(t) + np.random.normal(0, noise*500, 500),
            'y': 500 * np.sin(t) + np.random.normal(0, noise*500, 500),
            'z': 1000 + np.sin(t/2)*50 + np.random.normal(0, noise*100, 500),
            'vx': -50 * np.sin(t),
            'vy': 50 * np.cos(t),
            'vz': np.random.normal(0, 1, 500),
            'angular_progress': t * (180/np.pi)
        })
        df.to_csv(filepath, index=False)
        return df

    @staticmethod
    def generate_mock_bsg(filepath: str):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        root = ET.Element('Machine', version='1', name='ForgeLoop_Mock')
        blocks = ET.SubElement(root, 'Blocks')
        ET.SubElement(blocks, 'Block', id='0', guid='starting-block-123')
        for i in range(4):
            ET.SubElement(blocks, 'Block', id='18', guid=f'thruster-{i}')
        tree = ET.ElementTree(root)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)
        
    @staticmethod
    def setup_mock_experiment(exp_id='MOCK-001'):
        base_dir = Path(f"experiments/{exp_id}")
        ForgeLoopSimulator.generate_mock_bsg(base_dir / "machine_raw.bsg")
        ForgeLoopSimulator.generate_mock_bsg(base_dir / "machine_tuned.bsg")
        trajectory = ForgeLoopSimulator.generate_orbital_trajectory(base_dir / "trajectory.csv", periods=2.8)
        return base_dir, trajectory
