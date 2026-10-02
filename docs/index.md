---
title: Documentation
---

# Documentation

The public pages of this site. They are built straight from `docs/`, so the repo stays the source of truth. Only the pages listed in `site/docfx.json` are built (ADR 0031).

## Guides

| Page | What it covers |
| --- | --- |
| [Marketplace](marketplace.md) | How the marketplace, generated adapters, pinned upstreams and CI fit together |
| [dotagents](dotagents.md) | The dotagents convention: what was run and verified |
| [Offline kit](offline-kit.md) | Packing the repo for an offline machine |
| [Imports](imports.md) | What was imported from older repos and what changed |

## Product

| Page | What it covers |
| --- | --- |
| [Trail](product/trail.md) | Trail as a product: frame fields, rules, open questions |
| [Foundations](product/foundations.md) | The three ideas PMCR-O rests on |

## Decision records

Every numbered decision record is listed in the sidebar under **Decision records**. That list (`docs/toc.yml`) is generated from `docs/decisions/` by `tools/site_catalog.py`, so a new record appears without editing this page.
