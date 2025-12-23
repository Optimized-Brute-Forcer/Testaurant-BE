"""Authentication and authorization models."""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    ORG_MANAGER = "ORG_MANAGER"
    ORG_MEMBER = "ORG_MEMBER"


class OrganizationMembership(BaseModel):
    """User's membership in an organization."""
    organization_id: str
    role: UserRole


class Organization(BaseModel):
    """Organization model."""
    organization_id: str
    organization_name: str
    organization_created_date: datetime = Field(default_factory=datetime.utcnow)
    organization_is_active: bool = True


class User(BaseModel):
    """User model."""
    user_id: str
    email: EmailStr
    name: str
    google_id: str
    organizations: List[OrganizationMembership] = []
    user_created_date: datetime = Field(default_factory=datetime.utcnow)


class GoogleOAuthToken(BaseModel):
    """Google OAuth token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    id_token: str



class TokenPayload(BaseModel):
    """JWT token payload."""
    user_id: str
    email: str
    organization_id: Optional[str] = None
    role: Optional[UserRole] = None
    exp: datetime


class LoginRequest(BaseModel):
    """Login request with Google ID token."""
    id_token: str
    organization_id: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: Optional[str] = None
    token_type: str = "Bearer"
    user: User
    organizations: List[Organization]
    current_role: Optional[UserRole] = None


class CreateOrganizationRequest(BaseModel):
    """Request to create a new organization."""
    organization_name: str


class AddUserToOrganizationRequest(BaseModel):
    """Request to add user to organization."""
    email: EmailStr
    role: UserRole = UserRole.ORG_MEMBER
