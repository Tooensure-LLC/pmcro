#!/usr/bin/env python3
"""Generate a read-only .NET MCP skills server project from templates, in the owner's existing pattern.

  python generate_dotnet_server.py --name Pmcro.Mcp.Skills --out DIR [--tfm net10.0] [--mcp-version 2.1.0]
Renders assets/templates/dotnet-server/* into DIR: a .csproj, Program.cs, Configuration/SkillsConfig.cs,
Tools/SkillTools.cs, Resources/SkillResources.cs, Prompts/SkillPrompts.cs, appsettings.json and a README.
Layout and API usage mirror the owner's PMCR-O-Marketplace MCP servers (Configuration, Tools, Resources, Prompts,
stateless HTTP, MapMcp("/mcp"), ModelContextProtocol 2.1.0). It adds a symbolic-link guard and refuses to serve scripts.
Refuses: names that are not dotted PascalCase identifiers, an existing output folder, an unknown target framework.
Output: "generated NAME -> DIR"; "refused: ..." and exit 1 otherwise.
This tool does not build the project. This repository's CI compiles the default output (net10.0, ModelContextProtocol 2.1.0);
any other version or target is unverified until you run dotnet build.
"""
import argparse, pathlib, re, sys

TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates" / "dotnet-server"
NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(\.[A-Z][A-Za-z0-9]*)*$")
TFM_RE = re.compile(r"^net\d+\.\d+$")
MCP_RE = re.compile(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.]+)?$")


def generate(name, out, tfm="net10.0", mcp_version="2.1.0"):
    if not NAME_RE.match(name):
        sys.exit("refused: --name must be dotted PascalCase such as Pmcro.Mcp.Skills")
    if not TFM_RE.match(tfm) or not MCP_RE.match(mcp_version):
        sys.exit("refused: --tfm like net10.0 and --mcp-version like 2.1.0")
    out = pathlib.Path(out)
    if out.exists():
        sys.exit(f"refused: {out} already exists")
    values = {"{{ServerName}}": name, "{{Namespace}}": name, "{{Tfm}}": tfm, "{{McpVersion}}": mcp_version}
    for tmpl in sorted(TEMPLATES.rglob("*.tmpl")):
        rel = tmpl.relative_to(TEMPLATES).as_posix()[: -len(".tmpl")]
        if rel == "Server.csproj":
            rel = f"{name}.csproj"
        text = tmpl.read_text()
        for k, v in values.items():
            text = text.replace(k, v)
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
    print(f"generated {name} -> {out}")


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--name", required=True); a.add_argument("--out", required=True)
    a.add_argument("--tfm", default="net10.0"); a.add_argument("--mcp-version", default="2.1.0")
    a = a.parse_args()
    generate(a.name, a.out, a.tfm, a.mcp_version)
