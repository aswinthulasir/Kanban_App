from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import CRUDBase
from ..models.attachment import Attachment
from ..schemas.attachment import AttachmentCreate, AttachmentCreate


class CRUDAttachment(CRUDBase[Attachment, AttachmentCreate, AttachmentCreate]):
    async def get_task_attachments(
        self, db: AsyncSession, *, task_id: str
    ) -> List[Attachment]:
        result = await db.execute(
            select(Attachment)
            .filter(Attachment.task_id == task_id)
            .order_by(Attachment.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: AttachmentCreate, user_id: str
    ) -> Attachment:
        db_obj = Attachment(
            **obj_in.model_dump(),
            uploaded_by=user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


attachment = CRUDAttachment(Attachment)
