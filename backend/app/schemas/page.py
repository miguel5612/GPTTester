from pydantic import BaseModel
from typing import List, Optional
from .page_element import PageElement


class PageBase(BaseModel):
    name: str
    description: Optional[str] = None


class PageCreate(PageBase):
    pass


class PageUpdate(PageBase):
    pass


class Page(PageBase):
    id: int
    elements: List[PageElement] = []

    class Config:
        orm_mode = True
