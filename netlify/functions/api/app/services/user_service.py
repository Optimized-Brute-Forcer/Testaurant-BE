"""User service for resolving user information."""
from typing import List, Dict, Set
from app.database import get_database


class UserService:
    """Service for user-related operations."""

    @staticmethod
    async def resolve_user_names(user_ids: List[str]) -> Dict[str, str]:
        """
        Resolve a list of user IDs to their names.
        
        Args:
            user_ids: List of user IDs to resolve
            
        Returns:
            Dictionary mapping user_id to name
        """
        if not user_ids:
            return {}
            
        db = get_database()
        unique_ids = list(set(user_ids))
        
        # Batch fetch users from database
        cursor = db.users.find(
            {"user_id": {"$in": unique_ids}},
            {"user_id": 1, "name": 1}
        )
        
        user_map = {}
        async for user_doc in cursor:
            user_map[user_doc["user_id"]] = user_doc["name"]
            
        # Ensure every requested ID has an entry (fallback to ID)
        for uid in unique_ids:
            if uid not in user_map:
                user_map[uid] = uid
                
        return user_map
