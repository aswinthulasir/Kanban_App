from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import uuid
from ...database import get_db
from ...crud import attachment as crud_attachment, task as crud_task
from ...schemas.attachment import Attachment, AttachmentCreate
from ...models.user import User
from ...core.config import settings
from ..deps import get_current_active_user

router = APIRouter()


@router.post("/", response_model=Attachment, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    task_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload an attachment to a task"""
    # Check if task exists
    task = await crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create attachment record
    attachment_in = AttachmentCreate(
        filename=file.filename,
        file_path=file_path,
        file_size=len(contents),
        mime_type=file.content_type,
        task_id=task_id
    )
    
    attachment = await crud_attachment.create_with_user(db, obj_in=attachment_in, user_id=current_user.id)
    return attachment


@router.get("/task/{task_id}", response_model=List[Attachment])
async def read_task_attachments(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all attachments for a task"""
    task = await crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    attachments = await crud_attachment.get_task_attachments(db, task_id=task_id)
    return attachments


@router.get("/{attachment_id}")
async def download_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download an attachment"""
    attachment = await crud_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=attachment.file_path,
        filename=attachment.filename,
        media_type=attachment.mime_type
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an attachment"""
    attachment = await crud_attachment.get(db, id=attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete file from filesystem
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)
    
    await crud_attachment.remove(db, id=attachment_id)
