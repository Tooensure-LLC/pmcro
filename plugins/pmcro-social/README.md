# pmcro-social

Account operations for the founder who has many accounts: a credential-free registry, a brief of what needs a human now, and rules for drafting and approving posts.

## Skills

| Skill | Use it to |
| --- | --- |
| `account-ops` | Register accounts, flag neglected or purpose-less ones, show a short "needs you" brief, and record what a human posted (`scripts/registry.py`). |

## Install

```
/plugin install pmcro-social@pmcro-plugins
```

## Status

CANDIDATE. The registry is tested (credential refusal, append-only log, gitignore guard, brief ordering). NOT built: any connection to a real platform; posting, scheduling and analytics (the registry only records what a human reports); a content calendar. Registry data is local to one machine, in the private tier. Platform rules were not checked here. See ADR 0018.
