"""Authentication controller."""
from fastapi import APIRouter, HTTPException, status
from app.models.auth_models import (
    LoginRequest, LoginResponse, CreateOrganizationRequest,
    Organization
)
from app.services.auth_service import AuthService
from app.middleware.rbac import get_current_user
from fastapi import Depends
from app.models.auth_models import TokenPayload


router = APIRouter(prefix="/testaurant/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login with Google ID token.
    
    Args:
        request: Login request with Google ID token
        
    Returns:
        Login response with JWT token and user info
    """
    return await AuthService.login(request.id_token, request.organization_id)


@router.post("/create-organization", response_model=Organization)
async def create_organization(
    request: CreateOrganizationRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Create a new organization.
    
    Args:
        request: Organization creation request
        current_user: Current authenticated user
        
    Returns:
        Created organization
    """
    return await AuthService.create_organization(
        request.organization_name,
        current_user.user_id
    )


@router.get("/me")
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information from token
    """
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "organization_id": current_user.organization_id,
        "role": current_user.role
    }
