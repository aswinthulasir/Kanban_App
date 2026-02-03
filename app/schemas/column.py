from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ColumnBase(BaseModel):
    name: str
    position: int = 0
    color: Optional[str] = None


class ColumnCreate(ColumnBase):
    board_id: str


class ColumnUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None
    color: Optional[str] = None


class Column(ColumnBase):
    id: str
    board_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
