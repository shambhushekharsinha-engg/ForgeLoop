# ForgeLoop

ForgeLoop is a Python toolkit for preparing and reviewing experiments for the BuildArena Besiege spacecraft challenge. It records human decisions, inspects local flight data, estimates scores, drafts prompts/writeups, and packages existing artifacts.

**Current status:** a development toolkit, with synthetic demonstrations. It does not currently connect to an LLM or the BuildArena MCP, construct a playable spacecraft, or run the game. Local scores are estimates, not official leaderboard results. The synthetic trajectory generator is a plotting fixture, not a physics simulator.

## What does the missing API key mean?

There is no API-key requirement in ForgeLoop's implemented features. The existing strategist is a rule-based helper and the compiler formats a prompt. A hosted model provider may require credentials if you choose to add one. The organizer's tools can instead be used through a compatible existing agent or local model; public metadata does not replace model inference or game assets.

The official challenge uses **Besiege + The Broken Beyond**, with machines built through the organizer's MCP and flight evidence recorded by the game tracker. See the [competition overview](https://www.kaggle.com/competitions/build-arena-human-ai-colleberation-engineering-challenge/overview) and [organizer setup](https://github.com/build-arena/BuildArena-2.0). The overview checked September 12, 2026 lists the S01 deadline as September 12 AOE, 2026. Confirm current submission availability on Kaggle.

## Start without a key

Python 3.10+:

```sh
pip install -e .
forgeloop-catalog rocket
forgeloop-catalog --type connection
forgeloop-catalog --json > block-reference.json
```

The bundled catalog contains actual public block names, IDs, roles, and pointer axes from a pinned organizer commit. Searches run offline. It does **not** include game meshes, collision bounds, thrust specifications, or flight evidence.

Refresh the pinned source into a separate cache (internet needed, no account/key):

```sh
forgeloop-catalog --refresh .cache/block_catalog.json
forgeloop-catalog --catalog .cache/block_catalog.json wheel
```

Without installing, on Python 3.11+:

```sh
PYTHONPATH=src python -m forgeloop.cli.catalog rocket
```

The normalized catalog retains its source URL, commit, retrieval timestamp, SHA-256 and attribution. Upstream data is **CC BY-NC 4.0**; its license is included in `src/forgeloop/resources/BuildArena-LICENSE.txt`. This is a metadata reference for planning; block availability must still be checked against your installed game/DLC.

## Analysis and development

```sh
pip install -e ".[analysis,dev]"
python -m pytest -q
python simulate_phase5.py
python showcase.py
python -m forgeloop.cli.export_web
```

`simulate_phase5.py` and `showcase.py` use synthetic examples. Install `[tokens]` only if you need optional local tokenizer support. The default estimate works offline. Android/Termux can run the catalog and core utilities; scientific packages may require platform-specific installation. Full game testing requires the organizer-supported desktop setup.

## Implemented safeguards

- Invalid numeric scores and malformed local trajectories are rejected.
- Orbit, speed and integrity helpers expose local assumptions; missing measurements cannot prove success.
- Packaging requires existing, nonempty artifacts and preserves original transcript bytes.
- The transcript scrubber preserves text by default; optional marked tool-output redaction creates review text, not proof of official token eligibility.
- Dashboard/writeup output distinguishes recorded facts, estimates and missing evidence.

Basic file validation cannot prove MCP origin, legal geometry tuning, vanilla parameter ranges, or competition eligibility. Keep raw build files, histories and transcripts unchanged. Prompt compilation alone does not qualify a run as Autopilot.

See [current status and next steps](docs/PROJECT_STATUS.md) for the audit and remaining integration work.
