from .tasks import router as tasks_router
from .questions import router as questions_router
from .scenarios import router as scenarios_router
from .features import router as features_router

routers = [tasks_router, questions_router, scenarios_router, features_router]
