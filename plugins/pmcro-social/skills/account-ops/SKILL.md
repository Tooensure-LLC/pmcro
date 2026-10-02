---
name: account-ops
description: Take the load of managing many social, content and web accounts off the founder without handing over any credentials. Keeps a registry of accounts (platform, handle, purpose, how often it needs activity), flags accounts that are neglected or have no purpose, and produces a short brief of what needs a human now. Use when the user feels overwhelmed by accounts, says "I have 20 accounts", asks what to post or fix first, wants a weekly brief or content calendar, or wants to decide which accounts to keep. Not for logging in, posting, or holding passwords or tokens.
license: MIT
---

# Account operations

Twenty accounts means twenty small decisions a day. The relief is fewer, smaller decisions, not
giving agents the keys. So the company keeps the list, notices what is neglected, drafts the work,
and asks the founder for one short approval at a time.

## Do this

1. **Get the list in.** Ask the founder to paste or type their accounts as lines: platform, handle, what it is for, how often it should have activity. Do not ask for logins. Load them with `python <skill-dir>/scripts/registry.py import FILE.csv` (columns `platform,handle,purpose,cadence_days,owner`) or `add` one at a time. A rough guess is fine; blanks become flags, not errors.
2. **Show the brief.** Run `registry.py brief` and give the founder the top three items only, most overdue first. Do not dump all 20.
3. **Run the weekly review.** `registry.py review` flags accounts with no purpose, no cadence, or no activity. For each flagged account ask one question: keep, merge or retire? Fewer accounts is the biggest relief. Retire only when the founder says so, using `registry.py retire`.
4. **Draft, never post.** For an overdue account, draft the piece with the `content-script` skill (or a short caption). Put it in front of the founder as one approve-or-change choice. After a human posts, record it with `registry.py posted`.
5. **Queue the rest.** Anything the founder says goes into the `inbox` queue, so nothing is lost while they rest.

## Never

- Never ask for, store, or pass along a password, token, cookie or 2FA code. The registry refuses credential-shaped text.
- Never post, log in, follow, message or change settings on any account. A human does it.
- Never create accounts that pretend to be someone else, or several accounts to fake support for one message. Each account is clearly the founder's or the company's.
- Never retire or change an account on your own; a flag is a question for the founder.

## Output contract

For `brief`: the count that need the founder and the top three, one line each, then the single next
action. For `review`: the flagged accounts with one proposed question each. Say plainly that the
registry only records what a human reported; it cannot see the accounts.

Read `references/platform-rules.md` before drafting for a platform. `scripts/registry.py`
documents every command in its docstring.
