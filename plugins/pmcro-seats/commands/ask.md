---
description: Talk to the PMCR-O C-Suite. Name a seat (/pmcro-seats:ask cfo ...) or just say what you want and the Chief of Staff routes it to the one owning seat.
argument-hint: [seat-id] <message>
---

Message: "$ARGUMENTS"

1. List the seats with `python ${CLAUDE_PLUGIN_ROOT}/skills/round-table/scripts/run.py --list`.
2. If the first word of the message is one of those seat ids, that seat is the target and the rest is the message. Otherwise the whole message is for the Chief of Staff: call the `pmcro-seats:chief-of-staff` agent with the message, unchanged, and ask it only to name the one owning seat. It routes; it does not answer for that seat.
3. Call the target seat's agent (`pmcro-seats:<id>`) with the message, unchanged, including any `@agent /skill` words the founder wrote, so the seat sees the full request.
4. Return the seat's answer in its own words, and say which seat answered and, if routed, that the Chief of Staff chose it. If the seat says another seat owns part of it, offer to ask that seat or convene a round table. Never decide anything the seat marks "needs the founder".
5. Seats are read-only. If the message asks for a skill that writes (for example `/pmcro:seed`), the seat gives its framing, and the skill runs here in the main session only after the founder confirms.
