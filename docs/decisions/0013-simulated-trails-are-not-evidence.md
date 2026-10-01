# 0013: Simulated trails are not evidence

Status: accepted · 2026-10-01

## Context
An exported AI Studio session (Gemini 3.7 flash, 212 messages) ran 20+ PMCR-O cycles. Its settings had code execution off (`enableCodeExecution: false`), browsing off, and the export contains zero executed-code results. Yet Maker turns state they executed commands and show "real command output" and exit codes, and one model plays Orchestrator, Planner, Maker, Checker and Reflector. By the company's own laws (Verify First; Checker Verdict Only; an independent Checker) those trails prove nothing.

## Decision
Frames carry `executed`, `executor` and `checker_independent` (see `docs/product/trail.md`). Simulated frames may be kept as design material but are never training data and never count as verification. The session's design content (the seed contract, the strict marketplace layout) is valuable and is reconstructed in the docs for confirmation, not trusted as fact.

## Consequences
Training a model on unexecuted trails would teach it to claim verification it did not do. The trails in ProjectName that record real `dotnet build` and `dotnet test` output with an independent Checker agent are the evidence-grade ones (not audited here). Existing frames need a provenance backfill (OPEN).
