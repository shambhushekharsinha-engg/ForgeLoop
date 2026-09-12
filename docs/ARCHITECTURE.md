# ForgeLoop architecture

ForgeLoop is a local experiment toolkit. External model generation, BuildArena MCP calls, game execution, and official tracker integration are not implemented.

## Public reference data

`public_sources.py` reads a bundled, normalized block-role catalog. The CLI searches it offline or refreshes from a pinned organizer source. Provenance includes revision, retrieval time, source digest, attribution and license. These names and roles do not supply game geometry or physics.

## Experiment and review

`decisions/` records proposals and human decisions. `experiments/` associates a proposal, review, artifacts and estimated result with a unique experiment ID. Registration rejects duplicates. The in-memory registry is not a persistent audit database.

`agents/compiler.py` formats a strategy into a reusable prompt; this is not model inference or a guarantee of Autopilot eligibility. `agents/strategist.py` reports local telemetry observations and tentative next checks; it cannot establish flight causes from position alone.

## Local analysis

`data/trajectory.py` validates ForgeLoop's normalized CSV schema. Required columns are timestamp (seconds), x, y and z. Optional angular_progress uses signed cumulative degrees. Integrity estimation requires explicitly measured original tracked and connected block counts. These columns are not yet a verified adapter for the official tracker.

`evaluation/` provides bounded local proxies and a configurable token-cost estimate. Speed requires an explicit reference duration. Neither token estimation nor the local trajectory proxies exactly reproduce unpublished/unintegrated official scoring. The default tokenizer uses UTF-8 byte length; a requested tiktoken encoder is optional and may require a first-use data download.

## Artifacts and output

`cli/packager.py` requires six existing nonempty artifacts, validates basic formats, and atomically archives their original bytes. It does not prove MCP origin, legal tuning, or competition eligibility. Geometry verification is explicitly unimplemented.

`reporting/` plots supplied coordinates and drafts writeups with unknown evidence left for completion. `cli/export_web.py` renders supplied registry results as an HTML snapshot; without a registry, it displays an empty result table. It is not live telemetry.

`simulation/` creates synthetic test trajectories and placeholder machine XML. These fixtures are not playable validated machines, a physical simulation, or acceptable flight evidence.

See [project status](PROJECT_STATUS.md) for sources and next integration work.
