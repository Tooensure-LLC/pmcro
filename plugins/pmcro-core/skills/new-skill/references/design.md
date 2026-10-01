# Why every skill has the same shape

- **SKILL.md** carries only what every run needs: the steps, the rules and pointers. It stays short so small local models cope.
- **references/** holds detail read only when needed.
- **scripts/** does the exact work, so it is code and not prose a model might rephrase.
- **assets/templates/** holds the fixed shape of the output.

The owner's reasoning (2026-10-01): when the flow is templated like this, a capable but not very smart model follows it instead of guessing. This is Behavior Intent Programming applied to skills: the template carries the pattern, and the model only needs the behavior wanted. A count the same day showed that most dotnet/skills skills are a single SKILL.md, which is the case this shape avoids; whether the shape improves results on small models is a hypothesis (something we think is true and have not yet tested), to be tested with the evaluation harness in backlog row 52.

## A tension to settle

The owner's own `create-skill` says to create optional folders only when needed and to ship SKILL.md alone when a skill needs none. This skill defaults the other way: all three folders from the start, deleted deliberately. Both were the owner's words; which one wins is theirs to decide (queued).

## Where the shape lives

Only in `assets/templates/` here. `tools/pmcro.py new-plugin` calls `scripts/scaffold_skill.py` for its first skill, so there is one template to change, not two.
