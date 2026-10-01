---
name: dotnet-generic-crud
description: "Scaffold a .NET Web API where adding a model gives full CRUD for free: a BaseEntity with a Guid Id, a generic repository, a unit of work and a generic controller, with OpenAPI and Scalar. Use when the user wants a new .NET API, a new model or entity, a repository pattern, unit of work, clean architecture CRUD, or says 'all I should have to create is a model'."
license: MIT
---

# Generic CRUD for .NET (the owner's design)

The owner's way of building .NET APIs: write the model, and everything else comes from generics. This skill scaffolds that design so a small local model does not have to invent it.

## Do this

1. Run `python scripts/scaffold_crud.py --out DIR --namespace Acme.Shop --entity "User:Name=string,Email=string"`. Repeat `--entity` for more models, and rerun with the same `--out` to add models later; existing files are never overwritten.
2. Read `references/design.md` before changing anything: it explains each layer and why the repository and controller stay empty.
3. Put special behavior only in the model's own repository (`I{Name}Repository` / `{Name}Repository`), never in the generic base.
4. Build with `dotnet build`. Scalar's interactive API reference is at `/scalar` and the OpenAPI document at `/openapi/v1.json`.

## Never

- Never give an entity its own Id handling: `BaseEntity` sets `Id = Guid.NewGuid()` and the controller ignores any client-supplied id.
- Never call SaveChanges from a repository; only the unit of work saves.
- Never claim it builds from this skill alone: it was compiled and exercised only in this repository's CI job `dotnet-crud`.

## Output contract

The script prints `wrote N files into DIR` or `refused: ...` and exits 1. It writes only into `DIR`. The default stack is net10.0, EF Core (in-memory provider, swap for a real one), OpenAPI and Scalar.AspNetCore.
