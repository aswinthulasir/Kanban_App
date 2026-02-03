from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    column_id = Column(String, ForeignKey("columns.id"), nullable=False)
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(String, ForeignKey("users.id"), nullable=True)
    position = Column(Integer, nullable=False, default=0)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    column = relationship("Column", back_populates="tasks")
    board = relationship("Board", back_populates="tasks")
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[creator_id])
    assigned_to = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to_id])
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
