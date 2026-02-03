from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskCreate(TaskBase):
    column_id: str
    board_id: str
    assigned_to_id: Optional[str] = None
    position: int = 0


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    column_id: Optional[str] = None
    assigned_to_id: Optional[str] = None
    position: Optional[int] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tags: Optional[List[str]] = None


class Task(TaskBase):
    id: str
    column_id: str
    board_id: str
    creator_id: str
    assigned_to_id: Optional[str] = None
    position: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
