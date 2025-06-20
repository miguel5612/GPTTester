import json
import random
import time
from pathlib import Path
from typing import Any

from .data_objects import UserData


class DataFactory:
    """Load test data from environment-specific pools."""

    def __init__(self, env: str = "dev") -> None:
        self.env = env
        path = Path(__file__).parent / "pools" / f"{env}.json"
        if not path.exists():
            raise FileNotFoundError(f"Data pool not found: {path}")
        with path.open() as f:
            self.data: dict[str, Any] = json.load(f)

    def _resolve(self, value: str) -> str:
        if "{{timestamp}}" in value:
            value = value.replace("{{timestamp}}", str(int(time.time())))
        if "{{random}}" in value:
            value = value.replace("{{random}}", str(random.randint(1000, 9999)))
        return value

    def get_user(self, index: int = 0) -> UserData:
        user = self.data.get("users", [])[index]
        user = {k: self._resolve(v) if isinstance(v, str) else v for k, v in user.items()}
        return UserData(**user)
