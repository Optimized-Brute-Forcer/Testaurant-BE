"""Database connection and setup."""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from typing import Optional


class Database:
    """MongoDB database manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB."""
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        cls.db = cls.client[settings.mongodb_db_name]
        
        # Create indexes
        await cls._create_indexes()
        
        print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls.client:
            cls.client.close()
            print("❌ Disconnected from MongoDB")
    
    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for performance."""
        if cls.db is None:
            return
        
        # Organizations
        await cls.db.organizations.create_index("organization_id", unique=True)
        
        # Users
        await cls.db.users.create_index("email", unique=True)
        await cls.db.users.create_index("google_id")
        
        # Workitems
        await cls.db.workitem_master.create_index([
            ("organization_id", 1),
            ("workitem_id", 1)
        ], unique=True)
        await cls.db.workitem_master.create_index([
            ("organization_id", 1),
            ("workitem_is_deleted", 1)
        ])
        
        # Testcases
        await cls.db.testcase_master.create_index([
            ("organization_id", 1),
            ("testcase_id", 1)
        ], unique=True)
        await cls.db.testcase_master.create_index([
            ("organization_id", 1),
            ("testcase_is_deleted", 1)
        ])
        
        # Testsuites
        await cls.db.testsuite_master.create_index([
            ("organization_id", 1),
            ("testsuite_id", 1)
        ], unique=True)
        await cls.db.testsuite_master.create_index([
            ("organization_id", 1),
            ("testsuite_is_deleted", 1)
        ])
        
        # Environment configs
        await cls.db.env_config.create_index([
            ("organization_id", 1),
            ("config_key", 1),
            ("environment", 1)
        ], unique=True)
        
        # Run audits
        await cls.db.run_workitem_audit.create_index([
            ("organization_id", 1),
            ("run_workitem_created_date", -1)
        ])
        await cls.db.run_testcase_audit.create_index([
            ("organization_id", 1),
            ("run_testcase_created_date", -1)
        ])
        
        # Counter
        await cls.db.counter_master.create_index("counter_name", unique=True)


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if Database.db is None:
        raise RuntimeError("Database not initialized")
    return Database.db
