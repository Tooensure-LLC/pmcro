---
_layout: landing
title: Fund The Loop
---

<section class="pm-hero">
  <h1>Fund The Loop</h1>
  <p class="pm-tag">PMCR-O is a five-role loop for AI agents: Orchestrator, Planner, Maker, Checker and Reflector. Each role is a separate Agent Skill, and only an independent Checker can say the work passed.</p>
  <img class="pm-art" src="images/hero.svg" alt="The PMCR-O loop: Orchestrator, Planner, Maker, Checker and Reflector placed on an infinity loop, with funding flowing in from both sides">
  <div class="pm-cta">
    <a class="pm-btn pm-btn-primary" href="plugins.md">Browse the plugins</a>
    <a class="pm-btn pm-btn-ghost" href="docs/product/trail.md">How the Trail works</a>
  </div>
  <div class="pm-install">/plugin marketplace add Tooensure-LLC/pmcro
/plugin install pmcro-core@pmcro-plugins</div>
</section>

## The loop

<div class="pm-roles">
  <div class="pm-role"><span class="pm-step">1 · Route</span><h3>Orchestrator</h3><p>Names the next role in a fixed order and does none of that role's work.</p></div>
  <div class="pm-role"><span class="pm-step">2 · Plan</span><h3>Planner</h3><p>Writes the smallest plan that proves the purpose, with a falsifiable proof expectation.</p></div>
  <div class="pm-role"><span class="pm-step">3 · Make</span><h3>Maker</h3><p>Carries out the plan and records real command output. A claim is not a verdict.</p></div>
  <div class="pm-role"><span class="pm-step">4 · Check</span><h3>Checker</h3><p>A separate invocation reruns the proof read-only and issues PASS, LOOP or HALT.</p></div>
  <div class="pm-role"><span class="pm-step">5 · Reflect</span><h3>Reflector</h3><p>Adds lessons as append-only proposals. It never changes a verdict or the rules.</p></div>
</div>

## Why "Fund The Loop"

Every cycle leaves a Trail frame: what was decided, done, checked and learned, and what it cost. A loop that records its cost can be judged on its economics, and a loop that keeps passing independent checks is worth funding. See [Trail](docs/product/trail.md) and [Foundations](docs/product/foundations.md).

## Install

Works in Claude Code and Copilot CLI:

```
/plugin marketplace add Tooensure-LLC/pmcro
/plugin install pmcro-core@pmcro-plugins
/plugin install pmcro-dotnet@pmcro-plugins
```

The full list is in the [plugin catalog](plugins.md). How the marketplace is built and checked is in [Marketplace](docs/marketplace.md).

<p class="pm-note">Status: CANDIDATE. CI in the repo is deterministic and makes no model calls; each plugin's README says what was and was not tested. This site is built and checked in CI and is not deployed (<a href="docs/decisions/0031-docs-site-docfx-build-only.md">ADR 0031</a>).</p>
