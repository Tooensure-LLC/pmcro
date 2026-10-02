# toggle-governance: design notes

## Why OpenFeature's manifest

OpenFeature is the vendor-neutral feature-flag standard; its CLI reads `flags.json` (schema: `schema/v0/flag-manifest.json` in open-feature/cli) and generates typed accessors for C#, Python, Go, TypeScript and more. Keeping flags in that file means the same manifest feeds code generation, and this skill adds governance without forking the format.

## Why a sidecar file for governance

The manifest schema holds `flagType`, `defaultValue` and `description`. Owner, expiry and rollout stages are governance, not flag definition, so they live in `flags.governance.json`. The check reports any flag that is in one file but not the other.

## Roles

- Maker: `add`, and the code changes a `retire-plan` lists.
- Checker: `check`, which only reads. Its exit code and lines are evidence the Checker can rerun independently.
- Reflector: recurring findings (for example many expired flags) become one candidate constraint.

## Not covered or not verified

- No live flag service is called. LaunchDarkly's hosted MCP server exists but was not tested here; see `connectors.md`.
- Reference counting is a whole-word text search over common source suffixes; it does not parse code.
- Rollout stages are recorded, not enforced; stage progression belongs to the flag service.
