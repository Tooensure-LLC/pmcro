# Changelog: pmcro-core

## 0.6.0

- `new-skill`: every new skill now also gets an input shape (`assets/templates/input.md.tmpl`) and `scripts/check_input.py`, which accepts a complete request or denies it and returns the shape to fill in. The SKILL.md template gains a Gotchas section (the Agent Skills docs call gotchas the highest-value content), and `new-skill` now says to run `find-skill` and to consult the Agent Skills docs server when connected.
- Added `find-skill`: keyword search over this repository's skills plus the list of other places to check, so a skill is only created when none fits.

## 0.5.0

- Added `new-skill`: creates a skill inside an existing plugin in the templated shape; its `assets/templates/` is now the single template for every new skill, and `tools/pmcro.py new-plugin` uses it for a plugin's first skill.

## 0.4.0

- `inbox`: priority rubric (`references/priority.md`), `reprioritize` with a required reason and logged event, `list --stale DAYS` so no area starves, priority 0 needs `--reason`; an agent may raise but not lower a founder item.

## 0.3.0

- Role skills refreshed to the owner's exact bytes (orchestrate ebf5b3f7, plan 2b13abd7, make d826e231, check 0e7ff3fa, reflect e1f8bae7); the earlier copies were host-normalized (quoted frontmatter) and plan lacked the owner's repaired description bytes. Added the owner's `create-skill` (5b0799f6).

## 0.2.0

- Added `inbox`: file-based message queue with tiers, dedupe, atomic claim and append-only status events (see ADR 0012).

## 0.1.0

- Added the five role skills (orchestrate, plan, make, check, reflect), copied byte-identical from the skills drive.
- Added `trail-player`: tiered, append-only founder entries with a writer script and guards (see ADR 0003).
