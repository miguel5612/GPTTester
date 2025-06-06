from typing import Dict
from pydantic import BaseModel, validator
import re


class ActionBase(BaseModel):
    nombre: str
    tipo: str
    codigo: str
    argumentos: Dict[str, str]

    @validator("codigo")
    def validate_code(cls, v: str):
        disallowed = ["import os", "import sys", "subprocess", "system(", "eval(", "exec("]
        for bad in disallowed:
            if bad in v:
                raise ValueError("Insecure code detected")
        return v

    @validator("argumentos")
    def validate_args(cls, v: Dict[str, str]):
        if not isinstance(v, dict):
            raise ValueError("argumentos debe ser un objeto")
        pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        for key in v.keys():
            if not pattern.match(key):
                raise ValueError("Nombre de argumento invalido")
        return v


class ActionCreate(ActionBase):
    pass


class ActionUpdate(ActionBase):
    pass


class Action(ActionBase):
    id: int

    class Config:
        orm_mode = True
