from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...crud import column as crud_column, board as crud_board
from ...schemas.column import Column, ColumnCreate, ColumnUpdate
from ...models.user import User
from ..deps import get_current_active_user

router = APIRouter()


@router.post("/", response_model=Column, status_code=status.HTTP_201_CREATED)
async def create_column(
    column_in: ColumnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new column"""
    # Check if user has access to board
    board = await crud_board.get(db, id=column_in.board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        member = await crud_board.get_member(db, board_id=board.id, user_id=current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    column = await crud_column.create(db, obj_in=column_in)
    return column


@router.get("/board/{board_id}", response_model=List[Column])
async def read_board_columns(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all columns for a board"""
    board = await crud_board.get(db, id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    columns = await crud_column.get_board_columns(db, board_id=board_id)
    return columns


@router.get("/{column_id}", response_model=Column)
async def read_column(
    column_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get column by ID"""
    column = await crud_column.get(db, id=column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column


@router.put("/{column_id}", response_model=Column)
async def update_column(
    column_id: str,
    column_in: ColumnUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a column"""
    column = await crud_column.get(db, id=column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Check permissions
    board = await crud_board.get(db, id=column.board_id)
    if board.owner_id != current_user.id:
        member = await crud_board.get_member(db, board_id=board.id, user_id=current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    column = await crud_column.update(db, db_obj=column, obj_in=column_in)
    return column


@router.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(
    column_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a column"""
    column = await crud_column.get(db, id=column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Check permissions
    board = await crud_board.get(db, id=column.board_id)
    if board.owner_id != current_user.id:
        member = await crud_board.get_member(db, board_id=board.id, user_id=current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await crud_column.remove(db, id=column_id)
