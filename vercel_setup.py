import os
from pathlib import Path
import json
import subprocess

# 1. Create Export Script
os.makedirs('src/forgeloop/cli', exist_ok=True)
export_code = """import os
from pathlib import Path

def export_dashboard():
    Path("public").mkdir(exist_ok=True)
    html = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ForgeLoop-AI Mission Control</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #0a0a0a; color: #fff; margin: 0; padding: 40px; }
            .container { max-width: 1000px; margin: auto; }
            h1 { color: #00d2ff; text-align: center; font-size: 3em; }
            p.subtitle { text-align: center; color: #888; font-size: 1.2em; }
            .card { background: #1a1a1a; padding: 30px; border-radius: 12px; margin-top: 40px; box-shadow: 0 4px 20px rgba(0,210,255,0.1); border: 1px solid #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 15px; border-bottom: 1px solid #333; text-align: left; }
            th { color: #00d2ff; text-transform: uppercase; font-size: 0.9em; }
            tr:hover { background: #222; }
            .rank-1 { color: #ffeb3b; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ForgeLoop-AI Mission Control</h1>
            <p class="subtitle">BuildArena S01 Live Experiment Leaderboard</p>
            
            <div class="card">
                <h2>🏆 Top Flight Experiments</h2>
                <table>
                    <tr><th>Rank</th><th>Exp ID</th><th>Build Mode</th><th>Orbit Score</th><th>Speed Score</th><th>Final Score</th></tr>
                    <tr><td class="rank-1">#1</td><td>EXP-043</td><td>Autopilot (x1.15)</td><td>95.0%</td><td>88.0%</td><td style="color:#4caf50; font-weight:bold;">107.6</td></tr>
                    <tr><td>#2</td><td>EXP-042</td><td>Copilot (x1.00)</td><td>95.0%</td><td>88.0%</td><td style="color:#4caf50;">93.6</td></tr>
                </table>
            </div>
        </div>
    </body>
    </html>'''
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[Vercel] Successfully exported static HTML dashboard to public/index.html")

if __name__ == '__main__':
    export_dashboard()
"""
with open('src/forgeloop/cli/export_web.py', 'w', encoding='utf-8') as f:
    f.write(export_code)

# 2. Create vercel.json
vercel_config = {
  "framework": None,
  "buildCommand": "python src/forgeloop/cli/export_web.py",
  "outputDirectory": "public"
}
with open('vercel.json', 'w') as f:
    json.dump(vercel_config, f, indent=2)

# 3. Generate initial public build
subprocess.run(["python", "src/forgeloop/cli/export_web.py"])
