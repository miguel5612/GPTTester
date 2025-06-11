import json
import os
from pathlib import Path

# use SQLite by default to avoid requiring Postgres when importing app
os.environ.setdefault("DATABASE_URL", "sqlite:///./postman.db")

from fastapi.openapi.utils import get_openapi
from backend.app.main import app


def build_example_from_schema(schema):
    if not isinstance(schema, dict):
        return None
    if "example" in schema:
        return schema["example"]
    if schema.get("type") == "object" and "properties" in schema:
        return {
            key: build_example_from_schema(value)
            for key, value in schema["properties"].items()
        }
    if schema.get("type") == "array":
        return [build_example_from_schema(schema.get("items", {}))]
    if schema.get("type") == "integer":
        return 0
    if schema.get("type") == "number":
        return 0
    if schema.get("type") == "boolean":
        return False
    return ""


def build_collection(spec):
    collection = {
        "info": {
            "name": spec.get("info", {}).get("title", "API"),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000"},
            {"key": "token", "value": ""},
        ],
        "item": [],
    }

    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            request = {
                "method": method.upper(),
                "header": [
                    {"key": "Content-Type", "value": "application/json"},
                    {"key": "Authorization", "value": "Bearer {{token}}"},
                ],
                "url": {
                    "raw": f"{{{{base_url}}}}{path}",
                    "host": ["{{base_url}}"],
                    "path": [p for p in path.strip("/").split("/") if p],
                },
            }
            if operation.get("parameters"):
                query = [p for p in operation["parameters"] if p.get("in") == "query"]
                if query:
                    request["url"]["query"] = [
                        {"key": p["name"], "value": "", "description": p.get("description", "")}
                        for p in query
                    ]
            path_params = [p for p in operation.get("parameters", []) if p.get("in") == "path"]
            if path_params:
                request["url"]["variable"] = [
                    {"key": p["name"], "value": f"<{p['name']}>"}
                    for p in path_params
                ]
            if operation.get("requestBody"):
                content = operation["requestBody"].get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    example = content["application/json"].get("example") or build_example_from_schema(schema)
                    if example is not None:
                        request["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(example, indent=2),
                        }
            collection["item"].append({"name": f"{method.upper()} {path}", "request": request, "response": []})
    return collection


def main():
    spec = get_openapi(
        title=app.title,
        version=app.version if hasattr(app, "version") else "1.0",
        routes=app.routes,
    )
    collection = build_collection(spec)
    output_dir = Path("postman")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "collection.json", "w") as f:
        json.dump(collection, f, indent=2)
    env = {
        "id": "default",
        "name": "Local",
        "values": [
            {"key": "base_url", "value": "http://localhost:8000", "enabled": True},
            {"key": "token", "value": "", "enabled": True},
        ],
    }
    with open(output_dir / "environment.json", "w") as f:
        json.dump(env, f, indent=2)
    print(f"Postman collection generated at {output_dir}/collection.json")


if __name__ == "__main__":
    main()
