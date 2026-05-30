"""Statistics and dashboard business logic."""

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.alert import Alert
from models.defect_summary import DefectSummary
from models.inspection import Inspection


def get_dashboard_stats(db: Session) -> dict:
    """Return high-level dashboard metrics."""
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total = db.query(Inspection).count()
    today_count = db.query(Inspection).filter(func.date(Inspection.created_at) == today).count()
    today_passed = (
        db.query(Inspection)
        .filter(func.date(Inspection.created_at) == today, Inspection.overall_result == "pass")
        .count()
    )
    today_failed = (
        db.query(Inspection)
        .filter(func.date(Inspection.created_at) == today, Inspection.overall_result == "fail")
        .count()
    )

    week_count = db.query(Inspection).filter(func.date(Inspection.created_at) >= week_ago).count()
    month_count = (
        db.query(Inspection).filter(func.date(Inspection.created_at) >= month_ago).count()
    )

    unread_alerts = db.query(Alert).filter(Alert.is_read == False).count()
    critical_alerts = (
        db.query(Alert)
        .filter(Alert.severity == "critical", Alert.is_resolved == False)
        .count()
    )

    return {
        "total_inspections": total,
        "today": {
            "total": today_count,
            "passed": today_passed,
            "failed": today_failed,
            "pass_rate": round(today_passed / today_count * 100, 2) if today_count > 0 else 0.0,
        },
        "week_count": week_count,
        "month_count": month_count,
        "unread_alerts": unread_alerts,
        "critical_alerts": critical_alerts,
    }


def get_defect_trend(db: Session, days: int = 30, station_id: str | None = None) -> list[dict]:
    """Return daily defect counts for the last N days."""
    start = date.today() - timedelta(days=days)
    q = db.query(DefectSummary).filter(DefectSummary.summary_date >= start)
    if station_id:
        q = q.filter(DefectSummary.station_id == station_id)
    rows = q.order_by(DefectSummary.summary_date).all()

    return [
        {
            "date": str(r.summary_date),
            "station_id": r.station_id,
            "total_inspected": r.total_inspected,
            "total_passed": r.total_passed,
            "total_failed": r.total_failed,
            "pass_rate": r.pass_rate,
            "missing_components": r.missing_component_count,
            "qr_errors": r.qr_error_count,
            "sn_errors": r.sn_error_count,
            "antenna_errors": r.antenna_error_count,
        }
        for r in rows
    ]


def get_top_defects(db: Session, limit: int = 10, station_id: str | None = None) -> list[dict]:
    """Return defect type breakdown sorted by count."""
    q = db.query(Inspection).filter(Inspection.overall_result == "fail")
    if station_id:
        q = q.filter(Inspection.station_id == station_id)

    total_failures = q.count()
    if total_failures == 0:
        return []

    # Count each defect type from the fail records
    qr_fails = q.filter(Inspection.qr_result == "fail").count()
    sn_fails = q.filter(Inspection.sn_result == "fail").count()
    antenna_fails = q.filter(Inspection.antenna_result == "fail").count()

    # missing_components is JSON; count rows that have non-null/non-empty
    missing_comp_fails = q.filter(
        Inspection.missing_components.isnot(None),
        Inspection.missing_components != "[]",
        Inspection.missing_components != "",
    ).count()

    defects = [
        {"type": "Missing Components", "count": missing_comp_fails},
        {"type": "QR Error", "count": qr_fails},
        {"type": "SN Error", "count": sn_fails},
        {"type": "Antenna Error", "count": antenna_fails},
    ]
    defects.sort(key=lambda d: d["count"], reverse=True)
    return defects[:limit]
