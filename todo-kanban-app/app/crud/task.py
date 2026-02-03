from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from .base import CRUDBase
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    async def get_board_tasks(
        self, db: AsyncSession, *, board_id: str, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        result = await db.execute(
            select(Task)
            .filter(Task.board_id == board_id)
            .order_by(Task.position)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_column_tasks(
        self, db: AsyncSession, *, column_id: str
    ) -> List[Task]:
        result = await db.execute(
            select(Task)
            .filter(Task.column_id == column_id)
            .order_by(Task.position)
        )
        return list(result.scalars().all())

    async def get_user_tasks(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Task]:
        result = await db.execute(
            select(Task)
            .filter(
                or_(
                    Task.creator_id == user_id,
                    Task.assigned_to_id == user_id
                )
            )
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_tasks(
        self, db: AsyncSession, *, query: str, board_id: Optional[str] = None
    ) -> List[Task]:
        stmt = select(Task).filter(
            or_(
                Task.title.ilike(f"%{query}%"),
                Task.description.ilike(f"%{query}%")
            )
        )
        if board_id:
            stmt = stmt.filter(Task.board_id == board_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_with_creator(
        self, db: AsyncSession, *, obj_in: TaskCreate, creator_id: str
    ) -> Task:
        db_obj = Task(
            **obj_in.model_dump(),
            creator_id=creator_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


task = CRUDTask(Task)
