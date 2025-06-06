"""Expose router modules for easy inclusion in :mod:`main`.

This module re-exports the routers modules so that ``main`` can simply import
``from .routers import users, tests, ...``.  Each module also exposes a
``router`` object which is what FastAPI uses to register the routes.
"""

from . import (
    auth,
    users,
    tests,
    roles,
    clients,
    projects,
    testplans,
    pages,
    scenarios,
    actions,
    action_assignments as assignments,
    agents,
    execution_plans,
    executions,
)

auth_router = auth.router
users_router = users.router
tests_router = tests.router
roles_router = roles.router
clients_router = clients.router
projects_router = projects.router
testplans_router = testplans.router
pages_router = pages.router
scenarios_router = scenarios.router
actions_router = actions.router
assignments_router = assignments.router
agents_router = agents.router
execution_plans_router = execution_plans.router
executions_router = executions.router

__all__ = [
    "auth",
    "users",
    "tests",
    "roles",
    "clients",
    "projects",
    "testplans",
    "pages",
    "scenarios",
    "actions",
    "assignments",
    "agents",
    "execution_plans",
    "executions",
    "auth_router",
    "users_router",
    "tests_router",
    "roles_router",
    "clients_router",
    "projects_router",
    "testplans_router",
    "pages_router",
    "scenarios_router",
    "actions_router",
    "assignments_router",
    "agents_router",
    "execution_plans_router",
    "executions_router",
]
