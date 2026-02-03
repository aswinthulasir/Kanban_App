from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...crud import comment as crud_comment, task as crud_task, board as crud_board
from ...schemas.comment import Comment, CommentCreate, CommentUpdate
from ...models.user import User
from ..deps import get_current_active_user
from ...services.telegram_service import telegram_service

router = APIRouter()


@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new comment"""
    # Check if task exists
    task = await crud_task.get(db, id=comment_in.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    comment = await crud_comment.create_with_user(db, obj_in=comment_in, user_id=current_user.id)
    
    # Send Telegram notification to task creator
    if task.creator_id and task.creator_id != current_user.id:
        creator = await crud_board.get_user_by_id(db, id=task.creator_id)
        if creator and creator.telegram_chat_id:
            board = await crud_board.get(db, id=task.board_id)
            await telegram_service.send_comment_notification(
                creator.telegram_chat_id,
                task.title,
                current_user.full_name or current_user.username,
                comment.text,
                board.name
            )
    
    # Send Telegram notification to assigned user if different from creator
    if task.assigned_to_id and task.assigned_to_id != current_user.id and task.assigned_to_id != task.creator_id:
        assigned_user = await crud_board.get_user_by_id(db, id=task.assigned_to_id)
        if assigned_user and assigned_user.telegram_chat_id:
            board = await crud_board.get(db, id=task.board_id)
            await telegram_service.send_comment_notification(
                assigned_user.telegram_chat_id,
                task.title,
                current_user.full_name or current_user.username,
                comment.text,
                board.name
            )
    
    return comment


@router.get("/task/{task_id}", response_model=List[Comment])
async def read_task_comments(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all comments for a task"""
    task = await crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comments = await crud_comment.get_task_comments(db, task_id=task_id)
    return comments


@router.get("/{comment_id}", response_model=Comment)
async def read_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comment by ID"""
    comment = await crud_comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: str,
    comment_in: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a comment"""
    comment = await crud_comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    comment = await crud_comment.update(db, db_obj=comment, obj_in=comment_in)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment"""
    comment = await crud_comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await crud_comment.remove(db, id=comment_id)
