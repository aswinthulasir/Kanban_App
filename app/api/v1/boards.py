from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...crud import board as crud_board
from ...schemas.board import Board, BoardCreate, BoardUpdate, BoardMember, BoardMemberCreate
from ...models.user import User
from ..deps import get_current_active_user

router = APIRouter()


@router.post("/", response_model=Board, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_in: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new board"""
    board = await crud_board.create_with_owner(db, obj_in=board_in, owner_id=current_user.id)
    return board


@router.get("/", response_model=List[Board])
async def read_boards(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all boards for current user"""
    boards = await crud_board.get_user_boards(db, user_id=current_user.id, skip=skip, limit=limit)
    return boards


@router.get("/{board_id}", response_model=Board)
async def read_board(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get board by ID"""
    board = await crud_board.get(db, id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    # Check if user has access
    if board.owner_id != current_user.id and not board.is_public:
        # Check if user is a member
        member = await crud_board.get_member(db, board_id=board_id, user_id=current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    return board


@router.put("/{board_id}", response_model=Board)
async def update_board(
    board_id: str,
    board_in: BoardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a board"""
    board = await crud_board.get(db, id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    board = await crud_board.update(db, db_obj=board, obj_in=board_in)
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a board"""
    board = await crud_board.get(db, id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await crud_board.remove(db, id=board_id)


@router.get("/{board_id}/members", response_model=List[BoardMember])
async def read_board_members(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all members of a board"""
    board = await crud_board.get(db, id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    members = await crud_board.get_board_members(db, board_id=board_id)
    return members


@router.post("/{board_id}/members", response_model=BoardMember, status_code=status.HTTP_201_CREATED)
async def add_board_member(
    board_id: str,
    member_in: BoardMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a member to a board"""
    board = await crud_board.get(db, id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if user already a member
    existing_member = await crud_board.get_member(db, board_id=board_id, user_id=member_in.user_id)
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    member = await crud_board.add_member(db, board_id=board_id, obj_in=member_in)
    return member
