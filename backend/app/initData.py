from database import SessionLocal
import models
import deps


def init_data():
    db = SessionLocal()
    try:
        #Roles
        predefinedRoles = [
            "Administrador",
            "Automation Engineer",
            "Gerente de servicios",
            "Analista de Performance",
            "Automatizador de Pruebas",
            "Arquitecto de Automatización",
            "Analista de Pruebas con skill de automatización",
        ]
        for name in predefinedRoles:
            if not db.query(models.Role).filter(models.Role.name == name).first():
                db.add(models.Role(name=name))
        db.commit()
        #Paginas
        predefinedPages = [
            ['/dashboard',1,1,'Dashboard de resultados'],
            ['/dashboard',2,1,'Dashboard de resultados'],
            ['/clients',3,1,'Dashboard de resultados'],
            ['/clients',4,1,'Dashboard de resultados'],
            ['/clients',5,1,'Dashboard de resultados'],
            ['/interactions',6,1,'Dashboard de resultados'],
            ['/clients',7,1,'Dashboard de resultados'],
        ]
        for page in predefinedPages:
            if not db.query(models.PagePermission).filter(
                (models.PagePermission.page == page[1]) & 
                (models.PagePermission.role_id == page[2])
            ).first():
                db.add(models.PagePermission(
                    page =  page[1],
                    role_id =  page[2],
                    isStartPage =  page[3],
                    description =  page[4],
                ))
        db.commit()
        #Usuario admin
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin_role = (
                db.query(models.Role)
                .filter(models.Role.name == "Administrador")
                .first()
            )
            hashed = deps.get_password_hash("admin")
            admin = models.User(
                username="admin", password=hashed, role=admin_role
            )
            db.add(admin)
            db.commit()

        # Usuarios requeridos para controlar el sistema
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
