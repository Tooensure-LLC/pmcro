# Documentation index

Every file under `docs/` must be linked here (the validator checks).

| Document | What it covers |
| --- | --- |
| [marketplace.md](marketplace.md) | How the marketplace, generated adapters, pinned upstreams and CI fit together; what is not built |
| [imports.md](imports.md) | What was imported from older repos, what changed, defects found |
| [offline-kit.md](offline-kit.md) | Packing the repo for an offline machine (tested) and the unattended runner design (not built) |
| [dotagents.md](dotagents.md) | The dotagents convention: what was run and verified, consumer config, what is not verified |
| [product/company-model.md](product/company-model.md) | What the owner's company file says: product, laws, earned constraints, always-ask list, round table, queue, plus corrections to earlier guesses |
| [product/idea-backlog.md](product/idea-backlog.md) | Every direction the owner has given, with status and next step |
| [product/foundations.md](product/foundations.md) | The three ideas PMCR-O rests on (strange loops, I and Thou, self-replication) and what each asks of the design |
| [product/colab-and-cognitive-agents.md](product/colab-and-cognitive-agents.md) | Learning notes: Colab for cheap fine-tuning, the data rules, and what a cognitive agent means here |
| [product/everything-as-agent.md](product/everything-as-agent.md) | EverythingAsAgent: capture to draft skill, the pipeline, and the conditions for any steps recorder |
| [product/ghostwriter.md](product/ghostwriter.md) | Ghostwriter: phases from scripts to songs to voice, and the conditions for third-party voices |
| [product/training-data-spec.md](product/training-data-spec.md) | The owner's training-data contract, eligibility proposal, and what the validator found in the datasets (aggregate only) |
| [product/tts-reader-review.md](product/tts-reader-review.md) | Read-only review of the uploaded TTS Reader Chrome extension: what it sends where, permissions, recommendation |
| [product/competitors-and-models.md](product/competitors-and-models.md) | Competitors, the Agent Governance Toolkit, which model is good for what (owner's observations to fill in), and how much training data is enough, each marked sourced or owner observation |
| [product/skills-evaluation.md](product/skills-evaluation.md) | The pasted .NET skills evaluation dashboard (an LLM federation): how it measures skills, what it shows, and what it means for our eval gate |
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
| [0011](decisions/0011-cloudflare-sites-build-check-never-deploy.md) | Cloudflare site work builds and checks; humans deploy |
| [0012](decisions/0012-file-based-message-queue.md) | A file-based message queue for the founder's messages |
| [0013](decisions/0013-simulated-trails-are-not-evidence.md) | Simulated trails are not evidence |
| [0014](decisions/0014-cloudflare-mcp-read-first-allowlists.md) | Cloudflare MCP: read first, per-role allow-lists |
| [0015](decisions/0015-figma-factory-composes-with-figma-mcp.md) | The Figma factory composes with Figma's MCP, it does not proxy it |
| [0016](decisions/0016-self-reference-by-default-serve-everything-over-mcp.md) | Self-reference by default: every capability is also served over MCP |
| [0017](decisions/0017-ghostwriter-phases-and-third-party-voices.md) | Ghostwriter phases; third-party voices only under contract |
| [0018](decisions/0018-account-relief-without-credentials.md) | Relieve account overload without handing agents credentials |
| [0019](decisions/0019-everything-as-agent-capture-to-skill.md) | EverythingAsAgent starts as capture to draft skill, privacy by default |
| [0020](decisions/0020-bip-delegated-decisions.md) | BIP: decisions are delegated to the seats; the reserved list; the decision log |
| [0021](decisions/0021-shared-memory-is-the-founders-knowledge.md) | Shared memory is the founder's knowledge, tiered and human-accepted |
| [0022](decisions/0022-generate-the-owners-mcp-servers.md) | Generate the owner's MCP servers; the owner wires the connections |
| [0024](decisions/0024-no-personal-names-in-the-application.md) | The owner's personal name is not in the application |
| [0025](decisions/0025-generic-crud-design-from-the-owner.md) | The owner's generic CRUD design (BaseEntity, generic repository, unit of work) becomes a skill |
| [0026](decisions/0026-platform-apis-become-mcp-tools-not-agents.md) | Platform APIs become generated MCP tools, not agents; writes off by default |
| [0027](decisions/0027-company-tier-needs-declared-private-repo.md) | Company tier needs a repo declared private; tier entries scanned and numbered per tier |

New decision: copy the last record, increment the number, and add a row above.
