# Why every skill has the same shape

- **SKILL.md** carries only what every run needs: the steps, the rules and pointers. It stays short so small local models cope.
- **references/** holds detail read only when needed.
- **scripts/** does the exact work, so it is code and not prose a model might rephrase.
- **assets/templates/** holds the fixed shape of the output.

The owner's reasoning (2026-10-01): when the flow is templated like this, a capable but not very smart model follows it instead of guessing. This is Behavior Intent Programming applied to skills: the template carries the pattern, and the model only needs the behavior wanted. A count the same day showed that most dotnet/skills skills are a single SKILL.md, which is the case this shape avoids; whether the shape improves results on small models is a hypothesis (something we think is true and have not yet tested), to be tested with the evaluation harness in backlog row 52.

## Skills as commands: input shape, accept and deny

Skills are turning into commands for agents (the owner, 2026-10-01): a name plus arguments. So each skill carries the shape of its own request, `assets/templates/input.md.tmpl`, and a `scripts/check_input.py` that reads it. A request that fills every required field is ACCEPTED. One that does not is DENIED, and the denial returns the shape with what was supplied filled in and each missing field marked, so the request can be corrected and passed back. A messy request is never guessed at and never silently run.

The check is mechanical: it finds fields, not meaning. Turning a messy message into the fields is for a model or a person, using the shape the denial returned. Each skill's input shape and output shape are that skill's own; the shape of a skill as a whole is the template in this skill's `assets/templates/`, which is why a skill made here already matches it.

## Decided: all three folders by default, kept small

The owner's own `create-skill` says to add optional folders only when needed. The owner decided (2026-10-01) that the folders are required by default here, because the templated flow is the point. The counterweight is size: SKILL.md aims for 150 lines and about 5000 tokens (the Agent Skills specification recommends under 5000 tokens and under 500 lines), with detail moved to references so a skill is not bloated. `python tools/pmcro.py validate` warns when a SKILL.md is over those targets and fails over 500 lines.

## Where the shape lives

Only in `assets/templates/` here. `tools/pmcro.py new-plugin` calls `scripts/scaffold_skill.py` for its first skill, so there is one template to change, not two.
