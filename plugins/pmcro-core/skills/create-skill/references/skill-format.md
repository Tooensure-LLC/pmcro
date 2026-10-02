# Skill format reference

Read this when drafting frontmatter, deciding what to split out, or debugging a validation error.

## Contents
- Structure
- Frontmatter fields
- Writing the description
- Deciding what goes where
- Pre-ship checklist

## Structure

```
skill-name/
├── SKILL.md        required, exactly one per skill
├── references/     optional, docs loaded on demand
├── scripts/        optional, executable code
└── assets/         optional, files used in output
```

The folder name should match the `name` field. Nested SKILL.md files are rejected on upload, so supporting docs must use other filenames.

## Frontmatter fields

| Field | Required | Rules |
|---|---|---|
| `name` | yes | kebab-case, a-z 0-9 and hyphens, no leading/trailing/double hyphens, max 64 chars |
| `description` | yes | string, max 1024 chars, no angle brackets |
| `license` | no | license name or reference |
| `compatibility` | no | string, max 500 chars; only when the skill needs specific tools or dependencies |
| `allowed-tools` | no | tools the skill may use |
| `metadata` | no | free-form mapping |

Any other top-level key is invalid.

## Writing the description

The description is the trigger. Include:
- **What** the skill does.
- **When** to use it: concrete phrases and contexts, including indirect ones where the user never names the skill's subject.
- **Where it stops**, if a neighboring skill could be confused with it.

Weak: `Helps with dashboards.`
Strong: `Build a simple, fast dashboard for internal metrics. Use whenever the user mentions dashboards, data visualization, or wants to display company data, even without saying "dashboard".`

## Deciding what goes where

- Needed on nearly every run → SKILL.md.
- Needed only for some runs, or long → `references/`, linked with a "read when..." note.
- Must be deterministic or is re-written every time → `scripts/`.
- Copied or filled into the output → `assets/`.
- Several domains or variants → one reference file per variant; SKILL.md only routes between them.

## Pre-ship checklist

- [ ] Description says what and when, and would trigger on realistic requests
- [ ] SKILL.md contains only essentials, with every bundled file linked and explained
- [ ] No unused directories
- [ ] Scripts have a usage line and clear error messages
- [ ] `scripts/validate_skill.py` passes
- [ ] Nothing in the skill surprises someone who has read only its description
