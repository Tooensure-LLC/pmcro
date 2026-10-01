# Competitors, tools and models: what we know and where it came from

Status: started 2026-10-01 at the owner's request ("mark them down; the company needs to know this when it makes products"). Two kinds of entry only: **sourced** (from a web search on 2026-10-01, titles and snippets, not full reads) and **owner observation** (what the owner said from experience, not verified). Nothing here is a claim about a competitor's weaknesses beyond what the source says.

## Microsoft Agent Governance Toolkit (sourced, and part of the owner's own stack)

- Open-source (MIT), released 2026-04-02 per the sources; runtime security for agents: policy enforcement on every tool call before it runs, cryptographic agent identities, sandboxing, and an audit trail that is Merkle-chained and verifiable offline. Available in Python, Rust, TypeScript, Go and .NET. It plugs into agent frameworks; Microsoft's Agent Framework blog describes using the two together.
- This is probably what the owner remembered as "audit". Its audit trail records what an agent did at the tool-call level. It is prior art for the OPEN sealing question in PMCR-O, and a component the owner already plans to use, not a competitor.
- Sources: [Microsoft Agent Framework and Agent Governance Toolkit, better together](https://devblogs.microsoft.com/agent-framework/governance-at-the-speed-of-agents-microsoft-agent-framework-and-agent-governance-toolkit-better-together/), [Architecture deep dive](https://techcommunity.microsoft.com/blog/linuxandopensourceblog/agent-governance-toolkit-architecture-deep-dive-policy-engines-trust-and-sre-for/4510105), [InfoWorld](https://www.infoworld.com/article/4175859/microsofts-open-source-toolkit-for-controlling-out-of-control-ai-agents.html).

## Audit-trail products (sourced, titles and snippets only)

Lorikeet, Agent Receipts, Zambo, SovereignClaw, Traefik Labs Sovereign Trust Plane, and the open-source `verifiable-agent-trail` all sell or publish tamper-evident or replayable records of what agents did. See backlog row 45. What the snippets did not mention, and PMCR-O has: an independent Checker verdict and a separate Auditor sampling sealed trails.

## The owner's "accountability layer" idea (owner observation)

The pitch: others have trails; PMCR-O adds accountability, meaning a record of who is responsible for each action, so that if an agent does something it should not have done, the record shows who acted and under whose authority. This repo does not make legal claims about what an agent's action means for its owner; that is for the CLO seat and a real lawyer. What the design supports today: the trail's executor field names who acted, and authority attenuation names whose ceiling applied.

## Which model or tool is good for what (owner observation, to fill in)

The owner said Grok, ChatGPT, Copilot and others each have strengths and asked for them to be recorded. They did not say what the strengths are, so the table is empty on purpose; a guess here would be invented.

| Tool or model | Good for (owner's words) | Limits seen | Verified by a trail? |
| --- | --- | --- | --- |
| Grok | | | no |
| ChatGPT | | | no |
| Copilot | | | no |
| Claude | | | no |

## How much training data (sourced)

Search results on supervised fine-tuning agree that quality beats volume: the LIMA paper reports strong results from about 1,000 carefully curated examples; practical guides put roughly 500 good examples at enough for style and format, 1,000 to 5,000 for domain specialization, and diminishing returns beyond that unless genuinely new knowledge is added. "Boatloads" is for pretraining, not for this. For PMCR-O that means: the 90-example blueprint is a start for format and boundary behavior; the real limit is the number of examples an independent Dataset Checker has cleared, not the number generated. Sources: [LIMA](https://arxiv.org/pdf/2305.11206), [Databricks, Less is More for Instruction Tuning](https://www.databricks.com/blog/limit-less-more-instruction-tuning), [Raschka on LoRA](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms).
Data from the owner's many accounts is a source for candidates, not a shortcut: exports are conversations, not verified trails, and private content stays local.
