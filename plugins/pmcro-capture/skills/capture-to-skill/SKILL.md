---
name: capture-to-skill
description: "Turn screenshots or photos of a task, device or document, plus short notes, into a draft Agent Skill that an agent can follow and learn from. Use when the user wants to teach the company a task by showing it, says 'take a picture and learn this', 'turn this into an agent', 'record my steps', or hands over screenshots of a workflow, an appliance, a form or a document. Not for recording keystrokes, passwords or other people, and not for running the steps."
license: MIT
---

# Capture to skill

Showing is often easier than explaining. A few annotated pictures can become a skill the company
reuses. But pictures also carry things people forget: passwords on screen, other people's faces
and messages, and hidden metadata such as GPS location. So the draft step strips metadata
automatically and will not run until a human confirms they looked at every image.

## Do this

1. **Collect.** One photo can be enough: pass the single image as the argument. For several, put the screenshots or photos in one folder, named so they sort in step order (`01.png`, `02.jpg`). Optionally add `steps.txt`, one line per step in the same order.
2. **Review (human).** Ask the founder to look at every image and confirm none shows a password, personal data, a payment detail or another person. If any does, retake or crop it first. Do not proceed on a guess.
3. **Draft.** Run `python <skill-dir>/scripts/draft_skill.py <image-or-folder> --name <kebab-name> --description "<when to use it>" --out <dir> --confirm-reviewed`. It copies the images with metadata removed and writes a `SKILL.md` plus a capture-notes file into the new skill folder.
4. **Fill the TODOs.** Replace every TODO: why the skill exists, what must never happen, how to confirm it worked. Describe each step from what the image shows; if you cannot tell what a step does, ask rather than invent.
5. **Verify by doing.** A draft is not a skill until someone follows the steps and an independent Checker confirms the result. Say so in the status line. Only then add the skill to a plugin and run `python tools/pmcro.py validate`.

## Never

- Never record keystrokes, clipboards or password fields, or capture a screen continuously in the background. This skill works only from images a human chose to give.
- Never include another person's face, messages or data without their consent.
- Never act on a device or account from a draft: the steps are unverified, and a wrong step on a real device or account can cause harm.
- Never claim you "learned" a task from pictures alone. The draft records what was shown, not that it works.

## Output contract

The output folder, the number of steps drafted, the list of remaining TODOs, and the sentence
"Drafted from a capture; steps not run or verified." If the script refused, quote its reason.

Read `references/privacy.md` for what the stripping does and does not cover. `scripts/draft_skill.py`
documents its arguments and refusals in its docstring.
