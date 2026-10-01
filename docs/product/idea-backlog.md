# Idea backlog (every direction the owner has given, with status)

Status: maintained by hand from the 2026-10-01 session. Summaries only: no personal details, no verbatim private messages (those go in the private inbox queue). Status words: BUILT = code or docs exist and are tested; DOCS = designed or recorded only; OPEN = waiting on a decision or input; NOT BUILT = proposed, nothing exists.

| # | Idea or direction | Status | Where | Next |
| --- | --- | --- | --- | --- |
| 1 | Trail player: record goals, ideas, secrets with disclosure tiers; generate the C-Suite | BUILT (player); C-Suite imported (9 seats) | `pmcro-core/trail-player`, `pmcro-csuite` | reconcile 9 seats vs the 15 Chiefs in `Tooensure-LLC/pmcro-round-table` (`chiefs/`); seat-bot generator NOT BUILT here (that repo generates seat prompts from `company.json`) |
| 2 | Leverage dotnet/skills (MAUI, AI, MSBuild, ...) | BUILT | `upstream.json`, ADR 0004 | refresh pins deliberately |
| 3 | CI that costs no model credits | BUILT | `.github/workflows/ci.yml`, ADR 0002 | LLM eval job NOT BUILT |
| 4 | Skills must work for small local models via progressive disclosure | BUILT | `pmcro-dotnet/maf-local-skills` | live Ollama test NOT DONE |
| 5 | Trail as a product | DOCS | `docs/product/trail.md` | reconcile with the Trail Product PDFs |
| 6 | One marketplace; old repos become templates and assets | OPEN | `docs/imports.md` | decide the canonical repo; copy from private ProjectName only with permission |
| 7 | MCP leverage; local Ollama talks to GitHub MCP | BUILT (config, tested over stdio) | `pmcro-dotnet/mcp-local-models` | GitHub MCP tool names and live run NOT DONE |
| 8 | Plugins by capability: pmcro-github etc. | DOCS (recommended). Correction: a `pmcro-github` plugin with a `github-templates` skill already exists in `Tooensure-LLC/pmcro-round-table`; not reviewed in depth | this session, that repo | decide whether to adopt it instead of building another |
| 9 | Follow dotnet/skills design fully | PARTLY | layout, validator, upstream pins | adopt eval gate when evals exist |
| 10 | Documentation is law | BUILT | `tools/pmcro.py`, ADR 0006 | none |
| 11 | dotagents convention for the PMCR-O assistant | BUILT (install, lock, doctor verified) | `docs/dotagents.md`, ADR 0007 | host loading NOT VERIFIED |
| 12 | Offline i9, 24/7 experiments | BUILT (kit); runner DESIGN only | `tools/offline_kit.py`, ADR 0009 | need OS, RAM, GPU |
| 13 | Content creator plugin; own trained voice | BUILT (scripts); voice NOT BUILT | `pmcro-content`, ADR 0008, 0010 | voice tooling OPEN |
| 14 | Cloudflare site and affiliate pages; Cloudflare MCP | BUILT (checks, read-only allow-lists) | `pmcro-cloudflare`, ADR 0011, 0014 | nothing connected to a real account |
| 15 | Self-hosted Actions runner on the offline machine | ANSWERED | chat | only with outbound access; private repos |
| 16 | Message queue to catch everything | BUILT (inbox); backfilled 2026-10-01. Note: `pmcro-round-table` has its own `queue/` of seed items; the two have not been aligned | `pmcro-core/inbox`, ADR 0012 | align schemas; durable storage off this container OPEN |
| 17 | Generic template-driven MCP server (progressive disclosure, .NET pattern) | NOT BUILT (ADR 0016 PROPOSED) | `docs/decisions/0016` | needs owner approval; MCP projection is OPEN in the matrix |
| 18 | Harness, CodeAct, Hyperlight in MAF | DOCS | chat | `maf-harness-codeact` skill NOT BUILT |
| 19 | Figma plugins templated; MCP server for building them | BUILT (template, renderer, linter); server NOT BUILT | `pmcro-figma`, ADR 0015 | never run in Figma |
| 20 | Ghostwriter: scripts, then songs, then voices | BUILT (phase 1); phases 2 and 3 gated | `docs/product/ghostwriter.md`, ADR 0017 | revenue threshold OPEN |
| 21 | Relieve overload from about 20 accounts | BUILT (registry, brief); waiting for the list | `pmcro-social`, ADR 0018 | owner sends the account list |
| 22 | EverythingAsAgent: photo to skill; steps recorder | BUILT (capture-to-skill); recorder NOT BUILT | `pmcro-capture`, ADR 0019 | recorder conditions in the product doc |
| 23 | Foundations: strange loops, I and Thou, self-replication | DOCS | `docs/product/foundations.md` | confirm wording with the corpus |
| 24 | Understand seed intent and true intent | DOCS | `docs/product/trail.md` | which meaning of seed; frame skill NOT BUILT |
| 25 | Simulated trails are not evidence | BUILT (rule) | ADR 0013 | provenance backfill OPEN |

| 26 | The Round Table: the Chiefs' exchanges as a transcript page with one voice per Chief | EXISTS in `Tooensure-LLC/pmcro-round-table` (trail 0004, 8 blocks so far, all Chief of Staff); not built here | that repo | the public repo shows 8 verbatim founder seeds: review the disclosure tier (see queue) |
| 27 | Learn Colab; cognitive agents | DOCS (notes from one search) | `product/colab-and-cognitive-agents.md` | notebook template and data-eligibility check NOT BUILT |
| 28 | Shared memory (the founder's knowledge) | BUILT | `pmcro-memory`, ADR 0021 | MCP exposure with a server-fixed viewer |
| 29 | Generate the owner's MCP servers; the owner wires the connections | IN PROGRESS | ADR 0022 | see the next commit |

## Decisions waiting on the owner

Canonical marketplace repo (`pmcro-round-table` looks like the newest and most complete: one `company.json` driving seat prompts, the runtime, trails, queue and plugins; not audited); whether to copy the governance plugin from the private ProjectName; which meaning of seed; the i9's OS, RAM and GPU; the Ghostwriter phase 2 threshold; whether MCP servability is approved (ADR 0016).
