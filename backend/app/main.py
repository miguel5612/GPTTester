from fastapi import FastAPI
from . import models, deps
from .database import engine, SessionLocal
from .routes import router
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)


def init_data():
    db = SessionLocal()
    try:
        predefined = [
            "Administrador",
            "Arquitecto de Automatización",
            "Automation Engineer",
            "Automatizador de Pruebas",
            "Analista de Pruebas con skill de automatización"            
        ]
        for name in predefined:
            if not db.query(models.Role).filter(models.Role.name == name).first():
                db.add(models.Role(name=name))
        db.commit()

        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin_role = db.query(models.Role).filter(models.Role.name == "Administrador").first()
            hashed = deps.get_password_hash("admin")
            admin = models.User(username="admin", hashed_password=hashed, role=admin_role)
            db.add(admin)
            db.commit()
    finally:
        db.close()


init_data()

app = FastAPI(title="Test Automation API")
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ['http://localhost:4200'] para mayor seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)