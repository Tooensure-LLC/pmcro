# Skills evaluation dashboard: what it shows and what we take from it

Source: the dashboard of the dotnet/skills project (confirmed by the owner 2026-10-01; its public page is https://dotnet.github.io/skills/ and a web search the same day describes the project's own validator, "skill-validator", which compares each skill against a no-skill baseline, with each skill's evaluation kept in the repo so it can be inspected and run). The owner pasted the dashboard into chat as an example of an "LLM federation" (titled "Skills Evaluation Dashboard", tracking Copilot quality with and without skill plugins, covering dotnet, dotnet-ai, dotnet-aspnetcore, dotnet-blazor, dotnet-data, dotnet-diag, dotnet-maui, dotnet-msbuild, dotnet-nuget, dotnet-template-engine, dotnet-test, dotnet-test-migration, dotnet-upgrade and dotnet11). The owner described it as coming from the .NET skills material this session could not access earlier. Numbers below are read from the paste, not re-run or verified here.

## How it is built (the federation part)

- **Several model families act as executors** (in the paste: claude-haiku-4.5, claude-opus-5, claude-sonnet-5, gpt-5.3-codex, gpt-5.6-luna, gpt-5.6-sol, mai-code-1.1-flash).
- **A different model judges each run** (judges in the paste: gpt-5.6-terra, claude-haiku-4.5, claude-opus-4.8). An executor from one family is judged by a model from another, so no model grades its own work.
- **Each skill runs with and without the skill** on the same tasks. Reported per executor and judge pair: activation rate (did the skill fire when expected), tokens and time change, number of runs and a confidence range on the pass-rate difference, side-by-side preference (wins, ties, losses) and pass rate before and after.
- **Guardrails on the verdict:** at least 5 distinct tasks before any recommendation; "insufficient signal" when the skill fired in too few expected cases (the delta is diluted); "guidance withheld" when a skill fired where it should have stayed off; "helpful but costs more" when it wins but uses more tokens or time; models and commits are never blended; strong recommendations need consistent side-by-side wins.
- **Verdict labels used:** worth installing, looks helpful (more data needed), helpful but costs more, may help but costs more, no clear result (yet), insufficient signal, not recommended.

## What it shows

- **Most skills show no clear result.** The large majority of skill and model rows read "no clear result" or "insufficient signal" or "not enough data yet". Few skills show a dependable win.
- **Skills with specific, hard-to-guess knowledge win clearly.** For example, the Ignite UI Blazor skill reads: pass rate from about 22 to 55 percent up to 100 percent, with 50 to 88 percent fewer tokens on several models. A skill that carries facts the model lacks pays off; generic guidance often does not.
- **Skills often cost more tokens.** Many "helpful but costs more" rows add 30 to several hundred percent more tokens for a better result; a few migration skills were rated not recommended because they used the skill and did worse on side-by-side comparison.
- **Smaller or cheaper models often do not activate skills.** Rows for gpt-5.3-codex and mai-code-1.1-flash frequently show activation of 0 to 40 percent, which dilutes any measured gain and is flagged as insufficient signal.

## What this means for PMCR-O

1. **Our bet needs measuring.** The plan that small local models use skills through progressive disclosure assumes they activate and follow them. The paste suggests activation is the weak point for small models. Until we measure it on our own skills and local models, this is a hypothesis.
2. **A federation fixes a finding of ours.** The workflow the owner showed uses one chat client for Planner, Maker and Checker, so the Checker is independent in context only. A Checker or judge from a different model family, as this dashboard does, is stronger independence. This supports the queued item on Checker independence.
3. **Copy the verdict discipline.** Minimum task count, activation rate, a "stays off" test, side-by-side judging and refusing to blend models and versions are the rules our eval gate should have. Each of our skills would need tasks where it should fire and tasks where it should not.
4. **Zero model spend.** CI here makes no model calls and the owner has only Grok credits, so a real harness would run on local models (the i9) and a judge from a different family, outside CI. Proposal only, nothing built.
5. **This is the model strengths table.** The strengths table in `competitors-and-models.md` should be filled from runs like these, with a date, task and model pair, never from impressions.

## The owner's explanation, and a count that tests it

The owner's reading (2026-10-01): dotnet/skills mostly ships a single SKILL.md and does not use the optional `references/`, `scripts/` and `assets/` folders, so a model has to interpret prose and guess the flow; their own design uses all three, with the flow templated (assets hold templates, references hold the detail, scripts do the exact work), so even a less capable model follows the same steps every time. Models from the big labs are very capable; the bet is a smaller model with a fully templated skill can still do the job.

A count taken the same day on a shallow clone of dotnet/skills (commit 973cffb): of 105 skills, 66 have none of the three optional folders, 33 have only `references/`, 3 have references and scripts, 2 only scripts, 1 only assets, and none has all three. So the owner's description is borne out for that repo. Our own 29 skills are not uniformly full either: 9 have all three folders, 7 have references and scripts, 8 only references, 5 none (the role skills and a few small ones).

The owner's own forks of dotnet/skills (read 2026-10-01) show the same counts as upstream at their fork point, so the PMCR-O-style conversion the owner described is not in those three public forks. In a private PMCR-O repo of the owner's, 15 of 16 skills have both `references/` and `scripts/` and none has `assets/` (aggregate counts only).

This is a hypothesis, not a result: the dashboard cannot tell us that structure is why many skills show no clear result, and a skill with a rich structure could still fail on activation. It is exactly what a harness could test: the same task with a prose-only skill and a fully templated one, on the same small model.

## Reuse before build

dotnet/skills already publishes its validator and per-skill evaluations. Before designing our own harness, read that tooling in full and check whether it can run against our skills, with local models and a different-family judge. Its licence (MIT per the earlier upstream pin) and whether it can run without paid model calls are not yet checked.

## Not covered or unverified

The task sets, judge prompts and scoring rules behind the dashboard were not in the paste. Whether the same pattern holds for PMCR-O's skills is untested.
