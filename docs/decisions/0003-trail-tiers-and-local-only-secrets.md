# 0003: Trail disclosure tiers, secrets kept local

Status: accepted (candidate) · 2026-10-01

## Context
The founder wants to tell the company goals, secrets and personal problems. Some entries must not be shared, and a skill cannot create a legal NDA.

## Decision
Four tiers: public, company, roundtable (named seats), private. `roundtable` and `private` entries live in gitignored `.trail-local/`; the writer refuses to write them anywhere not ignored. Entries are append-only. Only `public` frames may ever be considered for training, after separate human acceptance (OPEN).

## Consequences
Local entries are lost with a temporary container; back them up on the founder's machine. `roundtable` is a house rule, not a contract.
