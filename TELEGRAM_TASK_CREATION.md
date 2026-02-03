# Telegram Task Creation Feature

## Overview
You can now create tasks directly from Telegram using the `/add` command. The bot will guide you through a simple conversation to collect all necessary information.

## How to Use

### Step 1: Start Task Creation
Send the `/add` command to the bot:
```
/add
```

### Step 2: Enter Task Name
The bot will ask: **"Give the name of your task"**

Example:
```
Buy groceries
```

### Step 3: Enter Task Description
The bot will ask: **"Give the description of the task"**

Example:
```
Buy milk, bread, eggs, and vegetables from the supermarket
```

### Step 4: Enter Due Date and Time
The bot will ask: **"Tell me its due date and time in the format DD/MM/YYYY and hh:mm am/pm format"**

**Format:** `DD/MM/YYYY hh:mm am/pm`

Examples:
```
15/02/2026 03:30 pm
20/02/2026 09:00 am
28/02/2026 11:45 pm
```

### Confirmation
Once you complete all steps, the bot will confirm:
```
✅ Task Created Successfully!

Task: Buy groceries
Description: Buy milk, bread, eggs, and vegetables from the supermarket
Due Date: 15/02/2026 03:30 PM
Priority: Medium
Column: To Do
Board: [Your Board Name]
```

## Requirements

1. **Telegram Account Must Be Linked**: Your Telegram account must be linked to your TodoKanban account. If not linked, you'll see:
   ```
   ❌ Your Telegram account is not linked to TodoKanban. Please link it first.
   ```

2. **Must Have a Board**: You need to have created at least one board in TodoKanban. If you don't have any boards:
   ```
   ❌ You don't have any boards. Please create a board in TodoKanban first.
   ```

3. **Board Must Have Columns**: Your board must have at least one column. If there are no columns:
   ```
   ❌ Your board doesn't have any columns. Please add columns first.
   ```

## Task Details

When a task is created via Telegram, it will have:

| Property | Value |
|----------|-------|
| **Title** | Text you entered in Step 2 |
| **Description** | Text you entered in Step 3 |
| **Due Date** | Date and time you entered in Step 4 |
| **Priority** | Medium (default) |
| **Column** | First column in your default board |
| **Creator** | Your account |
| **Status** | To Do |

## Date Format Examples

### Valid Formats:
- `15/02/2026 03:30 pm` ✅
- `01/03/2026 09:00 am` ✅
- `28/02/2026 11:45 pm` ✅
- `10/12/2025 12:30 am` ✅ (midnight)
- `10/12/2025 12:30 pm` ✅ (noon)

### Invalid Formats:
- `2026-02-15 15:30` ❌ (Wrong date format)
- `15/02 03:30 pm` ❌ (Missing year)
- `15/02/2026 3:30 pm` ❌ (Hour must be 2 digits)
- `15-02-2026 03:30 pm` ❌ (Use / not -)

## Real-Time Updates

When you create a task via Telegram:
1. The task is immediately saved to the database
2. **All connected users** viewing the board see the new task appear in real-time (via WebSocket)
3. You receive a confirmation message from the bot

## Troubleshooting

### Error: "Invalid date format"
**Solution**: Use the exact format `DD/MM/YYYY hh:mm am/pm`
- Example: `15/02/2026 03:30 pm`
- Make sure to include the space between time and am/pm
- Use 2-digit hours (01-12, not 1-12)

### Error: "Task name cannot be empty"
**Solution**: Enter a non-empty task name. Task names can be up to 200 characters.

### Error: "Description cannot be empty"
**Solution**: Enter a description for the task. Descriptions can be up to 1000 characters.

### Error: "User not found"
**Solution**: 
1. Unlink your Telegram account from the app settings
2. Re-link it by clicking "Connect Telegram" and sending the `/start` command with the link code

### Task doesn't appear on the board
**Solution**:
1. Refresh the board page
2. Check that you're viewing the correct board
3. Check that the task was created (you should have received a confirmation message from the bot)

## Conversation Flow Diagram

```
User sends: /add
    ↓
Bot: "Give the name of your task"
    ↓
User: [enters task name]
    ↓
Bot: "Give the description of the task"
    ↓
User: [enters description]
    ↓
Bot: "Tell me its due date and time in format DD/MM/YYYY hh:mm am/pm"
    ↓
User: [enters due date and time]
    ↓
Bot: ✅ Task Created Successfully!
Task appears on board in real-time
```

## Notes

- Each conversation state is stored per user (by Telegram chat ID)
- If you start a `/add` conversation and don't complete it, you can start a new one by sending `/add` again
- Tasks are always created in the first column of your default board (usually "To Do")
- Due dates can be in the past or future
- The bot will notify connected users in real-time when a new task is created
