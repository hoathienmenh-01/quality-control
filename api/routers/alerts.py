"""Alerts router — list, mark read, resolve, test notifications."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.dependencies import get_db
from config import settings
from models.user import User
from services import alert_service
from services.notification_service import _send_telegram_message

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    message: str
    station_id: str | None
    is_read: bool
    is_resolved: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


def _serialize(row) -> dict:
    return {
        "id": row.id,
        "alert_type": row.alert_type,
        "severity": row.severity,
        "title": row.title,
        "message": row.message,
        "station_id": row.station_id,
        "is_read": row.is_read,
        "is_resolved": row.is_resolved,
        "created_at": str(row.created_at),
        "updated_at": str(row.updated_at),
    }


@router.get("/", response_model=list[AlertResponse])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_read: bool | None = None,
    is_resolved: bool | None = None,
    severity: str | None = None,
    station_id: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    rows = alert_service.list_alerts(
        db,
        skip=skip,
        limit=limit,
        is_read=is_read,
        is_resolved=is_resolved,
        severity=severity,
        station_id=station_id,
    )
    return [_serialize(r) for r in rows]


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"unread": alert_service.get_unread_count(db)}


@router.patch("/{alert_id}/read", response_model=AlertResponse)
def mark_read(
    alert_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    alert = alert_service.mark_read(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _serialize(alert)


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    alert = alert_service.resolve_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _serialize(alert)


@router.post("/test-telegram")
def test_telegram(
    _user: User = Depends(get_current_user),
):
    """Gửi tin nhắn test qua Telegram để kiểm tra cấu hình."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        raise HTTPException(
            status_code=400,
            detail="Telegram chưa được cấu hình. Set TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID trong .env",
        )

    success = _send_telegram_message(
        token, chat_id,
        "✅ <b>Test alert từ QC System</b>\n\nKết nối Telegram thành công!",
    )
    if success:
        return {"status": "ok", "message": "Telegram test sent successfully"}
    raise HTTPException(status_code=500, detail="Failed to send Telegram message")
