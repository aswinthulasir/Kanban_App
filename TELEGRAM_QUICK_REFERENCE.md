# Quick Reference - Telegram Task Creation

## Command
```
/add
```

## Conversation Steps

### Step 1️⃣ - Task Name
**Bot asks:** "Give the name of your task"

**You enter:** Any task name (up to 200 characters)

Example: `Buy groceries`

---

### Step 2️⃣ - Task Description
**Bot asks:** "Give the description of the task"

**You enter:** Task description (up to 1000 characters)

Example: `Buy milk, bread, eggs, and vegetables from the supermarket`

---

### Step 3️⃣ - Due Date & Time
**Bot asks:** "Tell me its due date and time in the format DD/MM/YYYY and hh:mm am/pm format"

**Format:** `DD/MM/YYYY hh:mm am/pm`

**You enter:** Date and time

Examples:
- `15/02/2026 03:30 pm` (3:30 PM)
- `01/03/2026 09:00 am` (9:00 AM)
- `28/02/2026 11:45 pm` (11:45 PM)

---

## Result ✅

Task is created with:
- ✅ Your title
- ✅ Your description
- ✅ Your due date/time
- ✅ Priority: Medium
- ✅ Column: To Do (first column)
- ✅ Real-time update on board

---

## Date Format Cheat Sheet

| Example | Means |
|---------|-------|
| `15/02/2026 03:30 pm` | Feb 15, 2026 at 3:30 PM |
| `01/03/2026 09:00 am` | Mar 1, 2026 at 9:00 AM |
| `25/12/2025 11:59 pm` | Dec 25, 2025 at 11:59 PM |
| `10/01/2026 12:00 am` | Jan 10, 2026 at 12:00 AM |
| `10/01/2026 12:00 pm` | Jan 10, 2026 at 12:00 PM |

---

## Common Mistakes ❌

| Wrong | Right | Issue |
|-------|-------|-------|
| `2026-02-15 15:30` | `15/02/2026 03:30 pm` | Wrong date format |
| `15/02 03:30 pm` | `15/02/2026 03:30 pm` | Missing year |
| `15-02-2026 03:30 pm` | `15/02/2026 03:30 pm` | Use / not - |
| `15/02/2026 3:30 pm` | `15/02/2026 03:30 pm` | Hour must be 2 digits |
| `15/02/2026 03:30pm` | `15/02/2026 03:30 pm` | Space before am/pm |

---

## Requirements

Before using `/add`:
1. ✅ Telegram account linked to TodoKanban
2. ✅ At least one board created
3. ✅ Board has at least one column

---

## Troubleshooting

**"Not linked" error?**
→ Go to app settings and click "Connect Telegram"

**"No boards" error?**
→ Create a board in the app first

**"No columns" error?**
→ Add columns to your board

**"Invalid date" error?**
→ Use format: `DD/MM/YYYY hh:mm am/pm`

---

## Example Workflow

```
You: /add
Bot: 📝 Create New Task
     Step 1/3: Give the name of your task

You: Fix login bug
Bot: ✅ Task name saved: Fix login bug
     Step 2/3: Give the description of the task

You: Users unable to reset password via email
Bot: ✅ Description saved: Users unable to reset password via email
     Step 3/3: Tell me its due date and time in format DD/MM/YYYY hh:mm am/pm

You: 20/02/2026 05:00 pm
Bot: ✅ Task Created Successfully!
     Task: Fix login bug
     Description: Users unable to reset password via email
     Due Date: 20/02/2026 05:00 PM
     Priority: Medium
     Column: To Do
     Board: My Project Board
```

Task appears on your board immediately! 🎉
