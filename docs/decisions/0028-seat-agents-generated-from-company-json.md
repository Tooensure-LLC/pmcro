# 0028: Seat agents are generated from company.json, read-only, one per seat

Date: 2026-10-01. Status: built and tested (CANDIDATE plugin `pmcro-seats`); owner request: "marketplace skills, commands and agents so we can talk".

## Context

The founder wants to talk to the company's C-Suite from the marketplace. `pmcro-csuite` holds 9 imported seat skills that do not match the company roster (it has a CHRO; it lacks the CDO, CISO, CPO, CCO, Auditor, CTO Checker and Chief Agent Officer). The company repo's `company.json` is the source of truth for the 15 seats.

## Decision

- `tools/seats.py import` snapshots the seats, laws, earned constraints, founder-first list and round tables from `company.json` at a recorded commit into `plugins/pmcro-seats/skills/round-table/assets/seats.json`, replacing the founder's personal name (ADR 0024).
- `tools/seats.py gen` writes one agent per seat to `plugins/pmcro-seats/agents/`. CI fails if they differ (`gen --check`), so they are never hand-edited.
- Every seat agent is read-only (Read, Grep, Glob). Seats give views inside their boundary; work goes through the loop.
- Phases are not in `company.json`; they are fixed in `tools/seats.py` from the Company Foundation baseline (Phase 1 EXISTING; 2 to 4 PROPOSED), and every PROPOSED seat says it advises only.
- A round table is chaired by the Chief of Staff and holds at most six seats, as `company.json` records.

## Consequences

`pmcro-csuite` stays as an imported CANDIDATE; which of the two plugins survives is the owner's decision. A change to `company.json` reaches the agents only when someone re-runs `import` with the new commit. Not verified: a live conversation with the agents, and agent or command loading in hosts other than Claude Code.
