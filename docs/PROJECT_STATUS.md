# Project review — September 12, 2026

## Purpose

BuildArena asks participants to construct and pilot a Besiege spacecraft. ForgeLoop wraps the surrounding experiment/review workflow; it is not the game. The friend's message means: improve the project using public sources without depending on an unavailable provider API key.

## Key-free implementation

`forgeloop-catalog` searches 97 entries in a bundled, attributed organizer block-role snapshot and can refresh it from a pinned public GitHub revision. Runtime search is offline. This provides grounded block references for human/agent planning, without claiming to generate geometry or infer physics.

There is no existing LLM-provider client, key environment variable, or working MCP connection in this repository. `BuildArena-2.0/` was an empty directory. The strategist uses thresholds, and the prompt compiler formats a supplied strategy. A future model backend should be optional and expose whether it uses a local model, an existing agent, or a hosted provider.

## Audit findings addressed

- Submission packaging created empty required files and reported success.
- Generic regex scrubbing deleted arbitrary JSON/XML and collapsed transcript whitespace.
- Orbit, speed, and integrity calculations returned constant zero.
- Token helpers disagreed and claimed official accuracy for invented formulas.
- Registry IDs could collide or overwrite existing experiments.
- Dashboard contained hardcoded high scores, a pretend MCP stream and an unrelated video.
- Report generation asserted model usage and flight success without evidence; plotting invented absent coordinates.
- Dependencies omitted actual plotting/terminal packages while requiring unrelated notebooks/ML tools.
- `.gitignore` contained embedded NUL bytes and its broad data pattern hid the source data package.

## Remaining work

1. Connect a compatible agent/local model to the organizer's BuildArena MCP on a supported game machine.
2. Import an actual tracker CSV and match its exact schema/valid-run rules; current local normalized columns are not a verified official adapter.
3. Implement official scoring only against published organizer code and reference fixtures. Local scoring and token penalties remain estimates.
4. Verify tuned-vs-raw geometry and legal parameter ranges using the organizer's definitions; basic XML checks cannot establish eligibility.
5. Execute a real build/flight, retain original histories/transcript and produce an evidence-backed writeup. No real flight was run during this review.

## Sources

- [Competition overview and submissions](https://www.kaggle.com/competitions/build-arena-human-ai-colleberation-engineering-challenge/overview)
- [Official BuildArena setup](https://github.com/build-arena/BuildArena-2.0)
- [Pinned block roles](https://github.com/build-arena/BuildArena-2.0/blob/fc5ef3bd6be30a69bb7bc7b0c1f2b53ea794ddbc/blocks/block_roles.toml)

The competition overview checked during this review lists September 12 AOE, 2026 as the deadline. Verify current availability directly on Kaggle.

## Verification in this workspace

- 50 tests passed; 12 pandas-dependent telemetry/strategist tests skipped on Android Python 3.14 because scientific dependencies were unavailable. Plotting runtime was not exercised.
- Python source compilation, dashboard generation, both synthetic demonstration commands and wheel build succeeded.
- Public-source refresh succeeded against the pinned organizer revision; offline catalog queries and cache-failure behavior passed tests.
- CI installs the analysis dependencies to run the telemetry tests on its Linux runner; that remote CI run has not been executed here.
