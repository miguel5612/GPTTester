from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from . import models


class ExecutionGraph:
    """Build a simple DAG based on test dependencies."""

    def __init__(self, suite: models.TestSuite, deps: List[models.TestDependency]):
        self.suite = suite
        self.deps = deps
        self.nodes: Set[int] = {t.id for t in suite.tests}
        self.adj: Dict[int, List[int]] = defaultdict(list)
        self.indegree: Dict[int, int] = {t: 0 for t in self.nodes}
        for d in deps:
            if d.type in [models.DependencyType.REQUIRES.value, models.DependencyType.DATA_DEPENDENCY.value]:
                self.adj[d.depends_on_id].append(d.test_id)
                self.indegree[d.test_id] += 1

    def topological_levels(self) -> List[List[int]]:
        """Return nodes grouped by execution level."""
        level: List[int] = [n for n in self.nodes if self.indegree[n] == 0]
        visited = set(level)
        levels: List[List[int]] = []
        while level:
            levels.append(level)
            next_level: List[int] = []
            for node in level:
                for child in self.adj.get(node, []):
                    self.indegree[child] -= 1
                    if self.indegree[child] == 0 and child not in visited:
                        visited.add(child)
                        next_level.append(child)
            level = next_level
        return levels

    def get_blocking_pairs(self) -> Set[frozenset[int]]:
        pairs = set()
        for d in self.deps:
            if d.type == models.DependencyType.BLOCKS.value:
                pairs.add(frozenset({d.test_id, d.depends_on_id}))
        return pairs


async def _run_test(test_id: int) -> bool:
    # Placeholder for real execution logic
    await asyncio.sleep(0)  # yield control
    return True


async def execute_graph(graph: ExecutionGraph, retries: int = 0) -> Dict[int, str]:
    """Execute tests respecting dependencies. Returns mapping of test_id->status."""
    results: Dict[int, str] = {}
    blocking = graph.get_blocking_pairs()
    for level in graph.topological_levels():
        pending = set(level)
        while pending:
            batch: List[int] = []
            for test in list(pending):
                if not any(frozenset({test, other}) in blocking for other in batch):
                    batch.append(test)
                    pending.remove(test)
            tasks = [asyncio.create_task(_run_test(t)) for t in batch]
            for t_id, task in zip(batch, tasks):
                success = False
                for _ in range(retries + 1):
                    try:
                        success = await task
                        break
                    except Exception:
                        if _ == retries:
                            success = False
                results[t_id] = "passed" if success else "failed"
    return results


def build_execution_graph(db: Session, suite_id: int) -> ExecutionGraph:
    suite = db.query(models.TestSuite).filter(models.TestSuite.id == suite_id).first()
    if not suite:
        raise ValueError("Suite not found")
    deps = (
        db.query(models.TestDependency)
        .filter(models.TestDependency.suite_id == suite_id)
        .all()
    )
    return ExecutionGraph(suite, deps)
