"""
Admin endpoints for templates and statistics
KISS principle: Simple admin operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Report, ReportTemplate, ScheduledReport
from app.schemas import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    ScheduledReportCreate, ScheduledReportResponse,
    ReportStats
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# Templates
@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    _: Dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all templates"""
    result = await db.execute(select(ReportTemplate))
    templates = result.scalars().all()
    return [TemplateResponse.model_validate(t) for t in templates]


@router.post("/templates", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create template"""
    if current_user["rol"] != "administrador":
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Check uniqueness
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.name == template.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Template name exists")
    
    new_template = ReportTemplate(**template.model_dump())
    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)
    
    return TemplateResponse.model_validate(new_template)


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template: TemplateUpdate,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update template"""
    if current_user["rol"] != "administrador":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    existing = result.scalar_one_or_none()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    await db.commit()
    await db.refresh(existing)
    
    return TemplateResponse.model_validate(existing)


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete template"""
    if current_user["rol"] != "administrador":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    await db.delete(template)
    await db.commit()
    
    return {"message": "Template deleted"}


# Statistics
@router.get("/stats", response_model=ReportStats)
async def get_statistics(
    _: Dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get report statistics"""
    # Total reports
    total_result = await db.execute(select(func.count(Report.id)))
    total = total_result.scalar()
    
    # By status
    by_status = {}
    status_result = await db.execute(
        select(Report.status, func.count(Report.id)).group_by(Report.status)
    )
    for status, count in status_result:
        by_status[status] = count
    
    # By type
    by_type = {}
    type_result = await db.execute(
        select(Report.type, func.count(Report.id)).group_by(Report.type)
    )
    for rtype, count in type_result:
        by_type[rtype] = count
    
    # By format
    by_format = {}
    format_result = await db.execute(
        select(Report.format, func.count(Report.id)).group_by(Report.format)
    )
    for fmt, count in format_result:
        by_format[fmt] = count
    
    # Total size
    size_result = await db.execute(select(func.sum(Report.file_size_bytes)))
    total_size_bytes = size_result.scalar() or 0
    total_size_mb = total_size_bytes / (1024 * 1024)
    
    return ReportStats(
        total_reports=total,
        by_status=by_status,
        by_type=by_type,
        by_format=by_format,
        total_size_mb=round(total_size_mb, 2),
        avg_generation_time_seconds=None
    )
