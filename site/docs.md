---
title: Documentation
---

# Documentation

The public pages of this site. They are copied from `docs/` at build time, so the repo stays the source of truth. Only the pages listed in `site/docfx.json` are built (ADR 0031).

## Guides

| Page | What it covers |
| --- | --- |
| [Marketplace](../docs/marketplace.md) | How the marketplace, generated adapters, pinned upstreams and CI fit together |
| [dotagents](../docs/dotagents.md) | The dotagents convention: what was run and verified |
| [Offline kit](../docs/offline-kit.md) | Packing the repo for an offline machine |
| [Imports](../docs/imports.md) | What was imported from older repos and what changed |

## Product

| Page | What it covers |
| --- | --- |
| [Trail](../docs/product/trail.md) | Trail as a product: frame fields, rules, open questions |
| [Foundations](../docs/product/foundations.md) | The three ideas PMCR-O rests on |

## Decision records

| Record | Decision |
| --- | --- |
| [0001](../docs/decisions/0001-single-portable-core-generated-adapters.md) | One portable core, generated vendor adapters |
| [0002](../docs/decisions/0002-ci-makes-no-model-calls.md) | CI makes no model calls |
| [0003](../docs/decisions/0003-trail-tiers-and-local-only-secrets.md) | Trail tiers; secrets kept local |
| [0004](../docs/decisions/0004-reuse-dotnet-skills-as-pinned-upstream.md) | Reuse dotnet/skills as a pinned upstream |
| [0005](../docs/decisions/0005-mcp-role-allowlists.md) | MCP access per role by allow-list |
| [0006](../docs/decisions/0006-documentation-is-law.md) | Documentation is law |
| [0007](../docs/decisions/0007-follow-dotagents-convention.md) | Follow the dotagents convention |
| [0008](../docs/decisions/0008-synthetic-media-own-voice-local-disclosed.md) | Synthetic media: own voice, local, disclosed |
| [0009](../docs/decisions/0009-offline-kit-and-unattended-runner.md) | Offline kit; unattended runner stays read-only |
| [0010](../docs/decisions/0010-content-pipeline-drives-existing-tools.md) | Content pipeline drives existing tools |
| [0011](../docs/decisions/0011-cloudflare-sites-build-check-never-deploy.md) | Site work builds and checks; humans deploy |
| [0012](../docs/decisions/0012-file-based-message-queue.md) | A file-based message queue |
| [0013](../docs/decisions/0013-simulated-trails-are-not-evidence.md) | Simulated trails are not evidence |
| [0014](../docs/decisions/0014-cloudflare-mcp-read-first-allowlists.md) | Cloudflare MCP: read first, per-role allow-lists |
| [0015](../docs/decisions/0015-figma-factory-composes-with-figma-mcp.md) | The Figma factory composes with Figma's MCP |
| [0016](../docs/decisions/0016-self-reference-by-default-serve-everything-over-mcp.md) | Every capability is also served over MCP |
| [0017](../docs/decisions/0017-ghostwriter-phases-and-third-party-voices.md) | Ghostwriter phases; third-party voices only under contract |
| [0018](../docs/decisions/0018-account-relief-without-credentials.md) | Relieve account overload without handing agents credentials |
| [0019](../docs/decisions/0019-everything-as-agent-capture-to-skill.md) | Capture to draft skill, privacy by default |
| [0020](../docs/decisions/0020-bip-delegated-decisions.md) | Decisions delegated to the seats; the reserved list |
| [0021](../docs/decisions/0021-shared-memory-is-the-founders-knowledge.md) | Shared memory, tiered and human-accepted |
| [0022](../docs/decisions/0022-generate-the-owners-mcp-servers.md) | Generate the owner's MCP servers |
| [0024](../docs/decisions/0024-no-personal-names-in-the-application.md) | No personal names in the application |
| [0025](../docs/decisions/0025-generic-crud-design-from-the-owner.md) | Generic CRUD design becomes a skill |
| [0026](../docs/decisions/0026-platform-apis-become-mcp-tools-not-agents.md) | Platform APIs become generated MCP tools |
| [0027](../docs/decisions/0027-company-tier-needs-declared-private-repo.md) | Company tier needs a declared private repo |
| [0028](../docs/decisions/0028-seat-agents-generated-from-company-json.md) | Seat agents generated from company.json |
| [0029](../docs/decisions/0029-memory-ids-csuite-deprecation-seat-drift-toggles.md) | Per-tier memory ids, seat drift check, toggles |
| [0030](../docs/decisions/0030-law-loop-until-done-mirrored.md) | Law: Loop Until Done |
| [0031](../docs/decisions/0031-docs-site-docfx-build-only.md) | Docs site: docfx 2.81.0, curated pages, build-only |
