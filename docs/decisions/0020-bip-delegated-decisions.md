# 0020: Behavior Intent Programming (BIP): decisions are delegated to the seats

Status: accepted · 2026-10-01 (owner: "what I call BIP (Behavior Intent Programming). You should not need to ask me. That's what I have the C-Suite for.")

## Context
The owner programs the company by stating intent and behavior, not instructions. Asking the owner to choose between options defeats that. The company already has seats with owned domains and a short list of things reserved to the human.

## Decision
The agent acts as Chief of Staff: it routes each open question to the seat that owns it, decides within that seat's scope, records the decision with its reason and how to undo it, and carries on. It asks the owner only when an action is reserved to the human. The reserved list, assumed from the owner's trails and to be corrected by them, is: spending money; installing software on the owner's machines; pushing to or changing a repository the session was not given; publishing anything private (including copying private code or messages into a public place); deploying live; DNS, billing and account changes; legal contracts and licences; changing a law or accepting a constraint (ACCEPT); training eligibility; using any real person's voice or likeness; and anything involving credentials. When unsure whether an action is reserved, treat it as reserved and do the safe, reversible part.

## Consequences
Decisions are written down in `docs/decisions/` and the idea backlog, so they can be reviewed and reversed. The reserved list is a guess from the record and may be wrong in either direction. Delegation does not remove the Checker: decisions that matter are still checked by a role that did not make them.

## Decision log (open questions settled under this ADR, 2026-10-01)

| Question | Owner seat | Decision | Why | Undo |
| --- | --- | --- | --- | --- |
| Which repo is canonical? | CTO | Two roles, no merge: `pmcro` is the marketplace and tooling layer (plugins, validator, CI, directory); `pmcro-round-table` is the company layer (`company.json`, Chiefs, runtime, trails, queue). `PMCR-O-Marketplace` and the private `ProjectName` are quarries to mine, not canonical | each already does that job best; nothing is moved or deleted | change this row |
| Copy the governance plugin from the private ProjectName into this public repo? | CISO and CLO | No. Private code is not copied into a public repo by an agent; reference it once the owner publishes it | publishing is irreversible and reserved | the owner may publish it |
| Which meaning of seed? | CPO | Two named things: the *seed intent* is the starting anchor of a trail; the *next seed* is the Reflector's proposal, which becomes a new queue item. A `seed` skill compiles messy words into a queue item and asks only when the meaning is unclear (the contract in `product/trail.md`) | matches the code in both repos | rename |
| i9 operating system | CTO | Assume Windows; build the Windows wheelhouse too; Linux stays supported | the owner's repos use PowerShell and Windows paths | rebuild with another `--platform` |
| LLM eval gate | CTO | Defer until a model is available to run it; CI stays model-free (ADR 0002) | cost and no credentials here | adopt later |
| Round Table disclosure | CISO | Recommend a tier filter in that repo's builder; not changed here because the repo is not ours to edit in this session | reserved: another repository | the owner or a session with access applies it |
