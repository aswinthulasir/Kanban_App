import asyncio
import logging
import threading
from typing import Optional, Dict
from telegram import Update, Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid

from ..core.config import settings
from ..models.user import User
from ..database import engine

logger = logging.getLogger(__name__)

# Temporary storage for link codes (in production, use Redis or database)
pending_links: Dict[str, str] = {}  # code -> user_id


class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.bot: Optional[Bot] = None
        self.polling_thread: Optional[threading.Thread] = None
        self.is_polling = False
        self.last_update_id = None

    async def initialize(self):
        """Initialize the Telegram bot"""
        try:
            if not self.bot_token or self.bot_token == "":
                logger.warning("Telegram bot token not configured, skipping initialization")
                return
            
            self.bot = Bot(token=self.bot_token)
            
            # Test the bot token
            me = await self.bot.get_me()
            logger.info(f"Telegram bot initialized successfully: @{me.username}")
            
            # Delete any existing webhook to ensure polling works
            try:
                await self.bot.delete_webhook(drop_pending_updates=True)
                logger.info("Deleted any existing webhook configuration")
            except Exception as e:
                logger.warning(f"Could not delete webhook: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.bot = None

    async def _process_updates(self, updates):
        """Process incoming Telegram updates"""
        for update in updates:
            try:
                # Update the last update ID
                self.last_update_id = update.update_id
                
                # Handle /start command
                if update.message and update.message.text:
                    text = update.message.text
                    if text.startswith("/start"):
                        # Extract the link code
                        parts = text.split()
                        if len(parts) > 1:
                            link_code = parts[1]
                            await self._handle_start_with_code(update, link_code)
                        else:
                            await self._handle_start_no_code(update)
                            
            except Exception as e:
                logger.error(f"Error processing update: {e}")

    async def _handle_start_with_code(self, update: Update, link_code: str):
        """Handle /start command with a link code"""
        try:
            chat_id = str(update.effective_chat.id)
            
            # Verify and link the account
            if await self.verify_and_link_account(link_code, chat_id):
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "✅ Success! Your Telegram account has been linked to TodoKanban.\n\n"
                        "You'll now receive notifications for:\n"
                        "• Task assignments\n"
                        "• Due date reminders\n"
                        "• New comments on your tasks\n"
                        "• Task completion updates"
                    )
                )
                logger.info(f"User linked Telegram account {chat_id}")
                # Remove the used code
                if link_code in pending_links:
                    del pending_links[link_code]
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Invalid or expired link code. Please try again from the TodoKanban app."
                )
        except Exception as e:
            logger.error(f"Error handling start with code: {e}")

    async def _handle_start_no_code(self, update: Update):
        """Handle /start command without a link code"""
        try:
            chat_id = update.effective_chat.id
            await self.bot.send_message(
                chat_id=chat_id,
                text=(
                    "👋 Welcome to TodoKanban Telegram Notifications!\n\n"
                    "To link your account, click the 'Connect Telegram' button in the app settings."
                )
            )
        except Exception as e:
            logger.error(f"Error handling start without code: {e}")


    async def verify_and_link_account(self, link_code: str, chat_id: str) -> bool:
        """Verify link code and link the Telegram account to user"""
        try:
            logger.info(f"🔗 Attempting to link account - code: {link_code}, chat_id: {chat_id}")
            
            if link_code not in pending_links:
                logger.warning(f"❌ Link code {link_code} not found in pending_links")
                logger.info(f"Available codes: {list(pending_links.keys())}")
                return False
            
            user_id = pending_links[link_code]
            logger.info(f"✓ Link code verified, user_id: {user_id}")
            
            # Update user with telegram_chat_id
            async with AsyncSession(engine) as session:
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                
                logger.info(f"User found: {user.username if user else 'NOT FOUND'}")
                
                if user:
                    logger.info(f"Updating user {user.username} telegram_chat_id from {user.telegram_chat_id} to {chat_id}")
                    user.telegram_chat_id = chat_id
                    user.updated_at = datetime.utcnow()
                    await session.commit()
                    logger.info(f"✅ User {user.username} linked successfully to Telegram chat {chat_id}")
                    return True
            
            logger.warning(f"❌ User {user_id} not found in database")
            return False
        except Exception as e:
            logger.error(f"❌ Error linking account: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def generate_link_code(self, user_id: str) -> str:
        """Generate a unique link code for user"""
        link_code = str(uuid.uuid4())[:8]
        pending_links[link_code] = user_id
        
        # Auto-expire after 10 minutes
        asyncio.create_task(self._expire_code(link_code))
        
        return link_code

    async def _expire_code(self, code: str, timeout: int = 600):
        """Expire a link code after timeout (default 10 minutes)"""
        await asyncio.sleep(timeout)
        if code in pending_links:
            del pending_links[code]
            logger.info(f"Link code {code} expired")

    async def unlink_account(self, user_id: str) -> bool:
        """Unlink Telegram account from user"""
        try:
            async with AsyncSession(engine) as session:
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                
                if user:
                    user.telegram_chat_id = None
                    user.updated_at = datetime.utcnow()
                    await session.commit()
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error unlinking account: {e}")
            return False

    async def send_notification(self, chat_id: str, message: str) -> bool:
        """Send a notification message to a user's Telegram"""
        try:
            if not self.bot:
                logger.warning("❌ Bot not initialized, cannot send notification")
                return False
            
            logger.info(f"═" * 60)
            logger.info(f"📤 SENDING Telegram message")
            logger.info(f"   Chat ID: {chat_id}")
            logger.info(f"   Message: {message[:150]}...")
            logger.info(f"═" * 60)
            
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
            
            logger.info(f"✅ Message sent successfully to {chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram notification to {chat_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def send_task_assigned_notification(self, user_chat_id: str, task_title: str, assigned_by: str, board_name: str):
        """Send task assignment notification"""
        message = (
            f"📌 <b>New Task Assignment</b>\n\n"
            f"<b>Task:</b> {task_title}\n"
            f"<b>Board:</b> {board_name}\n"
            f"<b>Assigned by:</b> {assigned_by}"
        )
        logger.info(f"📌 Task assignment notification: {task_title} → {user_chat_id}")
        await self.send_notification(user_chat_id, message)

    async def send_due_date_reminder(self, user_chat_id: str, task_title: str, due_date: str, board_name: str):
        """Send due date reminder notification"""
        message = (
            f"⏰ <b>Task Due Soon</b>\n\n"
            f"<b>Task:</b> {task_title}\n"
            f"<b>Due:</b> {due_date}\n"
            f"<b>Board:</b> {board_name}"
        )
        logger.info(f"⏰ Due date reminder: {task_title} → {user_chat_id}")
        await self.send_notification(user_chat_id, message)

    async def send_comment_notification(self, user_chat_id: str, task_title: str, commenter: str, comment_text: str, board_name: str):
        """Send comment notification"""
        comment_preview = comment_text[:100] + "..." if len(comment_text) > 100 else comment_text
        message = (
            f"💬 <b>New Comment on Task</b>\n\n"
            f"<b>Task:</b> {task_title}\n"
            f"<b>Commented by:</b> {commenter}\n"
            f"<b>Board:</b> {board_name}\n"
            f"<b>Comment:</b> {comment_preview}"
        )
        logger.info(f"💬 Comment notification: {task_title} → {user_chat_id}")
        await self.send_notification(user_chat_id, message)

    async def send_task_completed_notification(self, user_chat_id: str, task_title: str, board_name: str):
        """Send task completion notification"""
        message = (
            f"✅ <b>Task Completed</b>\n\n"
            f"<b>Task:</b> {task_title}\n"
            f"<b>Board:</b> {board_name}"
        )
        logger.info(f"✅ Task completion notification: {task_title} → {user_chat_id}")
        await self.send_notification(user_chat_id, message)

    async def start_polling(self):
        """Start the bot polling in a separate thread"""
        try:
            if not self.bot or not self.bot_token or self.bot_token == "":
                logger.warning("Telegram bot not initialized, skipping polling")
                return
            
            logger.info("Starting Telegram bot polling in background thread...")
            
            # Run polling in a background thread to avoid blocking
            self.is_polling = True
            self.polling_thread = threading.Thread(
                target=self._run_polling,
                daemon=True
            )
            self.polling_thread.start()
            
        except Exception as e:
            logger.error(f"Error starting bot polling: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _run_polling(self):
        """Run polling in a thread - get updates using long polling"""
        try:
            logger.info("Telegram bot polling started")
            
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.is_polling:
                try:
                    # Get updates from Telegram
                    updates = loop.run_until_complete(self._get_updates())
                    
                    if updates:
                        # Process the updates
                        loop.run_until_complete(self._process_updates(updates))
                    
                    # Small delay to avoid hammering the API
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    import time
                    time.sleep(5)  # Longer delay on error
            
            loop.close()
                    
        except Exception as e:
            logger.error(f"Critical error in polling thread: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def _get_updates(self):
        """Get updates from Telegram using getUpdates"""
        try:
            if not self.bot:
                return []
            
            # Get updates with offset to get only new ones
            offset = None
            if self.last_update_id is not None:
                offset = self.last_update_id + 1
            
            updates = await self.bot.get_updates(offset=offset, timeout=30)
            return updates
            
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    async def stop(self):
        """Stop the bot"""
        try:
            self.is_polling = False
            if self.bot:
                await self.bot.close()
            
            # Wait for polling thread to finish
            if self.polling_thread and self.polling_thread.is_alive():
                self.polling_thread.join(timeout=5)
            
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")


# Global instance
telegram_service = TelegramService()
