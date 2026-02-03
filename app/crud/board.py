from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from .base import CRUDBase
from ..models.board import Board, BoardMember
from ..models.column import Column
from ..models.user import User
from ..schemas.board import BoardCreate, BoardUpdate, BoardMemberCreate


class CRUDBoard(CRUDBase[Board, BoardCreate, BoardUpdate]):
    async def get_user_boards(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Board]:
        # Get boards owned by user or where user is a member
        result = await db.execute(
            select(Board)
            .outerjoin(BoardMember)
            .filter(
                or_(
                    Board.owner_id == user_id,
                    BoardMember.user_id == user_id
                )
            )
            .distinct()
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: BoardCreate, owner_id: str
    ) -> Board:
        db_obj = Board(
            **obj_in.model_dump(),
            owner_id=owner_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_user_by_id(
        self, db: AsyncSession, *, id: str
    ) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).filter(User.id == id)
        )
        return result.scalar_one_or_none()

    async def get_column(
        self, db: AsyncSession, *, id: str
    ) -> Optional[Column]:
        """Get column by ID"""
        result = await db.execute(
            select(Column).filter(Column.id == id)
        )
        return result.scalar_one_or_none()


class CRUDBoardMember(CRUDBase[BoardMember, BoardMemberCreate, BoardMemberCreate]):
    async def get_board_members(
        self, db: AsyncSession, *, board_id: str
    ) -> List[BoardMember]:
        result = await db.execute(
            select(BoardMember).filter(BoardMember.board_id == board_id)
        )
        return list(result.scalars().all())

    async def get_member(
        self, db: AsyncSession, *, board_id: str, user_id: str
    ) -> Optional[BoardMember]:
        result = await db.execute(
            select(BoardMember).filter(
                BoardMember.board_id == board_id,
                BoardMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def add_member(
        self, db: AsyncSession, *, board_id: str, obj_in: BoardMemberCreate
    ) -> BoardMember:
        db_obj = BoardMember(
            board_id=board_id,
            **obj_in.model_dump()
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


board = CRUDBoard(Board)
board_member = CRUDBoardMember(BoardMember)
