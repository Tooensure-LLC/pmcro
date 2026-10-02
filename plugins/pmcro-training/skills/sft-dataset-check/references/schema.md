# pmcro-sft-working-v2 as the validator enforces it

Source: the owner's Training Data Schema and Final Spec PDFs. The schema is PROPOSED working architecture; the authoritative schema and training eligibility stay OPEN.

- Each line is `{"messages": [system, user, assistant], "meta": {...}}`, nothing else at the root.
- `meta` (all required): kind, sources, provenance, source_state, expected_state, architecture_disposition, invariants, open_items, candidate_items, requires_correction, requires_refusal, difficulty, domain, tags.
- v2 adds: example_id (unique), schema_version, split (train/validation/test), self_check_expected, independent_checker_required, eligibility_state (CANDIDATE, ELIGIBLE, WITHHELD; the Grok candidate file also uses CANDIDATE_DATASET, accepted with a note).
- 15 kinds: section_recall status_resolution source_precedence matrix_lookup matrix_group authority_reasoning routing_reasoning evidence_reasoning checker_reasoning marketplace_reasoning identity_reasoning discovery_reasoning architecture_reasoning guard_reasoning contradiction_resolution.
- 7 provenance classes: CANONICAL_OR_REPOSITORY_AUTHORITY, SOURCE_CORPUS_SNAPSHOT, APPROVED_SESSION_DECISION, APPROVED_ARCHITECTURAL_BOUNDARY, PROPOSED_ARCHITECTURE, CANDIDATE, OPEN.
- Dispositions: APPROVE_AS_ARCHITECTURAL_BOUNDARY, KEEP_AS_CANDIDATE, KEEP_OPEN, REJECT.
- Split labels stay separate from governance state.

## What is heuristic

Section 9 lists 17 rejection conditions. Mechanical ones (1-5) are errors. Meaning ones (6-17) are regex warnings on the assistant text (Maker issuing a verdict, Checker repairing, MATCH=PASS, MISMATCH=LOOP, Buyer=Customer, candidate promoted, OPEN resolved, platform evasion). A hit near a negation is skipped. They find candidates for review; they do not prove a record right or wrong. Conditions 8, 9, 14 and 16 are not detectable by regex and are left to the Checker.

## Privacy

The owner's data files stay local. Document counts, kind coverage and defect classes only.
