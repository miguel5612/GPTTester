import os
import json
from typing import Any, Dict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from backend.app.main import app

spec = app.openapi()

schemas = spec.get("components", {}).get("schemas", {})

def resolve_ref(ref: str) -> Dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    parts = ref.lstrip("#/" ).split("/")
    obj: Any = spec
    for p in parts:
        obj = obj.get(p, {})
    return obj

def example_from_schema(schema: Dict[str, Any]) -> Any:
    if "$ref" in schema:
        schema = resolve_ref(schema["$ref"])
    if not isinstance(schema, dict):
        return None
    if "example" in schema:
        return schema["example"]
    if "default" in schema:
        return schema["default"]
    t = schema.get("type")
    if t == "object":
        props = schema.get("properties", {})
        return {k: example_from_schema(v) for k, v in props.items()}
    if t == "array":
        return [example_from_schema(schema.get("items", {}))]
    if t == "integer" or t == "number":
        return 0
    if t == "boolean":
        return True
    return ""

collection = {
    "info": {
        "name": spec.get("title", "API"),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "item": [],
    "variable": [
        {"key": "base_url", "value": "http://localhost:8000"},
        {"key": "token", "value": ""},
    ],
}

for path, methods in spec.get("paths", {}).items():
    for method, op in methods.items():
        name = op.get("operationId", f"{method} {path}")
        url = {
            "raw": f"{{{{base_url}}}}{path}",
            "host": ["{{base_url}}"],
            "path": path.strip("/").split("/") if path != "/" else [],
        }
        request = {"method": method.upper(), "url": url, "header": []}
        if path != "/token":
            request["header"].append({"key": "Authorization", "value": "Bearer {{token}}"})
        if "requestBody" in op:
            content = op["requestBody"].get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                example = example_from_schema(schema)
                request["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(example, indent=2),
                    "options": {"raw": {"language": "json"}},
                }
        item = {"name": name, "request": request}
        collection["item"].append(item)

with open(os.path.join("postman", "GPTTester.postman_collection.json"), "w") as f:
    json.dump(collection, f, indent=2)

with open(os.path.join("postman", "GPTTester.environment.json"), "w") as f:
    json.dump({"name": "GPTTester", "values": [{"key": "base_url", "value": "http://localhost:8000"}, {"key": "token", "value": "", "type": "default"}]}, f, indent=2)
