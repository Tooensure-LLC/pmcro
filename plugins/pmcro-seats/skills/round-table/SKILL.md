---
name: round-table
description: "Convene a PMCR-O round table: the Chief of Staff chairs, each seat at the table gives its view inside its own boundary, and anything reserved to the founder is listed, not decided. Use when the user says round table, convene the C-Suite, get the chiefs' views, or wants several seats to discuss one topic."
license: MIT
---

# round-table

The founder talks to the company through its seats. Each seat is a separate read-only agent that answers only inside its own boundary. This skill gathers several of them on one topic, in a fixed order, and turns their views into seed intents without deciding anything that belongs to the founder.

## Do this

1. Check the request with `python scripts/check_input.py`. If it prints DENY, pass back the filled-in shape it prints instead of guessing what was meant. Its shape is `assets/templates/input.md.tmpl`.
2. Get the speaking order with `python scripts/run.py --table executive`, or `python scripts/run.py --seats cfo,cto,cmo` for an ad hoc table. To ask one seat alone, use `python scripts/run.py --seat cfo` and call only that agent.
3. Call each seat's agent (`pmcro-seats:<id>`) in the printed order with the same topic. Give the chair the topic first; give each later seat the topic plus the earlier views. Call the chair again last to name agreements, differences, and seed intents.
4. Fill `assets/templates/output.md.tmpl` with each seat's view in its own words. Do not merge or soften the views.
5. Record the minutes only if the founder asks, with the trail-player skill in pmcro-core, at the tier the founder picks. For `roundtable`, name exactly the seats that sat.

## Gotchas

- Only the Chief of Staff, CTO Chief and CTO Checker seats are EXISTING. Every other seat is PROPOSED and only advises; never present its view as a decision.
- The CEO may break a tie only if the CEO sat at the table, and only inside the founder's ceiling. Without the CEO, a tie is listed as a difference.
- A seat that answers outside its boundary is not wrong to be stopped. Keep its "that belongs to another seat" answer as it is.
- The script refuses more than six seats. Split the topic into two tables rather than raising the limit.

## Never

- Never let a seat decide anything in the founder-first list the script prints; list it under "Needs the founder".
- Never treat the table's output as a Checker verdict. Seats do not score work.
- Never pass private (`.trail-local/private/`) entries to any seat.

## Output contract

The filled `assets/templates/output.md.tmpl`. It is verified by reading it: every seat that sat has one view, every founder-first item is listed rather than decided, and each seed intent names one owning seat. Detail and rationale: `references/design.md`.
