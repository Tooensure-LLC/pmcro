# Company model (read from the owner's company repo)

Status: READ, NOT DESIGNED. Summarised on 2026-10-01 from `company.json` and `AGENTS.md` in the owner's `pmcro-round-table` repo at commit `f4468e1`. The twelve specification PDFs the owner mentioned never reached this session, so this is not a reading of them. The repo file may change; re-read before relying on it. This replaces guesses I made earlier (see the corrections list).

## What the repo says

- **Product:** "We sell audited, replayable trails." A buyer replays a trail with a replay tool and gets MATCH or MISMATCH. A trail is listed only after an independent Checker PASS and an Auditor AUDIT-PASS.
- **Principles:** Chiefs frame intents; the PMCR-O loop executes them. The Checker is always a separate bot: nobody scores their own work. Everything is generated from one file, `company.json`; generated files are never hand-edited.
- **Loop:** Orchestrator, Planner, Maker, Checker, Reflector. Two hosts, one definition: Grok Bot (one bot per seat) and the company's own Microsoft Agent Framework runtime on Aspire, loading the same seat prompts and the same Agent Skills.
- **Laws:** EC-SYS-003 Log Before Act (write the trail entry before changing any file); EC-VERIFY-FIRST-001 (no claim of done without real command output); EC-004 Checker Verdict Only; EC-009 Loop Until Done (a trail loops until a separate Checker says PASS or HALT, no fixed count; two LOOP verdicts in a row that name the same defect IDs stop the loop and ask the owner; changed from MaxLoops in the company repo, trail 0014, commit cd4c19b, 2026-10-02); EC-PORTABLE-005 relative paths only in trails; LAW-010 trail frames are append-only, corrections are new frames.
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

## Second reading, 2026-10-01 (the uploaded specification PDFs, trails corpus and datasets)

Read in full or near full: Architecture Specification, Declarative Agent Factory, Governed Autonomy (to section 20 of its sections), Lock Thought (about 60%), Orchestration API, Trail Product, Plugin Manager (to section 16), Production Runtime corpus (three overlapping versions, last one read by section list and sections 31-40), Training Data Schema and Final Spec, `trails-design-corpus.md`, enterprise QA phase 1 (first third). Two re-uploads (Lock Thought, Declarative Factory) were byte-identical to the first copies. Five uploaded PDFs were 0 bytes.

What matters, with the company's own status words:

- **Almost all implementation material is PROPOSED.** MAF, the Orchestration API as a gateway, one .NET service per role, gRPC and Protobuf between them, the `ProjectName.Mcp.[Name]` naming convention, the Plugin Manager Agent and its lifecycle, Governed Procedure and Autonomy Grant, Lock Thoughts, and the Declarative Agent Factory are all labeled proposed. The Runtime foundation itself selects none of them. Do not describe any of them as decided.
- **Grounded (EXISTING):** the five-role order, the six laws, the human-approval boundaries, the independent read-only Checker with PASS, LOOP or HALT, append-only trails, relative paths, and the listing gate (Checker PASS plus Auditor AUDIT-PASS) that applies to Trails only, not to plugins, skills or MCP servers.
- **The Trails baseline leaves these OPEN:** the trail and frame schema, frame format, sealing, replay and the MATCH/MISMATCH algorithm, ACCEPT semantics, evidence representation beyond real command output, storage, cryptography, and LOOP behavior beyond the loop law EC-009 (then MaxLoops, now Loop Until Done). So the frame fields in `docs/product/trail.md` are this repo's own proposal, not a company schema. Training eligibility belongs to the CDO and needs a Trail to end in ACCEPT first.
- **Plugin Manager rules worth keeping:** discover, retrieve, stage, install, activate and authorize are separate steps; a plugin's effective capabilities must be a subset of what it requested and of the project ceiling; QUARANTINE is an operating condition, never a Checker verdict; installation stays human-reserved. The exact manifest format and plugin qualification stay OPEN.
- **Credentials:** none in chat or Trails; masked sign-in handoff is the established pattern; identity injection, tokens and tenancy stay OPEN. MCP configuration is capability, not authorization. Platform controls are boundaries, not evasion targets.
- **A proposed 21-item must-fail conformance set** exists (for example the API cannot issue a Checker verdict; MATCH cannot be treated as PASS; a plugin cannot self-approve installation). Several are worth mirroring as tests here when the matching features exist.

Corrections to this repo, from the reading: the Grok candidate dataset's system prompt is not the first-person "I AM" form the Final Spec asks for; the training procedure and eligibility rules are summarized in `training-data-spec.md`; the owner's `create-skill` validator is lenient (Trail 011 found it accepts eight kinds of frontmatter that strict YAML rejects).

Still unread: the second half of Lock Thought, the end of Governed Autonomy, the Plugin Manager tail, the middle of the three Runtime corpus versions, and the rest of the enterprise QA document.

## Macro and micro workflows: two statements that differ

The Production Runtime corpus (PROPOSED) says a macro workflow is company or C-Suite coordination scope and a micro workflow is a bounded Runtime execution unit, and that a micro workflow is not a Trail frame. In chat on 2026-10-01 the owner described it as: the micro workflow runs PMCR-O Trails and the macro workflow runs the agent loop, with the workflow (not the model) as what guarantees a Trail is written, plus the Agent Governance Toolkit. These may be the same idea described from different sides, but they are not the same wording. Neither is recorded as decided: the owner to say which wording is canonical. Until then this repo says only that guarantees live in workflow code and judgment lives in agents.

