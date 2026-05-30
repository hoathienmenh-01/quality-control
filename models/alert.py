from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Alert(Base):
    """System alert for quality issues or operational events."""

    __tablename__ = "alerts"

    alert_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # "defect_spike", "camera_offline", "threshold_exceeded", "system"

    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    # "info", "warning", "critical"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    station_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<Alert id={self.id} type={self.alert_type!r} severity={self.severity!r}>"
