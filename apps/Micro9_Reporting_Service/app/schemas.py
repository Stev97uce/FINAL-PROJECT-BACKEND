"""
Pydantic schemas for request/response validation
KISS principle: Clear data validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# Enums
class ReportType(str, Enum):
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    CLINICAL = "clinical"
    ADMINISTRATIVE = "administrative"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    PDF = "pdf"
    XLSX = "xlsx"
    CSV = "csv"
    JSON = "json"


class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Report Schemas
class ReportCreate(BaseModel):
    """Create new report request"""
    template_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: ReportType
    format: ReportFormat
    parameters: Optional[Dict[str, Any]] = {}
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ReportResponse(BaseModel):
    """Report response"""
    id: int
    name: str
    description: Optional[str]
    type: str
    format: str
    status: str
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    generated_by: int
    parameters: Optional[Dict[str, Any]]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """List of reports"""
    reports: List[ReportResponse]
    total: int
    page: int
    page_size: int


# Template Schemas
class TemplateCreate(BaseModel):
    """Create report template"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: ReportType
    format: ReportFormat
    query_template: str = Field(..., min_length=1)
    default_parameters: Optional[Dict[str, Any]] = {}
    required_roles: List[str] = []
    active: bool = True


class TemplateUpdate(BaseModel):
    """Update report template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[ReportType] = None
    format: Optional[ReportFormat] = None
    query_template: Optional[str] = Field(None, min_length=1)
    default_parameters: Optional[Dict[str, Any]] = None
    required_roles: Optional[List[str]] = None
    active: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Template response"""
    id: int
    name: str
    description: Optional[str]
    type: str
    format: str
    query_template: str
    default_parameters: Optional[Dict[str, Any]]
    required_roles: List[str]
    active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Scheduled Report Schemas
class ScheduledReportCreate(BaseModel):
    """Create scheduled report"""
    template_id: int
    schedule_cron: str = Field(..., min_length=9)  # e.g., "0 8 * * 1"
    recipients: List[str] = Field(..., min_items=1)
    enabled: bool = True
    
    @field_validator('recipients')
    @classmethod
    def validate_emails(cls, v):
        """Validate email format"""
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for email in v:
            if not re.match(email_regex, email):
                raise ValueError(f"Invalid email format: {email}")
        return v


class ScheduledReportUpdate(BaseModel):
    """Update scheduled report"""
    schedule_cron: Optional[str] = Field(None, min_length=9)
    recipients: Optional[List[str]] = Field(None, min_items=1)
    enabled: Optional[bool] = None


class ScheduledReportResponse(BaseModel):
    """Scheduled report response"""
    id: int
    template_id: int
    schedule_cron: str
    recipients: List[str]
    enabled: bool
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Statistics
class ReportStats(BaseModel):
    """Report statistics"""
    total_reports: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_format: Dict[str, int]
    total_size_mb: float
    avg_generation_time_seconds: Optional[float]


# Generate Report Request
class GenerateReportRequest(BaseModel):
    """Request to generate a report"""
    template_id: int
    format: Optional[ReportFormat] = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = {}


# Health Check
class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    service: str
    database: str
    redis: str
    rabbitmq: str
    timestamp: datetime
