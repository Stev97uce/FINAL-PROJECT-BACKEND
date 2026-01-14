"""
User report endpoints
KISS principle: Simple CRUD for user reports
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List
import os

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Report, ReportTemplate
from app.schemas import (
    ReportResponse, ReportListResponse, GenerateReportRequest,
    TemplateResponse
)
from app.services.report_service import report_service

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("", response_model=ReportListResponse)
async def list_reports(
    status: str = Query(None),
    type: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's reports
    """
    user_id = current_user["user_id"]
    
    # Build query
    query = select(Report).where(Report.generated_by == user_id)
    
    if status:
        query = query.where(Report.status == status)
    if type:
        query = query.where(Report.type == type)
    
    query = query.order_by(Report.created_at.desc()).offset(skip).limit(limit)
    
    # Execute
    result = await db.execute(query)
    reports = result.scalars().all()
    
    # Count total
    count_query = select(func.count(Report.id)).where(Report.generated_by == user_id)
    if status:
        count_query = count_query.where(Report.status == status)
    if type:
        count_query = count_query.where(Report.type == type)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    return ReportListResponse(
        reports=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get report details
    """
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check ownership (admin can see all)
    if report.generated_by != current_user["user_id"] and current_user["rol"] not in ["administrador", "coordinador"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ReportResponse.model_validate(report)


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download report file
    """
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check ownership
    if report.generated_by != current_user["user_id"] and current_user["rol"] not in ["administrador", "coordinador"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if report.status != "completed":
        raise HTTPException(status_code=400, detail=f"Report is {report.status}")
    
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Determine media type
    media_type_map = {
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
        "json": "application/json"
    }
    media_type = media_type_map.get(report.format, "application/octet-stream")
    
    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=os.path.basename(report.file_path)
    )


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new report
    """
    # Get template
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.id == request.template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if not template.active:
        raise HTTPException(status_code=400, detail="Template is inactive")
    
    # Check permissions
    if template.required_roles:
        if current_user["rol"] not in template.required_roles and current_user["rol"] not in ["administrador", "coordinador"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Create report
    report = Report(
        name=template.name,
        description=template.description,
        type=template.type,
        format=request.format.value,
        status="pending",
        generated_by=current_user["user_id"],
        parameters=request.parameters
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    # Generate report synchronously (for testing/development)
    # TODO: Move to Celery task for production
    try:
        # Import report service
        from app.services.report_service import ReportService
        
        # Generate report
        report_service = ReportService()
        
        # For now, we'll pass None for token since we don't have it in the request context
        # In production, this should be done via Celery with proper token handling
        success = await report_service.generate_report(db, report.id, None)
        
        if success:
            # Refresh to get updated status
            await db.refresh(report)
    except Exception as e:
        # Log error but return the report in pending state
        import logging
        logging.error(f"Error generating report: {e}")
    
    return ReportResponse.model_validate(report)


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a report
    """
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check ownership
    if report.generated_by != current_user["user_id"] and current_user["rol"] not in ["administrador"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete file
    if report.file_path and os.path.exists(report.file_path):
        os.remove(report.file_path)
    
    # Delete record
    await db.delete(report)
    await db.commit()
    
    return {"message": "Report deleted successfully"}


@router.get("/templates/available", response_model=List[TemplateResponse])
async def list_available_templates(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List templates available to current user
    """
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.active == True)
    )
    templates = result.scalars().all()
    
    # Filter by role
    available = []
    for template in templates:
        if not template.required_roles or current_user["rol"] in template.required_roles or current_user["rol"] in ["administrador", "coordinador"]:
            available.append(template)
    
    return [TemplateResponse.model_validate(t) for t in available]
