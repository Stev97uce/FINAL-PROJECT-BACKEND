"""
Test SQLAlchemy models
"""
import pytest
from datetime import datetime
from app.models import Report, ReportTemplate


@pytest.mark.asyncio
async def test_create_report(db_session):
    """Test creating a report"""
    report = Report(
        name="Test Report",
        type="operational",
        format="pdf",
        status="pending",
        generated_by=1
    )
    
    db_session.add(report)
    await db_session.commit()
    await db_session.refresh(report)
    
    assert report.id is not None
    assert report.name == "Test Report"
    assert report.status == "pending"


@pytest.mark.asyncio
async def test_create_template(db_session):
    """Test creating a template"""
    template = ReportTemplate(
        name="Monthly Dashboard",
        description="Monthly executive dashboard",
        type="analytical",
        format="pdf",
        query_template="SELECT * FROM stats",
        required_roles=["administrador"]
    )
    
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    
    assert template.id is not None
    assert template.name == "Monthly Dashboard"
    assert "administrador" in template.required_roles
