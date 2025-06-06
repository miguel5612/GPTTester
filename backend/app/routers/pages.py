from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import schemas
from ..crud import page as crud_page
from ..crud import page_element as crud_element
from ..crud import scenario as crud_scenario
from ..utils import get_current_user, require_role

router = APIRouter(prefix="/pages", tags=["pages"])


@router.post("/", response_model=schemas.page.Page, status_code=201)
def create_page(
    page: schemas.page.PageCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_page = crud_page.create_page(db, page)
    if not db_page:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_page


@router.get("/", response_model=List[schemas.page.Page])
def read_pages(
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_page.get_pages(db)


@router.get("/{page_id}", response_model=schemas.page.Page)
def read_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    page = crud_page.get_page(db, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.put("/{page_id}", response_model=schemas.page.Page)
def update_page(
    page_id: int,
    page: schemas.page.PageUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_page = crud_page.update_page(db, page_id, page)
    if not db_page:
        raise HTTPException(status_code=404, detail="Page not found or duplicate")
    return db_page


@router.delete("/{page_id}", response_model=schemas.page.Page)
def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_page = crud_page.delete_page(db, page_id)
    if not db_page:
        raise HTTPException(status_code=404, detail="Page not found")
    return db_page


@router.post("/{page_id}/elements", response_model=schemas.page_element.PageElement, status_code=201)
def create_element(
    page_id: int,
    element: schemas.page_element.PageElementCreate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_element = crud_element.create_element(db, page_id, element)
    if not db_element:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_element


@router.get("/{page_id}/elements", response_model=List[schemas.page_element.PageElement])
def read_elements(
    page_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    return crud_element.get_elements(db, page_id)


@router.get("/{page_id}/elements/{element_id}", response_model=schemas.page_element.PageElement)
def read_element(
    page_id: int,
    element_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(get_current_user),
):
    element = crud_element.get_element(db, element_id)
    if not element or element.page_id != page_id:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.put("/{page_id}/elements/{element_id}", response_model=schemas.page_element.PageElement)
def update_element(
    page_id: int,
    element_id: int,
    element: schemas.page_element.PageElementUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_element = crud_element.get_element(db, element_id)
    if not db_element or db_element.page_id != page_id:
        raise HTTPException(status_code=404, detail="Element not found")
    db_element = crud_element.update_element(db, element_id, element)
    if not db_element:
        raise HTTPException(status_code=400, detail="Integrity error")
    return db_element


@router.delete("/{page_id}/elements/{element_id}", response_model=schemas.page_element.PageElement)
def delete_element(
    page_id: int,
    element_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    db_element = crud_element.get_element(db, element_id)
    if not db_element or db_element.page_id != page_id:
        raise HTTPException(status_code=404, detail="Element not found")
    return crud_element.delete_element(db, element_id)


@router.post("/elements/{element_id}/scenarios/{scenario_id}", response_model=schemas.page_element.PageElement)
def add_element_to_scenario(
    element_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    element = crud_element.get_element(db, element_id)
    scenario = crud_scenario.get_scenario(db, scenario_id)
    if not element or not scenario:
        raise HTTPException(status_code=404, detail="Element or Scenario not found")
    return crud_element.add_element_to_scenario(db, element, scenario)


@router.delete("/elements/{element_id}/scenarios/{scenario_id}", response_model=schemas.page_element.PageElement)
def remove_element_from_scenario(
    element_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.user.User = Depends(require_role("Administrador")),
):
    element = crud_element.get_element(db, element_id)
    scenario = crud_scenario.get_scenario(db, scenario_id)
    if not element or not scenario:
        raise HTTPException(status_code=404, detail="Element or Scenario not found")
    return crud_element.remove_element_from_scenario(db, element, scenario)
