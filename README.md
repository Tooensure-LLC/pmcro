# PMCR-O plugins

Marketplace: `pmcro-plugins`. Install in Claude Code or Copilot CLI:

```
/plugin marketplace add Tooensure-LLC/pmcro
/plugin install pmcro-core@pmcro-plugins
/plugin install pmcro-dotnet@pmcro-plugins
```

| Plugin | Contents |
| --- | --- |
| `pmcro-core` | Orchestrator, Planner, Maker, Checker, Reflector, Trail Player |
| `pmcro-dotnet` | `maf-local-skills`: wire skills into Microsoft Agent Framework for small local models |

The marketplace also lists 15 [dotnet/skills](https://github.com/dotnet/skills) plugins (MAUI, AI, MSBuild, test, ASP.NET Core and more), pinned to a commit and not copied: `/plugin install dotnet-maui@pmcro-plugins`.

Modeled on [dotnet/skills](https://github.com/dotnet/skills): one portable plugin per folder,
generated vendor adapters, deterministic CI. See `docs/marketplace.md` and `docs/product/trail.md`.

Status: CANDIDATE. No independent Checker has reviewed this repo.
