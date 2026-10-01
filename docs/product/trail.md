# Trail as a product (design draft)

Status: CANDIDATE. Written from the 2026-10-01 company direction only. The Trail Product and
Training Data PDFs in the shared zip were not available to me; reconcile this draft with them.

## What it is

The trail is the company's append-only record of what was decided, done, checked and learned. A
frame is one entry. As a product it lets a person (or a seat bot) record direction, replay it, and
prove what happened and at what cost.

## Frame requirements (proposed)

| Field | Why |
| --- | --- |
| number, time (stamped from the clock) | ordering and audit |
| role and kind | who spoke; goal, idea, decision, check, reflection and so on |
| tier: public, company, roundtable, private | who may read it (see `trail-player`) |
| refs | corrections and links; frames are never edited |
| cost: tokens, model, wall time, loop count, usd | "if the company is not running it is dying": a frame with no cost data cannot enter economic metrics |
| verdict (Checker frames only) | PASS, LOOP or HALT, issued by an independent Checker |

## Rules

1. Append-only. A correction is a new frame.
2. Only `public` frames from a cycle with an independent Checker PASS may be considered for training, tagged by authorship. Held-out evaluation sets are never trained on. Training eligibility (ACCEPT) is OPEN and human-owned.
3. `private` and `roundtable` frames live in gitignored `.trail-local/` and never reach commits, summaries to other seats, or training data.
4. Economic gates flag a product or trail with poor unit economics for human review. They never stop or delete anything on their own.

## Surfaces

Record (`trail-player`), replay by tier, and later: a seat-bot view that shows each C-Suite seat
only the tiers it is cleared for, and a cost dashboard. The C-Suite generator is a separate skill.

## OPEN

Trail schema details (AGT events, OpenTelemetry GenAI spans or custom), storage (Postgres ledger or files), pricing, what "value" means per product, and where `.trail-local/` is backed up. Local-only entries are lost with this temporary container; back them up on your own machine.

## Seed contract and queue item (reconstructed from a session, 2026-10-01)

Source: an exported Google AI Studio session (Gemini) in which PMCR-O was simulated. The wording of the contract below is quoted from that session's replies, which in turn quote `company.json` (the private company repo, not seen here). Treat this as a reconstruction to confirm, not the canonical text.

- `/pmcro:seed` is intake by the Chief of Staff: "Turn Shawn's messy words into a queue item: raw_intent verbatim, true_intent in one or two plain sentences, done_means with proofs that can fail, owners and pace. If the meaning is unclear, ask instead of guessing."
- When the meaning is unclear the seed answers `CLARIFICATION REQUIRED` with options and queues nothing. (This is the confirmation step; the C# `PmcroLoop` in ProjectName does not have it.)
- A queue item (JSON, `queue/NNNN-name.json`) carries: `id`, `name`, `status` (`queued`, then `taken` when a loop opens), `created_at`, `owners` (primary seat plus consulting boundaries), `raw_intent`, `true_intent`, `done_means[]` (each with `description`, `proof_that_can_fail`, `must_fail_check`), and `governance_and_constraints` (spend ceiling, human approvals required, laws bound).
- `/pmcro:loop NNNN` takes the item and opens a trail; `/pmcro:seal`, `/pmcro:replay` and an `@auditor /sample` follow. The human is "the board".

`pmcro-core`'s `inbox` queue is the raw-message layer under this. The structured queue item is not built here yet (OPEN).

## Provenance: simulated trails are not evidence (ADR 0013)

Every frame should record how it was produced:

| Field | Meaning |
| --- | --- |
| `executed` | true only if a real tool or command ran and its real output is in the frame |
| `executor` | the model or person that did the work |
| `checker_independent` | true only if the Checker was a different agent with fresh context |

Training eligibility requires `executed: true` and `checker_independent: true` on the cycle; everything else is excluded or tagged as simulated.
