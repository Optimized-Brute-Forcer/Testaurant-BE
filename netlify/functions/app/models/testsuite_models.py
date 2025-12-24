"""Testsuite models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.common_models import ModifiedContext, ExecutionStatus


class Testsuite(BaseModel) :
    """Testsuite model."""
    testsuite_id: str
    organization_id: str
    name: str = Field(alias="testsuite_title")
    description: Optional[str] = Field(None, alias="testsuite_subtitle")
    testcase_ids: List[str] = Field(default=[], alias="testsuite_testcase_list")
    testsuite_modified_context: Optional[ModifiedContext] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="testsuite_created_date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="testsuite_updated_date")
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_deleted: bool = Field(default=False, alias="testsuite_is_deleted")

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


class CreateTestsuiteRequest(BaseModel):
    """Request to create testsuite."""
    name: str
    description: Optional[str] = None
    testcase_ids: List[str] = []
    testsuite_modified_context: Optional[str] = None


class UpdateTestsuiteRequest(BaseModel):
    """Request to update testsuite."""
    testsuite_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    testcase_ids: Optional[List[str]] = None
    testsuite_modified_context: Optional[str] = None


class TestsuiteListResponse(BaseModel):
    """Testsuite list response."""
    testsuites: List[Testsuite]
    total: int
    page: int
    page_size: int
