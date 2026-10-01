# Viewers and tiers

Status: company rules (ADR 0021). Search is filtered by the viewer, so one shared memory can serve everyone without leaking.

| Viewer | Sees |
| --- | --- |
| `founder` | every tier |
| `seat:ID` (for example `seat:cfo`) | public, company, and roundtable entries that list that seat |
| `company` | public and company |
| `public` (the default) | public only |

## Rules

- A server or agent fixes its own viewer at start-up. A caller must never be able to choose a broader one (that would bypass the tiers).
- `private` and `roundtable` entries live in the gitignored local folder and are never committed.
- The default tier for anything personal is `private`.
- Roundtable memory is a house rule for named seats, not a legal confidentiality agreement.

## Candidate and accepted

Agents write `candidate`. The founder may mark `accepted`. This mirrors the company rule that learning is proposed by the Reflector and accepted by a human.
