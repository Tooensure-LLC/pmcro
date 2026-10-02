# pmcro-toggles

Feature-toggle governance for PMCR-O: every flag in an OpenFeature `flags.json` has an owner, an expiry and a removal plan, and a read-only check finds expired, orphaned and mistyped flags.

## Skills

| Skill | Use it to |
| --- | --- |
| `toggle-governance` | Add a governed flag, check all flags read-only (missing governance, expired, wrong default type, code references), and plan a flag's removal. |

## Install

```
/plugin marketplace add Tooensure-LLC/pmcro
/plugin install pmcro-toggles@pmcro-plugins
```

## Status

CANDIDATE. Verified by tests: add refuses a bad name, a wrong-typed default, a past expiry and a duplicate; check reports a flag without governance, a record without a flag, an expired flag and a wrong-typed default, and counts source references; check changes no file. NOT verified: the OpenFeature CLI reading the generated manifest, and any live flag service. No connector is wired; see `skills/toggle-governance/references/connectors.md`.
