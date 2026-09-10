import os
import shutil
from pathlib import Path

def export_dashboard():
    Path("public/plots").mkdir(parents=True, exist_ok=True)
    
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
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        keyframes: {
                            scanline: {
                                '0%': { transform: 'translateY(-100%)' },
                                '100%': { transform: 'translateY(100vh)' }
                            },
                            terminal: {
                                '0%': { transform: 'translateY(100%)' },
                                '100%': { transform: 'translateY(-100%)' }
                            }
                        },
                        animation: {
                            'scanline': 'scanline 8s linear infinite',
                            'terminal': 'terminal 15s linear infinite'
                        }
                    }
                }
            }
        </script>
        <style>
            body { background-color: #030303; color: #e5e5e5; font-family: 'Inter', system-ui, sans-serif; overflow-x: hidden; }
            .glass { background: rgba(15, 15, 15, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
            .text-cyan { color: #00f0ff; }
            .text-magenta { color: #ff003c; }
            .text-yellow { color: #ffea00; }
            .neon-border { box-shadow: 0 0 15px rgba(0, 240, 255, 0.1); border: 1px solid rgba(0, 240, 255, 0.2); }
            .neon-text { text-shadow: 0 0 10px rgba(0, 240, 255, 0.5); }
            .grid-bg { background-image: linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px); background-size: 30px 30px; }
        </style>
    </head>
    <body class="min-h-screen grid-bg relative selection:bg-cyan-500 selection:text-white pb-20">
        
        <!-- CRT Scanline Effect -->
        <div class="fixed inset-0 pointer-events-none z-50 opacity-[0.03] bg-[url('https://www.transparenttextures.com/patterns/stardust.png')]"></div>
        <div class="fixed inset-0 pointer-events-none z-50 overflow-hidden"><div class="w-full h-1 bg-cyan-400/20 shadow-[0_0_10px_rgba(0,240,255,0.5)] animate-scanline"></div></div>

        <header class="max-w-[1400px] mx-auto mb-10 pt-12 px-6">
            <div class="flex flex-col md:flex-row justify-between items-end border-b border-gray-800 pb-6">
                <div>
                    <h1 class="text-6xl md:text-8xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-200 to-cyan-600 drop-shadow-lg neon-text mb-2">
                        ForgeLoop<span class="text-3xl text-cyan-500">.AI</span>
                    </h1>
                    <p class="text-sm md:text-xl text-gray-400 tracking-[0.3em] uppercase font-semibold">BuildArena S01 Mission Control</p>
                </div>
                
                <!-- Quick Stats -->
                <div class="flex gap-6 mt-6 md:mt-0">
                    <div class="text-right">
                        <p class="text-[10px] text-gray-500 uppercase tracking-widest">Total Flights</p>
                        <p class="text-3xl font-black text-white">142</p>
                    </div>
                    <div class="text-right">
                        <p class="text-[10px] text-gray-500 uppercase tracking-widest">AI Proposals</p>
                        <p class="text-3xl font-black text-purple-400">384</p>
                    </div>
                    <div class="text-right">
                        <p class="text-[10px] text-gray-500 uppercase tracking-widest">Tokens Scrubbed</p>
                        <p class="text-3xl font-black text-green-400">1.2M</p>
                    </div>
                </div>
            </div>
            
            <div class="mt-4 flex flex-wrap gap-3">
                <span class="px-3 py-1 bg-cyan-950/50 border border-cyan-500/30 rounded text-[10px] font-bold text-cyan uppercase tracking-widest flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span> MCP Socket: Connected</span>
                <span class="px-3 py-1 bg-green-950/50 border border-green-500/30 rounded text-[10px] font-bold text-green-400 uppercase tracking-widest flex items-center gap-2"><span class="w-1.5 h-1.5 rounded-full bg-green-400"></span> Scoring Engine: Active</span>
                <span class="px-3 py-1 bg-purple-950/50 border border-purple-500/30 rounded text-[10px] font-bold text-purple-400 uppercase tracking-widest flex items-center gap-2">🛠️ Token Scrubber: Online</span>
            </div>
        </header>

        <main class="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 px-6">
            
            <!-- Center/Left: Live Leaderboard (Col span 7) -->
            <section class="lg:col-span-8 glass rounded-2xl p-8 neon-border relative overflow-hidden">
                <div class="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 blur-[120px] rounded-full pointer-events-none"></div>
                
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold flex items-center gap-3 text-white">
                        <span class="text-xl">📊</span> Global Experiment Ledger
                    </h2>
                    <span class="text-xs text-gray-500 font-mono">SORT: FINAL_SCORE DESC</span>
                </div>
                
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-gray-800 text-gray-500 uppercase text-[10px] tracking-widest">
                                <th class="py-3 px-2">Rank</th>
                                <th class="py-3 px-2">Exp ID</th>
                                <th class="py-3 px-2">Hypothesis / Strategy</th>
                                <th class="py-3 px-2">Mode</th>
                                <th class="py-3 px-2 text-right">Orbit</th>
                                <th class="py-3 px-2 text-right">Speed</th>
                                <th class="py-3 px-2 text-right text-magenta">Penalty</th>
                                <th class="py-3 px-2 text-right text-green-400">Final Score</th>
                            </tr>
                        </thead>
                        <tbody class="text-xs font-mono">
                            <!-- WINNING AUTOPILOT -->
                            <tr class="border-b border-cyan-900/30 bg-cyan-950/10 hover:bg-white/5 transition-colors">
                                <td class="py-4 px-2 font-black text-yellow-400 text-base">#1</td>
                                <td class="py-4 px-2 text-gray-300">EXP-142</td>
                                <td class="py-4 px-2 text-gray-400 truncate max-w-[200px]" title="Compiled Megaprompt (Quad symmetry, decoupled staging)">Compiled Megaprompt (Quad symm...)</td>
                                <td class="py-4 px-2"><span class="bg-blue-900/50 border border-blue-500/30 text-blue-300 px-2 py-0.5 rounded-full text-[10px]">Autopilot (x1.15)</span></td>
                                <td class="py-4 px-2 text-right text-white">99.8%</td>
                                <td class="py-4 px-2 text-right text-white">94.2%</td>
                                <td class="py-4 px-2 text-right text-magenta">-0.2</td>
                                <td class="py-4 px-2 font-black text-green-400 text-xl text-right drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]">114.7</td>
                            </tr>
                            <!-- HIGH TIER COPILOTS -->
                            <tr class="border-b border-gray-800 hover:bg-white/5 transition-colors">
                                <td class="py-4 px-2 font-bold text-gray-400">#2</td>
                                <td class="py-4 px-2 text-gray-400">EXP-138</td>
                                <td class="py-4 px-2 text-gray-500 truncate max-w-[200px]">Center of mass shift down 2 blocks</td>
                                <td class="py-4 px-2"><span class="bg-gray-800/80 border border-gray-600/50 text-gray-300 px-2 py-0.5 rounded-full text-[10px]">Copilot (x1.00)</span></td>
                                <td class="py-4 px-2 text-right">98.5%</td>
                                <td class="py-4 px-2 text-right">91.0%</td>
                                <td class="py-4 px-2 text-right text-magenta">-1.5</td>
                                <td class="py-4 px-2 font-bold text-green-500 text-right text-lg">98.1</td>
                            </tr>
                            <tr class="border-b border-gray-800 hover:bg-white/5 transition-colors">
                                <td class="py-4 px-2 font-bold text-gray-500">#3</td>
                                <td class="py-4 px-2 text-gray-500">EXP-121</td>
                                <td class="py-4 px-2 text-gray-600 truncate max-w-[200px]">Aerodynamic shielding added to nose</td>
                                <td class="py-4 px-2"><span class="bg-gray-800/80 border border-gray-600/50 text-gray-300 px-2 py-0.5 rounded-full text-[10px]">Copilot (x1.00)</span></td>
                                <td class="py-4 px-2 text-right">94.0%</td>
                                <td class="py-4 px-2 text-right">88.5%</td>
                                <td class="py-4 px-2 text-right text-magenta">-2.1</td>
                                <td class="py-4 px-2 font-bold text-green-600 text-right text-base">92.4</td>
                            </tr>
                            <!-- MID TIER -->
                            <tr class="border-b border-gray-800/50 hover:bg-white/5 transition-colors opacity-80">
                                <td class="py-3 px-2 text-gray-600">#4</td>
                                <td class="py-3 px-2 text-gray-600">EXP-094</td>
                                <td class="py-3 px-2 text-gray-600 truncate max-w-[200px]">Test heavy ballast removal</td>
                                <td class="py-3 px-2"><span class="bg-gray-800/50 text-gray-400 px-2 py-0.5 rounded-full text-[10px]">Copilot (x1.00)</span></td>
                                <td class="py-3 px-2 text-right">82.1%</td>
                                <td class="py-3 px-2 text-right">95.0%</td>
                                <td class="py-3 px-2 text-right text-magenta">-3.0</td>
                                <td class="py-3 px-2 font-bold text-green-700 text-right">85.2</td>
                            </tr>
                            <!-- FAILURES -->
                            <tr class="border-b border-gray-800/30 hover:bg-white/5 transition-colors opacity-60">
                                <td class="py-3 px-2 text-gray-600">#98</td>
                                <td class="py-3 px-2 text-gray-600">EXP-012</td>
                                <td class="py-3 px-2 text-gray-600 truncate max-w-[200px] line-through">Asymmetric thrust balancing</td>
                                <td class="py-3 px-2"><span class="bg-gray-800/50 text-gray-500 px-2 py-0.5 rounded-full text-[10px]">Copilot (x1.00)</span></td>
                                <td class="py-3 px-2 text-right text-red-400">12.0%</td>
                                <td class="py-3 px-2 text-right text-red-400">0.0%</td>
                                <td class="py-3 px-2 text-right text-magenta">-5.0</td>
                                <td class="py-3 px-2 font-bold text-red-500 text-right">4.8</td>
                            </tr>
                            <tr class="hover:bg-white/5 transition-colors opacity-40">
                                <td class="py-3 px-2 text-gray-700">#142</td>
                                <td class="py-3 px-2 text-gray-700">EXP-001</td>
                                <td class="py-3 px-2 text-gray-700 truncate max-w-[200px] line-through">Initial naive geometry generation</td>
                                <td class="py-3 px-2"><span class="bg-gray-800/50 text-gray-500 px-2 py-0.5 rounded-full text-[10px]">Autopilot (x1.15)</span></td>
                                <td class="py-3 px-2 text-right text-red-500">0.0%</td>
                                <td class="py-3 px-2 text-right text-red-500">0.0%</td>
                                <td class="py-3 px-2 text-right text-magenta">-12.0</td>
                                <td class="py-3 px-2 font-bold text-red-700 text-right">0.0</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Right Column (Col span 4) -->
            <div class="lg:col-span-4 flex flex-col gap-6">
                
                <!-- Trajectory Preview -->
                <section class="glass rounded-2xl p-6 relative overflow-hidden group border border-gray-800">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 blur-[50px] rounded-full pointer-events-none"></div>
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-sm font-bold text-gray-300 uppercase tracking-widest">🛰️ Telemetry Array</h2>
                        <span class="text-[10px] text-green-400 font-mono animate-pulse">LIVE</span>
                    </div>
                    <div class="bg-black/90 rounded-xl aspect-[4/3] flex items-center justify-center border border-gray-900 overflow-hidden relative">
                        <img src="plots/SIM-001_orbit.png" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" class="w-full h-full object-contain opacity-90 hover:opacity-100 transition-opacity hover:scale-[1.02] duration-500 mix-blend-screen" alt="Orbital Plot">
                        <div class="hidden flex-col items-center text-gray-600">
                            <span class="text-3xl mb-2">📡</span>
                            <span class="text-xs uppercase tracking-widest">Awaiting Flight Data</span>
                        </div>
                        
                        <!-- HUD overlay -->
                        <div class="absolute top-2 left-2 text-[8px] font-mono text-cyan-500/70">
                            ALT: 1042.5m<br>
                            VEL: 240.2m/s
                        </div>
                        <div class="absolute bottom-2 right-2 text-[8px] font-mono text-cyan-500/70">
                            TARGET: ORBIT
                        </div>
                    </div>
                </section>

                <!-- Live Terminal Feed -->
                <section class="glass rounded-2xl p-6 border border-gray-800">
                    <h2 class="text-sm font-bold text-gray-300 uppercase tracking-widest mb-4">🖥️ MCP Terminal Stream</h2>
                    <div class="bg-[#050505] rounded-xl p-4 h-48 overflow-hidden relative border border-gray-900 font-mono text-[10px] leading-relaxed shadow-inner">
                        <div class="absolute top-0 left-0 w-full h-8 bg-gradient-to-b from-[#050505] to-transparent z-10"></div>
                        <div class="absolute bottom-0 left-0 w-full h-8 bg-gradient-to-t from-[#050505] to-transparent z-10"></div>
                        
                        <div class="animate-terminal text-green-500/80 whitespace-nowrap">
                            > SYSTEM BOOT: ForgeLoop v2.0<br>
                            > Connecting to BuildArena MCP... [OK]<br>
                            > Fetching collider_dump.toml... [OK]<br>
                            > Validating BESIEGE_DATA_PATH... [OK]<br>
                            <span class="text-yellow-500">> AI Proposal AI-142 Received.</span><br>
                            > Parsing structural XML payload...<br>
                            > Checking mass distribution matrix... [OK]<br>
                            <span class="text-cyan-400">> Human Decision Override: ACCEPT</span><br>
                            > Initiating Simulation MOCK-142<br>
                            > Reading trajectory.csv...<br>
                            > Angular progress: 1080 deg<br>
                            > Speed scalar: 0.942<br>
                            > Integrity check: 42/42 blocks attached<br>
                            > RUNNING TOKEN SCRUBBER...<br>
                            <span class="text-purple-400">> Stripped 14,203 JSON tokens from transcript.</span><br>
                            > Cost Penalty applied: -0.2<br>
                            > Build Mode Multiplier: x1.15 (AUTOPILOT)<br>
                            <span class="text-green-400 font-bold">> FINAL PERFORMANCE SCORE: 114.7</span><br>
                            > Uploading artifact to registry...<br>
                            <br><br><br><br><br><br>
                        </div>
                    </div>
                </section>
                
                <!-- Decision Ledger (Compact) -->
                <section class="glass rounded-2xl p-6 border border-gray-800">
                    <h2 class="text-sm font-bold text-gray-300 uppercase tracking-widest mb-4">📖 Ledger Log</h2>
                    <div class="space-y-4 font-mono text-[10px]">
                        <div class="border-l-2 border-green-500 pl-3">
                            <span class="text-gray-500">AI-142 -> </span> <span class="text-green-400">ACCEPT</span><br>
                            <span class="text-gray-300 text-xs">Execute compiled megaprompt.</span>
                        </div>
                        <div class="border-l-2 border-green-500 pl-3">
                            <span class="text-gray-500">AI-138 -> </span> <span class="text-green-400">ACCEPT</span><br>
                            <span class="text-gray-300 text-xs">Shift COM down by 2 blocks.</span>
                        </div>
                        <div class="border-l-2 border-red-500 pl-3">
                            <span class="text-gray-500">AI-137 -> </span> <span class="text-red-400">REJECT</span><br>
                            <span class="text-gray-300 text-xs">Too much thrust, spins out.</span>
                        </div>
                        <div class="border-l-2 border-yellow-500 pl-3">
                            <span class="text-gray-500">AI-136 -> </span> <span class="text-yellow-400">MODIFY</span><br>
                            <span class="text-gray-300 text-xs">Keep shielding, lower thrust.</span>
                        </div>
                    </div>
                </section>

            </div>
            
        </main>
        
        <footer class="mt-20 text-center text-gray-600 text-xs font-mono tracking-widest pb-8">
            <p>FORGELOOP.AI // SYSTEM STATUS: NOMINAL // BUILD_ARENA S01</p>
        </footer>
    </body>
    </html>
    """
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[Vercel] Successfully exported SHOCKING premium frontend to public/index.html")

if __name__ == '__main__':
    export_dashboard()
