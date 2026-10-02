---
title: Documentation
---

# Documentation

The public pages of this site. They are copied from `docs/` at build time, so the repo stays the source of truth. Only the pages listed in `site/docfx.json` are built (ADR 0031).

## Guides

| Page | What it covers |
| --- | --- |
| [Marketplace](../../docs/marketplace.md) | How the marketplace, generated adapters, pinned upstreams and CI fit together |
| [dotagents](../../docs/dotagents.md) | The dotagents convention: what was run and verified |
| [Offline kit](../../docs/offline-kit.md) | Packing the repo for an offline machine |
| [Imports](../../docs/imports.md) | What was imported from older repos and what changed |

## Product

| Page | What it covers |
| --- | --- |
| [Trail](../../docs/product/trail.md) | Trail as a product: frame fields, rules, open questions |
| [Foundations](../../docs/product/foundations.md) | The three ideas PMCR-O rests on |

## Decision records

Every numbered decision record is listed in the sidebar under **Decision records**. That list is generated from `docs/decisions/` by `tools/site_catalog.py`, so a new record appears without editing this page.
