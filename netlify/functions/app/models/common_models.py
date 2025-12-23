"""Common models and enums."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Environment(str, Enum):
    """Supported environments."""
    QA = "QA"
    PREPROD = "PREPROD"
    PROD = "PROD"


class ExecutionStatus(str, Enum):
    """Execution status."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    PENDING = "PENDING"


class LogType(str, Enum):
    """Log types."""
    INFO = "INFO"
    ERROR = "ERROR"


class ExecutionLog(BaseModel):
    """Execution log entry."""
    log_type: LogType
    message: str
    payload: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModifiedContext(BaseModel):
    """Modification context for audit trail."""
    modified_by: str
    modified_reason: Optional[str] = None
    modified_date: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SortOrder(str, Enum):
    """Sort order."""
    ASC = "ASC"
    DESC = "DESC"
