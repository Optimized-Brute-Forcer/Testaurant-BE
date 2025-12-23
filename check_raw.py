import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_raw():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    db = client[os.getenv("DATABASE_NAME", "testaurant")]
    
    wi = await db.workitem_master.find_one()
    print(f"Raw Workitem keys: {list(wi.keys())}")
    for k, v in wi.items():
        if "id" in k.lower() or "by" in k.lower() or "date" in k.lower():
            print(f"  {k}: {v}")

asyncio.run(check_raw())
