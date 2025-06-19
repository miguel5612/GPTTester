from fastapi import FastAPI, Request
from . import models, deps
from .gateway import setup_gateway
from .database import engine, SessionLocal
from .routes import router
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from datetime import datetime
import threading
import time
import logging

models.Base.metadata.create_all(bind=engine)


def init_data():
    db = SessionLocal()
    try:
        predefined = [
            "Administrador",
            "Arquitecto de Automatización",
            "Automation Engineer",
            "Automatizador de Pruebas",
            "Analista de Pruebas con skill de automatización",
            "Gerente de servicios",
        ]
        for name in predefined:
            if not db.query(models.Role).filter(models.Role.name == name).first():
                db.add(models.Role(name=name))
        db.commit()

        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin_role = (
                db.query(models.Role)
                .filter(models.Role.name == "Administrador")
                .first()
            )
            hashed = deps.get_password_hash("admin")
            admin = models.User(
                username="admin", hashed_password=hashed, role=admin_role
            )
            db.add(admin)
            db.commit()

        # create additional default users if they do not exist
        defaults = {
            "architect": "Arquitecto de Automatización",
            "service_manager": "Gerente de servicios",
            "test_automator": "Automatizador de Pruebas",
        }
        for username, role_name in defaults.items():
            if not db.query(models.User).filter(models.User.username == username).first():
                role = db.query(models.Role).filter(models.Role.name == role_name).first()
                if role:
                    hashed = deps.get_password_hash(username)
                    user = models.User(username=username, hashed_password=hashed, role=role)
                    db.add(user)
        db.commit()
    finally:
        db.close()


init_data()

app = FastAPI(title="Test Automation API")
setup_gateway(app)
logger = logging.getLogger("audit")
logging.basicConfig(level=logging.INFO)


def schedule_worker():
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
            for sch in schedules:
                selected_agent = sch.agent_id or sch.plan.agent_id
                record = models.PlanExecution(
                    plan_id=sch.plan_id,
                    agent_id=selected_agent,
                    status=models.ExecutionStatus.CALLING.value,
                )
                db.add(record)
                sch.executed = True
            if schedules:
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Scheduler error: {e}")
        finally:
            db.close()
        time.sleep(10)


def start_scheduler():
    thread = threading.Thread(target=schedule_worker, daemon=True)
    thread.start()

app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ['http://localhost:4200'] para mayor seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_scheduler()
