---
name: content-script
description: Write a video, podcast or short-form script in the founder's own voice, with every factual claim sourced and a disclosure line when synthetic voice or images are used, then check it with a script. Use when the user wants a script, a content brief, a repurposed post, a voiceover text, or asks about training their voice or generating images for content, even if they only say "make a video about X". Not for impersonating anyone else, cloning another person's voice or likeness, or writing deceptive or fake-testimonial content.
license: MIT
---

# Content script

Scripts fail in two ways: they sound like nobody, and they state things that are not true. This
skill fixes both. The voice comes from a guide the founder owns; the facts come from a Claims
table you must fill before the script is finished.

## Do this

1. Read the voice guide at `references/voice-guide.md` if the user has filled it in. Use only what is written there. Never pull voice or facts from `private` or `roundtable` trail entries; they are not for publishing.
2. Copy `assets/script-template.md`. Fill the front matter: `title`, `duration_min`, `synthetic_voice`, `synthetic_image` (true or false).
3. Write `## Script` as spoken text: a hook in the first two sentences, three to five beats, one call to action. Aim for `duration_min` x 150 words.
4. Fill `## Claims`: one row per factual claim (numbers, dates, named studies, product behavior). The source is a link or file, or the word `opinion` if it is a view. If you cannot source a claim, cut it or mark it `opinion`.
5. If `synthetic_voice` or `synthetic_image` is true, write `## Disclosure` saying the content uses synthetic voice or images. Read `references/disclosure-and-consent.md` first.
6. Run `python <skill-dir>/scripts/check_script.py <script.md>`. Fix every `ERROR` line and run it again. It prints `ok` or `ERROR` lines and exits 1 on any error.

## Never

- Never clone or imitate a real person's voice or face other than the user's own, and never without the consent record described in `references/disclosure-and-consent.md`.
- Never invent a source, a quote or a testimonial. An unsourced claim is cut or labeled `opinion`.
- Never publish. This skill writes and checks a script; a human approves and posts it.
- Never say the script "passed": `check_script.py` reports `ok` or `ERROR`. Only the Checker role issues PASS, LOOP or HALT.

## Output contract

Return the script file path, the checker output verbatim, and a one-line note of anything marked
`opinion` or cut for lack of a source. State plainly that the checker verifies structure, not truth.

Read `references/voice-guide.md` (the founder's style), `references/disclosure-and-consent.md`
(synthetic voice and image rules). `scripts/check_script.py` is described above; its checks are
listed in its docstring.
