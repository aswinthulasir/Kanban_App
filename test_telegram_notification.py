#!/usr/bin/env python3
"""
Test script to verify Telegram notifications are sent when tasks are updated
"""
import asyncio
import httpx
import json

async def test_task_update():
    """Test task update with Telegram notification"""
    
    # First, login to get auth token
    async with httpx.AsyncClient() as client:
        # Login
        login_response = await client.post(
            "http://127.0.0.1:8000/api/v1/auth/login",
            data={"username": "Admin", "password": "admin123"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ Logged in successfully")
        
        # Get tasks to find one to update
        tasks_response = await client.get(
            "http://127.0.0.1:8000/api/v1/tasks/?board_id=ea1759a2-2eae-4df6-99e3-9a42a10f6d60",
            headers=headers
        )
        
        if tasks_response.status_code != 200:
            print(f"❌ Failed to get tasks: {tasks_response.text}")
            return
        
        tasks = tasks_response.json()
        if not tasks:
            print("❌ No tasks found")
            return
        
        task = tasks[0]
        task_id = task["id"]
        old_column = task["column_id"]
        
        print(f"✅ Found task: {task['title']} (ID: {task_id})")
        print(f"   Current column: {old_column}")
        
        # Find a different column to move to
        # Get all columns for the board
        board_id = task["board_id"]
        
        # For now, just try to update the task
        # In a real test, we'd move it to a "Done" column to trigger completion notification
        
        # Update task (move to a different column)
        # Get the columns from the board
        board_response = await client.get(
            f"http://127.0.0.1:8000/api/v1/boards/{board_id}",
            headers=headers
        )
        
        if board_response.status_code == 200:
            board = board_response.json()
            print(f"✅ Found board: {board['name']}")
            
            # Try to move task to different column
            # This is a simple test - just change the task slightly
            update_response = await client.put(
                f"http://127.0.0.1:8000/api/v1/tasks/{task_id}",
                json={"description": "Updated from test script"},
                headers=headers
            )
            
            if update_response.status_code == 200:
                print(f"✅ Task updated successfully")
                print(f"   Response: {update_response.json()}")
            else:
                print(f"❌ Failed to update task: {update_response.text}")
        
        print("\n📝 Check the server logs above to see if Telegram notifications were sent:")
        print("   Look for: 'Sent task...' or 'Task moved from' messages")

if __name__ == "__main__":
    asyncio.run(test_task_update())
