"""Testcase service."""
from app.database import get_database
from app.models.testcase_models import Testcase
from app.services.counter_service import get_next_testcase_id
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime


class TestcaseService:
    """Service for testcase management."""
    
    @staticmethod
    async def create_testcase(
        organization_id: str, 
        testcase_data: dict, 
        user_id: str
    ) -> Testcase:
        """Create a new testcase."""
        db = get_database()
        
        testcase_id = await get_next_testcase_id()
        
        testcase = Testcase(
            testcase_id=testcase_id,
            organization_id=organization_id,
            **testcase_data,
            created_by=user_id,
            updated_by=user_id
        )
        
        await db.testcase_master.insert_one(testcase.model_dump())
        return testcase

    @staticmethod
    async def get_testcase(testcase_id: str, organization_id: str) -> Optional[Testcase]:
        """Get testcase by ID."""
        db = get_database()
        doc = await db.testcase_master.find_one({
            "testcase_id": testcase_id,
            "organization_id": organization_id,
            "is_deleted": False
        })
        if doc:
            return Testcase(**doc)
        return None

    @staticmethod
    async def update_testcase(
        testcase_id: str, 
        organization_id: str, 
        update_data: dict, 
        user_id: str
    ) -> Testcase:
        """Update a testcase."""
        db = get_database()
        
        update_doc = {
            **update_data,
            "updated_by": user_id,
            "updated_at": datetime.utcnow()
        }
        
        result = await db.testcase_master.find_one_and_update(
            {
                "testcase_id": testcase_id, 
                "organization_id": organization_id,
                "is_deleted": False
            },
            {"$set": update_doc},
            return_document=True
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Testcase not found"
            )
            
        return Testcase(**result)

    @staticmethod
    async def delete_testcase(testcase_id: str, organization_id: str, user_id: str) -> bool:
        """Soft delete a testcase."""
        db = get_database()
        
        result = await db.testcase_master.update_one(
            {
                "testcase_id": testcase_id, 
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
    async def list_testcases(
        organization_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Testcase]:
        """List testcases with pagination."""
        db = get_database()
        
        query = {
            "organization_id": organization_id,
            "is_deleted": False
        }
            
        cursor = db.testcase_master.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        testcases = []
        async for doc in cursor:
            testcases.append(Testcase(**doc))
            
        return testcases

    @staticmethod
    async def count_testcases(organization_id: str) -> int:
        """Count testcases in an organization."""
        db = get_database()
        return await db.testcase_master.count_documents({
            "organization_id": organization_id,
            "is_deleted": False
        })
