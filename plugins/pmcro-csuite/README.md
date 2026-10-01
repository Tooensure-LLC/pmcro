# pmcro-csuite

C-Suite domain skills for the PMCR-O company, imported from the PMCR-O-Marketplace colony repo.

## Skills

| Skill | Seat |
| --- | --- |
| `ceo` | Chief Executive: direction, OKRs, compute and priority allocation |
| `cfo` | Chief Financial: budgeting, cash flow, forecasting (has 4 scripts under `scripts/`) |
| `coo` | Chief Operating: operations |
| `cto` | Chief Technology: architecture, security posture |
| `cmo` | Chief Marketing |
| `cro` | Chief Revenue |
| `chro` | Chief Human Resources |
| `clo` | Chief Legal |
| `chief-of-staff` | Cross-domain coordination |

## Install

```
/plugin install pmcro-csuite@pmcro-plugins
```

Install only the seat a bot plays; every installed skill adds to a small model's menu.

## Status

CANDIDATE. Imported from `ShawnDelaineBellazanLoop/PMCR-O-Marketplace@a25f7f0` with `tools/import_skills.py`. Known defects, none fixed: every seat links to a file outside its plugin (`../../../pmcro-engine/...`), and `ceo` lost one dead link. Full list in `docs/imports.md`. Nine seats here versus 15 Chiefs in the private ProjectName seat bot: reconcile before generating seat bots.
