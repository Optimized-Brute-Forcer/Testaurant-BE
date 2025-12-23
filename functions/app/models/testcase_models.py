"""Testcase models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.common_models import ModifiedContext, ExecutionStatus


class Testcase(BaseModel):
    """Testcase model."""
    testcase_id: str
    organization_id: str
    name: str = Field(alias="testcase_title")
    description: Optional[str] = Field(None, alias="testcase_subtitle")
    tag: Optional[str] = Field(None, alias="testcase_tag")
    workitem_ids: List[str] = Field(default=[], alias="testcase_workitem_list")
    testcase_modified_context: Optional[ModifiedContext] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="testcase_created_date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="testcase_updated_date")
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_deleted: bool = Field(default=False, alias="testcase_is_deleted")

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


class CreateTestcaseRequest(BaseModel):
    """Request to create testcase."""
    name: str
    description: Optional[str] = None
    tag: Optional[str] = None
    workitem_ids: List[str] = []
    testcase_modified_context: Optional[str] = None


class UpdateTestcaseRequest(BaseModel):
    """Request to update testcase."""
    testcase_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None
    workitem_ids: Optional[List[str]] = None
    testcase_modified_context: Optional[str] = None


class TestcaseListResponse(BaseModel):
    """Testcase list response."""
    testcases: List[Testcase]
    total: int
    page: int
    page_size: int
