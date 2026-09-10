import os
import shutil
from pathlib import Path

def export_dashboard():
    Path("public/plots").mkdir(parents=True, exist_ok=True)
    
    # Copy plots to public directory for hosting
    if Path("docs/plots").exists():
        for plot in Path("docs/plots").glob("*.png"):
            shutil.copy(plot, Path("public/plots") / plot.name)

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ForgeLoop-AI Mission Control</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: #050505; color: #e5e5e5; font-family: 'Inter', system-ui, sans-serif; }
            .glass { background: rgba(20, 20, 20, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
            .text-cyan { color: #00f0ff; }
            .text-magenta { color: #ff003c; }
            .neon-border { box-shadow: 0 0 15px rgba(0, 240, 255, 0.1); border: 1px solid rgba(0, 240, 255, 0.2); }
        </style>
    </head>
    <body class="min-h-screen p-4 md:p-8 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]">
        <header class="max-w-7xl mx-auto mb-10 text-center pt-8">
            <h1 class="text-5xl md:text-7xl font-black mb-4 tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 drop-shadow-lg">
                ForgeLoop-AI
            </h1>
            <p class="text-xl text-gray-400 tracking-[0.2em] uppercase font-semibold">BuildArena S01 Mission Control</p>
            <div class="mt-6 flex flex-wrap justify-center gap-4">
                <span class="px-4 py-1.5 glass rounded-full text-xs font-bold text-cyan uppercase tracking-wider flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span> Network Active</span>
                <span class="px-4 py-1.5 glass rounded-full text-xs font-bold text-green-400 uppercase tracking-wider flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-green-400"></span> Score Engine Online</span>
                <span class="px-4 py-1.5 glass rounded-full text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-2">🛠️ Token Scrubber Active</span>
            </div>
        </header>

        <main class="max-w-7xl mx-auto grid grid-cols-1 xl:grid-cols-3 gap-8">
            
            <!-- Left Column: Leaderboard -->
            <section class="xl:col-span-2 glass rounded-3xl p-8 neon-border relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 blur-[100px] rounded-full pointer-events-none"></div>
                <h2 class="text-3xl font-bold mb-8 flex items-center gap-3">
                    <span class="text-2xl">🏆</span> 
                    <span class="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Global Experiment Leaderboard</span>
                </h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-gray-800 text-gray-500 uppercase text-xs tracking-widest">
                                <th class="py-4 px-2">Rank</th>
                                <th class="py-4 px-2">Exp ID</th>
                                <th class="py-4 px-2">Build Mode</th>
                                <th class="py-4 px-2">Orbit</th>
                                <th class="py-4 px-2">Speed</th>
                                <th class="py-4 px-2 text-magenta">Penalty</th>
                                <th class="py-4 px-2 text-green-400">Final Score</th>
                            </tr>
                        </thead>
                        <tbody class="text-sm font-medium">
                            <tr class="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
                                <td class="py-5 px-2 font-black text-yellow-400 text-lg">#1</td>
                                <td class="py-5 px-2 font-mono text-gray-300">EXP-043</td>
                                <td class="py-5 px-2"><span class="bg-blue-900/50 border border-blue-500/30 text-blue-300 px-3 py-1 rounded-full text-xs">Autopilot (x1.15)</span></td>
                                <td class="py-5 px-2">95.0%</td>
                                <td class="py-5 px-2">88.0%</td>
                                <td class="py-5 px-2 text-magenta">-0.5</td>
                                <td class="py-5 px-2 font-black text-green-400 text-2xl drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]">107.6</td>
                            </tr>
                            <tr class="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
                                <td class="py-5 px-2 font-bold text-gray-400 text-lg">#2</td>
                                <td class="py-5 px-2 font-mono text-gray-300">EXP-042</td>
                                <td class="py-5 px-2"><span class="bg-gray-800/80 border border-gray-600/50 text-gray-300 px-3 py-1 rounded-full text-xs">Copilot (x1.00)</span></td>
                                <td class="py-5 px-2">95.0%</td>
                                <td class="py-5 px-2">88.0%</td>
                                <td class="py-5 px-2 text-magenta">-2.5</td>
                                <td class="py-5 px-2 font-bold text-green-400 text-xl">93.6</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Right Column: Sidebar Stats -->
            <div class="flex flex-col gap-8">
                <!-- Trajectory Preview -->
                <section class="glass rounded-3xl p-8 relative overflow-hidden group">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 blur-[50px] rounded-full pointer-events-none"></div>
                    <h2 class="text-xl font-bold mb-6 text-white flex items-center gap-2">🛰️ Latest Telemetry</h2>
                    <div class="bg-black/80 rounded-xl aspect-[4/3] flex items-center justify-center border border-gray-800 overflow-hidden relative group-hover:border-purple-500/50 transition-colors">
                        <img src="plots/SIM-001_orbit.png" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" class="w-full h-full object-contain opacity-90 hover:opacity-100 transition-opacity hover:scale-105 duration-500" alt="Orbital Plot">
                        <div class="hidden flex-col items-center text-gray-600">
                            <span class="text-3xl mb-2">📡</span>
                            <span class="text-xs uppercase tracking-widest">Awaiting Flight Data</span>
                        </div>
                    </div>
                    <p class="mt-5 text-sm text-gray-400 leading-relaxed">Live orbital insertion graph from the physics engine.</p>
                </section>

                <!-- Decision Ledger -->
                <section class="glass rounded-3xl p-8">
                    <h2 class="text-xl font-bold mb-6 text-white flex items-center gap-2">📖 Decision Ledger</h2>
                    <div class="space-y-6">
                        <div class="border-l-4 border-green-500 pl-5 relative">
                            <div class="absolute -left-[5px] top-0 w-2 h-2 bg-green-500 rounded-full"></div>
                            <p class="text-xs text-gray-500 mb-1 font-mono tracking-wider">AI-042 -> EXP-042</p>
                            <p class="text-sm font-medium text-gray-200">Quad-symmetry with staged decouplers</p>
                            <span class="text-[10px] bg-green-900/50 border border-green-500/30 text-green-300 px-2 py-0.5 rounded font-bold uppercase mt-3 inline-block tracking-wider">Human: Accept</span>
                        </div>
                        <div class="border-l-4 border-red-500 pl-5 relative">
                            <div class="absolute -left-[5px] top-0 w-2 h-2 bg-red-500 rounded-full"></div>
                            <p class="text-xs text-gray-500 mb-1 font-mono tracking-wider">AI-041 -> EXP-041</p>
                            <p class="text-sm font-medium text-gray-200">Asymmetric heavy nosecone geometry</p>
                            <span class="text-[10px] bg-red-900/50 border border-red-500/30 text-red-300 px-2 py-0.5 rounded font-bold uppercase mt-3 inline-block tracking-wider">Human: Reject</span>
                        </div>
                    </div>
                </section>
            </div>
            
            <!-- Architecture Section -->
            <section class="xl:col-span-3 glass rounded-3xl p-10 mt-2 border-t border-gray-800">
                <h2 class="text-3xl font-bold mb-8 text-white">⚙️ Core Architecture Strategy</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="p-6 bg-gradient-to-b from-gray-900 to-black rounded-2xl border border-gray-800 hover:border-cyan-500/50 transition-colors">
                        <div class="text-3xl mb-4">🔬</div>
                        <h3 class="font-bold text-xl mb-3 text-cyan">1. Copilot Iteration</h3>
                        <p class="text-sm text-gray-400 leading-relaxed">Human-guided exploration to discover aerodynamic stability and reliable orbital staging patterns before finalizing geometry.</p>
                    </div>
                    <div class="p-6 bg-gradient-to-b from-gray-900 to-black rounded-2xl border border-gray-800 hover:border-purple-500/50 transition-colors">
                        <div class="text-3xl mb-4">🧹</div>
                        <h3 class="font-bold text-xl mb-3 text-purple-400">2. Token Scrubber</h3>
                        <p class="text-sm text-gray-400 leading-relaxed">Automated regex-based optimization that strips verbose JSON/XML payloads from chat history to mathematically minimize the Cost Penalty.</p>
                    </div>
                    <div class="p-6 bg-gradient-to-b from-gray-900 to-black rounded-2xl border border-gray-800 hover:border-green-500/50 transition-colors">
                        <div class="text-3xl mb-4">🚀</div>
                        <h3 class="font-bold text-xl mb-3 text-green-400">3. Autopilot Extraction</h3>
                        <p class="text-sm text-gray-400 leading-relaxed">Compiling the winning structural strategy into a dense mega-prompt to claim the competition's massive x1.15 score multiplier.</p>
                    </div>
                </div>
            </section>
        </main>
        
        <footer class="mt-16 text-center text-gray-600 text-sm pb-8">
            <p>ForgeLoop-AI © 2026 | Built for BuildArena S01</p>
        </footer>
    </body>
    </html>
    """
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[Vercel] Successfully exported upgraded premium frontend to public/index.html")

if __name__ == '__main__':
    export_dashboard()
