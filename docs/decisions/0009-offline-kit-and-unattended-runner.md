# 0009: Offline kit; unattended runner stays read-only

Status: accepted (kit) / proposed (runner) · 2026-10-01 (owner has an offline i9 for 24/7 experiments)

## Decision
Ship `tools/offline_kit.py`, tested by installing from its output with no index access. Design the unattended runner as read-only plus a scratch directory, budget-capped, with output leaving only as a reviewed git bundle. Do not build it until the machine's OS, RAM and GPU are known.

## Consequences
Wheels are platform-specific, so the target platform must be given. Model weights travel separately. Details and what was not verified: `docs/offline-kit.md`.
