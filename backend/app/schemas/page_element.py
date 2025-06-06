from pydantic import BaseModel
from typing import List, Optional
from .scenario import Scenario


class PageElementBase(BaseModel):
    name: str
    tipo: str
    estrategia: str
    valor: str
    descripcion: Optional[str] = None


class PageElementCreate(PageElementBase):
    pass


class PageElementUpdate(PageElementBase):
    pass


class PageElement(PageElementBase):
    id: int
    page_id: int
    scenarios: List[Scenario] = []

    class Config:
        orm_mode = True
