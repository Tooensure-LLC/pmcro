---
name: landing-page
description: Build and check a static landing page for affiliate marketing or a product site, record each setup step as a trail frame, and prepare (never perform) a Cloudflare deploy. Use when the user wants a landing page, an affiliate or review site, a "set up the website" task, a Cloudflare Pages or Workers static site, disclosure or nofollow/sponsored link checks, or a deploy dry run, even if they only say "put this offer online". Not for DNS or billing changes, and not for publishing without human approval.
license: MIT
---

# Landing page (Cloudflare, affiliate-aware)

Affiliate pages go wrong in two ways: readers are not told the page earns commission, and the
page promises results nobody can promise. Publishing is also outward-facing and hard to undo.
So this skill builds and checks the page, records the work, and stops before going live.

## Do this

1. Copy `assets/landing-template.html` to a working folder. Fill the title, description, offer text and links. Keep the disclosure block above the first affiliate link.
2. Write only claims you can source. Describe the product; do not promise income or results. Read `references/affiliate-disclosure.md` before writing offer copy.
3. Run `python <skill-dir>/scripts/check_landing.py <page.html> --affiliate-domains example-network.com`. Fix every `ERROR` line and rerun until it prints `ok`.
4. Record each step as a trail frame (what was done, why, cost). Read `references/trail-frames.md` for the fields and command.
5. Preview the deploy only. Read `references/deploy.md`. Run the dry run, show the human its output, and wait for approval. Never run a real deploy yourself.

## Never

- Never deploy, change DNS, or touch billing or account settings. Give the human the exact command and let them run it.
- Never put an API token in a page, a script, a config or a trail frame. Tokens are environment variable names only (`CLOUDFLARE_API_TOKEN`).
- Never promise income or guaranteed results, invent reviews or testimonials, or hide that links earn commission.
- Never claim the page is "compliant". The checker verifies form (disclosure present, links marked, risky phrases absent), not law or truth.

## Output contract

Return the page path, the checker output verbatim, the dry-run command and its output, and a list
of anything unsourced or unverified. End with: "Not deployed. Awaiting human approval."

Read `references/cloudflare-mcp.md` and `assets/cloudflare-mcp-servers.json` when the user wants to inspect an existing Cloudflare site or account (read-only role allow-lists).
Read `references/affiliate-disclosure.md` (disclosure rules), `references/deploy.md` (verified
wrangler commands and approvals), `references/trail-frames.md` (frames per step).
`scripts/check_landing.py` lists its checks in its docstring; `assets/landing-template.html` is the starting page.
