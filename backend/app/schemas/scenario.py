from pydantic import BaseModel
from typing import List


class ScenarioBase(BaseModel):
    name: str


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(ScenarioBase):
    pass


class Scenario(ScenarioBase):
    id: int

    class Config:
        orm_mode = True
