"""RBAC middleware and dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import AuthService
from app.models.auth_models import TokenPayload, UserRole


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Token payload with user info
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    return AuthService.decode_access_token(token)


async def require_org_member(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Require user to be at least an organization member.
    
    Args:
        current_user: Current user token payload
        
    Returns:
        Token payload
    """
    return current_user


async def require_org_admin(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Require user to be an organization admin.
    
    Args:
        current_user: Current user token payload
        
    Returns:
        Token payload
        
    Raises:
        HTTPException: If user is not org admin
    """
    if current_user.role not in [UserRole.ORG_ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access required"
        )
    return current_user


async def require_super_admin(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Require user to be a super admin.
    
    Args:
        current_user: Current user token payload
        
    Returns:
        Token payload
        
    Raises:
        HTTPException: If user is not super admin
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def get_organization_id(current_user: TokenPayload = Depends(get_current_user)) -> str:
    """
    Get organization ID from current user context.
    
    Args:
        current_user: Current user token payload
        
    Returns:
        Organization ID
    """
    return current_user.organization_id
