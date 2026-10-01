# Offline kit and the unattended runner

Status: kit CANDIDATE and tested; runner is a DESIGN only (not built). 2026-10-01.

## Why

The owner has a second computer (an i9) with no internet, to run models and experiments 24/7. Offline, skills, MAF, stdio MCP servers and local Ollama models all work; anything that needs the network does not. The trail player's private tiers are safest there because nothing can leave.

## The kit (`tools/offline_kit.py`)

Run on an internet-connected machine, after committing:

```
python tools/offline_kit.py --out kit/ --platform win_amd64 --python-version 3.11
```

It writes `pmcro.bundle` (git bundle of all refs), `wheelhouse/` (pinned wheels: pyyaml 6.0.2, agent-framework-core 1.19.0, agent-framework-ollama 1.0.0b260813, mcp 1.28.1), `INSTALL.md` and `SHA256SUMS`. `--with-dotagents` also packs `@sentry/dotagents` 3.2.0 under `node/`.

**Verified:** built for `manylinux2014_x86_64` / Python 3.11, then, in a fresh virtual environment, installed with `pip install --no-index`, cloned from the bundle, ran `tools/pmcro.py validate` (ok) and the unit tests (46 passed). The offline test caught one real bug (a global `--pre` pulled a prerelease pydantic); fixed.

**Not verified:** a Windows or macOS wheelhouse (the `--platform` option was not run for those); installing from `node/` offline; Ollama itself.

**Not in the kit:** model weights. Download models on an online machine and copy Ollama's model directory across (check Ollama's current docs for the location and format), and install Ollama from its offline installer.

## Unattended runner (design, not built)

A 24/7 agent cannot wait for a human approval, so it must be safe without one.

| Rule | Why |
| --- | --- |
| Tools are read-only plus one scratch directory; no network, no shell outside the scratch directory | nothing it does can damage anything that matters |
| `allowed_tools` per role (ADR 0005); the Checker has read tools only | a mistake cannot become a write |
| MaxLoops = 3, a wall-clock and token budget per cycle, then HALT and wait | no runaway loops |
| Every cycle writes a trail frame with cost (tokens, model, seconds, loops) before acting | Log Before Act; economic accounting |
| Output leaves as a git bundle the founder reviews; nothing pushes itself | a human decides what reaches a real repo |
| Private and roundtable tiers stay on that machine and are never in a bundle | ADR 0003 |

Quality depends on the GPU and RAM, which are not yet known; a small local model suits drafts, replay, checks and experiments better than hard judgment. OPEN: scheduler, model choice, budget numbers.
