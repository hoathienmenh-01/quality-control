"""Defects router — summary, trend, top defects."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.dependencies import get_db
from models.user import User
from services import stats_service

router = APIRouter(prefix="/api/defects", tags=["defects"])


@router.get("/trend")
def defect_trend(
    days: int = Query(30, ge=1, le=365),
    station_id: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return stats_service.get_defect_trend(db, days, station_id)


@router.get("/top")
def top_defects(
    limit: int = Query(10, ge=1, le=50),
    station_id: str | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return stats_service.get_top_defects(db, limit, station_id)
