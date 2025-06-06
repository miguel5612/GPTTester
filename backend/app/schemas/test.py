from pydantic import BaseModel
from typing import Optional


class TestBase(BaseModel):
    name: str
    description: Optional[str] = None


class TestCreate(TestBase):
    pass


class Test(TestBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
