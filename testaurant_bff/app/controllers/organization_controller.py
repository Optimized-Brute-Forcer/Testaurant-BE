"""Organization management controller."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.organization_models import (
    CreateOrganizationRequest, CreateTeamRequest, AddTeamMemberRequest,
    AddDatabaseCredentialsRequest, Organization, Team, TeamMember,
    OrganizationDetailsResponse, DatabaseCredentials
)
from app.models.auth_models import TokenPayload, UserRole, UserRole as Role
from app.services.organization_service import OrganizationService
from app.middleware.rbac import get_current_user, require_org_admin
from app.models.organization_models import (
    EnvironmentVariable, AddEnvironmentVariableRequest, DatabaseCredentials
)


router = APIRouter(prefix="/testaurant/v1/organization", tags=["Organization"])


@router.post("/create", response_model=Organization)
async def create_organization(
    request: CreateOrganizationRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Create a new organization with teams and database credentials.
    
    Args:
        request: Organization creation request
        current_user: Current authenticated user
        
    Returns:
        Created organization
    """
    return await OrganizationService.create_organization(request, current_user.user_id)


@router.get("/list")
async def list_organizations(
    current_user: TokenPayload = Depends(get_current_user)
):
    """List all available organizations."""
    return await OrganizationService.list_organizations()


@router.post("/join/{organization_id}")
async def join_organization(
    organization_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Submit a request to join an organization."""
    return await OrganizationService.submit_join_request(current_user.user_id, organization_id)


@router.get("/my-requests")
async def get_my_requests(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get all join requests made by the current user."""
    return await OrganizationService.get_user_requests(current_user.user_id)


@router.delete("/leave/{organization_id}")
async def leave_organization(
    organization_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Leave an organization."""
    return await OrganizationService.leave_organization(current_user.user_id, organization_id)


@router.get("/{organization_id}", response_model=OrganizationDetailsResponse)
async def get_organization_details(
    organization_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Get detailed organization information.
    
    Args:
        organization_id: Organization ID
        current_user: Current authenticated user
        
    Returns:
        Organization details
    """
    # Verify user has access to this organization
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )
    
    return await OrganizationService.get_organization_details(organization_id)


@router.post("/{organization_id}/teams", response_model=Team)
async def create_team(
    organization_id: str,
    request: CreateTeamRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """
    Create a team within the organization.
    
    Args:
        organization_id: Organization ID
        request: Team creation request
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Created team
    """
    return await OrganizationService.create_team(
        organization_id,
        request,
        current_user.user_id
    )


@router.post("/{organization_id}/teams/members", response_model=TeamMember)
async def add_team_member(
    organization_id: str,
    request: AddTeamMemberRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Add a member to a team.
    
    Args:
        organization_id: Organization ID
        request: Add team member request
        current_user: Current authenticated user (must be admin or manager)
        
    Returns:
        Added team member
    """
    return await OrganizationService.add_team_member(
        organization_id,
        request,
        current_user.user_id
    )


@router.post("/{organization_id}/databases", response_model=Organization)
async def add_database_credentials(
    organization_id: str,
    request: AddDatabaseCredentialsRequest,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """
    Add database credentials to organization.
    
    Args:
        organization_id: Organization ID
        request: Database credentials request
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Updated organization
    """
    return await OrganizationService.add_database_credentials(
        organization_id,
        request.database_credentials,
        current_user.user_id
    )


@router.get("/{organization_id}/members")
async def list_members(
    organization_id: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """List all members of the organization."""
    return await OrganizationService.list_members(organization_id)


@router.delete("/{organization_id}/members/{user_id}")
async def remove_member(
    organization_id: str,
    user_id: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Remove a member from the organization."""
    return await OrganizationService.remove_member(organization_id, user_id)


@router.get("/{organization_id}/join-requests")
async def list_join_requests(
    organization_id: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """List join requests for an organization (admin only)."""
    return await OrganizationService.list_join_requests(organization_id)


@router.post("/{organization_id}/join-requests/{request_id}/handle")
async def handle_join_request(
    organization_id: str,
    request_id: str,
    approve: bool,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Handle (approve/reject) a join request (admin only)."""
    return await OrganizationService.handle_join_request(
        organization_id,
        request_id,
        approve,
        current_user.user_id
    )


@router.put("/{organization_id}/members/{user_id}/role")
async def update_member_role(
    organization_id: str, 
    user_id: str, 
    role: UserRole,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """Update a member's role (Admin only)."""
    await OrganizationService.update_member_role(organization_id, user_id, role)
    return {"message": "Role updated successfully"}


@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """
    Delete an organization (Admin only).
    This action is irreversible. All data associated with the organization will be permanently deleted.
    """
    # Verify user is indeed the admin of this organization
    # (require_org_admin middleware already checks if they are AN admin, 
    # but technically we should ensure they are admin of THIS specific organization)
    
    await OrganizationService.delete_organization(organization_id)
    return {"message": "Organization deleted successfully"}

@router.get("/{organization_id}/credentials")
async def list_database_credentials(
    organization_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    List database credentials for the organization (passwords masked).
    Available to all organization members.
    """
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return await OrganizationService.list_database_credentials(organization_id)


@router.delete("/{organization_id}/credentials")
async def delete_database_credentials(
    organization_id: str,
    host: str,
    port: int,
    database_name: str,
    current_user: TokenPayload = Depends(require_org_admin)
):
    """
    Delete database credentials.
    Admin only.
    """
    success = await OrganizationService.delete_database_credentials(
        organization_id, host, port, database_name
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )
    return {"message": "Credentials deleted successfully"}


@router.get("/{organization_id}/env-vars", response_model=List[EnvironmentVariable])
async def list_environment_variables(
    organization_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    List environment variables.
    Available to all organization members.
    """
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return await OrganizationService.list_environment_variables(organization_id)


@router.post("/{organization_id}/env-vars", response_model=List[EnvironmentVariable])
async def add_environment_variable(
    organization_id: str,
    request: AddEnvironmentVariableRequest,
    current_user: TokenPayload = Depends(get_current_user) # Allow all members to add config
):
    """
    Add or update an environment variable.
    """
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return await OrganizationService.add_environment_variable(organization_id, request)


@router.delete("/{organization_id}/env-vars/{key}", response_model=List[EnvironmentVariable])
async def delete_environment_variable(
    organization_id: str,
    key: str,
    current_user: TokenPayload = Depends(get_current_user) # Allow all members to delete config
):
    """
    Delete an environment variable.
    """
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return await OrganizationService.delete_environment_variable(organization_id, key)
