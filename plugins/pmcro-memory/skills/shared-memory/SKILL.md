---
name: shared-memory
description: "Remember and recall the founder's knowledge and the company's lessons across sessions and agents, so nothing has to be re-explained. Use when the user shares knowledge, preferences, facts about their work or accounts, says 'remember this', 'what do we know about', 'did I tell you', or when an agent needs prior context before acting, a lesson recorded after a cycle, or a stale fact corrected. Not for secrets or credentials, and not a replacement for the trail or the inbox."
license: MIT
---

# Shared memory

One person cannot hold everything in their head, and agents forget between sessions. This memory is
the company's shared knowledge: the founder's knowledge first, and lessons agents propose second.
It is plain files, so it works offline, survives any one model, and a human can read and fix it.

## Do this

1. **Recall before acting.** Before you plan or answer from assumptions, run `python <skill-dir>/scripts/memory.py search "<words>" --viewer <viewer>`. Use your own viewer (see below). Read the top hits with `show`. If memory contradicts what the user just said, the user wins; record a correction.
2. **Remember what the founder tells you.** When the founder shares knowledge, run `memory.py add --tier <tier> --title "<short title>" --text "<their words>" --tags a,b --source founder`. Use their wording; add tags people would search for. Pick the tier like trail-player (`private` when unsure).
3. **Record lessons as candidates.** After a cycle, an agent may add `--source agent` (status `candidate` is automatic). A candidate is a suggestion, not knowledge. Only the founder marks a memory `accepted`.
4. **Correct, never edit.** If a fact changed, add a new entry with `--supersedes P0003` (ids carry their tier's letter: public P, company M, roundtable R, private V). The old one stays on record and is hidden from normal search.
5. **Respect who may see it.** Read `references/viewers.md` before searching on someone else's behalf.

## Never

- Never store credentials, tokens or anything credential-shaped; the tool refuses them.
- Never search with a broader viewer than your own, and never show a private or roundtable memory to someone who may not see it.
- Never treat a candidate as established fact, and never mark your own lesson accepted.
- Never invent a memory. If you do not know, say so and offer to record what the founder tells you.

## Output contract

For a recall: the ids and titles you used, with accepted memories distinguished from candidates, and
a plain statement if nothing relevant was found. State that search is keyword search and can miss
a memory worded differently.

Read `references/viewers.md` for who sees which tier. `scripts/memory.py` documents every command.
