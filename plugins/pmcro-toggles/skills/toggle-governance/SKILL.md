---
name: toggle-governance
description: "Govern feature toggles in an OpenFeature flags.json: add a flag with an owner, expiry and rollout stages; check every flag read-only for missing governance, expiry, type errors and leftover code references; plan removal. Use when the user mentions feature flags, toggles, rollout, flag cleanup or stale flags."
license: MIT
---

# toggle-governance

Feature flags are cheap to add and expensive to forget: a flag with no owner and no end date becomes permanent dead code and a hidden risk. This skill keeps every flag in a standard OpenFeature `flags.json` paired with an owner, an expiry and a removal plan, and gives the Checker a read-only way to find the ones that slipped.

## Do this

1. Check the request with `python scripts/check_input.py`. If it prints DENY, pass back the filled-in shape it prints. Its shape is `assets/templates/input.md.tmpl`.
2. Add a flag (Maker): `python scripts/toggles.py add NAME --type boolean --default false --description "..." --owner cto --expires 2026-12-31 --stages "internal,10%,100%"`. Log the change in the trail before running it.
3. Check all flags (Checker, read-only): `python scripts/toggles.py check --src src`. Exit 1 means findings; each line names the flag and the problem.
4. Plan a removal: `python scripts/toggles.py retire-plan NAME --src src`, then carry it out as normal Maker work.
5. Report with `assets/templates/output.md.tmpl`.

## Gotchas

- Governance lives in `flags.governance.json` beside the manifest, not inside `flags.json`, so the manifest stays valid for the OpenFeature CLI's code generator.
- The script never sets an age limit. The owner chooses `--expires`; the check only reports a date that has passed.
- A reference count of 0 is not proof the flag is unused at runtime (it may be read by name from configuration). Say so when it matters.
- `true` is not a number: a flag of type `integer` or `float` with default `true` is reported as a type error.

## Never

- Never change a flag in a live flag service (LaunchDarkly or another) from this skill. Live changes go through that service, with the founder's approval; see `references/connectors.md`.
- Never edit an existing flag's definition in place; retire it and add a new one.
- Never put a credential in `flags.json` or the governance file.

## Output contract

The filled `assets/templates/output.md.tmpl`, built from the script's own output, with its exit code. A clean check is evidence for the Checker, not a verdict. Detail: `references/design.md`.
