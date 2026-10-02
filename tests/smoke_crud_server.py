"""Smoke test for a scaffolded generic CRUD API: create, list, get, update, delete, and 404s. Usage: smoke_crud_server.py BASE_URL ROUTE."""
import json, sys, urllib.error, urllib.request


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        return e.code, None


base, route = sys.argv[1].rstrip("/"), sys.argv[2]
url = f"{base}/api/{route}"
s, created = call("POST", url, {"name": "Ada", "email": "ada@example.test", "age": 36})
assert s == 201 and created["id"], (s, created)
uid = created["id"]
assert len(uid) == 36
s, rows = call("GET", url); assert s == 200 and any(r["id"] == uid for r in rows), (s, rows)
s, one = call("GET", f"{url}/{uid}"); assert s == 200 and one["name"] == "Ada", (s, one)
s, _ = call("PUT", f"{url}/{uid}", {"name": "Ada L", "email": "ada@example.test", "age": 37}); assert s == 204, s
s, one = call("GET", f"{url}/{uid}"); assert one["name"] == "Ada L", one
s, _ = call("DELETE", f"{url}/{uid}"); assert s == 204, s
s, _ = call("GET", f"{url}/{uid}"); assert s == 404, s
s, _ = call("DELETE", f"{url}/{uid}"); assert s == 404, s
s, _ = call("PUT", f"{url}/{uid}", {"name": "x"}); assert s == 404, s
print("crud smoke ok")
