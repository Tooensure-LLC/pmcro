#!/usr/bin/env python3
"""Turn an OpenAPI 3 document into the JSON spec that generate_platform_mcp.py reads.

  python openapi_to_spec.py --openapi API.json|API.yaml --name Acme.Mcp.Shop --platform "Acme Shop" \\
      --base-url-env ACME_BASE_URL --token-env ACME_TOKEN --out spec.json [--include-writes] [--tag TAG] [--max-ops 30]
By default only GET operations are kept (read-only). --include-writes also keeps POST, PUT, PATCH and DELETE, each marked write
so the generated server refuses them unless Platform__AllowWrites=true. At most 30 operations (the generator's limit): if more
match, it refuses and lists the tags so you can narrow with --tag instead of silently dropping some.
Names: operationId (or method plus path) becomes PascalCase; path and query parameters become camelCase. A request body becomes
one optional "body" JSON string parameter. Parameters in headers or cookies are skipped and counted in the output.
Output: "wrote N operations to FILE" or "refused: ..." with exit 1. The result is validated with the generator's own rules.
Not covered: auth schemes (the token env var is sent as a Bearer token), $ref resolution beyond parameters and bodies, callbacks.
The document is the author's claim about the platform; check it against the platform's own documentation.
"""
import argparse, importlib.util, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
spec_ = importlib.util.spec_from_file_location("generate_platform_mcp", HERE / "generate_platform_mcp.py")
gen = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(gen)
METHODS = ["get", "post", "put", "patch", "delete"]


def load(path):
    text = pathlib.Path(path).read_text()
    if str(path).lower().endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError:
            gen.refuse("YAML input needs PyYAML (pip install pyyaml), or convert the file to JSON")
        return yaml.safe_load(text)
    return json.loads(text)


def pascal(s):
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", s) if p]
    out = "".join(p[:1].upper() + p[1:] for p in parts)
    if not out or not out[0].isalpha():
        out = "Op" + out
    return out


def camel(s):
    p = pascal(s)
    out = p[:1].lower() + p[1:]
    return out + "Value" if out in gen.KEYWORDS else out


def resolve(doc, node):
    """Follow a local $ref (#/components/...) if present."""
    seen = 0
    while isinstance(node, dict) and "$ref" in node and seen < 5:
        ref = node["$ref"]
        if not ref.startswith("#/"):
            gen.refuse(f"only local $ref is supported, found {ref}")
        cur = doc
        for part in ref[2:].split("/"):
            cur = cur.get(part.replace("~1", "/").replace("~0", "~"), {}) if isinstance(cur, dict) else {}
        node, seen = cur, seen + 1
    return node


def convert(doc, a):
    if not isinstance(doc, dict) or not str(doc.get("openapi", "")).startswith("3"):
        gen.refuse("expected an OpenAPI 3 document (openapi: 3.x)")
    wanted = METHODS if a.include_writes else ["get"]
    ops, used, skipped = [], set(), 0
    tags = {}
    for path, item in (doc.get("paths") or {}).items():
        item = resolve(doc, item)
        shared = [resolve(doc, p) for p in item.get("parameters", [])]
        for method in wanted:
            o = item.get(method)
            if not o:
                continue
            for t in o.get("tags") or ["(untagged)"]:
                tags[t] = tags.get(t, 0) + 1
            if a.tag and a.tag not in (o.get("tags") or []):
                continue
            ops.append((path, method, o, shared))
    if len(ops) > a.max_ops:
        listing = ", ".join(f"{t} ({n})" for t, n in sorted(tags.items()))
        gen.refuse(f"{len(ops)} operations match and the limit is {a.max_ops}; narrow with --tag. Tags: {listing}")
    if not ops:
        gen.refuse("no operations matched")
    out = []
    for path, method, o, shared in ops:
        base = pascal(o.get("operationId") or f"{method}-{path}")
        name, k = base, 2
        while name in used:
            name, k = f"{base}{k}", k + 1
        used.add(name)
        params, renames = [], {}
        for raw in shared + [resolve(doc, p) for p in o.get("parameters", [])]:
            where = raw.get("in")
            if where not in ("path", "query"):
                skipped += 1
                continue
            pn = camel(raw.get("name", "param"))
            if where == "path":
                renames[raw["name"]] = pn
            if any(p["name"] == pn for p in params):
                continue
            entry = {"name": pn, "in": where}
            if where == "query" and not raw.get("required"):
                entry["optional"] = True
            params.append(entry)
        new_path = path
        for old, new in renames.items():
            new_path = new_path.replace("{" + old + "}", "{" + new + "}")
        if method != "get" and o.get("requestBody") is not None:
            params.append({"name": "body", "in": "body"})
        desc = (o.get("summary") or o.get("description") or name).strip().replace("\n", " ")[:300]
        entry = {"name": name, "method": method.upper(), "path": new_path, "description": desc, "params": params}
        if method != "get":
            entry["write"] = True
        out.append(entry)
    spec = {"name": a.name, "platform": a.platform, "base_url_env": a.base_url_env, "token_env": a.token_env, "operations": out}
    gen.validate(spec)
    return spec, skipped


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--openapi", required=True); p.add_argument("--out", required=True)
    p.add_argument("--name", required=True); p.add_argument("--platform", required=True)
    p.add_argument("--base-url-env", required=True); p.add_argument("--token-env", required=True)
    p.add_argument("--include-writes", action="store_true"); p.add_argument("--tag")
    p.add_argument("--max-ops", type=int, default=30)
    a = p.parse_args()
    try:
        doc = load(a.openapi)
    except (OSError, ValueError) as e:
        gen.refuse(f"cannot read {a.openapi}: {e}")
    spec, skipped = convert(doc, a)
    dest = pathlib.Path(a.out)
    if dest.exists():
        gen.refuse(f"{dest} already exists")
    dest.write_text(json.dumps(spec, indent=2) + "\n")
    print(f"wrote {len(spec['operations'])} operations to {dest}" + (f" ({skipped} header or cookie parameters skipped)" if skipped else ""))
