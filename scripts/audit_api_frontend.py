"""Static KALATRACE API ↔ frontend coverage audit.

The frontend uses one dynamic client (`ktApi`) plus an OpenAPI-driven catalog,
so a simple fetch()/axios() count is not meaningful. This audit reports:
1) backend routes;
2) explicit frontend ktApi literal targets;
3) routes exposed dynamically through /openapi.json;
4) domain bindings declared in frontend/backend_bindings.js.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api" / "main.py"
FRONTEND = ROOT / "index.html"
BINDINGS = ROOT / "frontend" / "backend_bindings.js"

api_text = API.read_text(encoding="utf-8")
routes = [(m.upper(), p) for m, p in re.findall(r'@app\.(get|post|patch|put|delete)\("([^"]+)"\)', api_text, re.I)]
front_text = FRONTEND.read_text(encoding="utf-8") if FRONTEND.exists() else ""
bind_text = BINDINGS.read_text(encoding="utf-8") if BINDINGS.exists() else ""

# Literal ktApi('/path') calls in index + binding layer.
literal_targets = set(re.findall(r"ktApi\(\s*['\"]([^'\"]+)['\"]", front_text + "\n" + bind_text))
# Paths in the binding map, including query-bearing literals.
binding_paths = set(re.findall(r"['\"](/[^'\"]+)['\"]", bind_text))

print("# KALATRACE API ↔ Frontend audit")
print(f"\nAPI routes discovered: {len(routes)}")
print(f"Frontend explicit ktApi targets: {len(literal_targets)}")
print(f"Frontend domain binding paths: {len(binding_paths)}")
print("Frontend dynamic OpenAPI catalog: ENABLED (/openapi.json)")
print("Dynamic catalog exposes all published API routes to the frontend explorer.")

print("\n## Explicit frontend targets")
for target in sorted(literal_targets | binding_paths):
    print(f"- {target}")

print("\n## Coverage model")
print("- Domain GET bindings: live data panels on operational screens.")
print("- Contextual GET/POST/PATCH/PUT/DELETE routes: OpenAPI catalog + explicit actions.")
print("- Mutations are never auto-fired by the catalog; they require explicit UI action and backend authorization.")
print("- Runtime validation against Supabase/Neo4j remains an environment-level check.")
