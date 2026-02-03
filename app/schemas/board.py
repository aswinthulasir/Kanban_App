from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class MemberRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


class BoardBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class Board(BoardBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BoardMemberBase(BaseModel):
    board_id: str
    user_id: str
    role: MemberRole = MemberRole.MEMBER


class BoardMemberCreate(BaseModel):
    user_id: str
    role: MemberRole = MemberRole.MEMBER


class BoardMember(BoardMemberBase):
    id: str
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
