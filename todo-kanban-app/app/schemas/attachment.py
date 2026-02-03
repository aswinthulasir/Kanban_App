from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AttachmentBase(BaseModel):
    filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    file_path: str
    task_id: str


class Attachment(AttachmentBase):
    id: str
    file_path: str
    task_id: str
    uploaded_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
