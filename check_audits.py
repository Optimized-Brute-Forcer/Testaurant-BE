import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_audits():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DATABASE_NAME", "testaurant")]
    
    print("--- run_workitem_audit ---")
    async for audit in db.run_workitem_audit.find().limit(5):
        print(f"ID: {audit.get('run_workitem_id')}, Org: {audit.get('organization_id')}, Status: {audit.get('execution_status')}")
    
    print("\n--- Users ---")
    async for user in db.users.find():
        print(f"ID: {user.get('user_id')}, Org Membership: {[m.get('organization_id') for m in user.get('organizations', [])]}")

asyncio.run(check_audits())
