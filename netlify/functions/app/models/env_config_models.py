"""Environment configuration models."""
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime
from app.models.common_models import Environment, ModifiedContext


class EnvConfig(BaseModel):
    """Environment configuration model."""
    organization_id: str
    config_key: str
    environment: Environment
    config_value: Dict[str, Any]  # Can be complex objects
    env_config_modified_context: Optional[ModifiedContext] = None
    env_config_created_date: datetime = Field(default_factory=datetime.utcnow)
    env_config_updated_date: datetime = Field(default_factory=datetime.utcnow)


class AddEnvConfigRequest(BaseModel):
    """Request to add environment configuration."""
    config_key: str
    environment: Environment
    config_value: Dict[str, Any]
    env_config_modified_context: Optional[str] = None


class UpdateEnvConfigRequest(BaseModel):
    """Request to update environment configuration."""
    config_key: str
    environment: Environment
    config_value: Dict[str, Any]
    env_config_modified_context: Optional[str] = None


class FetchEnvConfigRequest(BaseModel):
    """Request to fetch environment configuration."""
    config_key: str
    environment: Environment
