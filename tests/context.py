import os
from dataclasses import dataclass


@dataclass
class Context:
    env: str
    base_url: str


def load_context() -> Context:
    env = os.getenv("TEST_ENV", "dev")
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    return Context(env=env, base_url=base_url)
