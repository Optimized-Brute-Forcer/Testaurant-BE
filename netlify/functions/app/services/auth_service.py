"""Authentication service."""
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from app.config import settings
from app.database import get_database
from app.models.auth_models import (
    User, Organization, TokenPayload, UserRole,
    OrganizationMembership, LoginResponse
)
from app.services.counter_service import get_next_user_id, get_next_organization_id
from fastapi import HTTPException, status


class AuthService:
    """Authentication and authorization service."""
    
    @staticmethod
    async def verify_google_token(id_token_str: str) -> dict:
        """
        Verify Google ID token.
        
        Args:
            id_token_str: Google ID token
            
        Returns:
            Token payload with user info
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.google_client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
    
    @staticmethod
    async def get_or_create_user(google_info: dict) -> User:
        """
        Get existing user or create new user from Google info.
        
        Args:
            google_info: Google token payload
            
        Returns:
            User object
        """
        db = get_database()
        
        email = google_info.get('email')
        google_id = google_info.get('sub')
        name = google_info.get('name', email)
        
        # Check if user exists
        user_doc = await db.users.find_one({"email": email})
        
        if user_doc:
            return User(**user_doc)
        
        # Create new user
        user_id = await get_next_user_id()
        user = User(
            user_id=user_id,
            email=email,
            name=name,
            google_id=google_id,
            organizations=[]
        )
        
        await db.users.insert_one(user.model_dump())
        return user
    
    @staticmethod
    async def create_organization(org_name: str, creator_user_id: str) -> Organization:
        """
        Create a new organization.
        
        Args:
            org_name: Organization name
            creator_user_id: User ID of creator (will be made ORG_ADMIN)
            
        Returns:
            Organization object
        """
        db = get_database()
        
        org_id = await get_next_organization_id()
        org = Organization(
            organization_id=org_id,
            organization_name=org_name
        )
        
        await db.organizations.insert_one(org.model_dump())
        
        # Add creator as ORG_ADMIN
        await db.users.update_one(
            {"user_id": creator_user_id},
            {
                "$push": {
                    "organizations": OrganizationMembership(
                        organization_id=org_id,
                        role=UserRole.ORG_ADMIN
                    ).model_dump()
                }
            }
        )
        
        return org
    
    @staticmethod
    async def get_user_organizations(user_id: str) -> List[Organization]:
        """
        Get all organizations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of organizations
        """
        db = get_database()
        
        user_doc = await db.users.find_one({"user_id": user_id})
        if not user_doc:
            return []
        
        user = User(**user_doc)
        org_ids = [membership.organization_id for membership in user.organizations]
        
        orgs = []
        async for org_doc in db.organizations.find({"organization_id": {"$in": org_ids}}):
            orgs.append(Organization(**org_doc))
        
        return orgs
    
    @staticmethod
    def create_access_token(
        user_id: str,
        email: str,
        organization_id: Optional[str] = None,
        role: Optional[UserRole] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            user_id: User ID
            email: User email
            organization_id: Organization ID
            role: User role in organization
            
        Returns:
            JWT token string
        """
        expires = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "organization_id": organization_id,
            "role": role.value if role else None,
            "exp": expires
        }
        
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return token
    
    @staticmethod
    def decode_access_token(token: str) -> TokenPayload:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            return TokenPayload(
                user_id=payload["user_id"],
                email=payload["email"],
                organization_id=payload.get("organization_id"),
                role=UserRole(payload["role"]) if payload.get("role") else None,
                exp=datetime.fromtimestamp(payload["exp"])
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    @staticmethod
    async def login(id_token_str: str, organization_id: Optional[str] = None) -> LoginResponse:
        """
        Login user with Google ID token.
        
        Args:
            id_token_str: Google ID token
            organization_id: Optional organization ID to login to
            
        Returns:
            Login response with JWT token
            
        Raises:
            HTTPException: If login fails
        """
        # Verify Google token
        google_info = await AuthService.verify_google_token(id_token_str)
        
        # Get or create user
        user = await AuthService.get_or_create_user(google_info)
        
        # Get user's organizations
        organizations = await AuthService.get_user_organizations(user.user_id)
        
        # If no organizations and no organization_id provided, return user info with partial token
        if not organizations and not organization_id:
            access_token = AuthService.create_access_token(
                user.user_id,
                user.email
            )
            return LoginResponse(
                access_token=access_token,
                user=user,
                organizations=[],
                current_role=None
            )
        
        # If organization_id provided but user not member, or if no org selected yet
        if not organization_id:
            organization_id = organizations[0].organization_id
        
        # Get user's role in selected organization
        membership = next(
            (m for m in user.organizations if m.organization_id == organization_id),
            None
        )
        
        if not membership:
            # If they have other orgs, maybe they just haven't selected one yet or tried to join a new one
            if organizations:
                return LoginResponse(
                    access_token=None,
                    user=user,
                    organizations=organizations,
                    current_role=None
                )
            
            # This should not normally happen if organizations is empty as handled above
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organization"
            )
        
        # Create JWT token
        access_token = AuthService.create_access_token(
            user.user_id,
            user.email,
            organization_id,
            membership.role
        )
        
        return LoginResponse(
            access_token=access_token,
            user=user,
            organizations=organizations,
            current_role=membership.role
        )
