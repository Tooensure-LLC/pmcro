# pmcro-training

Validate and gate PMCR-O fine-tuning datasets (SFT JSONL) against the owner's working schema before any training run.

## Skills

| Skill | Use it to |
| --- | --- |
| `sft-dataset-check` | Check a PMCR-O training dataset (SFT JSONL with messages and meta) for schema, enum, split-leak, duplicate and governanc |

## Install

```
/plugin install pmcro-training@pmcro-plugins
```

## Prior art

The schema and rejection profile come from the owner's Training Data Schema and Final Spec. No external validator is reused: none knows the PMCR-O enums.

## Status

CANDIDATE. Verified by the repo tests (valid and must-fail records, split leak, credential, ELIGIBLE warning). Not verified: that the regex guards catch real semantic errors; they are heuristics. No fine-tuning pipeline exists here yet; the owner's procedure (freeze, validate, independent Dataset Checker, split, train on cleared data, evaluate on held-out guard cases) is in `docs/product/training-data-spec.md`.
