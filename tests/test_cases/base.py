from __future__ import annotations

from ..context import Context
from ..data_factory import DataFactory


class BaseHappyPath:
    """Base happy path for all channels."""

    def __init__(self, factory: DataFactory, context: Context) -> None:
        self.factory = factory
        self.context = context

    def run(self) -> bool:
        raise NotImplementedError
