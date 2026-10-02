# Training data: what the owner's specs say, and what we found

Status: read from the owner's Training Data Schema and Final Spec PDFs plus three datasets, 2026-10-01. The specs are PROPOSED working architecture. Authoritative schema and training eligibility remain OPEN. Only aggregate findings are recorded here; the data files are the owner's and are not in this repo.

## The contract (summary)

Each record is `messages` [system, user, assistant] plus `meta`. Meta carries kind (15 classes), provenance (7 classes), source_state, expected_state, invariants, open_items, candidate_items, split, and in v2 example_id, schema_version, eligibility_state, independent_checker_required. The system prompt uses the first-person "I AM" profile. A 90-example balanced blueprint (6 per kind) is the working target. Training split labels are kept separate from governance state.

Eligibility (PROPOSED FOR APPROVAL): ELIGIBLE only when schema, provenance, state resolution, invariants, no OPEN resolved, no CANDIDATE promoted, source set available and an independent Dataset Checker PASS. A correctable defect returns the record as CANDIDATE; unverifiable provenance or a boundary violation makes it WITHHELD. This is not the Trail ACCEPT definition.

Provider-neutral procedure: freeze dataset, validate, independent Dataset Checker, split, fine-tune only on cleared data, evaluate on held-out guard/contradiction/evidence/Checker cases, reject any release that increases authority or regresses, record the run as evidence.

## Findings from running `sft-dataset-check`

| File | Records | Result |
| --- | --- | --- |
| pmcro-sft-v1.jsonl | 90 | Passes the base meta contract; all 15 kinds, 6 each; splits 72/9/9. Lacks v2 fields (example_id aside, no schema_version, eligibility_state, checker flags). Two warnings are the record that *teaches* MATCH is not PASS, so they are false positives. |
| pmcro_sft.jsonl (earlier) | 299 | Meta has only kind (and a few fields); fails the contract. Covers 4 of 15 kinds, no splits. Two repeated prompts. |
| pmcro-candidate (Grok run) | 70 | Structurally clean under the candidate profile, but uses 25 kind names of its own, none of the 15; its system prompt is not the "I AM" form; its generation report says one split while the manifest says 48/12/10. Status CANDIDATE_DATASET; its own handoff requires an independent Dataset Checker. |
| pmcro_corpus.jsonl | 137 | Source corpus (id, section, text, status_labels), not SFT records; not checked as SFT. |

## What this means

- None of the files is training-eligible today, and nothing here changes that: the independent Dataset Checker verdict is still owed.
- The candidate file's kinds should be mapped to the 15 (or the spec extended by the owner) before any merge.
- A validator pass is necessary, not sufficient.
