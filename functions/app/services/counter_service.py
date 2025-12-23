"""Counter service for generating unique IDs."""
from app.database import get_database
from typing import Optional


class CounterService:
    """Service for managing auto-incrementing counters."""
    
    @staticmethod
    async def get_next_id(counter_name: str, prefix: str) -> str:
        """
        Get next ID for a counter.
        
        Args:
            counter_name: Name of the counter (e.g., 'workitem', 'testcase')
            prefix: Prefix for the ID (e.g., 'WI', 'TC')
            
        Returns:
            Next ID in format {PREFIX}-{COUNTER}
        """
        db = get_database()
        
        # Find and update counter atomically
        result = await db.counter_master.find_one_and_update(
            {"counter_name": counter_name},
            {"$inc": {"counter_value": 1}},
            upsert=True,
            return_document=True
        )
        
        counter_value = result.get("counter_value", 1)
        return f"{prefix}-{counter_value:05d}"


async def get_next_workitem_id() -> str:
    """Get next workitem ID."""
    return await CounterService.get_next_id("workitem", "WI")


async def get_next_testcase_id() -> str:
    """Get next testcase ID."""
    return await CounterService.get_next_id("testcase", "TC")


async def get_next_testsuite_id() -> str:
    """Get next testsuite ID."""
    return await CounterService.get_next_id("testsuite", "TS")


async def get_next_run_workitem_id() -> str:
    """Get next run workitem ID."""
    return await CounterService.get_next_id("run_workitem", "RWI")


async def get_next_run_testcase_id() -> str:
    """Get next run testcase ID."""
    return await CounterService.get_next_id("run_testcase", "RTC")


async def get_next_run_testsuite_id() -> str:
    """Get next run testsuite ID."""
    return await CounterService.get_next_id("run_testsuite", "RTS")


async def get_next_organization_id() -> str:
    """Get next organization ID."""
    return await CounterService.get_next_id("organization", "ORG")


async def get_next_user_id() -> str:
    """Get next user ID."""
    return await CounterService.get_next_id("user", "USR")
