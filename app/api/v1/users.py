from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...crud import user as crud_user
from ...schemas.user import User, UserUpdate
from ...models.user import User as UserModel
from ..deps import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=User)
async def read_user_me(
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get current user"""
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update current user"""
    user = await crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get user by ID"""
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get all users (paginated)"""
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users
