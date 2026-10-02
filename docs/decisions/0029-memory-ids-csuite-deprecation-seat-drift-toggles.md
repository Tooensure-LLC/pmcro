# 0029: Per-tier memory ids, pmcro-csuite deprecated, seat drift check, toggle governance

Date: 2026-10-01. Status: built and tested; owner direction ("all, if you recommend").

## Context

ADR 0027 left two gaps in shared memory: one id counter across tiers (gaps in public ids revealed private entries) and no absolute-path scan. ADR 0028 left two plugins describing the C-Suite, and seat agents copied from `company.json` with nothing to show when the company changes. The owner's Copilot domain list named feature-toggle governance, which no plugin covered.

## Decision

- Shared-memory ids carry one letter and counter per tier: public P, company M (so existing M0001 onward stay valid), roundtable R, private V. `add` refuses absolute paths after proving the check can fail. The MCP server's `memory_show` accepts the four letters.
- `pmcro-csuite` is marked deprecated in favor of `pmcro-seats`. It is not removed; removal is a deletion and the owner's decision.
- `tools/seats.py drift COMPANY_JSON` reports when the seats snapshot no longer matches `company.json`. The company repo is private, so the CI job reads it only when the owner adds a read-only `COMPANY_REPO_TOKEN` secret; without it the job says it was skipped.
- New CANDIDATE plugin `pmcro-toggles`: governance (owner, expiry, stages) for flags in an OpenFeature `flags.json`, kept in a sidecar so the manifest stays standard, with a read-only `check` for the Checker. LaunchDarkly's hosted MCP server is documented as a real but untested connector; none is wired.

## Consequences

Memory entries written before this change in tiers other than company keep their M ids on disk but are no longer listed by the new reader; none exist in this repository. The seats snapshot was copied from a private repository into this public one (ADR 0028); whether that text may stay public is the owner's decision. Not verified: the drift job with a real token, the OpenFeature CLI reading a generated manifest, and any live flag service.
