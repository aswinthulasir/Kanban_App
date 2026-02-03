# Telegram Integration Guide

## Setup Instructions

### 1. Bot Already Created ✅
You've already created a bot with BotFather and have the token in `.env` as `TELEGRAM_BOT_TOKEN`.

### 2. Install Dependencies
The `python-telegram-bot==21.3` library has been added to `requirements.txt`. Install it:

```bash
pip install -r requirements.txt
```

### 3. Database Migration
The `telegram_chat_id` field has been added to the User model. The app will automatically create the column on startup due to this line in `app/main.py`:

```python
await conn.run_sync(Base.metadata.create_all)
```

If using Alembic migrations, you can also run:
```bash
alembic upgrade head
```

### 4. How It Works

#### Architecture Flow:
```
User clicks "Connect Telegram" (frontend)
     ↓
Backend generates unique link code (e.g., "abc12345")
     ↓
User opens Telegram and sends: /start abc12345
     ↓
Bot receives message and verifies code
     ↓
Bot links user's chat_id to their TodoKanban account
     ↓
User now receives notifications
```

#### Supported Notifications:
1. **Task Assignment**: When someone assigns a task to you
2. **Task Completion**: When a task you created is moved to "Done" column
3. **New Comment**: When someone comments on your task
4. **Future: Due Date Reminders**: When a task is due soon (requires background job)

## API Endpoints

### 1. Generate Link Code
```bash
POST /api/v1/telegram/link
Headers: Authorization: Bearer {token}

Response:
{
  "link_code": "abc12345",
  "message": "Visit Telegram bot and send: /start abc12345"
}
```

### 2. Check Connection Status
```bash
GET /api/v1/telegram/status
Headers: Authorization: Bearer {token}

Response:
{
  "is_linked": true,
  "telegram_chat_id": "123456789"
}
```

### 3. Unlink Telegram
```bash
POST /api/v1/telegram/unlink
Headers: Authorization: Bearer {token}

Response:
{
  "message": "Telegram account unlinked successfully"
}
```

## Frontend Integration

### Add Connect Telegram Button to User Settings

```html
<div id="telegram-section">
  <h3>Telegram Notifications</h3>
  <div id="telegram-status">Loading...</div>
  <button id="connect-telegram-btn" onclick="connectTelegram()">Connect Telegram</button>
  <button id="disconnect-telegram-btn" onclick="disconnectTelegram()" style="display:none;">Disconnect Telegram</button>
</div>

<div id="telegram-modal" class="modal-overlay hidden">
  <div class="modal">
    <div class="modal-header">
      <h2>Connect Telegram</h2>
      <button class="modal-close" onclick="closeTelegramModal()">&times;</button>
    </div>
    <div class="modal-body">
      <ol>
        <li>Open Telegram and search for your bot (name: @YourBotName)</li>
        <li>Copy this code: <code id="telegram-code"></code></li>
        <li>Send to the bot: <code>/start {code}</code></li>
        <li>Done! You'll start receiving notifications</li>
      </ol>
      <p style="margin-top: 1rem; padding: 1rem; background: #f0f0f0; border-radius: 4px;">
        <strong>Example:</strong> If your code is "abc12345", send exactly:<br>
        <code>/start abc12345</code>
      </p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeTelegramModal()">Close</button>
    </div>
  </div>
</div>

<script>
async function connectTelegram() {
  try {
    const response = await api.request('/telegram/link', { method: 'POST' });
    document.getElementById('telegram-code').textContent = response.link_code;
    document.getElementById('telegram-modal').classList.remove('hidden');
  } catch (error) {
    alert('Failed to generate link code: ' + error.message);
  }
}

async function disconnectTelegram() {
  if (!confirm('Are you sure you want to disconnect Telegram?')) return;
  
  try {
    await api.request('/telegram/unlink', { method: 'POST' });
    alert('Telegram disconnected');
    checkTelegramStatus();
  } catch (error) {
    alert('Failed to disconnect: ' + error.message);
  }
}

async function checkTelegramStatus() {
  try {
    const response = await api.request('/telegram/status');
    const section = document.getElementById('telegram-status');
    const connectBtn = document.getElementById('connect-telegram-btn');
    const disconnectBtn = document.getElementById('disconnect-telegram-btn');
    
    if (response.is_linked) {
      section.innerHTML = '<p style="color: green;">✅ Telegram connected</p>';
      connectBtn.style.display = 'none';
      disconnectBtn.style.display = 'block';
    } else {
      section.innerHTML = '<p style="color: #888;">Not connected</p>';
      connectBtn.style.display = 'block';
      disconnectBtn.style.display = 'none';
    }
  } catch (error) {
    console.error('Failed to check status:', error);
  }
}

function closeTelegramModal() {
  document.getElementById('telegram-modal').classList.add('hidden');
}

// Check status on page load
checkTelegramStatus();
</script>
```

