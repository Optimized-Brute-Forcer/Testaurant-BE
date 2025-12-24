"""Execution and run audit models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.common_models import ExecutionStatus, ExecutionLog, Environment


class RunWorkitemAudit(BaseModel):
    """Run workitem audit model."""
    run_workitem_id: str
    organization_id: str
    workitem_id: str
    workitem_title: str
    environment: Environment
    execution_status: ExecutionStatus
    workitem_config: Dict[str, Any]  # Snapshot of workitem at execution time
    execution_logs: List[ExecutionLog] = []
    feed_forward_data: Optional[Dict[str, Any]] = None
    actual_response: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    run_workitem_created_date: datetime = Field(default_factory=datetime.utcnow)
    run_workitem_start_time: Optional[datetime] = None
    run_workitem_end_time: Optional[datetime] = None
    executor_context: Optional[str] = None


class WorkitemExecutionResult(BaseModel):
    """Result of workitem execution."""
    workitem_id: str
    workitem_title: str
    execution_status: ExecutionStatus
    execution_logs: List[ExecutionLog]
    feed_forward_data: Optional[Dict[str, Any]] = None
    actual_response: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None


class RunTestcaseAudit(BaseModel):
    """Run testcase audit model."""
    run_testcase_id: str
    organization_id: str
    testcase_id: str
    testcase_title: str
    environment: Environment
    overall_status: ExecutionStatus
    workitem_results: List[WorkitemExecutionResult] = []
    run_testcase_created_date: datetime = Field(default_factory=datetime.utcnow)
    run_testcase_start_time: Optional[datetime] = None
    run_testcase_end_time: Optional[datetime] = None
    executor_context: Optional[str] = None


class RunWorkitemRequest(BaseModel):
    """Request to run a workitem."""
    workitem_id: str
    environment: Environment
    executor_context: Optional[str] = None
    previous_feed_forward: Optional[Dict[str, Any]] = None


class RunTestcaseRequest(BaseModel):
    """Request to run a testcase."""
    testcase_id: str
    environment: Environment
    executor_context: Optional[str] = None


class RunTestcasesBulkRequest(BaseModel):
    """Request to run multiple testcases."""
    testcase_ids: List[str]
    environment: Environment
    executor_context: Optional[str] = None


class RunWorkitemListResponse(BaseModel):
    """Run workitem list response."""
    runs: List[RunWorkitemAudit]
    total: int
    page: int
    page_size: int


class RunTestcaseListResponse(BaseModel):
    """Run testcase list response."""
    runs: List[RunTestcaseAudit]
    total: int
    page: int
    page_size: int
class RunTestsuiteAudit(BaseModel):
    """Run testsuite audit model."""
    run_testsuite_id: str
    organization_id: str
    testsuite_id: str
    testsuite_title: str
    environment: Environment
    overall_status: ExecutionStatus
    testcase_results: List[RunTestcaseAudit] = []
    run_testsuite_created_date: datetime = Field(default_factory=datetime.utcnow)
    run_testsuite_start_time: Optional[datetime] = None
    run_testsuite_end_time: Optional[datetime] = None
    executor_context: Optional[str] = None


class RunTestsuiteRequest(BaseModel):
    """Request to run a testsuite."""
    testsuite_id: str
    environment: Environment
    executor_context: Optional[str] = None
