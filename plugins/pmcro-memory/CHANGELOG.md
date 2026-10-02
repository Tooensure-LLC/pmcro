# Changelog: pmcro-memory

## 0.3.0

- `shared-memory`: ids carry their tier's letter and counter (public P, company M, roundtable R, private V), so ids never collide and no tier's numbering reveals another; existing company ids M0001 onward are unchanged. `add` refuses absolute paths (EC-0001), after proving the check can fail. Closes the two gaps ADR 0027 left (ADR 0029).

## 0.2.0

- `shared-memory`: `memory.py add` refuses the `company` tier unless the repo is declared private (ADR 0027). Not changed: memory ids are still numbered across tiers, and memory bodies are not scanned for absolute paths.

## 0.1.0

- Scaffolded with `tools/pmcro.py new-plugin`.
- Filled the scaffold: `shared-memory` with `memory.py`, viewers reference and tests (see ADR 0021).
