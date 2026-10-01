# pmcro-cloudflare

Website and landing-page setup on Cloudflare for the PMCR-O company, built for affiliate and product pages. It builds and checks pages and records each step as a trail frame; it never deploys.

## Skills

| Skill | Use it to |
| --- | --- |
| `landing-page` | Start from a template, check affiliate-disclosure basics with `scripts/check_landing.py`, record trail frames, and prepare a deploy dry run for a human to approve. |

## Install

```
/plugin install pmcro-cloudflare@pmcro-plugins
```

## Status

CANDIDATE. The checker is tested (form only: disclosure before the first affiliate link, `rel=sponsored`, no income promises, privacy link, no tokens). Not tested: any real Cloudflare deploy or account; the wrangler commands were read from `wrangler` 4.146.0 `--help`, and Cloudflare's own docs were unreachable here, so the recommended route (Pages versus Workers static assets) is unverified. Affiliate and consumer-protection rules vary by country and change; nothing here is legal advice. See ADR 0011.
