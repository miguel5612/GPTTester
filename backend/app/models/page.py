from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    elements = relationship("PageElement", back_populates="page")
