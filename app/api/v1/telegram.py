from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from ...database import get_db
from ...models.user import User
from ...services.telegram_service import telegram_service, pending_links
from ...api.deps import get_current_user

router = APIRouter(tags=["telegram"])


class TelegramLinkResponse(BaseModel):
    link_code: str
    message: str


class TelegramStatusResponse(BaseModel):
    is_linked: bool
    telegram_chat_id: str | None


class UnlinkResponse(BaseModel):
    message: str


@router.post("/telegram/link", response_model=TelegramLinkResponse)
async def get_telegram_link(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a link code for Telegram connection
    
    User will use this code with the Telegram bot: /start <code>
    """
    try:
        link_code = await telegram_service.generate_link_code(current_user.id)
        
        return TelegramLinkResponse(
            link_code=link_code,
            message=f"Visit Telegram bot and send: /start {link_code}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate link code: {str(e)}"
        )


@router.get("/telegram/status", response_model=TelegramStatusResponse)
async def get_telegram_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current Telegram connection status"""
    return TelegramStatusResponse(
        is_linked=current_user.telegram_chat_id is not None,
        telegram_chat_id=current_user.telegram_chat_id
    )


@router.post("/telegram/unlink", response_model=UnlinkResponse)
async def unlink_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unlink Telegram from user account"""
    try:
        success = await telegram_service.unlink_account(current_user.id)
        
        if success:
            return UnlinkResponse(message="Telegram account unlinked successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unlink Telegram account"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlink account: {str(e)}"
        )


class TelegramUpdate(BaseModel):
    """Handle Telegram webhook updates"""
    update_id: int
    message: dict = None


@router.post("/telegram/webhook")
async def telegram_webhook(update: dict, db: AsyncSession = Depends(get_db)):
    """Webhook to receive Telegram updates
    
    Users send: /start {code}
    """
    try:
        # Extract message and chat info
        message = update.get("message", {})
        chat_id = str(message.get("chat", {}).get("id", ""))
        text = message.get("text", "").strip()
        
        if not text.startswith("/start"):
            return {"ok": True}
        
        # Parse the command: /start code
        parts = text.split()
        if len(parts) < 2:
            # Send message back that code is required
            if telegram_service.bot:
                try:
                    await telegram_service.bot.send_message(
                        chat_id=chat_id,
                        text="👋 Welcome to TodoKanban!\n\nTo link your account, please use: /start {code}\n\nGet your code from the Settings page in TodoKanban."
                    )
                except:
                    pass
            return {"ok": True}
        
        link_code = parts[1]
        
        # Verify and link the account
        if link_code in pending_links:
            user_id = pending_links[link_code]
            
            # Update user with telegram chat_id
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if user:
                user.telegram_chat_id = chat_id
                user.updated_at = datetime.utcnow()
                await db.commit()
                
                # Send success message
                if telegram_service.bot:
                    try:
                        await telegram_service.bot.send_message(
                            chat_id=chat_id,
                            text="✅ Success! Your Telegram account has been linked to TodoKanban.\n\nYou'll now receive notifications for:\n• Task assignments\n• Due date reminders\n• New comments on your tasks\n• Task completion updates"
                        )
                    except:
                        pass
                
                # Remove the used code
                del pending_links[link_code]
                return {"ok": True}
        
        # Invalid or expired code
        if telegram_service.bot:
            try:
                await telegram_service.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Invalid or expired link code. Please try again from the TodoKanban app."
                )
            except:
                pass
        
        return {"ok": True}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error handling Telegram webhook: {e}")
        return {"ok": True}
