from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    task_id: str


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class Comment(CommentBase):
    id: str
    task_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
