import time
import logging
import threading
from jose import jwt
from .routes import router
from . import models, deps
from datetime import datetime
from .initData import init_data
from .gateway import setup_gateway
from fastapi import FastAPI, Request
from .agent_manager import agent_manager
from .database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

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


@app.on_event("startup")
async def start_agent_manager():
    agent_manager.start()
