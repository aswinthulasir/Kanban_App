from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    content = Column(String, nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")
