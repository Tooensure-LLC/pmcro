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
