"""
Router principal de la API mejorada
"""
from fastapi import APIRouter

from .auth.router import router as auth_router
from .workspace.router import router as workspace_router
from .flows.router import router as flows_router
from .execution.router import router as execution_router

# Importar routers adicionales cuando estén listos
# from .admin.router import router as admin_router
# from .service_manager.router import router as service_manager_router

api_router = APIRouter()

# Incluir todos los routers
api_router.include_router(auth_router)
api_router.include_router(workspace_router)
api_router.include_router(flows_router)
api_router.include_router(execution_router)

# Incluir routers adicionales cuando estén listos
# api_router.include_router(admin_router)
# api_router.include_router(service_manager_router)
