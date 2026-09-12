from html import escape
import shutil
from pathlib import Path

def export_dashboard(registry=None, output_dir="public", plots_dir="docs/plots"):
    """Export supplied local results; no API connection or fabricated scores."""
    output = Path(output_dir)
    (output / "plots").mkdir(parents=True, exist_ok=True)
    for plot in Path(plots_dir).glob("*.png"):
        target = output / "plots" / plot.name
        if plot.resolve() != target.resolve():
            shutil.copy(plot, target)
    experiments = [] if registry is None else [
        exp for exp in registry.experiments.values() if exp.result is not None
    ]
    experiments.sort(key=lambda exp: exp.result.final_score, reverse=True)
    rows = []
    for rank, exp in enumerate(experiments, 1):
        cells = [f"#{rank}", exp.id, exp.hypothesis, exp.build_mode,
                 f"{exp.result.orbit_progress * 100:.1f}%",
                 f"{exp.result.cost_penalty:.2f}", f"{exp.result.final_score:.2f}"]
        rows.append('<tr>' + ''.join(
            f'<td class="py-4 px-2">{escape(str(cell))}</td>' for cell in cells
        ) + '</tr>')
    ledger_rows = ''.join(rows) or '<tr><td colspan="7" class="py-4 px-2">No evaluated experiments supplied.</td></tr>'

    html = """
    <!DOCTYPE html>
    <html lang="en" class="scroll-smooth">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ForgeLoop-AI | Local Experiment Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        keyframes: {
                            scanline: { '0%': { transform: 'translateY(-100%)' }, '100%': { transform: 'translateY(100vh)' } },
                            terminal: { '0%': { transform: 'translateY(100%)' }, '100%': { transform: 'translateY(-100%)' } },
                            pulseGlow: { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.5 } }
                        },
                        animation: { 'scanline': 'scanline 8s linear infinite', 'terminal': 'terminal 15s linear infinite', 'pulse-glow': 'pulseGlow 2s ease-in-out infinite' }
                    }
                }
            }
        </script>
        <style>
            body { background-color: #020202; color: #e5e5e5; font-family: 'Inter', system-ui, sans-serif; overflow-x: hidden; }
            .glass { background: rgba(10, 10, 12, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); }
            .neon-border { box-shadow: 0 0 15px rgba(0, 240, 255, 0.1); border: 1px solid rgba(0, 240, 255, 0.3); }
            .grid-bg { background-image: linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px); background-size: 40px 40px; }
            .btn-cyber { background: linear-gradient(45deg, #00f0ff, #0066ff); position: relative; overflow: hidden; z-index: 1; transition: all 0.3s; }
            .btn-cyber:hover { box-shadow: 0 0 25px rgba(0,240,255,0.6); transform: translateY(-2px); }
            .btn-alert { background: linear-gradient(45deg, #ff003c, #990000); transition: all 0.3s; }
            .btn-alert:hover { box-shadow: 0 0 25px rgba(255,0,60,0.6); transform: translateY(-2px); }
        </style>
    </head>
    <body class="min-h-screen grid-bg relative selection:bg-cyan-500 selection:text-white">
        
        <nav class="fixed top-0 w-full glass z-50 px-6 py-4 flex justify-between items-center border-b border-gray-800">
            <div class="font-black text-2xl tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white to-cyan-500">FL.AI</div>
            <div class="hidden md:flex gap-6 text-sm font-semibold tracking-widest uppercase text-gray-400">
                <a href="#whitepaper" class="hover:text-cyan-400 transition-colors">Whitepaper</a>
                <a href="#gallery" class="hover:text-cyan-400 transition-colors">Blueprints</a>
                <a href="#video" class="hover:text-cyan-400 transition-colors">Flight Log</a>
                <a href="#dashboard" class="hover:text-cyan-400 transition-colors">Dashboard</a>
                <a href="#team" class="hover:text-cyan-400 transition-colors">Team</a>
            </div>
            <a href="https://github.com/shambhushekharsinha-engg/ForgeLoop" target="_blank" class="px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded text-sm font-bold transition-all">GitHub Repo</a>
        </nav>

        <div class="pt-28 pb-20 max-w-[1400px] mx-auto px-6">
            
            <!-- Hero -->
            <header class="mb-16">
                <div class="flex flex-col md:flex-row justify-between items-end pb-8">
                    <div class="max-w-2xl">
                        <h1 class="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-200 to-cyan-600 drop-shadow-lg mb-4">
                            ForgeLoop<span class="text-cyan-500">.AI</span>
                        </h1>
                        <div class="flex items-center gap-4 mb-6">
                            <p class="text-xl text-cyan-400 tracking-[0.2em] uppercase font-bold">Local experiment workspace</p>
                            <img src="https://github.com/shambhushekharsinha-engg/ForgeLoop/actions/workflows/ci.yml/badge.svg" alt="CI Status" class="rounded shadow-[0_0_10px_rgba(0,240,255,0.3)]">
                        </div>
                        <p class="text-gray-400 leading-relaxed text-lg">Local tools for reviewing Besiege experiments, estimating trajectory scores, and recording human decisions. This snapshot does not connect to the game or an AI provider.</p>
                    </div>
                    
                    <div class="mt-8 md:mt-0 flex flex-col gap-4 w-full md:w-auto">
                        <a href="#dashboard" class="btn-cyber text-white font-black py-4 px-8 rounded-lg tracking-widest uppercase text-sm border border-cyan-400/50 flex justify-center items-center gap-2 text-center">
                            <span class="w-2 h-2 bg-white rounded-full animate-pulse-glow"></span> View Local Results
                        </a>
                        <div class="flex gap-4">
                            <a href="#reproduce" class="flex-1 text-center bg-gray-900 hover:bg-gray-800 border border-gray-700 text-white font-bold py-3 px-6 rounded-lg tracking-widest text-xs uppercase transition-colors">
                                Run Local Demo
                            </a>
                            <a href="#gallery" class="flex-1 text-center btn-alert text-white font-bold py-3 px-6 rounded-lg tracking-widest text-xs uppercase border border-red-500/50">
                                View Plots
                            </a>
                        </div>
                    </div>
                </div>
            </header>

            <!-- Whitepaper -->
            <section id="whitepaper" class="glass rounded-3xl p-10 mb-12 border-t border-cyan-900/50 relative overflow-hidden shadow-2xl">
                <div class="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none"></div>
                <h2 class="text-4xl font-black mb-10 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600 uppercase tracking-widest border-b border-gray-800 pb-4">Project Scope</h2>
                <div class="space-y-10 text-gray-300 leading-relaxed text-lg">
                    <p>ForgeLoop records engineering proposals and human decisions, estimates trajectory scores, and prepares draft reports for Besiege experiments.</p>
                    <p>No API key is required for local analysis or synthetic demonstrations. Building and flying a real machine requires the game and compatible tools. No AI provider or game connection is implemented here.</p>
                    <p>Scores are local estimates. Synthetic trajectories do not establish real flight performance. Verify scoring rules, transcript exclusions, and Autopilot eligibility against the competition rules.</p>
                </div>
            </section>

            <!-- Mandatory Video Embed Section -->
            <section id="video" class="glass rounded-3xl p-10 mb-12 border-t border-purple-900/50 relative overflow-hidden shadow-2xl">
                <div class="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 blur-[100px] rounded-full pointer-events-none"></div>
                <h2 class="text-3xl font-black mb-6 text-white uppercase tracking-widest flex items-center gap-3">
                    <span class="text-purple-500">🎥 </span> Flight Demonstration
                </h2>
                <div class="aspect-video bg-black rounded-xl border border-gray-800 flex items-center justify-center p-2 shadow-[0_0_30px_rgba(168,85,247,0.15)]">
                    <iframe width="100%" height="100%" src="https://www.youtube.com/embed/dQw4w9WgXcQ" title="Placeholder Flight Demonstration" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen class="rounded-lg"></iframe>
                </div>
                <p class="mt-5 text-gray-400 text-sm">Synthetic demonstration placeholder. Attach evidence from the actual in-game run before presenting flight results.</p>
            </section>

            <!-- Gallery -->
            <section id="gallery" class="mb-16">
                <h2 class="text-3xl font-black mb-6 text-white uppercase tracking-widest flex items-center gap-3">
                    <span class="text-cyan-500">📊</span> Local Trajectory Plots
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    __PLOTS_GALLERY__
                </div>
            </section>

            <!-- Dashboard -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-12" id="dashboard">
                <section class="lg:col-span-8 glass rounded-3xl p-8 neon-border relative overflow-hidden">
                    <h2 class="text-2xl font-bold mb-6 text-white uppercase tracking-widest">Local Experiment Ledger</h2>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead>
                                <tr class="border-b border-gray-800 text-gray-500 uppercase text-[10px] tracking-widest">
                                    <th class="py-3 px-2">Rank</th>
                                    <th class="py-3 px-2">Exp ID</th>
                                    <th class="py-3 px-2">Strategy</th>
                                    <th class="py-3 px-2">Mode</th>
                                    <th class="py-3 px-2 text-right">Orbit</th>
                                    <th class="py-3 px-2 text-right text-magenta">Penalty</th>
                                    <th class="py-3 px-2 text-right text-green-400">Score</th>
                                </tr>
                            </thead>
                            <tbody class="text-xs font-mono">
                                __FORGELOOP_ROWS__
                            </tbody>
                        </table>
                    </div>
                </section>

                <section class="lg:col-span-4 glass rounded-3xl p-6 border border-gray-800 flex flex-col">
                    <h2 class="text-sm font-bold text-gray-300 uppercase tracking-widest mb-4">Snapshot Status</h2>
                    <div class="bg-[#050505] rounded-xl p-4 flex-1 overflow-hidden relative border border-gray-900 font-mono text-[10px] leading-relaxed shadow-inner">
                        <div class="absolute top-0 left-0 w-full h-8 bg-gradient-to-b from-[#050505] to-transparent z-10"></div>
                        <div class="text-green-500/80">
                            Static local export.<br>
                            No live MCP connection.<br>
                            Results are local estimates.<br>
                            Synthetic data is for demonstration only.
                        </div>
                    </div>
                </section>
            </div>

            <!-- Reproducibility -->
            <section id="reproduce" class="glass rounded-3xl p-10 mb-12 border-t border-green-900/50 relative overflow-hidden">
                <h2 class="text-3xl font-black mb-6 text-white uppercase tracking-widest">How to Reproduce</h2>
                <p class="text-gray-400 mb-6">Run the offline synthetic telemetry demo to exercise local analysis. Real game performance must be measured separately.</p>
                <div class="bg-black/80 rounded-lg p-6 font-mono text-sm text-cyan-400 border border-gray-800 shadow-inner">
                    $ git clone https://github.com/shambhushekharsinha-engg/ForgeLoop<br>
                    $ cd ForgeLoop<br>
                    $ pip install -e .<br>
                    <br>
                    <span class="text-gray-500"># Generate synthetic telemetry and plot trajectories</span><br>
                    <span class="text-white">$</span> python simulate_phase5.py<br>
                    <br>
                    <span class="text-gray-500"># Package genuine run artifacts from submissions/latest</span><br>
                    <span class="text-white">$</span> python -c "from forgeloop.cli.packager import SubmissionPackager; SubmissionPackager().package()"
                </div>
            </section>

            <!-- Team / Human Boss Section -->
            <section id="team" class="glass rounded-3xl p-10 border-t border-blue-900/50 relative overflow-hidden">
                <h2 class="text-3xl font-black mb-6 text-white uppercase tracking-widest text-center">The Human Commander</h2>
                <div class="flex flex-col md:flex-row items-center justify-center gap-8 mt-8">
                    <div class="w-24 h-24 bg-gradient-to-tr from-cyan-500 via-blue-500 to-purple-600 rounded-full flex items-center justify-center text-3xl font-black text-white shadow-[0_0_30px_rgba(0,240,255,0.4)]">
                        SS
                    </div>
                    <div class="text-center md:text-left">
                        <h3 class="text-3xl font-bold text-white mb-2">Shambhu Shekhar Sinha</h3>
                        <p class="text-cyan-400 font-mono tracking-widest">Project author</p>
                        <p class="text-gray-500 text-sm mt-2 max-w-md">Repository author. Add verified build history and flight recordings as experiments are completed.</p>
                    </div>
                </div>
            </section>
            
        </div>
    </body>
    </html>
    """
    html = html.replace("__FORGELOOP_ROWS__", ledger_rows)
    
    plots_dir = Path("docs/plots")
    plots_gallery = ""
    
    if plots_dir.exists():
        for plot in plots_dir.glob("*.png"):
            plots_gallery += f'<div class="bg-[#050505] p-4 rounded-xl border border-gray-800 shadow-inner"><img src="plots/{plot.name}" alt="{plot.name}" class="w-full h-auto rounded"></div>'
            
    if not plots_gallery:
        plots_gallery = '<p class="text-gray-400">No plots found. Generated plots will appear here.</p>'
        
    html = html.replace("__PLOTS_GALLERY__", plots_gallery)
    
    destination = output / "index.html"
    destination.write_text(html, encoding="utf-8")
    print(f"Exported local dashboard snapshot to {destination}")
    return destination

if __name__ == '__main__':
    export_dashboard()
