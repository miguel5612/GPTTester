import json
import os
from pathlib import Path

# Use SQLite to avoid requiring Postgres when importing the app
os.environ.setdefault("DATABASE_URL", "sqlite:///./k6.db")

from fastapi.openapi.utils import get_openapi
from backend.app.main import app
from tests.data_factory import DataFactory


def build_k6_script(base_url: str, users: list[dict[str, str]]) -> str:
    lines: list[str] = []
    lines.append("import http from 'k6/http';")
    lines.append("import { check, sleep } from 'k6';")
    lines.append("")
    lines.append("export const options = {")
    lines.append("  scenarios: {")
    lines.append("    baseline: { executor: 'constant-vus', vus: 10, duration: '1m' },")
    lines.append("    stress: { executor: 'ramping-vus', stages: [ { duration: '1m', target: 50 }, { duration: '2m', target: 200 } ] },")
    lines.append("    spike: { executor: 'ramping-arrival-rate', startRate: 0, timeUnit: '1s', stages: [ { duration: '10s', target: 100 }, { duration: '10s', target: 0 } ], preAllocatedVUs: 100 },")
    lines.append("    soak: { executor: 'constant-vus', vus: 20, duration: '5m' }")
    lines.append("  }")
    lines.append("};")
    lines.append("")
    lines.append(f"const BASE_URL = '{base_url}';")
    lines.append(f"const users = {json.dumps(users)};")
    lines.append("")
    lines.append("export default function () {")
    lines.append("  const user = users[Math.floor(Math.random() * users.length)];")
    lines.append("  const loginRes = http.post(`${BASE_URL}/token`, { username: user.username, password: user.password });")
    lines.append("  check(loginRes, { 'login ok': r => r.status === 200 });")
    lines.append("  const token = loginRes.json('access_token');")
    lines.append("  const params = { headers: { Authorization: `Bearer ${token}` } };")
    lines.append("  http.get(`${BASE_URL}/users/me`, params);")
    lines.append("  sleep(1);")
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    env = os.getenv("TEST_ENV", "dev")
    factory = DataFactory(env=env)
    base_url = factory.data.get("base_url", "http://localhost:8000")
    users = [factory.get_user(i).__dict__ for i in range(len(factory.data.get("users", [])))]
    script = build_k6_script(base_url, users)
    output_dir = Path("k6")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "script.js", "w") as f:
        f.write(script)
    print(f"K6 script generated at {output_dir}/script.js")


if __name__ == "__main__":
    # Build OpenAPI spec to ensure app loads correctly (unused but validates startup)
    get_openapi(title=app.title, version="1.0", routes=app.routes)
    main()
