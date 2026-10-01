# 0011: Cloudflare site work builds and checks; humans deploy

Status: accepted (candidate) · 2026-10-01 (owner idea: pmcro-cloudflare with trail frames, landing pages for affiliate marketing)

## Context
Cloudflare changes are outward-facing (live pages, DNS, billing) and hard to undo. Affiliate pages carry disclosure duties and tempt income promises.

## Decision
A separate plugin, because its blast radius differs from read-only knowledge plugins. It builds a page from a template, checks form with a deterministic script, records each step as a company-tier trail frame with cost, and prepares a dry run. A human runs every real deploy. DNS, billing and account settings are out of scope. Tokens are environment variable names only.

## Consequences
The checker cannot prove compliance or truth; the docs say so. Wrangler commands come from `--help` only; Cloudflare's docs, MCP servers and agent skills were not evaluated. Revenue and cost frames feed the economic gates, which flag and never act.
