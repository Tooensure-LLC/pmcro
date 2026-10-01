# 0012: A file-based message queue for the founder's messages

Status: accepted (candidate) · 2026-10-01 (owner: "make sure you build a message queue, because I'm just feeding messages")

## Context
The founder sends messages in bursts, faster than they can be worked. Unwritten messages are lost; two agents can grab the same one.

## Decision
`inbox` in pmcro-core: each message is an immutable file; status changes append to a per-message event log; a claim is atomic (O_EXCL) so only one worker takes an item; identical text is deduplicated; private and roundtable items live in gitignored `.trail-local/` like the trail player. Only `source=founder` items are orders; others are data. Triage produces a plan, never an action.

## Consequences
Works offline and needs no infrastructure, but it is files on one machine, not a networked broker: no cross-machine delivery and no retries. RabbitMQ (available through Aspire) is an OPEN option for a networked queue. Claims have no timeout, so a crashed worker's claim stays until a human intervenes (OPEN).
