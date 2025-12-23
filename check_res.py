import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_resolution():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DATABASE_NAME", "testaurant")]
    
    unique_ids = ["USR-00001"]
    
    print(f"Querying for: {unique_ids}")
    cursor = db.users.find(
        {"user_id": {"$in": unique_ids}},
        {"user_id": 1, "name": 1}
    )
    
    user_map = {}
    async for user_doc in cursor:
        print(f"Found doc: {user_doc}")
        user_map[user_doc["user_id"]] = user_doc["name"]
        
    print(f"Resulting user_map: {user_map}")

asyncio.run(check_resolution())
