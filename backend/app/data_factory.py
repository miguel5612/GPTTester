import csv
import json
import random
import time
from pathlib import Path
from sqlalchemy.orm import Session

from . import models


class DataFactory:
    """Utility to generate or import data objects."""

    def __init__(self, db: Session):
        self.db = db

    def _get_pool(self, type_: str, env: str) -> models.DataPool:
        pool = (
            self.db.query(models.DataPool)
            .filter(models.DataPool.type == type_, models.DataPool.environment == env)
            .first()
        )
        if not pool:
            pool = models.DataPool(type=type_, environment=env)
            self.db.add(pool)
            self.db.commit()
            self.db.refresh(pool)
        return pool

    def import_csv(self, csv_path: Path, type_: str, env: str) -> None:
        pool = self._get_pool(type_, env)
        with csv_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                obj = models.TestDataObject(
                    pool_id=pool.id,
                    data=json.dumps(row),
                    state=models.DataState.NEW.value,
                )
                self.db.add(obj)
        self.db.commit()

    def generate(self, type_: str, env: str, rules: dict[str, str], count: int = 1) -> None:
        pool = self._get_pool(type_, env)
        for _ in range(count):
            data = {k: self._resolve_rule(v) for k, v in rules.items()}
            obj = models.TestDataObject(
                pool_id=pool.id,
                data=json.dumps(data),
                state=models.DataState.NEW.value,
            )
            self.db.add(obj)
        self.db.commit()

    def _resolve_rule(self, rule: str) -> str:
        if rule == "{{timestamp}}":
            return str(int(time.time()))
        if rule == "{{random}}":
            return str(random.randint(1000, 9999))
        return rule
