# Changelog: pmcro-memory

## 0.2.0

- `shared-memory`: `memory.py add` refuses the `company` tier unless the repo is declared private (ADR 0027). Not changed: memory ids are still numbered across tiers, and memory bodies are not scanned for absolute paths.

## 0.1.0

- Scaffolded with `tools/pmcro.py new-plugin`.
- Filled the scaffold: `shared-memory` with `memory.py`, viewers reference and tests (see ADR 0021).
