from sqlalchemy import Column, Integer, String, Text, Date
from ..database import Base


class TestPlan(Base):
    __tablename__ = "testplans"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    objetivo = Column(Text)
    alcance = Column(Text)
    criterios_entrada = Column(Text)
    criterios_salida = Column(Text)
    estrategia_pruebas = Column(Text)
    responsables = Column(Text)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    bdd_stories = Column(Text)
