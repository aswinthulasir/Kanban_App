from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...database import get_db
from ...crud import task as crud_task, board, board_member
from ...schemas.task import Task, TaskCreate, TaskUpdate
from ...models.user import User
from ..deps import get_current_active_user
from ...services.telegram_service import telegram_service

router = APIRouter()


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task"""
    # Check if user has access to board
    board_obj = await board.get(db, id=task_in.board_id)
    if not board_obj:
        raise HTTPException(status_code=404, detail="Board not found")
    if board_obj.owner_id != current_user.id:
        member = await board_member.get_member(db, board_id=board_obj.id, user_id=current_user.id)
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
    board_obj = await board.get(db, id=task.board_id)
    if board_obj.owner_id != current_user.id:
        member = await board_member.get_member(db, board_id=board_obj.id, user_id=current_user.id)
        if not member and task.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Track old values for notifications
    old_column_id = task.column_id
    old_assigned_to_id = task.assigned_to_id
    
    task = await crud_task.update(db, db_obj=task, obj_in=task_in)
    
    # Send Telegram notifications (with error handling to not break the request)
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📋 TASK UPDATE NOTIFICATION CHECK")
        logger.info(f"{'='*80}")
        logger.info(f"Task ID: {task.id}")
        logger.info(f"Task Title: {task.title}")
        logger.info(f"Task Creator ID: {task.creator_id}")
        logger.info(f"Task Assigned To: {task.assigned_to_id}")
        logger.info(f"Old Column: {old_column_id}")
        logger.info(f"New Column: {task_in.column_id}")
        logger.info(f"Old Assigned To: {old_assigned_to_id}")
        logger.info(f"New Assigned To: {task_in.assigned_to_id}")
        logger.info(f"Board: {board_obj.name}")
        
        # ALWAYS notify the creator that their task was updated
        if task.creator_id:
            logger.info(f"\n📌 Checking creator notification")
            creator = await board.get_user_by_id(db, id=task.creator_id)
            logger.info(f"   Creator: {creator.username if creator else 'NOT FOUND'}")
            logger.info(f"   Creator Telegram ID: {creator.telegram_chat_id if creator else 'N/A'}")
            
            if creator and creator.telegram_chat_id:
                message = (
                    f"📝 <b>Your Task Was Updated</b>\n\n"
                    f"<b>Task:</b> {task.title}\n"
                    f"<b>Updated by:</b> {current_user.full_name or current_user.username}\n"
                    f"<b>Board:</b> {board_obj.name}"
                )
                logger.info(f"✅ SENDING notification to creator {creator.username} ({creator.telegram_chat_id})")
                await telegram_service.send_notification(creator.telegram_chat_id, message)
            else:
                logger.warning(f"⚠️ Cannot notify creator: user={creator}, telegram_chat_id={creator.telegram_chat_id if creator else 'no_user'}")
        else:
            logger.info(f"⚠️ No creator ID for task")
        
        # If task is assigned, notify the assigned user
        if task.assigned_to_id and task.assigned_to_id != task.creator_id:
            logger.info(f"\n📌 Checking assigned user notification")
            assigned_user = await board.get_user_by_id(db, id=task.assigned_to_id)
            logger.info(f"   Assigned User: {assigned_user.username if assigned_user else 'NOT FOUND'}")
            logger.info(f"   Assigned User Telegram ID: {assigned_user.telegram_chat_id if assigned_user else 'N/A'}")
            
            if assigned_user and assigned_user.telegram_chat_id:
                message = (
                    f"📊 <b>Your Assigned Task Was Updated</b>\n\n"
                    f"<b>Task:</b> {task.title}\n"
                    f"<b>Updated by:</b> {current_user.full_name or current_user.username}\n"
                    f"<b>Board:</b> {board_obj.name}"
                )
                logger.info(f"✅ SENDING notification to assigned user {assigned_user.username} ({assigned_user.telegram_chat_id})")
                await telegram_service.send_notification(assigned_user.telegram_chat_id, message)
            else:
                logger.warning(f"⚠️ Cannot notify assigned user: user={assigned_user}, telegram_chat_id={assigned_user.telegram_chat_id if assigned_user else 'no_user'}")
        else:
            logger.info(f"⚠️ Task not assigned or assigned to creator")
        
        logger.info(f"{'='*80}\n")
        
    except Exception as e:
        # Log the error but don't fail the request
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"❌ CRITICAL ERROR in notification sending: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
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
    board_obj = await board.get(db, id=task.board_id)
    if board_obj.owner_id != current_user.id:
        member = await board_member.get_member(db, board_id=board_obj.id, user_id=current_user.id)
        if not member and task.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await crud_task.remove(db, id=task_id)
