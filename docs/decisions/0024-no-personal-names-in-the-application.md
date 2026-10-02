# 0024: The owner's personal name is not in the application

Status: accepted · 2026-10-01 (owner: "make sure my name isn't in the application")

## Decision
No file in this repository (code, plugins, generated manifests, docs, tests) contains the owner's personal name or personal handle. Provenance is written as "the owner's PMCR-O-Marketplace repo @ commit". `tools/pmcro.py validate` and CI scan every text file and every filename for forbidden words stored only as hashes, including camelCase and email-style forms, so the name is not written in the check either. Documents refer to "the owner" or "the founder". Quotations from the owner's corpus that use the name are reworded.

## Consequences
The hashes of short words can be guessed, so this keeps the name out of the text but is not a secret. One early commit in this repository's history was authored under the owner's account handle; history on a pushed branch is not rewritten here, so that commit's author field still shows it. Other repositories (the owner's private and personal ones) are not covered. Future commits use the session's own identity. If the application ever ships to users, check metadata not in the repository, such as store listings and package authors.
