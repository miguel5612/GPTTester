from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum


class OSType(str, Enum):
    Windows = "Windows"
    Linux = "Linux"
    Mac = "Mac"
    Android = "Android"
    iOS = "iOS"


class AgentBase(BaseModel):
    alias: str
    hostname: str
    sistema_operativo: OSType
    categoria: Optional[str] = None

    @validator("categoria")
    def check_categoria(cls, v, values):
        if v is None:
            return v
        if v != "granja móvil":
            raise ValueError("categoria invalida")
        so = values.get("sistema_operativo")
        if so not in (OSType.Android, OSType.iOS):
            raise ValueError("categoria solo permitida para Android/iOS")
        return v


class AgentCreate(AgentBase):
    pass


class AgentUpdate(AgentBase):
    pass


class Agent(AgentBase):
    id: int

    class Config:
        orm_mode = True
