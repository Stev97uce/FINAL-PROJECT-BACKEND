"""
SQLAlchemy models for Reporting Service
KISS principle: Simple, clear data models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, BigInteger, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class Report(Base):
    """
    Reports metadata and status
    """
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Type and Format
    type = Column(String(50), nullable=False, index=True)  # operational, analytical, clinical, administrative, custom
    format = Column(String(10), nullable=False)  # pdf, xlsx, csv, json
    
    # Status
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending, processing, completed, failed
    
    # File info
    file_path = Column(Text, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    
    # User info
    generated_by = Column(Integer, nullable=False, index=True)  # user_id
    
    # Parameters and dates
    parameters = Column(JSONB, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)


class ReportTemplate(Base):
    """
    Predefined report templates
    """
    __tablename__ = "report_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Type and Format
    type = Column(String(50), nullable=False)
    format = Column(String(10), nullable=False)
    
    # Query and parameters
    query_template = Column(Text, nullable=False)  # SQL or JSON query
    default_parameters = Column(JSONB, nullable=True)
    
    # Permissions
    required_roles = Column(ARRAY(String), nullable=False, default=[])
    
    # Status
    active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ScheduledReport(Base):
    """
    Scheduled/automated reports
    """
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, nullable=False, index=True)
    
    # Schedule
    schedule_cron = Column(String(100), nullable=False)  # Cron expression
    
    # Recipients
    recipients = Column(ARRAY(String), nullable=False, default=[])
    
    # Status
    enabled = Column(Boolean, default=True, nullable=False)
    
    # Execution tracking
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True, index=True)
    
    # User info
    created_by = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AggregatedMetric(Base):
    """
    Pre-calculated metrics for fast reports
    """
    __tablename__ = "aggregated_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metric identification
    metric_type = Column(String(100), nullable=False, index=True)  # daily_appointments, monthly_users
    metric_date = Column(DateTime, nullable=False, index=True)
    
    # Metric data
    metric_value = Column(JSONB, nullable=False)
    
    # Timestamp
    calculated_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Unique constraint
    __table_args__ = (
        {'schema': None},
    )
