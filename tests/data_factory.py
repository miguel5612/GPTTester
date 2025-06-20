import json
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

    def get_user(self, index: int = 0) -> UserData:
        user = self.data.get("users", [])[index]
        return UserData(**user)
