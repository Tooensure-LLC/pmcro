# 0001: One portable core, generated vendor adapters

Status: accepted (candidate) · 2026-10-01

## Context
Claude, Cursor, Codex and Copilot each want their own manifest files. Hand-maintaining four copies drifts.

## Decision
`plugins/<name>/plugin.json` (Agent Plugins 1.0.0) and `skills/` are the source. `python tools/pmcro.py gen` writes every vendor file; CI fails if they differ. The Claude manifest omits `$schema` because Claude strips unknown keys with a warning.

## Consequences
Never hand-edit generated files. Codex's marketplace layout is unverified (secondary sources); its copy follows the Claude shape.
