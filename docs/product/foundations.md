# Foundations: three ideas PMCR-O is built on

Status: DESIGN NOTES. The owner named these inspirations on 2026-10-01: Hofstadter's strange loops, Buber's I and Thou, von Neumann's self-replication. The mapping below is an interpretation written from the repo's existing rules; it is not a quotation of the company corpus, and the corpus may say it differently. Where a lens suggests something not yet in the design, it is marked PROPOSED.

## The manual loop, as the owner describes it

The five role skills (`orchestrate`, `plan`, `make`, `check`, `reflect`) are run by hand, one at a time, and the result reads like a conversation with each role in turn. That is deliberate: a human is in the loop at every step, and each role speaks only for itself.

## Hofstadter: the strange loop

A strange loop is a hierarchy that, as you climb it, returns to where it started: the system ends up describing and changing itself. PMCR-O has one: the Reflector's output (a candidate constraint, the next seed intent) goes back to the Orchestrator, trails become training data for the model that writes trails, and the marketplace is built with its own tools.

What the lens asks of the design, and what already answers it:

- A system that only checks itself cannot certify itself. Hence the Checker must be independent and must rerun the proof (ADR 0013).
- Loops need brakes: MaxLoops is 3, HALT hands control to the human, and records are append-only so the loop cannot rewrite its own past.
- Self-reference must not become self-authorization: a constraint proposed by the Reflector stays a candidate until a human accepts it (ACCEPT is human-owned).

## Buber: I and Thou

Buber distinguishes treating the other as a thing to use (I-It) from meeting it as a real other (I-Thou). Applied to roles: each role is addressed as an other with its own duty, and the Checker's value comes from being a genuine other that can say no.

- This is why one model playing all five roles in one chat collapses the dialogue into a monologue. The Gemini session (ADR 0013) shows it: the "Checker" agreed with the "Maker" because they were the same voice.
- PROPOSED: when a manual loop needs real independence, run the Checker in a fresh context (a separate session or agent) that receives only the raw intent and the artifacts, never the Maker's reasoning.
- The human is also a Thou in the loop: the "board" can disagree, and a refusal is a valid outcome, not a failure.

## von Neumann: self-replication

Von Neumann's self-reproducing automaton has a constructor, a description (the tape) it can read, and a copier that copies the description as data. Reliable replication also needs error tolerance, because copies degrade.

| Von Neumann | PMCR-O |
| --- | --- |
| Constructor | the runtime and agents that build things |
| Description | skills, `plugin.json`, trails, `company.json` |
| Copier | the marketplace and generators (`tools/pmcro.py gen`, `new-plugin`) |
| Fidelity checks | validators, tests, pinned commits and hashes, provenance |
| Resources | the company must earn what it spends: "if it is not running it is dying" |

What the lens asks of the design: a copy must be checkable against its description (we validate and pin); replication must not outrun authority (a replicated agent inherits the authority ceiling, it does not gain permission by existing); and unbounded replication needs a human limit and a budget (OPEN: the numbers are human-owned).

## Open questions

Which wording of these ideas the company corpus actually uses; how the manual loop's dialogue is stored as trail frames with provenance (`executed`, `executor`, `checker_independent`, see `product/trail.md`); and whether a fresh-context Checker becomes the default for manual runs.
