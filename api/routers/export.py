"""Export router — Excel, CSV, SQL download."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.dependencies import get_db
from models.user import User
from services import export_service

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/excel")
def export_excel(
    station_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    filepath = export_service.export_excel(db, station_id, start_date, end_date)
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filepath.split("/")[-1],
    )


@router.get("/csv")
def export_csv(
    station_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    filepath = export_service.export_csv(db, station_id, start_date, end_date)
    return FileResponse(filepath, media_type="text/csv", filename=filepath.split("/")[-1])


@router.get("/sql")
def export_sql(
    station_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    filepath = export_service.export_sql(db, station_id, start_date, end_date)
    return FileResponse(filepath, media_type="text/sql", filename=filepath.split("/")[-1])
