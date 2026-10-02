#!/usr/bin/env python3
"""Scaffold the owner's generic CRUD design for .NET: BaseEntity, generic repository, unit of work, generic controller.

  python scaffold_crud.py --out DIR --namespace Acme.Shop --entity User:Name=string,Email=string [--entity Order:Total=decimal]
Writes a Web API project (net10.0, EF Core, OpenAPI + Scalar). The base files (BaseEntity with Id = Guid.NewGuid(), IGenericRepository<T>,
IUnitOfWork, GenericRepository<T>, GenericController<T>, DI wiring) are written once; each --entity adds a model, an empty I{Name}Repository,
an empty {Name}Repository and a one-line {Name}sController. Run again with the same --out to add models; existing files are never overwritten.
Refuses: bad identifiers, property types outside the allowed list, a file that already exists. Output: "wrote N files" or "refused: ...".
Not built here (no .NET SDK in this session); this repository's CI compiles and exercises the default output.
"""
import argparse, pathlib, re, sys

T = pathlib.Path(__file__).resolve().parent.parent / "assets" / "templates" / "crud"
IDENT = re.compile(r"^[A-Z][A-Za-z0-9]*$")
NS = re.compile(r"^[A-Z][A-Za-z0-9]*(\.[A-Z][A-Za-z0-9]*)*$")
TYPES = {"string", "int", "long", "decimal", "double", "bool", "DateTime", "Guid"}
BASE = [("App.csproj.tmpl", "{ns}.csproj"), ("Program.cs.tmpl", "Program.cs"), ("Domain/BaseEntity.cs.tmpl", "Domain/BaseEntity.cs"),
        ("Application/IGenericRepository.cs.tmpl", "Application/IGenericRepository.cs"),
        ("Application/IUnitOfWork.cs.tmpl", "Application/IUnitOfWork.cs"),
        ("Infrastructure/AppDbContext.cs.tmpl", "Infrastructure/AppDbContext.cs"),
        ("Infrastructure/GenericRepository.cs.tmpl", "Infrastructure/GenericRepository.cs"),
        ("Infrastructure/UnitOfWork.cs.tmpl", "Infrastructure/UnitOfWork.cs"),
        ("Infrastructure/DependencyInjection.cs.tmpl", "Infrastructure/DependencyInjection.cs"),
        ("Api/GenericController.cs.tmpl", "Api/GenericController.cs")]
PER_ENTITY = [("Domain/Entity.cs.tmpl", "Domain/{e}.cs"), ("Application/IEntityRepository.cs.tmpl", "Application/I{e}Repository.cs"),
              ("Infrastructure/EntityRepository.cs.tmpl", "Infrastructure/{e}Repository.cs"),
              ("Api/Controllers/EntityController.cs.tmpl", "Api/Controllers/{e}sController.cs")]


def parse_entity(spec):
    name, _, props = spec.partition(":")
    if not IDENT.match(name):
        sys.exit(f"refused: entity name {name!r} must be PascalCase")
    out = []
    for p in filter(None, props.split(",")):
        pname, _, ptype = p.partition("=")
        base = ptype.rstrip("?")
        if not IDENT.match(pname) or pname == "Id" or base not in TYPES:
            sys.exit(f"refused: property {p!r} (name PascalCase, not Id; type one of {sorted(TYPES)}, optional ?)")
        out.append((pname, ptype))
    return name, out


def render(tmpl, values):
    text = (T / tmpl).read_text()
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def scaffold(out, ns, entities, tfm="net10.0"):
    if not NS.match(ns):
        sys.exit("refused: --namespace must be dotted PascalCase such as Acme.Shop")
    out = pathlib.Path(out)
    plan = []
    for tmpl, dest in BASE:
        d = out / dest.format(ns=ns)
        if not d.exists():
            plan.append((d, render(tmpl, {"Namespace": ns, "Tfm": tfm})))
    for spec in entities:
        e, props = parse_entity(spec)
        body = "".join(f"    public {t} {n} {{ get; set; }}{' = string.Empty;' if t == 'string' else ''}\n" for n, t in props)
        for tmpl, dest in PER_ENTITY:
            d = out / dest.format(e=e)
            if d.exists():
                sys.exit(f"refused: {d} already exists")
            plan.append((d, render(tmpl, {"Namespace": ns, "Entity": e, "Props": body})))
    for d, text in plan:
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(text)
    print(f"wrote {len(plan)} files into {out}")


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("--out", required=True)
    a.add_argument("--namespace", required=True)
    a.add_argument("--entity", action="append", default=[])
    a.add_argument("--tfm", default="net10.0")
    a = a.parse_args()
    scaffold(a.out, a.namespace, a.entity, a.tfm)
