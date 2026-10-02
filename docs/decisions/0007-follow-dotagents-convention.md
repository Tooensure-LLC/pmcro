# 0007: Follow the dotagents convention

Status: accepted (candidate) · 2026-10-01 (owner instruction: the PMCR-O assistant will use dotagents)

## Context
The owner is building a replica of Claude on the dotagents convention and wants this marketplace to support it. The research claimed `@sentry/dotagents` 3.2.0 existed and consumed a portable plugin bundle.

## Decision
Keep plugins as portable folders (`plugin.json` + `skills/`) so dotagents can consume them directly. Verify with the real CLI rather than guessing its schema: `tools/dotagents_smoke.py` runs init, add, doctor and checks the lock. Do not commit a hand-written `agents.toml` to this repo; consumers generate theirs.

## Consequences
A real run passed (see `docs/dotagents.md`). Not verified: host loading, MCP and hook projection, dotnet/skills through dotagents. Private trail entries must never be projected into `.agents/`.
