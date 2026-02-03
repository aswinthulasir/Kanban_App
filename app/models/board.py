from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..database import Base


def generate_uuid():
    return str(uuid.uuid4())


class MemberRole(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"


class Board(Base):
    __tablename__ = "boards"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="owned_boards", foreign_keys=[owner_id])
    members = relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")


class BoardMember(Base):
    __tablename__ = "board_members"

    id = Column(String, primary_key=True, default=generate_uuid)
    board_id = Column(String, ForeignKey("boards.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    board = relationship("Board", back_populates="members")
    user = relationship("User", back_populates="board_memberships")
