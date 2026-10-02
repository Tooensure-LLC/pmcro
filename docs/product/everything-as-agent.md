# EverythingAsAgent (product design draft)

Status: PROPOSED. Owner idea, 2026-10-01: anyone can turn anything into an agent: photograph a document or device and learn to use it. Only the first step is built (`pmcro-capture`, ADR 0019).

## The idea in the company's terms

A capability becomes a reusable artifact (a skill), then gets evidence, independent verification and, much later, qualification. EverythingAsAgent is the front door: a way to create the *artifact* from something a person shows. The company's own architecture (as summarised in the owner's notebook and checked against the repos on 2026-10-01) says an agent is an identity inside a role and an authority ceiling; a skill answers "what bounded procedure can this agent perform?", never "what is it authorized to do?". Skills, plugins, sites and build services have no settled qualification rules yet (OPEN); only Trails have a grounded listing gate (independent Checker PASS plus Auditor AUDIT-PASS).

## Pipeline

| Step | Who | State |
| --- | --- | --- |
| 1. Capture | Human takes photos or screenshots and writes short notes | by hand |
| 2. Review | Human confirms nothing private is in any image | gate in the script |
| 3. Draft | `capture-to-skill` strips metadata and writes a draft skill with TODOs | built, tested |
| 4. Fill and follow | Agent fills the TODOs from the images; a person follows the steps | not built |
| 5. Verify | Independent Checker confirms the task really worked | existing role |
| 6. Package | Add to a plugin; `tools/pmcro.py validate` | built |
| 7. Qualify and offer | Product-specific rules | OPEN |

## A steps recorder (Problem-Steps-Recorder style): not built, conditions

The notes you pasted describe building one on Windows from UI Automation, event hooks, screen capture APIs and OCR. Those names are Windows APIs, not verified here, and the claims about Snipping Tool and the old recorder came from another model and were not checked. If it is ever built, the minimum conditions are:

- Opt-in per session, with a visible indicator and one-key stop; never background or continuous capture.
- Record UI element names and clicks, **not keystrokes**; never capture password fields; blur or skip them.
- Everything stays local; the output goes through the same review gate and metadata strip as `capture-to-skill`.
- A recording is evidence of what a person did, not a verified procedure; it goes through steps 4 to 6 above.
- Recording other people (screens that show their messages, calls) needs their consent.

## Where "learn to use things" is risky

Following steps drawn from pictures can operate real devices, accounts or money. A draft must never run unattended; any step that changes something real needs the human approval the rest of the company already requires.

## OPEN

Vision and OCR tools and their licences; where drafts are stored (never in a servable plugin if private); how users outside the company would contribute and be protected; pricing; legal review for recording, copyright and device-manual content; qualification rules for skills as products.
