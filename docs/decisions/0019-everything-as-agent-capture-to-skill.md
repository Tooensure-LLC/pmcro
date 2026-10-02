# 0019: EverythingAsAgent starts as capture to draft skill, with privacy by default

Status: accepted (candidate) · 2026-10-01 (owner product idea: anyone can turn anything into an agent, for example by photographing a document or device and learning to use it)

## Context
The idea needs input from the real world (pictures, screens, steps) and a reusable output. Our output format already exists: an Agent Skill (instructions, references, assets, scripts) that any agent can load. Captured pictures carry hidden metadata (GPS, device ids) and visible secrets (passwords, other people). A Windows-style steps recorder (clicks, window titles, screenshots, OCR) would also capture far more than the person intends.

## Decision
Start with the safe core: `pmcro-capture` / `capture-to-skill`. A human chooses the images; a human confirms they reviewed every one; the script strips metadata always, refuses anything it cannot parse, and writes a draft skill full of TODO markers that states the steps were not run. A draft becomes a skill only after someone follows it and an independent Checker confirms (evidence, completion claim and independent check stay separate). A live recorder is not built; its conditions are in `docs/product/everything-as-agent.md`.

## Consequences
The company can turn demonstrations into reusable skills without ever watching a screen. Quality depends on the human notes and review; the script cannot see pixels. Qualification of non-Trail products (skills, plugins) remains OPEN in the company's own marketplace corpus, so nothing here is a listed product. Third-party device or document content may carry copyright; check before sharing a skill.
