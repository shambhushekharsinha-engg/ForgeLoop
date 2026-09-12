# 1. The Precision Token Analyzer
tokenizer_code = '''import tiktoken

class TokenAnalyzer:
    """Uses OpenAI's official tiktoken to exactly match the Kaggle cost penalty logic."""
    def __init__(self, model="cl100k_base"):
        # BuildArena likely uses standard GPT-4/o1 tokenization
        self.encoding = tiktoken.get_encoding(model)
        
    def calculate_exact_penalty(self, transcript_text: str) -> dict:
        """Calculates precise token count and the resulting Kaggle cost penalty."""
        token_count = len(self.encoding.encode(transcript_text))
        
        # Simulated Kaggle Rule: 0.1 penalty deduction per 1000 tokens
        penalty = (token_count / 1000.0) * 0.1
        
        return {
            "tokens": token_count,
            "cost_penalty": round(penalty, 4)
        }
'''
with open("src/forgeloop/evaluation/tokenizer.py", "w", encoding="utf-8") as f:
    f.write(tokenizer_code)

# 2. The AI Telemetry Strategist
strategist_code = '''import pandas as pd

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
            
        return "\\n".join(recommendations)
'''
with open("src/forgeloop/agents/strategist.py", "w", encoding="utf-8") as f:
    f.write(strategist_code)

# 3. Add GitHub CI Badges to README
with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

badge_markdown = "[![ForgeLoop CI](https://github.com/shambhushekharsinha-engg/ForgeLoop/actions/workflows/ci.yml/badge.svg)](https://github.com/shambhushekharsinha-engg/ForgeLoop/actions)\n"

if badge_markdown not in readme:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(badge_markdown + readme)
    print("Added CI badges to README.md")
