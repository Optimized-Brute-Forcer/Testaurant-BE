"""Workitem service."""
from app.database import get_database
from app.models.workitem_models import Workitem, WorkitemType
from app.services.counter_service import get_next_workitem_id
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime


class WorkitemService:
    """Service for workitem management."""
    
    @staticmethod
    async def create_workitem(
        organization_id: str, 
        workitem_data: dict, 
        user_id: str
    ) -> Workitem:
        """Create a new workitem."""
        db = get_database()
        
        workitem_id = await get_next_workitem_id()
        
        workitem = Workitem(
            workitem_id=workitem_id,
            organization_id=organization_id,
            **workitem_data,
            created_by=user_id,
            updated_by=user_id
        )
        
        await db.workitem_master.insert_one(workitem.model_dump())
        return workitem

    @staticmethod
    async def get_workitem(workitem_id: str, organization_id: str) -> Optional[Workitem]:
        """Get workitem by ID."""
        db = get_database()
        doc = await db.workitem_master.find_one({
            "workitem_id": workitem_id,
            "organization_id": organization_id,
            "is_deleted": False
        })
        if doc:
            return Workitem(**doc)
        return None

    @staticmethod
    async def update_workitem(
        workitem_id: str, 
        organization_id: str, 
        update_data: dict, 
        user_id: str
    ) -> Workitem:
        """Update a workitem."""
        db = get_database()
        
        update_doc = {
            **update_data,
            "updated_by": user_id,
            "updated_at": datetime.utcnow()
        }
        
        result = await db.workitem_master.find_one_and_update(
            {
                "workitem_id": workitem_id, 
                "organization_id": organization_id,
                "is_deleted": False
            },
            {"$set": update_doc},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workitem not found"
            )
            
        return Workitem(**result)

    @staticmethod
    async def delete_workitem(workitem_id: str, organization_id: str, user_id: str) -> bool:
        """Soft delete a workitem."""
        db = get_database()
        
        result = await db.workitem_master.update_one(
            {
                "workitem_id": workitem_id, 
                "organization_id": organization_id,
                "is_deleted": False
            },
            {
                "$set": {
                    "is_deleted": True,
                    "updated_by": user_id,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0

    @staticmethod
    async def list_workitems(
        organization_id: str,
        workitem_type: Optional[WorkitemType] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Workitem]:
        """List workitems with pagination and filtering."""
        db = get_database()
        
        query = {
            "organization_id": organization_id,
            "is_deleted": False
        }
        
        if workitem_type:
            query["workitem_type"] = workitem_type
            
        cursor = db.workitem_master.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        workitems = []
        async for doc in cursor:
            workitems.append(Workitem(**doc))
            
        return workitems
    @staticmethod
    async def count_workitems(organization_id: str) -> int:
        """Count workitems in an organization."""
        db = get_database()
        return await db.workitem_master.count_documents({
            "organization_id": organization_id,
            "is_deleted": False
        })
