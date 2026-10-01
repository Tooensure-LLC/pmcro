---
name: sft-dataset-check
description: "Check a PMCR-O training dataset (SFT JSONL with messages and meta) for schema, enum, split-leak, duplicate and governance-guard problems. Use when the user shares or generates training data, asks if a dataset is ready to fine-tune, or wants a dataset checker report."
license: MIT
---

# sft-dataset-check

Fine-tuning on a flawed dataset bakes the flaw into the model, and the owner's spec says generated data is only a CANDIDATE until an independent Dataset Checker passes it. This skill does the mechanical part of that check so the independent Checker spends its time on meaning.

## Do this

1. Run `python scripts/validate_sft.py FILE.jsonl --profile v2` for a file meant to follow `pmcro-sft-working-v2`. Use `--profile base` for older files with only the section 4 meta, and `--profile candidate` when the file invents its own `kind` names.
2. Read the grouped output: errors (structure, enums, duplicate ids, split leaks, credentials) fail the run; warnings (guard heuristics, missing coverage, missing "I AM" prompt) need a human or Checker to read the record.
3. Report counts and per-kind coverage, never the records themselves when the data is private (see `references/schema.md`).
4. Hand the file to an independent Dataset Checker (a different model or context than the generator) with the warning list.

## Never

- Never set `eligibility_state` to ELIGIBLE. The script cannot know the Checker verdict, and generating context never labels its own data verified.
- Never commit the owner's training files to the public repo; only aggregate findings go in docs.
- Never read a clean run as "ready to train": heuristics miss meaning errors.

## Output contract

Exit 0 means no structural errors; exit 1 means at least one. `--json` prints the full report. The final line always says an independent Dataset Checker is required.

Details of the schema, enums and the guards are in `references/schema.md`.
