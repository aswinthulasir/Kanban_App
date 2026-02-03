from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Column(Base):
    __tablename__ = "columns"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)
    color = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
