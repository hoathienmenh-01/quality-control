"""Alert business logic."""

from sqlalchemy.orm import Session

from models.alert import Alert


def create_alert(db: Session, data: dict) -> Alert:
    alert = Alert(**data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def list_alerts(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    is_read: bool | None = None,
    is_resolved: bool | None = None,
    severity: str | None = None,
    station_id: str | None = None,
) -> list[Alert]:
    q = db.query(Alert)
    if is_read is not None:
        q = q.filter(Alert.is_read == is_read)
    if is_resolved is not None:
        q = q.filter(Alert.is_resolved == is_resolved)
    if severity:
        q = q.filter(Alert.severity == severity)
    if station_id:
        q = q.filter(Alert.station_id == station_id)
    return q.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def mark_read(db: Session, alert_id: int) -> Alert | None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_read = True
        db.commit()
        db.refresh(alert)
    return alert


def resolve_alert(db: Session, alert_id: int) -> Alert | None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_resolved = True
        db.commit()
        db.refresh(alert)
    return alert


def get_unread_count(db: Session) -> int:
    return db.query(Alert).filter(Alert.is_read == False).count()
