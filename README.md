# ForgeLoop-AI 🚀

**An auditable, high-performance Human-AI Collaboration framework for the BuildArena Construction Challenge S01.**

## 1. The Problem
While state-of-the-art LLMs possess vast conceptual knowledge, they struggle with spatial reasoning and physics-aligned engineering. Simply asking an LLM to "build a rocket" through the BuildArena MCP often results in chaotic, non-functional geometry. To achieve stable orbital flight in *Besiege*, we need more than a smart model—we need a rigorous engineering process.

## 2. Why ForgeLoop?
ForgeLoop goes beyond the standard "AI generated this" narrative. It is a systematic, auditable pipeline that proves *how* humans and AI collaborated. 

We built ForgeLoop around three core pillars:
*   **The Experiment Engine:** Every build attempt is tracked (e.g., `EXP-001`), capturing the AI's prompt, the resulting `.bsg` machine, flight telemetry, and projected score.
*   **The Decision Ledger:** Every AI proposal is explicitly marked `ACCEPT`, `MODIFY`, or `REJECT` by a human engineer, preserving a clear record of human judgment.
*   **Local Scoring Engine:** Before we submit anything, our local evaluator automatically grades the flight trajectory (`trajectory.csv`) using the official Kaggle weights (70% Orbit, 20% Speed, 10% Integrity) minus the token cost penalty.

## 3. The Human-AI Workflow
Our workflow is designed to maximize the competition's unique scoring math:

1.  **Copilot Exploration:** We use human-in-the-loop guidance (`x1.00` multiplier) to rapidly iterate on machine architectures, testing mass distribution, staging, and symmetry.
2.  **Autopilot Extraction:** Once a successful engineering strategy is discovered, we compress the knowledge into a dense, token-efficient mega-prompt.
3.  **Final Autopilot Execution:** We run the final official build purely in **Autopilot Mode** to claim the massive `x1.15` score multiplier while heavily minimizing the token cost penalty.
4.  **Legal Human Boss Tuning:** In strict compliance with the rules, humans never manually alter geometry. Human input is isolated entirely to post-generation tuning of non-geometry fields (controls, timings, keybindings) to maximize the flight's Speed Score.

## 4. Repository Structure

```text
ForgeLoop-AI/
├── README.md                 # Project overview and reproduction instructions
├── pyproject.toml            # Dependencies and package configuration
├── src/forgeloop/
│   ├── data/                 # Data contracts for BSG artifacts, CSV trajectories, and JSON histories
│   ├── evaluation/           # Local Kaggle math grading (Orbit, Speed, Integrity, Cost)
│   ├── experiments/          # The Experiment Engine tracking each flight
│   └── decisions/            # Human-AI ledger tracking ACCEPT/REJECT proposals
├── docs/                     # Briefs, Architecture, and Decision ledgers
├── experiments/              # Raw data for EXP-001, EXP-002, etc.
└── submissions/              # Hardened final packages for Kaggle upload
```

## 5. Reproducibility
Every experiment in this repository is designed to be fully reproducible. The official `machine_raw.bsg`, `trajectory.csv`, and `chat_transcript.md` are securely logged. Judges can run our local evaluator against our generated trajectory files to mathematically verify our claimed performance metrics.
