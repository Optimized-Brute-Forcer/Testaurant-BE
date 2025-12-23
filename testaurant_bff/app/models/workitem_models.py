"""Workitem models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from app.models.common_models import ModifiedContext, ExecutionStatus


class WorkitemType(str, Enum):
    """Types of workitems."""
    REST = "REST"
    SQL = "SQL"
    MONGO = "MONGO"


class HttpMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class SqlQueryType(str, Enum):
    """SQL query types."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class MongoQueryType(str, Enum):
    """MongoDB query types."""
    FIND = "FIND"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    AGGREGATE = "AGGREGATE"


class RestApiRequestParams(BaseModel):
    """REST API request parameters."""
    method: HttpMethod
    path: str
    headers: Dict[str, str] = {}
    query_params: Dict[str, str] = {}
    body: Optional[str] = None


class SqlRequestParams(BaseModel):
    """SQL query request parameters."""
    query: str
    query_type: SqlQueryType
    database_name: str = "default"


class MongoRequestParams(BaseModel):
    """MongoDB query request parameters."""
    collection: str
    operation: MongoQueryType
    query: str = "{}"
    document: Optional[str] = None
    database_name: Optional[str] = "default"


class Workitem(BaseModel):
    """Workitem model."""
    workitem_id: str
    organization_id: str
    name: str = Field(alias="workitem_title")
    description: Optional[str] = None
    workitem_type: WorkitemType
    rest_config: Optional[RestApiRequestParams] = None
    sql_config: Optional[SqlRequestParams] = None
    mongo_config: Optional[MongoRequestParams] = None
    workitem_expected_resp: Optional[Dict[str, Any]] = None
    workitem_feed_forward: Optional[Dict[str, Any]] = None
    workitem_modified_context: Optional[ModifiedContext] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="workitem_created_date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="workitem_updated_date")
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_deleted: bool = Field(default=False, alias="workitem_is_deleted")
    
    # Execution Metadata
    last_ran_at: Optional[datetime] = None
    last_ran_by: Optional[str] = None
    last_run_status: Optional[ExecutionStatus] = None
    last_run_id: Optional[str] = None

    # UI Enhancement: Resolved Names
    created_by_name: Optional[str] = None
    last_ran_by_name: Optional[str] = None

    class Config:
        populate_by_name = True


class CreateWorkitemRequest(BaseModel):
    """Unified request to create any workitem."""
    name: str
    description: Optional[str] = None
    workitem_type: WorkitemType
    rest_config: Optional[RestApiRequestParams] = None
    sql_config: Optional[SqlRequestParams] = None
    mongo_config: Optional[MongoRequestParams] = None
    workitem_expected_resp: Optional[Dict[str, Any]] = None
    workitem_feed_forward: Optional[Dict[str, Any]] = None
    workitem_modified_context: Optional[str] = None


class UpdateWorkitemRequest(BaseModel):
    """Request to update workitem."""
    workitem_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    workitem_type: Optional[WorkitemType] = None
    rest_config: Optional[RestApiRequestParams] = None
    sql_config: Optional[SqlRequestParams] = None
    mongo_config: Optional[MongoRequestParams] = None
    workitem_expected_resp: Optional[Dict[str, Any]] = None
    workitem_feed_forward: Optional[Dict[str, Any]] = None
    workitem_modified_context: Optional[str] = None


class WorkitemListResponse(BaseModel):
    """Workitem list response."""
    workitems: List[Workitem]
    total: int
    page: int
    page_size: int
