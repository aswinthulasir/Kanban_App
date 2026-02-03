# Code Changes - Telegram Task Creation Feature

## File Modified: `app/services/telegram_service.py`

### Change 1: Added Global State Management (Line 20-22)

**Before:**
```python
pending_links: Dict[str, str] = {}  # code -> user_id
```

**After:**
```python
pending_links: Dict[str, str] = {}  # code -> user_id

# User states for conversation flow (chat_id -> state)
user_states: Dict[str, Dict] = {}  # chat_id -> {"step": int, "data": {...}}
```

---

### Change 2: Enhanced `_process_updates()` Method (Line 59-88)

**Before:**
```python
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
```

**After:**
```python
async def _process_updates(self, updates):
    """Process incoming Telegram updates"""
    for update in updates:
        try:
            # Update the last update ID
            self.last_update_id = update.update_id
            
            # Handle /start command
            if update.message and update.message.text:
                text = update.message.text
                chat_id = str(update.effective_chat.id)
                
                if text.startswith("/start"):
                    # Extract the link code
                    parts = text.split()
                    if len(parts) > 1:
                        link_code = parts[1]
                        await self._handle_start_with_code(update, link_code)
                    else:
                        await self._handle_start_no_code(update)
                
                elif text.startswith("/add"):
                    # Start task creation flow
                    await self._start_task_creation(update)
                
                elif chat_id in user_states:
                    # Handle conversation flow for task creation
                    state = user_states[chat_id]
                    step = state.get("step", 0)
                    
                    if step == 1:
                        await self._handle_task_name(update)
                    elif step == 2:
                        await self._handle_task_description(update)
                    elif step == 3:
                        await self._handle_task_due_date(update)
                        
        except Exception as e:
            logger.error(f"Error processing update: {e}")
```

---

### Change 3: Added New Methods (After `_handle_start_no_code()`)

#### Method 1: `_start_task_creation()`
```python
async def _start_task_creation(self, update: Update):
    """Start the task creation conversation"""
    try:
        chat_id = str(update.effective_chat.id)
        
        # Check if user is linked
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(User).where(User.telegram_chat_id == chat_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Your Telegram account is not linked to TodoKanban. Please link it first."
                )
                return
        
        # Initialize conversation state
        user_states[chat_id] = {
            "step": 1,
            "data": {}
        }
        
        await self.bot.send_message(
            chat_id=chat_id,
            text="📝 <b>Create New Task</b>\n\nStep 1/3: Give the name of your task",
            parse_mode="HTML"
        )
        
        logger.info(f"Started task creation flow for user {chat_id}")
        
    except Exception as e:
        logger.error(f"Error starting task creation: {e}")
```

#### Method 2: `_handle_task_name()`
```python
async def _handle_task_name(self, update: Update):
    """Handle task name input"""
    try:
        chat_id = str(update.effective_chat.id)
        task_name = update.message.text
        
        # Validate task name
        if not task_name or len(task_name.strip()) == 0:
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Task name cannot be empty. Please try again."
            )
            return
        
        if len(task_name) > 200:
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Task name is too long (max 200 characters). Please try again."
            )
            return
        
        # Store the task name and move to next step
        user_states[chat_id]["data"]["title"] = task_name
        user_states[chat_id]["step"] = 2
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Task name saved: <b>{task_name}</b>\n\nStep 2/3: Give the description of the task",
            parse_mode="HTML"
        )
        
        logger.info(f"Task name received for user {chat_id}: {task_name}")
        
    except Exception as e:
        logger.error(f"Error handling task name: {e}")
```

#### Method 3: `_handle_task_description()`
```python
async def _handle_task_description(self, update: Update):
    """Handle task description input"""
    try:
        chat_id = str(update.effective_chat.id)
        description = update.message.text
        
        # Validate description
        if not description or len(description.strip()) == 0:
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Description cannot be empty. Please try again."
            )
            return
        
        if len(description) > 1000:
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Description is too long (max 1000 characters). Please try again."
            )
            return
        
        # Store the description and move to next step
        user_states[chat_id]["data"]["description"] = description
        user_states[chat_id]["step"] = 3
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Description saved: <b>{description}</b>\n\nStep 3/3: Tell me its due date and time in the format <b>DD/MM/YYYY hh:mm am/pm</b>\n\n(Example: 15/02/2026 03:30 pm)",
            parse_mode="HTML"
        )
        
        logger.info(f"Task description received for user {chat_id}: {description}")
        
    except Exception as e:
        logger.error(f"Error handling task description: {e}")
```

