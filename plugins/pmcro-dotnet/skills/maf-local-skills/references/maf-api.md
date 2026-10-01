# MAF skills API notes

Status: Python rows tested against `agent-framework` 1.19.0 on 2026-10-01. .NET rows are from Microsoft Learn and NOT compiled here.

## Tools the model sees

| Tool | Appears when | Purpose |
| --- | --- | --- |
| `load_skill` | always | returns a skill's body |
| `read_skill_resource` | some skill has resources | returns one file from `references/` or `assets/` |
| `run_skill_script` | some skill has scripts | runs one script |

## Python (tested)

```python
from agent_framework import SkillsProvider
provider = SkillsProvider.from_paths(
    "plugins/pmcro-core/skills",
    script_filter=lambda skill, script: (skill, script) in ALLOWED,  # allow-list
    # disable_*_approval flags stay at their default False
)
```

- `search_depth=2` by default, so pass the `skills/` directory, not the plugin root.
- `resource_extensions` defaults to `.md .json .yaml .yml .csv .xml .txt`; `script_extensions` to `.py`.
- `FileSkillsSource` skips symbolic links inside skill directories.
- `SkillsProvider.read_only_tools_auto_approval_rule` exists: use it to auto-approve only `load_skill` and `read_skill_resource`, never `run_skill_script`.

## Read-only Checker

Put the rule in function-call middleware that raises on any tool not in a read-only set, so it fails closed. A prompt instruction alone does not enforce Checker Verdict Only.

## .NET (unverified)

Types named in Learn: `AgentSkillsProvider`, `AgentSkillsProviderBuilder`, `SubprocessScriptRunner`. Tool approval uses `ApprovalRequiredAIFunction`. Verify names with `dotnet build` before relying on them. Package versions: pin `Microsoft.Agents.AI` and the Python package separately; they are on different version lines.
