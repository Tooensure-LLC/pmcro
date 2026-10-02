#!/usr/bin/env python3
"""Generate a .NET MCP server that wraps one third-party HTTP API, from a small JSON spec.

  python generate_platform_mcp.py --spec SPEC.json --out DIR [--tfm net10.0] [--mcp-version 2.1.0]
The spec names the platform, two environment variables (base URL and token) and a list of operations (name, method, path,
description, params with in = path, query or body). Output: a Web project with PlatformClient (the only code that calls the
platform) and one MCP tool per operation, in the owner's layout (Configuration, Tools, stateless HTTP, /mcp).
Safety rules baked in: identity is read from an environment variable at call time and never stored; every non-GET operation must
be marked write and is refused unless Platform__AllowWrites=true; the base URL must be https (http only for localhost).
Refuses: bad names, non-GET operations not marked write, a path parameter with no matching param, an existing output folder.
Output: "generated NAME -> DIR" or "refused: ...". Not built here (no .NET SDK in the authoring session); this repository's CI builds
and smoke-tests the example spec. Endpoints in a spec are the author's claim: check them against the platform's own documentation.
"""
import argparse, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = HERE / "assets" / "templates"
NAME = re.compile(r"^[A-Z][A-Za-z0-9]*(\.[A-Z][A-Za-z0-9]*)*$")
OP = re.compile(r"^[A-Z][A-Za-z0-9]*$")
PARAM = re.compile(r"^[a-z][A-Za-z0-9]*$")
ENV = re.compile(r"^[A-Z][A-Z0-9_]*$")
METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
KEYWORDS = {"abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char", "class", "const", "continue", "decimal",
            "default", "delegate", "do", "double", "else", "enum", "event", "false", "finally", "fixed", "float", "for",
            "foreach", "goto", "if", "in", "int", "interface", "internal", "is", "lock", "long", "namespace", "new", "null",
            "object", "operator", "out", "override", "params", "private", "protected", "public", "readonly", "ref", "return",
            "string", "struct", "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong", "unsafe", "using",
            "virtual", "void", "volatile", "while"}


def refuse(msg):
    sys.exit(f"refused: {msg}")


def validate(spec):
    for k in ("name", "platform", "base_url_env", "token_env", "operations"):
        if k not in spec:
            refuse(f"spec is missing {k}")
    if not NAME.match(spec["name"]):
        refuse("name must be dotted PascalCase such as Acme.Mcp.Example")
    if not re.match(r"^[A-Za-z0-9 ._-]{1,60}$", spec["platform"]):
        refuse("platform may use letters, digits, space, dot, dash and underscore")
    for k in ("base_url_env", "token_env"):
        if not ENV.match(spec[k]):
            refuse(f"{k} must be an environment variable name like EXAMPLE_API_TOKEN")
    ops = spec["operations"]
    if not isinstance(ops, list) or not 1 <= len(ops) <= 30:
        refuse("operations must be a list of 1 to 30")
    seen = set()
    for op in ops:
        n = op.get("name", "")
        if not OP.match(n) or n in seen:
            refuse(f"operation name {n!r} must be unique PascalCase")
        seen.add(n)
        if op.get("method") not in METHODS:
            refuse(f"{n}: method must be one of {sorted(METHODS)}")
        write = bool(op.get("write", False))
        if op["method"] != "GET" and not write:
            refuse(f"{n}: a {op['method']} operation must be marked write: true")
        if op["method"] == "GET" and write:
            refuse(f"{n}: a GET operation is not a write")
        path = op.get("path", "")
        if not path.startswith("/") or ".." in path or "?" in path or "#" in path or "//" in path:
            refuse(f"{n}: path must start with / and contain no .., ?, # or //")
        d = op.get("description", "")
        if not 1 <= len(d) <= 300:
            refuse(f"{n}: description must be 1 to 300 characters")
        params = op.get("params", [])
        names = set()
        for p in params:
            pn = p.get("name", "")
            if not PARAM.match(pn) or pn in KEYWORDS or pn in names:
                refuse(f"{n}: parameter name {pn!r} must be unique camelCase and not a C# keyword")
            names.add(pn)
            if p.get("in") not in ("path", "query", "body"):
                refuse(f"{n}: parameter {pn} must be in path, query or body")
        in_path = set(re.findall(r"\{([a-z][A-Za-z0-9]*)\}", path))
        declared = {p["name"] for p in params if p["in"] == "path"}
        if in_path != declared:
            refuse(f"{n}: path parameters {sorted(in_path)} do not match declared {sorted(declared)}")
        bodies = [p for p in params if p["in"] == "body"]
        if len(bodies) > 1 or (bodies and not write):
            refuse(f"{n}: at most one body parameter, and only on a write operation")


def cs(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")


def method_code(op):
    write = bool(op.get("write", False))
    params = op.get("params", [])
    ordered = sorted(params, key=lambda p: bool(p.get("optional")) or p["in"] != "path")
    sig = ", ".join(f"string {p['name']}" if not p.get("optional") and p["in"] == "path" else f"string? {p['name']} = null"
                    for p in ordered)
    path_d = ", ".join(f'["{p["name"]}"] = {p["name"]}' for p in params if p["in"] == "path")
    query_d = ", ".join(f'["{p["name"]}"] = {p["name"]}' for p in params if p["in"] == "query")
    body = next((p["name"] for p in params if p["in"] == "body"), None)
    desc = cs(op["description"]) + (" WRITE: refused unless the owner enabled writes for this run." if write else " Read-only.")
    return (f'    [McpServerTool(Name = "{op["name"]}")]\n    [Description("{desc}")]\n'
            f'    public Task<string> {op["name"]}({sig}) =>\n'
            f'        client.CallAsync("{op["method"]}", "{cs(op["path"])}", new() {{ {path_d} }}, new() {{ {query_d} }}, '
            f'{body or "null"}, {"true" if write else "false"});\n')


def generate(spec, out, tfm="net10.0", mcp_version="2.1.0"):
    validate(spec)
    if not re.match(r"^net\d+\.\d+$", tfm) or not re.match(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.]+)?$", mcp_version):
        refuse("--tfm like net10.0 and --mcp-version like 2.1.0")
    out = pathlib.Path(out)
    if out.exists():
        refuse(f"{out} already exists")
    v = {"Namespace": spec["name"], "Platform": spec["platform"], "BaseUrlEnv": spec["base_url_env"],
         "TokenEnv": spec["token_env"], "Tfm": tfm, "McpVersion": mcp_version,
         "Methods": "\n".join(method_code(o) for o in spec["operations"])}

    def render(name):
        t = (TEMPLATES / name).read_text()
        for k, val in v.items():
            t = t.replace("{{" + k + "}}", val)
        return t
    files = {f"{spec['name']}.csproj": "Server.csproj.tmpl", "Program.cs": "Program.cs.tmpl",
             "Configuration/PlatformClient.cs": "PlatformClient.cs.tmpl", "Tools/PlatformTools.cs": "PlatformTools.cs.tmpl"}
    for dest, tmpl in files.items():
        d = out / dest
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(render(tmpl))
    (out / "spec.json").write_text(json.dumps(spec, indent=2) + "\n")
    print(f"generated {spec['name']} -> {out}")


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--spec", required=True); a.add_argument("--out", required=True)
    a.add_argument("--tfm", default="net10.0"); a.add_argument("--mcp-version", default="2.1.0")
    a = a.parse_args()
    try:
        spec = json.loads(pathlib.Path(a.spec).read_text())
    except (OSError, ValueError) as e:
        refuse(f"cannot read spec: {e}")
    generate(spec, a.out, a.tfm, a.mcp_version)
