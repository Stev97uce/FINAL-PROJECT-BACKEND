"""
Notification endpoints - User notifications
KISS principle: Simple CRUD for internal notifications
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict
from app.dependencies import get_current_user
from app.models import InternalNotification
from app.schemas import NotificationResponse

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    is_read: bool = Query(None),
    limit: int = Query(50, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """List user's internal notifications"""
    user_id = current_user["user_id"]
    
    # Build query
    query = {"user_id": user_id}
    if is_read is not None:
        query["is_read"] = is_read
    
    notifications = await InternalNotification.find(
        query
    ).sort("-created_at").limit(limit).to_list()
    
    return [
        NotificationResponse(
            id=str(n.id),
            user_id=n.user_id,
            title=n.title,
            body=n.body,
            category=n.category,
            priority=n.priority,
            is_read=n.is_read,
            action_url=n.action_url,
            created_at=n.created_at
        )
        for n in notifications
    ]


@router.get("/unread-count")
async def get_unread_count(
    current_user: Dict = Depends(get_current_user)
):
    """Get count of unread notifications"""
    user_id = current_user["user_id"]
    
    count = await InternalNotification.find(
        InternalNotification.user_id == user_id,
        InternalNotification.is_read == False
    ).count()
    
    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get specific notification"""
    from beanie import PydanticObjectId
    
    notification = await InternalNotification.get(PydanticObjectId(notification_id))
    
    if not notification or notification.user_id != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationResponse(
        id=str(notification.id),
        user_id=notification.user_id,
        title=notification.title,
        body=notification.body,
        category=notification.category,
        priority=notification.priority,
        is_read=notification.is_read,
        action_url=notification.action_url,
        created_at=notification.created_at
    )


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Mark notification as read"""
    from beanie import PydanticObjectId
    from datetime import datetime
    
    notification = await InternalNotification.get(PydanticObjectId(notification_id))
    
    if not notification or notification.user_id != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await notification.save()
    
    return {"message": "Notification marked as read"}


@router.patch("/read-all")
async def mark_all_as_read(
    current_user: Dict = Depends(get_current_user)
):
    """Mark all notifications as read"""
    from datetime import datetime
    
    user_id = current_user["user_id"]
    
    notifications = await InternalNotification.find(
        InternalNotification.user_id == user_id,
        InternalNotification.is_read == False
    ).to_list()
    
    for notification in notifications:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await notification.save()
    
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete notification"""
    from beanie import PydanticObjectId
    
    notification = await InternalNotification.get(PydanticObjectId(notification_id))
    
    if not notification or notification.user_id != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await notification.delete()
    
    return {"message": "Notification deleted"}
