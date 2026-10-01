# 0025: Encode the owner's generic CRUD design as a skill

Date: 2026-10-01. Status: accepted by the owner's direction ("this is very important to our agent skills").

## Context

The owner builds .NET APIs one way: an abstract `BaseEntity` with `Id = Guid.NewGuid()`, a generic repository interface and class over `T : BaseEntity`, empty per-model repositories, a generic unit of work and a generic controller, so the only hand-written code is the model. They described it in chat; no repo we could read contains it (the private ProjectName repo has the Scalar and OpenAPI host but no repository code).

## Decision

Add `dotnet-generic-crud` to `pmcro-dotnet`: templates plus a generator, with the design recorded in `references/design.md` and the choices we added listed separately from what the owner said. Add a CI job that builds the scaffold and exercises create, list, get, update and delete over HTTP, and fetches `/openapi/v1.json` and `/scalar`.

## Consequences

- A small local model can reproduce the owner's pattern from files instead of inventing it.
- The scaffold is verified only by CI. If the owner later finds the real repository, compare it to `design.md` and correct whichever is wrong.
- Package versions follow the private repo's pins for OpenAPI and Scalar; EF Core uses a 10.0.* range.
