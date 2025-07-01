"""
Main mejorado con la nueva estructura de API
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from . import models
from .database import engine
from .api import api_router
from .agent_manager import agent_manager
import threading
import time
import logging
from datetime import datetime
from .database import SessionLocal

# Crear tablas
models.Base.metadata.create_all(bind=engine)


def init_default_data():
    """Inicializar datos por defecto del sistema"""
    db = SessionLocal()
    try:
        # Crear roles predefinidos
        predefined_roles = [
            "Administrador",
            "Arquitecto de Automatización", 
            "Gerente de servicios",
            "Analista de Pruebas con skill de automatización",
            "Automatizador de Pruebas",
            "Automation Engineer"
        ]
        
        for role_name in predefined_roles:
            if not db.query(models.Role).filter(models.Role.name == role_name).first():
                db.add(models.Role(name=role_name))
        
        db.commit()
        
        # Crear usuario admin por defecto
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin_role = db.query(models.Role).filter(
                models.Role.name == "Administrador"
            ).first()
            
            from .deps import get_password_hash
            hashed = get_password_hash("admin123")
            
            admin = models.User(
                username="admin",
                hashed_password=hashed,
                role_id=admin_role.id,
                is_active=True
            )
            db.add(admin)
            db.commit()
            
        # Crear acciones básicas si no existen
        basic_actions = [
            {"name": "click", "tipo": "interaction", "codigo": "element.click()"},
            {"name": "type", "tipo": "input", "codigo": "element.sendKeys(value)", "argumentos": "value"},
            {"name": "clear", "tipo": "input", "codigo": "element.clear()"},
            {"name": "select", "tipo": "select", "codigo": "Select(element).selectByVisibleText(value)", "argumentos": "value"},
            {"name": "wait", "tipo": "wait", "codigo": "WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element))", "argumentos": "timeout"},
            {"name": "verify_text", "tipo": "assertion", "codigo": "assert element.text == expected", "argumentos": "expected"},
            {"name": "navigate", "tipo": "navigation", "codigo": "driver.get(url)", "argumentos": "url"},
            {"name": "screenshot", "tipo": "utility", "codigo": "driver.save_screenshot(filename)", "argumentos": "filename"}
        ]
        
        for action_data in basic_actions:
            if not db.query(models.AutomationAction).filter(
                models.AutomationAction.name == action_data["name"]
            ).first():
                db.add(models.AutomationAction(**action_data))
        
        db.commit()
        
    finally:
        db.close()


# Inicializar datos
init_default_data()

# Crear aplicación
app = FastAPI(
    title="GPT Tester API",
    description="API para automatización de pruebas con enfoque en experiencia de usuario",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router)

# Mantener compatibilidad con endpoints antiguos críticos
from .routes import router as legacy_router
app.include_router(legacy_router, prefix="/legacy", tags=["Legacy"])


# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log solo para endpoints de API
    if request.url.path.startswith("/api/"):
        logger = logging.getLogger("api")
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
    
    return response


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger = logging.getLogger("error")
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "type": type(exc).__name__
        }
    )


# Scheduler para ejecuciones programadas
def schedule_worker():
    """Worker para ejecutar pruebas programadas"""
    while True:
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            schedules = (
                db.query(models.ExecutionSchedule)
                .filter(
                    models.ExecutionSchedule.run_at <= now,
                    models.ExecutionSchedule.executed == False,
                )
                .all()
            )
            
            for schedule in schedules:
                selected_agent = schedule.agent_id or schedule.plan.agent_id
                record = models.PlanExecution(
                    plan_id=schedule.plan_id,
                    agent_id=selected_agent,
                    status=models.ExecutionStatus.CALLING.value,
                )
                db.add(record)
                schedule.executed = True
                
            if schedules:
                db.commit()
                
        except Exception as e:
            db.rollback()
            logger = logging.getLogger("scheduler")
            logger.error(f"Scheduler error: {e}")
        finally:
            db.close()
            
        time.sleep(30)  # Revisar cada 30 segundos


def start_scheduler():
    """Iniciar el scheduler en un thread separado"""
    thread = threading.Thread(target=schedule_worker, daemon=True)
    thread.start()


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Iniciar servicios
start_scheduler()


@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    agent_manager.start()
    logger = logging.getLogger("startup")
    logger.info("GPT Tester API iniciada correctamente")


@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    logger = logging.getLogger("shutdown")
    logger.info("Cerrando GPT Tester API...")


# Endpoint de salud
@app.get("/health")
async def health_check():
    """Verificar el estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


# Página de inicio con información útil
@app.get("/")
async def root():
    """Información básica de la API"""
    return {
        "message": "Bienvenido a GPT Tester API v2.0",
        "docs": "/api/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/api/auth",
            "workspace": "/api/workspace", 
            "flows": "/api/flows",
            "execution": "/api/execution"
        }
    }
