import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DATABASE_NAME", "testaurant")]
    
    print("--- Users ---")
    async for user in db.users.find():
        print(f"ID: {user.get('user_id')}, Name: {user.get('name')}, Email: {user.get('email')}")
        
    print("\n--- Workitems ---")
    async for wi in db.workitem_master.find().limit(2):
        print(f"ID: {wi.get('workitem_id')}, Title: {wi.get('workitem_title')}, CreatedBy: {wi.get('created_by')}")

asyncio.run(check_db())
