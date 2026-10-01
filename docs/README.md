# Documentation index

Every file under `docs/` must be linked here (the validator checks).

| Document | What it covers |
| --- | --- |
| [marketplace.md](marketplace.md) | How the marketplace, generated adapters, pinned upstreams and CI fit together; what is not built |
| [imports.md](imports.md) | What was imported from older repos, what changed, defects found |
| [offline-kit.md](offline-kit.md) | Packing the repo for an offline machine (tested) and the unattended runner design (not built) |
| [dotagents.md](dotagents.md) | The dotagents convention: what was run and verified, consumer config, what is not verified |
| [product/trail.md](product/trail.md) | Trail as a product: frame fields, rules, open questions |

## Decision records

| Record | Decision |
| --- | --- |
| [0001](decisions/0001-single-portable-core-generated-adapters.md) | One portable core, generated vendor adapters |
| [0002](decisions/0002-ci-makes-no-model-calls.md) | CI makes no model calls |
| [0003](decisions/0003-trail-tiers-and-local-only-secrets.md) | Trail tiers; secrets kept local |
| [0004](decisions/0004-reuse-dotnet-skills-as-pinned-upstream.md) | Reuse dotnet/skills as a pinned upstream |
| [0005](decisions/0005-mcp-role-allowlists.md) | MCP access per role by allow-list |
| [0006](decisions/0006-documentation-is-law.md) | Documentation is law |
| [0007](decisions/0007-follow-dotagents-convention.md) | Follow the dotagents convention |
| [0008](decisions/0008-synthetic-media-own-voice-local-disclosed.md) | Synthetic media: own voice, local, disclosed |
| [0009](decisions/0009-offline-kit-and-unattended-runner.md) | Offline kit; unattended runner stays read-only |
| [0010](decisions/0010-content-pipeline-drives-existing-tools.md) | Content pipeline drives existing tools; the founder approves |

New decision: copy the last record, increment the number, and add a row above.
