from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import CRUDBase
from ..models.comment import Comment
from ..schemas.comment import CommentCreate, CommentUpdate


class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    async def get_task_comments(
        self, db: AsyncSession, *, task_id: str
    ) -> List[Comment]:
        result = await db.execute(
            select(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_with_user(
        self, db: AsyncSession, *, obj_in: CommentCreate, user_id: str
    ) -> Comment:
        db_obj = Comment(
            content=obj_in.content,
            task_id=obj_in.task_id,
            user_id=user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


comment = CRUDComment(Comment)
