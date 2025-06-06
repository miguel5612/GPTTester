from pydantic import BaseModel, validator
from datetime import date
from typing import Optional


class TestPlanBase(BaseModel):
    nombre: str
    objetivo: Optional[str] = None
    alcance: Optional[str] = None
    criterios_entrada: Optional[str] = None
    criterios_salida: Optional[str] = None
    estrategia_pruebas: Optional[str] = None
    responsables: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    bdd_stories: Optional[str] = None

    @validator("nombre")
    def validate_nombre(cls, v):
        if len(v) < 5:
            raise ValueError("nombre must be at least 5 characters")
        return v

    @validator("fecha_fin")
    def validate_fechas(cls, v, values):
        start = values.get("fecha_inicio")
        if start and v and v < start:
            raise ValueError("fecha_fin must be after fecha_inicio")
        return v


class TestPlanCreate(TestPlanBase):
    pass


class TestPlanUpdate(TestPlanBase):
    pass


class TestPlan(TestPlanBase):
    id: int

    class Config:
        orm_mode = True
