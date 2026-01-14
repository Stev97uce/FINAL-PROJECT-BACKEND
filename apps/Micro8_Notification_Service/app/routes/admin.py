"""
Admin endpoints - Templates and manual sending
KISS principle: Simple admin operations
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from app.dependencies import require_admin
from app.models import NotificationTemplate, NotificationLog
from app.schemas import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    NotificationSendRequest, DeliveryLogResponse, StatsResponse
)
from app.services.notification_service import notification_service
from datetime import datetime

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# Templates
@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    admin: Dict = Depends(require_admin)
):
    """List all notification templates"""
    templates = await NotificationTemplate.find_all().to_list()
    
    return [
        TemplateResponse(
            id=str(t.id),
            name=t.name,
            channel=t.channel,
            event_type=t.event_type,
            subject=t.subject,
            body=t.body,
            variables=t.variables,
            active=t.active,
            created_at=t.created_at
        )
        for t in templates
    ]


@router.post("/templates", response_model=TemplateResponse)
async def create_template(
    template: TemplateCreate,
    admin: Dict = Depends(require_admin)
):
    """Create new notification template"""
    # Check if name already exists
    existing = await NotificationTemplate.find_one(
        NotificationTemplate.name == template.name
    )
    
    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")
    
    new_template = NotificationTemplate(**template.model_dump())
    await new_template.insert()
    
    return TemplateResponse(
        id=str(new_template.id),
        name=new_template.name,
        channel=new_template.channel,
        event_type=new_template.event_type,
        subject=new_template.subject,
        body=new_template.body,
        variables=new_template.variables,
        active=new_template.active,
        created_at=new_template.created_at
    )


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template: TemplateUpdate,
    admin: Dict = Depends(require_admin)
):
    """Update notification template"""
    from beanie import PydanticObjectId
    
    existing = await NotificationTemplate.get(PydanticObjectId(template_id))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)
    
    existing.updated_at = datetime.utcnow()
    await existing.save()
    
    return TemplateResponse(
        id=str(existing.id),
        name=existing.name,
        channel=existing.channel,
        event_type=existing.event_type,
        subject=existing.subject,
        body=existing.body,
        variables=existing.variables,
        active=existing.active,
        created_at=existing.created_at
    )


# Manual notification sending
@router.post("/send")
async def send_notification(
    request: NotificationSendRequest,
    admin: Dict = Depends(require_admin)
):
    """Manually send notification (admin only)"""
    success = await notification_service.send_notification(
        user_id=request.user_id,
        channel=request.channel,
        template_name=request.template_name,
        variables=request.variables,
        recipient=request.recipient
    )
    
    if success:
        return {"message": "Notification sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send notification")


# Delivery logs
@router.get("/delivery-logs", response_model=List[DeliveryLogResponse])
async def get_delivery_logs(
    user_id: int = None,
    status: str = None,
    limit: int = 100,
    admin: Dict = Depends(require_admin)
):
    """Get delivery logs (admin only)"""
    query = {}
    if user_id:
        query["user_id"] = user_id
    if status:
        query["status"] = status
    
    logs = await NotificationLog.find(query).sort("-created_at").limit(limit).to_list()
    
    return [
        DeliveryLogResponse(
            id=str(log.id),
            notification_id=log.notification_id,
            user_id=log.user_id,
            channel=log.channel,
            status=log.status,
            recipient=log.recipient,
            subject=log.subject,
            sent_at=log.sent_at,
            error_message=log.error_message,
            retry_count=log.retry_count,
            created_at=log.created_at
        )
        for log in logs
    ]


# Stats
@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    admin: Dict = Depends(require_admin)
):
    """Get notification statistics (admin only)"""
    from app.models import NotificationStatus, NotificationChannel
    
    total_logs = await NotificationLog.find_all().to_list()
    
    total_sent = sum(1 for log in total_logs if log.status == NotificationStatus.SENT)
    total_delivered = sum(1 for log in total_logs if log.status == NotificationStatus.DELIVERED)
    total_failed = sum(1 for log in total_logs if log.status == NotificationStatus.FAILED)
    
    by_channel = {}
    for channel in NotificationChannel:
        by_channel[channel.value] = sum(1 for log in total_logs if log.channel == channel)
    
    by_status = {}
    for status in NotificationStatus:
        by_status[status.value] = sum(1 for log in total_logs if log.status == status)
    
    return StatsResponse(
        total_sent=total_sent,
        total_delivered=total_delivered,
        total_failed=total_failed,
        by_channel=by_channel,
        by_status=by_status
    )
