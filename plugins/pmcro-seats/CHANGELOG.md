# Changelog: pmcro-seats

## 0.2.1

- Re-imported from the company repo at commit cd4c19b: law EC-009 is now Loop Until Done (no fixed count; two LOOP verdicts in a row naming the same defect IDs stop the loop and ask the founder). All 15 seat agents regenerated; `drift` reports 0.
- Fixed `tools/seats.py import`, which crashed on its own status line after writing the snapshot; `import` and `drift` now have an end-to-end test on a temp snapshot.

## 0.2.0

- Every seat agent carries the company roster, so the Chief of Staff can route and any seat can name an owner who is not present.
- Round table: the chair's closing receives its own opening, and the output has an "Owners not at the table" section. Both fixes come from a live test of the executive table (see `skills/round-table/references/design.md`).
- `tools/seats.py drift` reports when the snapshot no longer matches `company.json` (ADR 0029).

## 0.1.0

- 15 read-only seat agents generated from the company's `company.json` by `tools/seats.py` (founder's personal name replaced, ADR 0024).
- `round-table` skill with `scripts/run.py` (speaking order, chair first, at most six seats) and the input and output shapes.
- Commands `/pmcro-seats:ask` and `/pmcro-seats:round-table`.
