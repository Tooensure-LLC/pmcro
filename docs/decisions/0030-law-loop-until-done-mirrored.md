# 0030: Law EC-009 Loop Until Done is mirrored into this repository

Date: 2026-10-02. Status: built and tested. Decision made by the founder in the company repo (trail 0014); this repo only mirrors it.

## Context

The law "MaxLoops: max 3 loops per trail, then stop and ask the founder" was replaced in `company.json` of the company repo by the founder, as trail 0014: branch `law-loop-until-done`, merged to main at commit `cd4c19b`, Checker verdict PASS, sealed. The source of truth for laws is `company.json`; this repository holds mirrors and a generated snapshot.

## Decision

- The law now reads: a trail loops until a separate Checker says PASS or HALT; there is no fixed count; two LOOP verdicts in a row that name the same defect IDs stop the loop and ask the founder.
- The snapshot was re-imported with `tools/seats.py import ... --sha cd4c19b...` and the 15 seat agents regenerated; `tools/seats.py drift` reports 0 parts differing.
- Mirrored by hand where the old rule was stated: `AGENTS.md`, `docs/offline-kit.md`, `docs/product/company-model.md`, `docs/product/foundations.md`, backlog row 67.
- Unchanged on purpose: the offline kit keeps its wall-clock and token budget per cycle, and spending stays the founder's. Removing the loop count does not remove the cost brake.

## Consequences

- How the Checker ran in the company repo: it reran `tools/build.ps1` three times with PowerShell 7.5.3 on Linux (exit 0, identical state), `tools/check-queue.ps1` (PASS over 21 items) and a case-insensitive search for the old rule that can fail. Loop 1 gave LOOP naming `D1-old-rule-in-index-generator`; loop 2 gave PASS.
- Not tested: build determinism on Windows PowerShell 5.1.
- Open observation for the founder: the COO seat text still lists "loop caps" next to routine cycle caps. It is a seat boundary, not the law, and was left unchanged.
- `tools/seats.py import` had a bug (it printed a variable that only exists in another function, after writing the snapshot). Fixed, with a test that fails on the old code.
- "Two LOOP verdicts naming the same defect IDs" depends on defect IDs staying stable between loops; rewording a defect under a new ID would dodge the stop. The Checker names IDs; keeping them stable is part of the Checker's job.
