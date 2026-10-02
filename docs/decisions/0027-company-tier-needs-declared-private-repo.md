# 0027: The company tier needs a repo declared private; tier entries are scanned and numbered per tier

Date: 2026-10-01. Status: built and tested; amends ADR 0003. Found by an outside review of PR #1.

## Context

ADR 0003 said `company` entries are committable only if the repository is private, and the trail-player docs said the writer checked. It did not, and this repository is public, so `trail/company/` is published. The same review showed `record.py` saving a credential-shaped string and an absolute path into `trail/public/`, `--replay` printing private entries to any caller although the docs promised a reader check, and one counter shared by all tiers, so gaps in public numbering revealed hidden entries.

## Decision

- Writing the `company` tier (trail player, shared memory, inbox) requires `git config pmcro.repoVisibility private`, set once by a person and only when true. Without it the writer refuses (fail closed).
- `record.py` scans the body and summary for credential-shaped text and absolute paths in every tier, after proving the scan fails on a sample built by its own serializer (EC-0001). A refusal names the rule, never the text.
- Each tier is numbered on its own.
- Replay is documented as what it is: it prints the tier asked for and cannot check who is calling.

## Consequences

Existing files under `trail/company/memory/` (M0001 to M0004) are already public in git history; whether they stay is the owner's decision and is not changed here. Not done: shared-memory ids are still numbered across tiers, and shared-memory bodies are not scanned for absolute paths. The repo-visibility declaration is a local setting a person can set wrongly; it is not checked against GitHub.
