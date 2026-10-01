# pmcro-core

The PMCR-O role skills and the Trail Player. Every seat bot installs this plugin first.

## Skills

| Skill | Role | What it does |
| --- | --- | --- |
| `orchestrate` | Orchestrator | Coordinates one manual role transition and names the next fixed-order role. Never plans, makes, checks or reflects. |
| `plan` | Planner | Writes the minimum sufficient plan: purpose, required observations, satisfaction boundaries. |
| `make` | Maker | Executes one plan and records observed evidence. Makes no completion claim without it. |
| `check` | Checker | Independently reruns the proof, read-only, and issues exactly one verdict: PASS, LOOP or HALT. |
| `reflect` | Reflector | Records what a finished cycle revealed. Append-only; changes no verdict or policy. |
| `inbox` | (founder aid) | Durable, append-only message queue: capture every message verbatim, claim items safely, triage, close with evidence (`scripts/queue.py`). |
| `trail-player` | (founder aid) | Interviews the founder and records entries with a disclosure tier; see `skills/trail-player/references/tiers.md`. |

The five role skills are byte-identical to the owner's skills drive. Do not edit them here.

## Install

```
/plugin marketplace add Tooensure-LLC/pmcro
/plugin install pmcro-core@pmcro-plugins
```

Under MAF, load with `SkillsProvider.from_paths("plugins/pmcro-core/skills", script_filter=...)`; see `pmcro-dotnet` `maf-local-skills`.

## Status

CANDIDATE. 7 skills load under MAF 1.19.0 (tested in CI). No independent Checker has reviewed this plugin. Trail Player and Inbox storage for private tiers is local only (files on one machine, not a networked broker) and is lost with a temporary container.
