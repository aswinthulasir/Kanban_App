#!/usr/bin/env python3
"""Debug script to check Telegram status and user data"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import engine
from app.models.user import User
from app.models.task import Task

async def check_telegram_status():
    """Check current user's Telegram status"""
    async with AsyncSession(engine) as session:
        # Get Admin user
        result = await session.execute(select(User).where(User.username == "Admin"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Admin user not found")
            return
        
        print(f"✅ Found user: {user.username}")
        print(f"   Full name: {user.full_name}")
        print(f"   Telegram Chat ID: {user.telegram_chat_id}")
        print(f"   Is Linked: {'✅ YES' if user.telegram_chat_id else '❌ NO'}")
        
        # Check tasks
        print("\n📋 Tasks in the board:")
        result = await session.execute(
            select(Task).where(Task.board_id == "ea1759a2-2eae-4df6-99e3-9a42a10f6d60").limit(5)
        )
        tasks = result.scalars().all()
        
        for i, task in enumerate(tasks, 1):
            print(f"\n   {i}. {task.title}")
            print(f"      - Column: {task.column_id}")
            print(f"      - Assigned to: {task.assigned_to_id}")
            print(f"      - Created by: {task.creator_id}")

if __name__ == "__main__":
    asyncio.run(check_telegram_status())
