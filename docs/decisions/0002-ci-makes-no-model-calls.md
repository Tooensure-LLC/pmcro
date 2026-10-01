# 0002: CI makes no model calls

Status: accepted · 2026-10-01

## Context
The owner has only Grok credits. A CI that calls a paid model would cost money on every push and could not be trusted when a key is missing.

## Decision
CI runs the validator, unit tests and a MAF reachability check only: no secrets, no network model calls. LLM evals are a separate manual job, not built yet (OPEN).

## Consequences
CI proves structure and guards, not that a skill beats a no-skill baseline. That needs evals, which dotnet/skills does with `eval.yaml` graders.
