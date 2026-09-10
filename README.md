[![ForgeLoop CI](https://github.com/shambhushekharsinha-engg/ForgeLoop/actions/workflows/ci.yml/badge.svg)](https://github.com/shambhushekharsinha-engg/ForgeLoop/actions)
# ForgeLoop-AI 🚀

**An advanced, auditable Human-AI Collaboration framework built to dominate the BuildArena Construction Challenge S01.**

![BuildArena](https://img.shields.io/badge/BuildArena-S01-00d2ff?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge) ![Vercel](https://img.shields.io/badge/Vercel-Ready-black?style=for-the-badge)

## 🌌 The Mission
The BuildArena S01 challenge tasks us with using an AI agent to structurally build a spacecraft in *Besiege*, which a human then manually pilots into orbit in *The Broken Beyond* sandbox. 

While SOTA LLMs struggle with spatial reasoning, ForgeLoop mathematically orchestrates their outputs into winning designs by shifting the paradigm from "blind generation" to a **Rigorous Experiment Engine**.

---

## 🏗️ Core Architecture & Features

### 1. The Experiment Engine & Decision Ledger
We don't overwrite files. Every single AI build is logged as an Experiment (e.g., `EXP-042`). Every AI architectural proposal is explicitly reviewed by the human engineer (`ACCEPT` / `MODIFY` / `REJECT`). This creates a mathematically auditable trail of Human-AI collaboration.

### 2. Local Kaggle Math Engine
Before we submit, ForgeLoop locally calculates our score exactly matching Kaggle's formula:
* **70% Orbit Progress** (Maxes at 3 full periods / 1080 degrees)
* **20% Speed Score** (Fastest orbital insertion)
* **10% Structure Integrity** (Parts remaining attached)
* **Cost Penalty** (Token footprint estimation)

### 3. The "Token Scrubber" (Cost Minimizer)
Kaggle penalizes large token footprints but allows excluding generated structural payloads. Our `TranscriptScrubber` uses Regex to automatically strip massive JSON/XML geometric payloads from the `chat_transcript.md` before submission, mathematically lowering our Cost Penalty to maximize the final score.

### 4. The Autopilot Mega-Prompt Compiler
The competition offers a `x1.15` multiplier for "Autopilot" (zero-shot) runs, but a `x1.00` multiplier for "Copilot" (iterative) runs.
Our strategy:
1. Iterate locally using **Copilot** to find the winning structural design.
2. Run the `AutopilotCompiler`, which distills the successful strategy into a highly dense, token-efficient mega-prompt.
3. Submit the final run via **Autopilot** to claim the massive `x1.15` multiplier with minimum token penalty.

### 5. 3D Orbital Trajectory Plotter
Using `matplotlib`, ForgeLoop parses the tracker's `trajectory.csv` to generate beautiful 3D graphs of our orbital insertions, providing robust visual proof of our aerospace engineering logic for the judges.

### 6. Synthetic Flight Simulator
Designed for offline capability, the `ForgeLoopSimulator` uses `numpy` trigonometry to simulate realistic orbital physics (X/Y/Z telemetry + atmospheric noise) to train our grading models and plotters entirely without the game installed.

### 7. Automated One-Click Packager
To eliminate manual error on submission day, our `SubmissionPackager` automatically verifies the 6 strictly required Kaggle files (`machine_raw.bsg`, `trajectory.csv`, etc.), scrubs the tokens, and securely zips them into `ForgeLoop_Submission.zip`. It also auto-generates the mandatory Markdown writeup template.

### 8. Web Dashboard (Vercel Ready)
ForgeLoop exports a static HTML mission control dashboard that displays our Live Leaderboard, making it 1-click deployable to Vercel to publicly showcase our engineering dominance to the community.

---

## 📂 Repository Structure

```text
ForgeLoop/
├── .github/workflows/        # Automated CI/CD Pytest pipelines
├── src/forgeloop/
│   ├── agents/               # Prompt Compiler and Token Scrubber
│   ├── cli/                  # Packager, Leaderboard, and Web Exporter
│   ├── data/                 # Strict contracts for BSG and CSV artifacts
│   ├── decisions/            # Human-AI ACCEPT/REJECT Ledger
│   ├── evaluation/           # Kaggle math engine
│   ├── experiments/          # Telemetry and score tracking
│   ├── reporting/            # 3D Orbit Plotter & Auto-Writeup Generator
│   └── simulation/           # Synthetic Besiege Physics Engine
├── public/                   # Static HTML Dashboard for Vercel
├── vercel.json               # Vercel Deployment Configuration
└── README.md                 
```

## 🚀 Deployment (Vercel)
This project is configured for instant hosting on Vercel. 
1. Link your GitHub repository to Vercel.
2. The `vercel.json` file will automatically run the export script to generate the Live Leaderboard HTML into the `public/` directory.
3. Your Mission Control dashboard is instantly live!
