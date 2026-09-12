# 🚀 ForgeLoop

[![ForgeLoop CI](https://github.com/shambhushekharsinha-engg/ForgeLoop/actions/workflows/ci.yml/badge.svg)](https://github.com/shambhushekharsinha-engg/ForgeLoop/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**ForgeLoop** is a comprehensive Python toolkit designed for the **BuildArena Besiege Spacecraft Challenge**. It provides a rigorous, offline-first pipeline for evaluating flight telemetry, standardizing AI prompts, searching offline block catalogs, and securely packaging final artifacts for Kaggle submissions.

---

## 🌟 Key Features

- **📊 Telemetry Strategist**: Ingests offline game trajectory data (CSV) and computes rigorous mathematical diagnostics (e.g., standard deviations and precise z-axis bounds) to inform your next engineering iterations.
- **🏗️ Offline Block Catalog**: Search through a pinned, fully attributed organizer snapshot of 97+ Besiege block roles completely offline. No API key required for planning geometry.
- **🤖 Safe Autopilot Compiler**: Formats human-reviewed strategies into token-efficient prompts. Automatically prevents unreviewed or failed experiments from being compiled.
- **🛡️ Submission Packager**: A pre-flight engine that verifies the exact presence of `machine_raw.bsg`, `chat_transcript.md`, and other Kaggle artifacts, ensuring you are never disqualified for missing files.
- **🌐 Static Web Dashboard**: Instantly exports your local experiment ledger and trajectory plots into a beautiful, static web dashboard ready for Vercel.

## ⚡ Quick Start (Submission Deadline)

We have streamlined the workflow for fast execution via a `Makefile`.

### 1. Setup
```bash
git clone https://github.com/shambhushekharsinha-engg/ForgeLoop
cd ForgeLoop

# Install all analysis and development dependencies
make install
```

### 2. Configure Environment
Rename the template file to `.env` and fill in your LLM API keys:
```bash
cp .env.template .env
```
*(Note: ForgeLoop's core analysis tools run offline. The API key is only required if you choose to connect a hosted model provider for prompt inference.)*

### 3. Core Commands
Run these commands to execute the pipeline:
- `make test` — Run the entire 146+ unit test suite to ensure system integrity.
- `make simulate` — Run a synthetic trajectory generation demo and test the evaluators.
- `make dashboard` — Generate the static Vercel web UI into the `public/` directory.
- `make verify` — **Crucial for Kaggle:** Run the strict pre-flight checklist to ensure all your artifacts are present.
- `make package` — Securely zip your final `ForgeLoop_Submission.zip`.

---

## 🔍 Offline Block Catalog Usage

ForgeLoop bundles actual public block names, IDs, and pointer axes from a pinned organizer commit.

**Search Blocks Offline:**
```bash
forgeloop-catalog rocket
forgeloop-catalog --type connection
```
*Outputs JSON data representing the block metadata.*

**Refresh Cache from Source:**
```bash
forgeloop-catalog --refresh .cache/block_catalog.json
```

---

## 🛠️ Implemented Safeguards & Architecture

ForgeLoop was audited and re-engineered for strict defensive programming:
- **No Hallucinated Scores**: Invalid numeric scores and malformed trajectories are aggressively rejected.
- **Missing Telemetry Handling**: The `TelemetryStrategist` verifies exact column presence before asserting mathematical claims.
- **Graceful Tokenizer Fallbacks**: If `tiktoken` is unavailable, the pipeline falls back to an offline UTF-8 byte estimate (`math.ceil(len(bytes) / 4)`).
- **Atomic Concurrency**: Safe concurrent lock handling for file updates, preventing Windows OS locking crashes.

For a deeper dive, read the [Architecture Guide](docs/ARCHITECTURE.md) or the latest [Project Status Audit](docs/PROJECT_STATUS.md).

---

## 📜 Official Competition Rules

The official challenge uses **Besiege + The Broken Beyond**. Machines must be built through the organizer's MCP and flight evidence must be recorded by the official game tracker.
- [Kaggle Competition Overview](https://www.kaggle.com/competitions/build-arena-human-ai-colleberation-engineering-challenge/overview)
- [Official BuildArena Setup](https://github.com/build-arena/BuildArena-2.0)

> **Disclaimer:** Basic file validation cannot prove MCP origin, legal geometry tuning, or competition eligibility. Keep raw build files, histories, and transcripts unchanged.
