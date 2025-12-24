"""Testsuite service."""
from app.database import get_database
from app.models.testsuite_models import Testsuite
from app.services.counter_service import get_next_testsuite_id
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime


class TestsuiteService:
    """Service for testsuite management."""
    
    @staticmethod
    async def create_testsuite(
        organization_id: str, 
        testsuite_data: dict, 
        user_id: str
    ) -> Testsuite:
        """Create a new testsuite."""
        db = get_database()
        
        testsuite_id = await get_next_testsuite_id()
        
        testsuite = Testsuite(
            testsuite_id=testsuite_id,
            organization_id=organization_id,
            **testsuite_data,
            created_by=user_id,
            updated_by=user_id
        )
        
        await db.testsuite_master.insert_one(testsuite.model_dump())
        return testsuite

    @staticmethod
    async def get_testsuite(testsuite_id: str, organization_id: str) -> Optional[Testsuite]:
        """Get testsuite by ID."""
        db = get_database()
        doc = await db.testsuite_master.find_one({
            "testsuite_id": testsuite_id,
            "organization_id": organization_id,
            "is_deleted": False
        })
        if doc:
            return Testsuite(**doc)
        return None

    @staticmethod
    async def update_testsuite(
        testsuite_id: str, 
        organization_id: str, 
        update_data: dict, 
        user_id: str
    ) -> Testsuite:
        """Update a testsuite."""
        db = get_database()
        
        update_doc = {
            **update_data,
            "updated_by": user_id,
            "updated_at": datetime.utcnow()
        }
        
        result = await db.testsuite_master.find_one_and_update(
            {
                "testsuite_id": testsuite_id, 
                "organization_id": organization_id,
                "is_deleted": False
            },
            {"$set": update_doc},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Testsuite not found"
            )
            
        return Testsuite(**result)

    @staticmethod
    async def delete_testsuite(testsuite_id: str, organization_id: str, user_id: str) -> bool:
        """Soft delete a testsuite."""
        db = get_database()
        
        result = await db.testsuite_master.update_one(
            {
                "testsuite_id": testsuite_id, 
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
    async def list_testsuites(
        organization_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Testsuite]:
        """List testsuites with pagination."""
        db = get_database()
        
        query = {
            "organization_id": organization_id,
            "is_deleted": False
        }
            
        cursor = db.testsuite_master.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        testsuites = []
        async for doc in cursor:
            testsuites.append(Testsuite(**doc))
            
        return testsuites

    @staticmethod
    async def count_testsuites(organization_id: str) -> int:
        """Count testsuites in an organization."""
        db = get_database()
        return await db.testsuite_master.count_documents({
            "organization_id": organization_id,
            "is_deleted": False
        })
