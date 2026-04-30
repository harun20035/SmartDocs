from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
from app.database import Base


class ValidationError(Base):
    __tablename__ = "validation_errors"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.id"))

    error_type = Column(String)   # MATH_MISMATCH, MISSING_FIELD, DUPLICATE
    field_name = Column(String)   # total, supplier_name, etc
    message = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    document: Optional["Document"] = relationship(
        "Document",
        back_populates="validation_errors"
    )