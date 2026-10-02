# 0032: Docs site configuration upgrade: generated sidebar, edit links, page metadata, docfx kept current

Date: 2026-10-02. Status: built; see Consequences for what was and was not tested. Asked for by the founder ("upgrade full site configuration"), following ADR 0031.

## Context

ADR 0031 shipped the docfx 2.81.0 site with a top navbar only: docs pages had no sidebar, no "edit this page" link, no language or description metadata, and the decision list in the docs index had to be edited by hand for every new record. The pinned docfx version also had no way to learn about new releases.

## Decision

- **Generated sidebar.** `tools/site_catalog.py gen` now also writes `site/docs/toc.yml` from the curated page list in `site/docfx.json`, titled from each page's first heading and grouped as Guides, Product and Decision records. CI's `gen --check` fails when it is stale. The docs index moved to `site/docs/index.md` so it sits inside the sidebar; its hand-kept decision table was replaced by the generated sidebar.
- **Edit links.** `_gitContribute` points at `Tooensure-LLC/pmcro` on `main`; git features are on so docfx can compute each page's source path. The generated pages (`plugins.md`, the sidebar) have edit links turned off, because editing them by hand is wrong.
- **Page metadata.** `_lang` is `en`; a site-wide `_description` plus per-section descriptions (`fileMetadata`) fill the description meta tag. The footer credits docfx.
- **docfx kept current.** `.github/dependabot.yml` watches only the `docfx` local tool, weekly, at most two open pull requests. A person merges after CI's `docs-site` job passes.
- **CI asserts the upgrade.** The `docs-site` job also checks that a docs page has the sidebar and an edit link, that a decision page has a description, and that the generated plugin page has no edit link.

Considered and not done:
- **xref to Microsoft's .NET docs** (`https://learn.microsoft.com/en-us/dotnet/.xrefmap.json`). It exists but is over 48 MB, and it would be downloaded on every build while no page uses `<xref:...>` links yet. Add it when the first API cross-reference is written.
- **Sitemap and canonical URL.** There is still no chosen host (ADR 0031); a placeholder URL would be false metadata.
- **Analytics.** Not added; it would collect visitor data, which is a founder decision.

## Consequences

- Adding a page to the site is still one edit to the list in `site/docfx.json`, then `python tools/site_catalog.py gen`.
- Tested: see the pull request for the real `docfx build --warningsAsErrors` output, the visual review and the CI run.
- Not tested: whether Dependabot actually opens a docfx pull request (it only can once a newer docfx exists), Safari and Firefox, screen readers, and edit links for pages after a file is renamed.
