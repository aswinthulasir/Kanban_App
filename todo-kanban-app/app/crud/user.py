from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import CRUDBase
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active


user = CRUDUser(User)
