from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owned_boards = relationship("Board", back_populates="owner", foreign_keys="Board.owner_id")
    board_memberships = relationship("BoardMember", back_populates="user")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    assigned_tasks = relationship("Task", back_populates="assigned_to", foreign_keys="Task.assigned_to_id")
    comments = relationship("Comment", back_populates="user")
    attachments = relationship("Attachment", back_populates="uploaded_by_user")
