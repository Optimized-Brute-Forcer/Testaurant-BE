"""Organization management service."""
from app.database import get_database
from app.models.organization_models import (
    Organization, Team, TeamMember, DatabaseCredentials,
    CreateOrganizationRequest, CreateTeamRequest, AddTeamMemberRequest,
    UserRole, OrganizationDetailsResponse, JoinRequestStatus, JoinRequest,
    EnvironmentVariable, AddEnvironmentVariableRequest, DatabaseType
)
from app.services.counter_service import get_next_organization_id, get_next_user_id
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets
from pydantic import SecretStr 


class OrganizationService:
    """Service for organization management."""
    
    @staticmethod
    async def create_organization(request: CreateOrganizationRequest, creator_user_id: str) -> Organization:
        """
        Create a new organization with admin, teams, and database credentials.
        """
        db = get_database()
        
        # Check if user is already admin of another org
        existing_org = await db.organizations.find_one({"admin_user_id": creator_user_id})
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already admin of another organization"
            )
        
        # Generate organization ID
        org_id = await get_next_organization_id()
        
        # Create organization
        org = Organization(
            organization_id=org_id,
            organization_name=request.organization_name,
            organization_description=request.organization_description,
            admin_user_id=creator_user_id,
            teams=[],
            database_credentials=request.database_credentials or []
        )
        
        await db.organizations.insert_one(org.model_dump())
        
        # Update user's role and membership
        membership = {
            "organization_id": org_id,
            "role": UserRole.ORG_ADMIN.value
        }
        await db.users.update_one(
            {"user_id": creator_user_id},
            {
                "$set": {
                    "organization_id": org_id,
                    "role": UserRole.ORG_ADMIN.value
                },
                "$push": {
                    "organizations": membership
                }
            }
        )
        
        return org
    
    @staticmethod
    async def get_organization(organization_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        db = get_database()
        org_doc = await db.organizations.find_one({"organization_id": organization_id})
        if org_doc:
            return Organization(**org_doc)
        return None
    
    @staticmethod
    async def create_team(organization_id: str, request: CreateTeamRequest, requester_user_id: str) -> Team:
        """Create a team within an organization."""
        db = get_database()
        
        org = await OrganizationService.get_organization(organization_id)
        if not org or org.admin_user_id != requester_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization admin can create teams"
            )
        
        team_id = f"TEAM-{secrets.token_hex(4).upper()}"
        manager_id = None
        if request.manager_email:
            manager_doc = await db.users.find_one({"email": request.manager_email})
            if manager_doc:
                manager_id = manager_doc["user_id"]
        
        team = Team(
            team_id=team_id,
            team_name=request.team_name,
            team_description=request.team_description,
            manager_id=manager_id,
            members=[]
        )
        
        await db.organizations.update_one(
            {"organization_id": organization_id},
            {
                "$push": {"teams": team.model_dump()},
                "$set": {"organization_updated_date": datetime.utcnow()}
            }
        )
        
        return team
    
    @staticmethod
    async def add_team_member(organization_id: str, request: AddTeamMemberRequest, requester_user_id: str) -> TeamMember:
        """Add a member to a team."""
        db = get_database()
        org = await OrganizationService.get_organization(organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        team = next((t for t in org.teams if t.team_id == request.team_id), None)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        if org.admin_user_id != requester_user_id and team.manager_id != requester_user_id:
            raise HTTPException(status_code=403, detail="Only admin or team manager can add members")
        
        user_doc = await db.users.find_one({"email": request.user_email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        member = TeamMember(
            user_id=user_doc["user_id"],
            email=user_doc["email"],
            name=user_doc["name"],
            role=request.role
        )
        
        await db.organizations.update_one(
            {"organization_id": organization_id, "teams.team_id": request.team_id},
            {
                "$push": {"teams.$.members": member.model_dump()},
                "$set": {"organization_updated_date": datetime.utcnow()}
            }
        )
        
        await db.users.update_one(
            {"user_id": user_doc["user_id"]},
            {
                "$set": {
                    "organization_id": organization_id,
                    "team_id": request.team_id,
                    "role": request.role.value
                }
            }
        )
        
        return member

    @staticmethod
    async def add_database_credentials(organization_id: str, credentials: List[DatabaseCredentials], requester_user_id: str) -> Organization:
        """Add database credentials to organization (Upsert logic)."""
        db = get_database()
        
        # We handle this as a list of additions/updates
        for cred in credentials:
            await db.organizations.update_one(
                {"organization_id": organization_id},
                {
                    "$pull": {
                        "database_credentials": {
                            "host": cred.host,
                            "port": cred.port,
                            "database_name": cred.database_name
                        }
                    }
                }
            )

            data = cred.model_dump()
            for k, v in data.items():
                if isinstance(v, SecretStr):
                    data[k] = v.get_secret_value()

            await db.organizations.update_one(
                {"organization_id": organization_id},
                {"$push": {"database_credentials": data}}
            )

        return await OrganizationService.get_organization(organization_id)


    @staticmethod
    async def submit_join_request(user_id: str, organization_id: str, role: UserRole = UserRole.ORG_MEMBER) -> bool:
        """Submit a request to join an organization."""
        db = get_database()
        org = await db.organizations.find_one({"organization_id": organization_id})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
            
        user_doc = await db.users.find_one({"user_id": user_id})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
            
        if any(m["organization_id"] == organization_id for m in user_doc.get("organizations", [])):
            return True 
            
        existing = await db.join_requests.find_one({
            "user_id": user_id,
            "organization_id": organization_id,
            "status": JoinRequestStatus.PENDING
        })
        if existing:
            return True
            
        request = JoinRequest(
            request_id=f"REQ-{secrets.token_hex(4).upper()}",
            user_id=user_id,
            user_name=user_doc.get("name", ""),
            user_email=user_doc.get("email", ""),
            organization_id=organization_id,
            organization_name=org["organization_name"],
            requested_role=role
        )
        
        await db.join_requests.insert_one(request.model_dump())
        return True

    @staticmethod
    async def list_join_requests(organization_id: str, status: Optional[JoinRequestStatus] = None) -> List[Dict[str, Any]]:
        """List join requests for an organization with user details."""
        db = get_database()
        query = {"organization_id": organization_id}
        if status:
            query["status"] = status
            
        requests = await db.join_requests.find(query).sort("created_at", -1).to_list(100)
        
        # Enrich with user information
        enriched_requests = []
        for r in requests:
            user_id = r.get("user_id")
            user_doc = await db.users.find_one({"user_id": user_id})
            
            enriched_request = {
                "_id": str(r["_id"]),
                "request_id": r.get("request_id"),
                "user_id": user_id,
                "name": user_doc.get("name") if user_doc else "Unknown User",
                "email": user_doc.get("email") if user_doc else "unknown@email.com",
                "requested_role": r.get("requested_role", UserRole.ORG_MEMBER.value),
                "organization_id": r.get("organization_id"),
                "status": r.get("status"),
                "created_at": r.get("created_at"),
                "resolved_at": r.get("resolved_at"),
                "resolved_by": r.get("resolved_by")
            }
            enriched_requests.append(enriched_request)
            
        return enriched_requests

    @staticmethod
    async def handle_join_request(organization_id: str, request_id: str, approve: bool, resolver_user_id: str) -> bool:
        """Approve or reject a join request."""
        db = get_database()
        request_doc = await db.join_requests.find_one({
            "request_id": request_id, 
            "organization_id": organization_id,
            "status": JoinRequestStatus.PENDING
        })
        if not request_doc:
            raise HTTPException(status_code=404, detail="Join request not found or already resolved")
            
        if approve:
            user_id = request_doc["user_id"]
            requested_role = request_doc.get("requested_role", UserRole.ORG_MEMBER.value)
            
            membership = {
                "organization_id": organization_id,
                "role": requested_role
            }
            await db.users.update_one(
                {"user_id": user_id},
                {
                    "$push": {"organizations": membership},
                    "$set": {
                        "organization_id": organization_id,
                        "role": requested_role
                    }
                }
            )
            status_val = JoinRequestStatus.APPROVED
        else:
            status_val = JoinRequestStatus.REJECTED
            
        await db.join_requests.update_one(
            {"request_id": request_id},
            {
                "$set": {
                    "status": status_val,
                    "resolved_at": datetime.utcnow(),
                    "resolved_by": resolver_user_id
                }
            }
        )
        return True

    @staticmethod
    async def get_user_requests(user_id: str) -> List[Dict[str, Any]]:
        """List all requests made by a user."""
        db = get_database()
        requests = await db.join_requests.find({"user_id": user_id}).to_list(100)
        for r in requests:
            r["_id"] = str(r["_id"])
        return requests

    @staticmethod
    async def list_organizations() -> List[Dict[str, Any]]:
        """List all active organizations."""
        db = get_database()
        orgs = []
        async for org_doc in db.organizations.find({"organization_is_active": True}):
            orgs.append({
                "organization_id": org_doc["organization_id"],
                "organization_name": org_doc["organization_name"],
                "organization_description": org_doc.get("organization_description", "")
            })
        return orgs

    @staticmethod
    async def get_organization_details(organization_id: str) -> OrganizationDetailsResponse:
        """Get detailed organization information."""
        org = await OrganizationService.get_organization(organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Simple count for members (inc admin)
        members_count = await get_database().users.count_documents({"organizations.organization_id": organization_id})
        
        return OrganizationDetailsResponse(
            organization=org,
            total_members=members_count,
            total_teams=len(org.teams),
            total_databases=len(org.database_credentials)
        )

    @staticmethod
    async def list_members(organization_id: str) -> List[Dict[str, Any]]:
        """List all members of an organization."""
        db = get_database()
        members = []
        async for user_doc in db.users.find({"organizations.organization_id": organization_id}):
            membership = next(m for m in user_doc["organizations"] if m["organization_id"] == organization_id)
            members.append({
                "user_id": user_doc["user_id"],
                "email": user_doc["email"],
                "name": user_doc["name"],
                "role": membership["role"]
            })
        return members

    @staticmethod
    async def delete_organization(organization_id: str) -> bool:
        """
        Delete an organization and clean up all associations.
        - Removes organization from all members' profiles
        - Deletes the organization document
        - Deletes associated join requests
        """
        db = get_database()
        
        # 1. Remove organization from all users' organizations array
        await db.users.update_many(
            {"organizations.organization_id": organization_id},
            {"$pull": {"organizations": {"organization_id": organization_id}}}
        )
        
        # 2. Reset active organization_id for users who have this as current org
        await db.users.update_many(
            {"organization_id": organization_id},
            {"$set": {"organization_id": None, "role": None, "team_id": None}}
        )
        
        # 3. Delete join requests
        await db.join_requests.delete_many({"organization_id": organization_id})
        
        # 4. Delete the organization itself
        result = await db.organizations.delete_one({"organization_id": organization_id})
        
        return result.deleted_count > 0

    @staticmethod
    async def leave_organization(user_id: str, organization_id: str) -> bool:
        """Allow a user to leave an organization."""
        db = get_database()
        
        # Check if user is the LAST member
        members_count = await db.users.count_documents({"organizations.organization_id": organization_id})
        
        org = await db.organizations.find_one({"organization_id": organization_id})
        
        # If admin tries to leave and they are NOT the last member, forbid it
        if org and org.get("admin_user_id") == user_id and members_count > 1:
            raise HTTPException(
                status_code=400, 
                detail="Organization administrators cannot leave while there are other members. Please transfer ownership or delete the organization."
            )
            
        return await OrganizationService.remove_member(organization_id, user_id)

    @staticmethod
    async def remove_member(organization_id: str, user_id: str) -> bool:
        """Remove a member from an organization."""
        db = get_database()
        
        # Check current member count
        members_count = await db.users.count_documents({"organizations.organization_id": organization_id})
        
        # Implement Auto-Delete: If this is the last member, delete the organization
        if members_count <= 1:
            return await OrganizationService.delete_organization(organization_id)

        org = await db.organizations.find_one({"organization_id": organization_id})
        
        # Normal removal logic: cannot remove admin if they are not the last one (handled above but safety check)
        if org and org.get("admin_user_id") == user_id:
             # This block should technically be unreachable via remove_member directly if validation is done,
             # but acts as a safeguard against manual API calls. 
             # However, since remove-member is also used by admin to kick others, 
             # we must ensure admin can't kick THEMSELVES unless it's via leave_organization logic.
             # But here we assume the caller has verified permissions.
             # If admin is being removed by another admin (future proofing), it's fine.
             # BUT specifically for "leave_organization", we allowed it if last member.
             pass

        await db.users.update_one(
            {"user_id": user_id},
            {"$pull": {"organizations": {"organization_id": organization_id}}}
        )
        
        if org and org.get("teams"):
            await db.organizations.update_one(
                {
                    "organization_id": organization_id, 
                    "teams": {"$exists": True, "$type": "array"}
                },
                {"$pull": {"teams.$[].members": {"user_id": user_id}}}
            )
        
        return True

    @staticmethod
    async def update_member_role(organization_id: str, target_user_id: str, new_role: UserRole) -> bool:
        """Update a member's role."""
        db = get_database()
        
        # Verify organization exists
        org = await db.organizations.find_one({"organization_id": organization_id})
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Verify target user is a member
        user = await db.users.find_one({
            "user_id": target_user_id,
            "organizations.organization_id": organization_id
        })
        if not user:
            raise HTTPException(status_code=404, detail="User is not a member of this organization")

        # Update role in users collection (organizations array)
        await db.users.update_one(
            {
                "user_id": target_user_id, 
                "organizations.organization_id": organization_id
            },
            {
                "$set": {
                    "organizations.$.role": new_role.value
                }
            }
        )
        
        # If this is their currently active org, update root role too
        if user.get("organization_id") == organization_id:
            await db.users.update_one(
                {"user_id": target_user_id},
                {"$set": {"role": new_role.value}}
            )
            
        return True

    @staticmethod
    async def list_database_credentials(organization_id: str) -> List[Dict[str, Any]]:
        """List database credentials with passwords masked."""
        org = await OrganizationService.get_organization(organization_id)
        if not org:
            return []
            
        masked_creds = []
        for cred in org.database_credentials:
            masked = cred.model_dump()
            masked["password"] = "********"  # Mask password
            masked_creds.append(masked)
            
        return masked_creds

    @staticmethod
    async def delete_database_credentials(organization_id: str, host: str, port: int, database_name: str) -> bool:
        """Delete database credentials."""
        db = get_database()
        
        # Pull from array where all 3 identifying fields match
        result = await db.organizations.update_one(
            {"organization_id": organization_id},
            {
                "$pull": {
                    "database_credentials": {
                        "host": host,
                        "port": port,
                        "database_name": database_name
                    }
                }
            }
        )
        return result.modified_count > 0

    @staticmethod
    async def list_environment_variables(organization_id: str) -> List[EnvironmentVariable]:
        """List environment variables."""
        org = await OrganizationService.get_organization(organization_id)
        if not org:
            return []
        return org.environment_variables

    @staticmethod
    async def add_environment_variable(
        organization_id: str, 
        request: AddEnvironmentVariableRequest
    ) -> List[EnvironmentVariable]:
        """Add or update an environment variable."""
        db = get_database()
        
        new_var = EnvironmentVariable(
            key=request.key,
            value=request.value,
            description=request.description
        )
        
        # Remove existing if present (upsert logic)
        await db.organizations.update_one(
            {"organization_id": organization_id},
            {"$pull": {"environment_variables": {"key": request.key}}}
        )
        
        # Add new
        await db.organizations.update_one(
            {"organization_id": organization_id},
            {"$push": {"environment_variables": new_var.model_dump()}}
        )
        
        return await OrganizationService.list_environment_variables(organization_id)

    @staticmethod
    async def delete_environment_variable(organization_id: str, key: str) -> List[EnvironmentVariable]:
        """Delete an environment variable."""
        db = get_database()
        
        await db.organizations.update_one(
            {"organization_id": organization_id},
            {"$pull": {"environment_variables": {"key": key}}}
        )
        
        return await OrganizationService.list_environment_variables(organization_id)
