from __future__ import annotations

from .base import BaseHappyPath


class WebHappyPath(BaseHappyPath):
    """Web channel variant of the happy path."""

    def run(self) -> bool:
        user = self.factory.get_user()
        # Placeholder for real web automation logic
        print(f"[WEB] Login {user.username} at {self.context.base_url}")
        return True
