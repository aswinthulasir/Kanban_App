from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...crud import task as crud_task, board as crud_board
from ...schemas.task import Task, TaskCreate, TaskUpdate
from ...models.user import User
from ..deps import get_current_active_user

router = APIRouter()


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task"""
    # Check if user has access to board
    board = await crud_board.get(db, id=task_in.board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if board.owner_id != current_user.id:
        member = await crud_board.get_member(db, board_id=board.id, user_id=current_user.id)
        if not member:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = await crud_task.create_with_creator(db, obj_in=task_in, creator_id=current_user.id)
    return task


@router.get("/", response_model=List[Task])
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    board_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tasks (optionally filtered by board)"""
    if board_id:
        tasks = await crud_task.get_board_tasks(db, board_id=board_id, skip=skip, limit=limit)
    else:
        tasks = await crud_task.get_user_tasks(db, user_id=current_user.id, skip=skip, limit=limit)
    return tasks


@router.get("/search", response_model=List[Task])
async def search_tasks(
    q: str = Query(..., min_length=1),
    board_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search tasks by title or description"""
    tasks = await crud_task.search_tasks(db, query=q, board_id=board_id)
    return tasks


@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task by ID"""
    task = await crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a task"""
    task = await crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    board = await crud_board.get(db, id=task.board_id)
    if board.owner_id != current_user.id:
        member = await crud_board.get_member(db, board_id=board.id, user_id=current_user.id)
        if not member and task.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = await crud_task.update(db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a task"""
    task = await crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    board = await crud_board.get(db, id=task.board_id)
    if board.owner_id != current_user.id:
        member = await crud_board.get_member(db, board_id=board.id, user_id=current_user.id)
        if not member and task.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await crud_task.remove(db, id=task_id)
