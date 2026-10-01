# Company model (read from the owner's company repo)

Status: READ, NOT DESIGNED. Summarised on 2026-10-01 from `company.json` and `AGENTS.md` in the owner's `pmcro-round-table` repo at commit `f4468e1`. The twelve specification PDFs the owner mentioned never reached this session, so this is not a reading of them. The repo file may change; re-read before relying on it. This replaces guesses I made earlier (see the corrections list).

## What the repo says

- **Product:** "We sell audited, replayable trails." A buyer replays a trail with a replay tool and gets MATCH or MISMATCH. A trail is listed only after an independent Checker PASS and an Auditor AUDIT-PASS.
- **Principles:** Chiefs frame intents; the PMCR-O loop executes them. The Checker is always a separate bot: nobody scores their own work. Everything is generated from one file, `company.json`; generated files are never hand-edited.
- **Loop:** Orchestrator, Planner, Maker, Checker, Reflector. Two hosts, one definition: Grok Bot (one bot per seat) and the company's own Microsoft Agent Framework runtime on Aspire, loading the same seat prompts and the same Agent Skills.
- **Laws:** EC-SYS-003 Log Before Act (write the trail entry before changing any file); EC-VERIFY-FIRST-001 (no claim of done without real command output); EC-004 Checker Verdict Only; EC-009 MaxLoops, 3 per trail, then stop and ask the owner; EC-PORTABLE-005 relative paths only in trails; LAW-010 trail frames are append-only, corrections are new frames.
- **Earned constraints:** EC-0001, scan a trail frame for absolute paths before writing it, with a check first proven able to fail. EC-0002, a platform's control (bot detection, rate limit, terms of service) is a boundary, not an obstacle: on a block the Checker gives HALT, the Reflector records the policy and a permitted path (the official API, the account owner acting, or a different goal), and the loop never learns to look more human to get past a control.
- **Reflector rule RR-001:** the Reflector always writes one candidate constraint with evidence, even on PASS. A candidate becomes an earned constraint only when a check for it is first proven able to fail, or when the same issue appears in a second trail.
- **Always ask the owner first:** anything irreversible; deleting; installing; git pushes and git writes other than the local commit the loop makes; changing laws or policy; spending; giving any bot more authority.
- **Round Table:** the Executive Round Table has the Chief of Staff as chair and the CEO, CTO, CPO, COO and CFO as members. A Grok Bot group chat holds at most six bots, so a round table has at most six seats.
- **Queue:** items move through queued, taken, partly_done, done, dropped.
- **Marketplace:** named `tooensure-pmcro-skills`, core plugin `pmcro` with the loop as skills (`seed`, `loop`, `frame`, `check`, `seal`, `replay`, `commit`) and the seats as agents; generated from `company.json`.
- **Hook:** a log-before-act hook blocks an edit unless a trail is open (a Claude Code PreToolUse hook that exits 2, or Microsoft Agent Framework function-invocation middleware).
- **Seats:** the repo has 15 seat prompts (for example the CEO, CFO, CTO, CISO, CPO, CMO, CLO, a Chief Agent Officer, an Auditor and a CTO Checker).

## Corrections to what this repo said before

| Earlier claim in this repo | Correction |
| --- | --- |
| ADR 0020 gave a reserved list "assumed from the trails" | The real always-ask list is above; ADR 0020 now uses it |
| "Round table" was a confidentiality tier with named seats | A round table is a group chat of up to six Chiefs with a chair. The tier named `roundtable` is this repo's own disclosure device for entries shared with named seats; it is not a company term and not an NDA |
| Trail product described only from the owner's direction note | The product statement and listing gate above are in the company file |
| Memory: "agent proposes, founder accepts" | The company's own rule is RR-001: a candidate is promoted by a failing-first check or by recurrence in a second trail; the owner approves policy changes |

## Alignment still to do

Our marketplace is named `pmcro-plugins`; the company's is `tooensure-pmcro-skills`. `pmcro-core` copies the loop skills from the owner's drive while the company repo generates `pmcro:*` skills from `company.json`. The two have not been reconciled.
