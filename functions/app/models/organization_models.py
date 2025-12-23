"""Enhanced organization models with teams and database credentials."""
from pydantic import BaseModel, Field, SecretStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles within an organization."""
    ORG_ADMIN = "ORG_ADMIN"
    ORG_MANAGER = "ORG_MANAGER"
    ORG_MEMBER = "ORG_MEMBER"


class DatabaseType(str, Enum):
    """Supported database types."""
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRESQL"
    MONGODB = "MONGODB"


class DatabaseCredentials(BaseModel):
    """Database connection credentials."""
    database_type: DatabaseType
    host: str
    port: int
    username: str
    password: SecretStr  # Encrypted in storage
    database_name: str
    additional_params: Optional[Dict[str, Any]] = None  # SSL, etc.


class TeamMember(BaseModel):
    """Team member information."""
    user_id: str
    email: str
    name: str
    role: UserRole
    joined_date: datetime = Field(default_factory=datetime.utcnow)


class Team(BaseModel):
    """Team within an organization."""
    team_id: str
    team_name: str
    team_description: Optional[str] = None
    manager_id: Optional[str] = None  # User ID of team manager
    members: List[TeamMember] = []
    created_date: datetime = Field(default_factory=datetime.utcnow)
    updated_date: datetime = Field(default_factory=datetime.utcnow)


class EnvironmentVariable(BaseModel):
    """Environment variable configuration."""
    key: str
    value: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Organization(BaseModel):
    """Enhanced organization model."""
    organization_id: str
    organization_name: str
    organization_description: Optional[str] = None
    admin_user_id: Optional[str] = None  # Only 1 admin per organization
    teams: List[Team] = []
    database_credentials: List[DatabaseCredentials] = []  # Multiple DB configs
    environment_variables: List[EnvironmentVariable] = [] # Global env vars
    organization_created_date: datetime = Field(default_factory=datetime.utcnow)
    organization_updated_date: datetime = Field(default_factory=datetime.utcnow)
    organization_is_active: bool = True


class CreateOrganizationRequest(BaseModel):
    """Request to create organization with full setup."""
    organization_name: str
    organization_description: Optional[str] = None
    admin_email: str  # Email of the admin user
    teams: Optional[List[Dict[str, Any]]] = None  # Initial teams
    database_credentials: Optional[List[DatabaseCredentials]] = None


class CreateTeamRequest(BaseModel):
    """Request to create a team."""
    team_name: str
    team_description: Optional[str] = None
    manager_email: Optional[str] = None


class AddTeamMemberRequest(BaseModel):
    """Request to add member to team."""
    team_id: str
    user_email: str
    role: UserRole


class AddDatabaseCredentialsRequest(BaseModel):
    """Request to add database credentials."""
    database_credentials: List[DatabaseCredentials]


class UpdateDatabaseCredentialsRequest(BaseModel):
    """Request to update database credentials."""
    credential_id: str
    database_credentials: DatabaseCredentials


class AddEnvironmentVariableRequest(BaseModel):
    """Request to add environment variable."""
    key: str
    value: str
    description: Optional[str] = None


class OrganizationDetailsResponse(BaseModel):
    """Detailed organization response."""
    organization: Organization
    total_members: int
    total_teams: int
    total_databases: int


class JoinRequestStatus(str, Enum):
    """Status of a request to join an organization."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class JoinRequest(BaseModel):
    """Model for a join request."""
    request_id: str
    user_id: str
    user_name: str
    user_email: str
    organization_id: str
    organization_name: str
    requested_role: UserRole = UserRole.ORG_MEMBER
    status: JoinRequestStatus = JoinRequestStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
