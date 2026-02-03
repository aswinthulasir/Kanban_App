#!/bin/bash
# Test creating and deleting tasks via API

TOKEN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Admin","password":"admin123"}')

echo "Login response: $TOKEN_RESPONSE"
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

# Get boards
BOARDS=$(curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/v1/boards)
echo "Boards: $BOARDS"

BOARD_ID=$(echo $BOARDS | jq -r '.[0].id')
echo "Board ID: $BOARD_ID"

# Get columns
COLUMNS=$(curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/api/v1/columns?board_id=$BOARD_ID")
echo "Columns: $COLUMNS"

COLUMN_ID=$(echo $COLUMNS | jq -r '.[0].id')
echo "Column ID: $COLUMN_ID"

# Create task
echo "Creating task..."
TASK=$(curl -s -X POST http://127.0.0.1:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Notification Task\",
    \"description\": \"Testing telegram notifications for create/delete\",
    \"board_id\": \"$BOARD_ID\",
    \"column_id\": \"$COLUMN_ID\",
    \"priority\": \"HIGH\",
    \"due_date\": \"2026-02-10T00:00:00\"
  }")

echo "Task created: $TASK"
TASK_ID=$(echo $TASK | jq -r '.id')
echo "Task ID: $TASK_ID"

sleep 2

# Delete task
echo "Deleting task..."
curl -s -X DELETE "http://127.0.0.1:8000/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"

echo "Task deleted"
sleep 2

echo "Test completed! Check server logs for notification details."
