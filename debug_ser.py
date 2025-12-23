import asyncio
import json
from datetime import datetime
from typing import List
from pydantic import TypeAdapter
from app.models.workitem_models import Workitem, WorkitemType
from app.services.user_service import UserService
from app.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_serialization():
    await Database.connect()
    db = Database.db
    
    # Get workitems
    cursor = db.workitem_master.find({"organization_id": "ORG-00001", "is_deleted": False})
    items = []
    async for doc in cursor:
        items.append(Workitem(**doc))
        
    print(f"BFF: Fetched {len(items)} items")
    
    # Resolve names
    user_ids = []
    for item in items:
        if item.created_by: user_ids.append(item.created_by)
    
    user_map = await UserService.resolve_user_names(user_ids)
    print(f"BFF: user_map = {user_map}")
    
    for item in items:
        item.created_by_name = user_map.get(item.created_by, item.created_by)
        print(f"BFF: Enriched {item.workitem_id} with {item.created_by_name}")
        
    # Serialize as FastAPI would
    adapter = TypeAdapter(List[Workitem])
    serialized = adapter.dump_python(items, mode='json', by_alias=True)
    
    print("--- Serialized JSON (first item) ---")
    if serialized:
        print(json.dumps(serialized[0], indent=2))
    
    await Database.disconnect()

asyncio.run(debug_serialization())
