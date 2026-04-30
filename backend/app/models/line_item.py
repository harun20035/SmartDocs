from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship
from typing import Optional

class LineItem(Base):
    __tablename__ = "line_items"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"))

    description = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total = Column(Float)

    document: Optional["Document"] = relationship(
        "Document",
        back_populates="line_items"
    )