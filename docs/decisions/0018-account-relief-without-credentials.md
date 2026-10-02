# 0018: Relieve account overload without handing agents credentials

Status: accepted (candidate) · 2026-10-01 (owner: about 20 accounts, hard to manage, needs the company to step in)

## Context
Managing many accounts is a decision-load problem. Giving agents logins would create security, terms-of-service and impersonation risk across every account at once.

## Decision
The company keeps a registry of accounts (platform, handle, purpose, cadence), flags neglected or purpose-less accounts, and produces a short brief of what needs the founder. It drafts; the founder approves and posts. The registry never stores credentials and refuses credential-shaped text. It lives in the private local tier. Retiring an account is always the founder's decision; flags are questions, not actions. Pruning accounts is treated as the largest relief.

## Consequences
Relief comes from fewer and smaller decisions, not from automation of logins. The registry cannot see the accounts, so activity is whatever a human reports. Posting automation through official APIs, with approval, is OPEN and would need its own decision. Local-only storage is lost with a temporary container.
