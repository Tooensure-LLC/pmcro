# Deploying to Cloudflare (human approval required)

Status: commands read from `wrangler` 4.146.0 `--help` on 2026-10-01; NOT run against a real account. Cloudflare's docs were unreachable from this workspace, so which route Cloudflare currently recommends is UNVERIFIED. Check developers.cloudflare.com before choosing.

## Two routes found in the CLI

| Route | Command | Notes |
| --- | --- | --- |
| Workers static assets | `wrangler deploy --assets <dir> --name <worker> --dry-run` | `--dry-run` compiles and checks without uploading; use it first |
| Pages | `wrangler pages deploy <dir> --project-name <name> --branch <branch>` | no dry-run flag was listed |

## Steps

1. Run the dry run (or, for Pages, only a local `wrangler pages dev <dir>`). Show the output to the human.
2. The human decides. Only they run the real deploy.
3. Authentication comes from the human's environment (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`). Never write a token anywhere. Use a token scoped to the one project, not the account.

## Never

DNS records, domains, billing, account or zone settings, or deleting a project. These are outside this skill; the human does them in the dashboard.

## OPEN

Cloudflare MCP servers and Cloudflare's own agent skills (`wrangler --install-skills` exists) may suit this; not evaluated here. Custom domain and DNS setup, analytics and form handling are not covered.