#### Method 4: `_handle_task_due_date()`
```python
async def _handle_task_due_date(self, update: Update):
    """Handle task due date input and create the task"""
    try:
        chat_id = str(update.effective_chat.id)
        due_date_str = update.message.text.strip()
        
        # Parse the due date
        due_date = self._parse_due_date(due_date_str)
        
        if not due_date:
            await self.bot.send_message(
                chat_id=chat_id,
                text="❌ Invalid date format. Please use: <b>DD/MM/YYYY hh:mm am/pm</b>\n(Example: 15/02/2026 03:30 pm)",
                parse_mode="HTML"
            )
            return
        
        # Get user and create task
        async with AsyncSession(engine) as session:
            result = await session.execute(
                select(User).where(User.telegram_chat_id == chat_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ User not found. Please link your account again."
                )
                del user_states[chat_id]
                return
            
            # Get user's first owned board
            from ..models.board import Board
            from ..models.column import Column
            
            result = await session.execute(
                select(Board).where(Board.owner_id == user.id).limit(1)
            )
            board = result.scalar_one_or_none()
            
            if not board:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ You don't have any boards. Please create a board in TodoKanban first."
                )
                del user_states[chat_id]
                return
            
            # Get the "To Do" column or first column
            result = await session.execute(
                select(Column).where(Column.board_id == board.id).order_by(Column.position).limit(1)
            )
            column = result.scalar_one_or_none()
            
            if not column:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Your board doesn't have any columns. Please add columns first."
                )
                del user_states[chat_id]
                return
            
            # Create the task
            from ..models.task import Task
            
            task_data = user_states[chat_id]["data"]
            new_task = Task(
                title=task_data["title"],
                description=task_data["description"],
                column_id=column.id,
                board_id=board.id,
                creator_id=user.id,
                priority="medium",
                due_date=due_date,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)
            
            # Send confirmation message
            due_date_formatted = due_date.strftime("%d/%m/%Y %I:%M %p")
            await self.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"✅ <b>Task Created Successfully!</b>\n\n"
                    f"<b>Task:</b> {task_data['title']}\n"
                    f"<b>Description:</b> {task_data['description']}\n"
                    f"<b>Due Date:</b> {due_date_formatted}\n"
                    f"<b>Priority:</b> Medium\n"
                    f"<b>Column:</b> {column.name}\n"
                    f"<b>Board:</b> {board.name}"
                ),
                parse_mode="HTML"
            )
            
            # Broadcast to board via WebSocket
            from ..websockets.manager import manager
            
            broadcast_message = {
                "type": "task_created",
                "task": {
                    "id": new_task.id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "column_id": new_task.column_id,
                    "board_id": new_task.board_id,
                    "due_date": due_date_formatted,
                    "priority": "medium",
                    "created_by": user.username
                }
            }
            await manager.broadcast_to_board(str(board.id), broadcast_message)
            
            logger.info(f"✅ Task created via Telegram by {user.username}: {task_data['title']}")
            
            # Clean up user state
            del user_states[chat_id]
            
    except Exception as e:
        logger.error(f"Error handling task due date: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await self.bot.send_message(
            chat_id=chat_id,
            text="❌ An error occurred while creating the task. Please try again."
        )
        if chat_id in user_states:
            del user_states[chat_id]
```

#### Method 5: `_parse_due_date()`
```python
def _parse_due_date(self, date_str: str) -> Optional[datetime]:
    """Parse due date from DD/MM/YYYY hh:mm am/pm format"""
    try:
        # Try to parse the date string
        # Expected format: "DD/MM/YYYY hh:mm am/pm"
        date_str = date_str.strip()
        
        # Split date and time
        parts = date_str.split()
        if len(parts) < 3:
            return None
        
        date_part = parts[0]  # DD/MM/YYYY
        time_part = parts[1]  # hh:mm
        period = parts[2].lower()  # am/pm
        
        # Parse date
        date_obj = datetime.strptime(date_part, "%d/%m/%Y")
        
        # Parse time
        time_obj = datetime.strptime(time_part, "%H:%M")
        
        # Adjust for AM/PM
        hour = time_obj.hour
        minute = time_obj.minute
        
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        
        # Combine date and time
        due_date = date_obj.replace(hour=hour, minute=minute)
        
        # Ensure the date is in the future or today
        if due_date < datetime.utcnow():
            # Allow past dates for flexibility
            pass
        
        return due_date
        
    except Exception as e:
        logger.error(f"Error parsing due date: {e}")
        return None
```

---

## Summary of Changes

### Lines Added: ~300
### Methods Added: 5
### State Management: 1 global dictionary
### Database Operations: 3 (select board, select column, insert task)
### WebSocket Broadcasts: 1 (task_created event)

### Key Features:
- ✅ Multi-step conversation flow
- ✅ Input validation (name, description, date)
- ✅ Date/time parsing (DD/MM/YYYY hh:mm am/pm)
- ✅ Task creation with automatic defaults
- ✅ Real-time WebSocket broadcasting
- ✅ Error handling and user feedback
- ✅ State cleanup after completion
- ✅ Comprehensive logging

---

## Testing the Changes

1. **Verify syntax**: No errors should appear
2. **Start server**: `python -m uvicorn app.main:app`
3. **Link Telegram**: Use `/start <code>`
4. **Create task**: Send `/add` and complete conversation
5. **Verify storage**: Check database for new task
6. **Verify UI**: Check board for real-time update

---

## No Breaking Changes

- ✅ Existing `/start` command still works
- ✅ Existing notifications still work
- ✅ Existing endpoints unaffected
- ✅ Backward compatible with all existing features
