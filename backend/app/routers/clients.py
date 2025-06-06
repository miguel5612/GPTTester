from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import client as crud_client
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=schemas.client.Client, status_code=201)
def create_client(
    client: schemas.client.ClientCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    return crud_client.create_client(db, client)


@router.get("/", response_model=List[schemas.client.Client])
def read_clients(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_client.get_clients(db)


@router.get("/{client_id}", response_model=schemas.client.Client)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    client = crud_client.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=schemas.client.Client)
def update_client(
    client_id: int,
    client: schemas.client.ClientUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_client = crud_client.update_client(db, client_id, client)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client
