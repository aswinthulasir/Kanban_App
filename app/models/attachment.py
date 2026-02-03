from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    uploaded_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploaded_by_user = relationship("User", back_populates="attachments")
