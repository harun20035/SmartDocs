from sqlalchemy import Column, Integer, String, Date, DateTime, Float
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship
from typing import List

class Document(Base):
    __tablename__ = "documents"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    document_type = Column(String)

    supplier_name = Column(String)
    document_number = Column(String)

    issue_date = Column(Date)
    due_date = Column(Date)

    currency = Column(String)

    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)

    status = Column(String, default="uploaded")

    created_at = Column(DateTime, default=datetime.utcnow)

    line_items: List["LineItem"] = relationship(
        "LineItem",
        back_populates="document",
        cascade="all, delete-orphan"
    )

    validation_errors: List["ValidationError"] = relationship(
        "ValidationError",
        back_populates="document",
        cascade="all, delete-orphan"
    )