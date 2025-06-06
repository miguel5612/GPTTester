from sqlalchemy.orm import Session
from .. import models, schemas


def get_clients(db: Session):
    return db.query(models.Client).all()


def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def create_client(db: Session, client: schemas.client.ClientCreate):
    db_client = models.Client(name=client.name, is_active=client.is_active)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: int, client: schemas.client.ClientUpdate):
    db_client = get_client(db, client_id)
    if db_client:
        db_client.name = client.name
        db_client.is_active = client.is_active
        db.commit()
        db.refresh(db_client)
    return db_client
