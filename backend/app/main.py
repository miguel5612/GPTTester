from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .rate_limiter import limiter

from .database import Base, engine
from .routers import (
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
    assignments,
    agents,
    execution_plans,
    executions,
)
from .init_db import init_db

Base.metadata.create_all(bind=engine)
init_db()

app = FastAPI(title="GPTTester Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tests.router)
app.include_router(roles.router)
app.include_router(clients.router)
app.include_router(projects.router)
app.include_router(testplans.router)
app.include_router(pages.router)
app.include_router(scenarios.router)
app.include_router(actions.router)
app.include_router(assignments.router)
app.include_router(agents.router)
app.include_router(execution_plans.router)
app.include_router(executions.router)
