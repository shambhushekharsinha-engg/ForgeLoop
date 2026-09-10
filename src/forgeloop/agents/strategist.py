import pandas as pd

class TelemetryStrategist:
    """
    An autonomous agent module that reads the failed flight telemetry 
    and mathematically diagnoses the aerodynamic flaw to generate the next prompt.
    """
    def analyze_flight(self, trajectory_df: pd.DataFrame) -> str:
        if trajectory_df.empty: 
            return "[STRATEGIST] No telemetry data available."
        
        max_z = trajectory_df['z'].max()
        final_z = trajectory_df['z'].iloc[-1]
        max_ang = trajectory_df['angular_progress'].max()
        vz_std = trajectory_df['vz'].std()
        
        recommendations = ["[STRATEGIST DIAGNOSTICS]"]
        
        # Detect Altitude Loss
        if final_z < max_z * 0.5:
            recommendations.append("❌ CRITICAL: Severe altitude loss detected.")
            recommendations.append("   -> PROMPT INJECTION: 'Add ventral staging thrusters to maintain Z-axis elevation.'")
            
        # Detect Sub-Orbital Speed
        if max_ang < 360:
            recommendations.append("❌ WARNING: Orbital insertion failed (Sub 1-period).")
            recommendations.append("   -> PROMPT INJECTION: 'Increase primary forward thrust blocks and reduce drag.'")
            
        # Detect Tumbling / Unbalanced Mass
        if vz_std > 20:
            recommendations.append("❌ WARNING: Y/Z axis tumbling detected (Unstable Center of Mass).")
            recommendations.append("   -> PROMPT INJECTION: 'Add aerodynamic shielding and reaction wheels to stabilize rotational torque.'")
            
        if len(recommendations) == 1:
            return "[STRATEGIST] SUCCESS: Flight envelope is perfectly stable. Transition to Autopilot compiler."
            
        return "\n".join(recommendations)
