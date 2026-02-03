from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import CRUDBase
from ..models.column import Column
from ..schemas.column import ColumnCreate, ColumnUpdate


class CRUDColumn(CRUDBase[Column, ColumnCreate, ColumnUpdate]):
    async def get_board_columns(
        self, db: AsyncSession, *, board_id: str
    ) -> List[Column]:
        result = await db.execute(
            select(Column)
            .filter(Column.board_id == board_id)
            .order_by(Column.position)
        )
        return list(result.scalars().all())


column = CRUDColumn(Column)
