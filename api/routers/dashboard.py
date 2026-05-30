"""Dashboard router — aggregated stats and realtime data."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.dependencies import get_db
from models.user import User
from services import stats_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return stats_service.get_dashboard_stats(db)


@router.get("/realtime")
def realtime(
    station_id: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Return latest inspection stats (polled by frontend for realtime view)."""
    stats = stats_service.get_dashboard_stats(db)
    trend = stats_service.get_defect_trend(db, days=7, station_id=station_id)
    return {
        "current": stats,
        "trend_7d": trend,
    }
