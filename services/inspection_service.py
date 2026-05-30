"""Inspection business logic."""

import json
from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.inspection import Inspection
from services.notification_service import check_and_alert


def create_inspection(db: Session, data: dict) -> Inspection:
    """Create a new inspection record.
    
    Automatically triggers alert if inspection result is 'fail'.
    """
    inspection = Inspection(**data)
    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    # Tự động kiểm tra và tạo alert nếu sản phẩm lỗi
    if inspection.overall_result == "fail":
        check_and_alert(db, inspection)

    return inspection


def get_inspection(db: Session, inspection_id: int) -> Inspection | None:
    return db.query(Inspection).filter(Inspection.id == inspection_id).first()


def list_inspections(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    station_id: str | None = None,
    product_type: str | None = None,
    overall_result: str | None = None,
    batch_number: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Inspection]:
    """List inspections with optional filters."""
    q = db.query(Inspection)
    if station_id:
        q = q.filter(Inspection.station_id == station_id)
    if product_type:
        q = q.filter(Inspection.product_type == product_type)
    if overall_result:
        q = q.filter(Inspection.overall_result == overall_result)
    if batch_number:
        q = q.filter(Inspection.batch_number == batch_number)
    if start_date:
        q = q.filter(func.date(Inspection.created_at) >= start_date)
    if end_date:
        q = q.filter(func.date(Inspection.created_at) <= end_date)
    return q.order_by(Inspection.created_at.desc()).offset(skip).limit(limit).all()


def get_inspection_stats(db: Session, station_id: str | None = None) -> dict:
    """Return aggregated inspection statistics."""
    q = db.query(Inspection)
    if station_id:
        q = q.filter(Inspection.station_id == station_id)

    total = q.count()
    passed = q.filter(Inspection.overall_result == "pass").count()
    failed = q.filter(Inspection.overall_result == "fail").count()

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 2) if total > 0 else 0.0,
        "pending": total - passed - failed,
    }
