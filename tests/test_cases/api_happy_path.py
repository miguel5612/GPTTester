from __future__ import annotations

from .base import BaseHappyPath


class ApiHappyPath(BaseHappyPath):
    """API channel variant of the happy path."""

    def run(self) -> bool:
        user = self.factory.get_user()
        print(f"[API] Authenticate {user.username} against {self.context.base_url}")
        return True
