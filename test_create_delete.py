#!/usr/bin/env python3
"""Test creating and deleting tasks via API to check notifications."""

import asyncio
import aiohttp
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_task_creation():
    """Test task creation notification."""
    async with aiohttp.ClientSession() as session:
        # Login
        login_data = {"username": "Admin", "password": "admin123"}
        async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as resp:
            if resp.status != 200:
                print(f"❌ Login failed: {resp.status}")
                return
            
            login_response = await resp.json()
            token = login_response["access_token"]
            print(f"✅ Logged in, token: {token[:20]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get board ID
        async with session.get(f"{BASE_URL}/api/v1/boards", headers=headers) as resp:
            if resp.status != 200:
                print(f"❌ Get boards failed: {resp.status}")
                return
            
            boards = await resp.json()
            if not boards:
                print("❌ No boards found")
                return
            
            board_id = boards[0]["id"]
            print(f"✅ Found board: {boards[0]['name']} ({board_id})")
        
        # Get first column
        async with session.get(f"{BASE_URL}/api/v1/columns?board_id={board_id}", headers=headers) as resp:
            if resp.status != 200:
                print(f"❌ Get columns failed: {resp.status}")
                return
            
            columns = await resp.json()
            if not columns:
                print("❌ No columns found")
                return
            
            column_id = columns[0]["id"]
            print(f"✅ Found column: {columns[0]['name']} ({column_id})")
        
        # Create task
        task_data = {
            "title": "Test Notification Task",
            "description": "Testing telegram notifications for create/delete",
            "board_id": board_id,
            "column_id": column_id,
            "priority": "HIGH",
            "due_date": "2026-02-10T00:00:00"
        }
        
        print("\n📝 Creating task...")
        async with session.post(f"{BASE_URL}/api/v1/tasks", json=task_data, headers=headers) as resp:
            if resp.status != 201:
                print(f"❌ Create task failed: {resp.status}")
                error = await resp.text()
                print(f"   Error: {error}")
                return
            
            task = await resp.json()
            task_id = task["id"]
            print(f"✅ Task created: {task['title']} ({task_id})")
        
        # Wait to see notification in server logs
        await asyncio.sleep(2)
        
        # Delete task
        print("\n🗑️ Deleting task...")
        async with session.delete(f"{BASE_URL}/api/v1/tasks/{task_id}", headers=headers) as resp:
            if resp.status != 204:
                print(f"❌ Delete task failed: {resp.status}")
                error = await resp.text()
                print(f"   Error: {error}")
                return
            
            print(f"✅ Task deleted successfully")
        
        # Wait to see notification in server logs
        await asyncio.sleep(2)
        
        print("\n✅ Test completed! Check server logs for notification details.")

if __name__ == "__main__":
    asyncio.run(test_task_creation())
