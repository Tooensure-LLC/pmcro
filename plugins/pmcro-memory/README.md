# pmcro-memory

Shared, tiered, append-only memory for the founder and every agent: the company's knowledge, searchable, with provenance and human-owned acceptance.

## Skills

| Skill | Use it to |
| --- | --- |
| `shared-memory` | Remember and recall knowledge and lessons with tiers, viewers, provenance and human-owned acceptance (`scripts/memory.py`). |

## Install

```
/plugin install pmcro-memory@pmcro-plugins
```

## Status

CANDIDATE. `memory.py` is tested (ranking, tier visibility per viewer, append-only supersede, candidate versus accepted, credential refusal, gitignore guard). It is keyword search, not meaning search, and can miss a differently worded memory. Local tiers live on one machine and are lost with a temporary container. NOT built: embeddings, automatic summarising, syncing between machines. See ADR 0021.
