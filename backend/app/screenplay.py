from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from sqlalchemy.orm import Session
from fastapi import HTTPException

from . import models


class Ability:
    """Base ability type."""


class Browser(Ability):
    """Ability to interact with web pages via Selenium."""


class API(Ability):
    """Ability to send HTTP requests using requests library."""


class Mobile(Ability):
    """Ability to drive mobile apps with Appium."""


@dataclass
class Actor:
    """Actor executing tasks with abilities and shared context."""

    name: str
    abilities: Dict[str, Ability] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    def ability(self, name: str) -> Ability | None:
        return self.abilities.get(name)


@dataclass
class Task:
    """Group multiple actions under a single name."""

    name: str
    actions: List[Callable[[Actor], Any]]

    def perform_as(self, actor: Actor) -> None:
        for action in self.actions:
            action(actor)


@dataclass
class Question:
    """Verification step answered by an actor."""

    name: str
    resolver: Callable[[Actor], Any]

    def answered_by(self, actor: Actor) -> Any:
        return self.resolver(actor)


def _render_action_code(code: str, params: dict[str, Any]) -> str:
    """Replace variables in action code using params."""

    try:
        return code.format(**params)
    except Exception:
        return code


def compile_test(db: Session, test_id: int) -> str:
    """Create a Screenplay script for the given test."""

    test = db.query(models.TestCase).filter(models.TestCase.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    assignments = (
        db.query(models.ActionAssignment)
        .filter(models.ActionAssignment.test_id == test_id)
        .all()
    )

    actor_name = test.actor.name if test.actor else "Actor"
    lines = [
        "# Auto-generated Screenplay script",
        "from screenplay import Actor, Browser, API, Mobile",
        "",
        f"actor = Actor('{actor_name}', abilities={{'Browser': Browser(), 'API': API(), 'Mobile': Mobile()}})",
        "",
    ]

    if test.given:
        lines.append(f"# Given: {test.given}")
    if test.when:
        lines.append(f"# When: {test.when}")
    if test.then:
        lines.append(f"# Then: {test.then}")

    for assign in assignments:
        params = json.loads(assign.parametros or "{}")
        code = _render_action_code(assign.action.codigo, params)
        lines.append("")
        lines.append(f"# {assign.action.name} -> {assign.element.name}")
        lines.append(code)

    return "\n".join(lines)


def generate_executable_script(script: str) -> str:
    """Wrap screenplay script with required imports for execution."""

    header = [
        "from selenium import webdriver",
        "import requests",
        "from appium import webdriver as appium_webdriver",
        "",
    ]
    return "\n".join(header + [script])