## Testing the Integration

1. **Start the app:**
```bash
python -m uvicorn app.main:app --reload
```

2. **Create a link code:**
```bash
curl -X POST http://localhost:8000/api/v1/telegram/link \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **In Telegram, send:**
```
/start abc12345
```

4. **Verify the connection:**
```bash
curl http://localhost:8000/api/v1/telegram/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## How Notifications Are Sent

### 1. Task Assignment
When you assign a task to someone:
```python
# In app/api/v1/tasks.py - update_task()
if task_in.assigned_to_id and assigned_user.telegram_chat_id:
    await telegram_service.send_task_assigned_notification(...)
```

### 2. Comment Notification
When someone comments on a task:
```python
# In app/api/v1/comments.py - create_comment()
if task.creator_id and creator.telegram_chat_id:
    await telegram_service.send_comment_notification(...)
```

### 3. Task Completion
When a task is moved to "Done" column:
```python
# In app/api/v1/tasks.py - update_task()
if new_column.name.lower() contains "done":
    await telegram_service.send_task_completed_notification(...)
```

## Future Enhancements

### 1. Due Date Reminders
Implement a background scheduler (using APScheduler or Celery) to send reminders:

```python
# Example with APScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

async def check_due_dates():
    # Find tasks due in next 24 hours
    # Send reminders via Telegram
    pass

scheduler.add_job(check_due_dates, 'interval', hours=1)
await scheduler.start()
```

### 2. User Preferences
Add notification preferences table:

```python
class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    notify_assignment = Column(Boolean, default=True)
    notify_comments = Column(Boolean, default=True)
    notify_completion = Column(Boolean, default=True)
    notify_due_dates = Column(Boolean, default=True)
```

### 3. Notification History
Track sent notifications for audit:

```python
class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    notification_type = Column(String)
    message = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # 'sent', 'failed'
```

## Troubleshooting

### Bot Not Receiving Messages
1. Check that the bot token is correct in `.env`
2. Verify the bot was created with BotFather
3. Make sure the bot is in your Telegram account
4. Check logs for any errors: `python -m uvicorn app.main:app --reload`

### Link Code Not Working
1. Codes expire after 10 minutes (configurable in `telegram_service.py`)
2. Generate a new code if it's expired
3. Make sure you send exactly: `/start {code}` (with space)

### Notifications Not Sending
1. Check that the user has Telegram linked: `GET /api/v1/telegram/status`
2. Verify the `telegram_chat_id` is stored in database
3. Check app logs for notification send errors
4. Ensure the bot has permission to send messages

## Security Notes

1. **Link codes** are stored in memory (temporary storage). For production, use Redis or database
2. **Chat IDs** are private and only stored for linked users
3. **Messages** are sent directly to users without storing content
4. **Tokens** are standard Telegram bot tokens - keep in `.env` file
5. For production, generate a new bot token and update `.env`

## Support

For issues with python-telegram-bot library, see: https://python-telegram-bot.readthedocs.io/
For Telegram bot development: https://core.telegram.org/bots
