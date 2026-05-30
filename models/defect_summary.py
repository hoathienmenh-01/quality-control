from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class DefectSummary(Base):
    """Aggregated daily defect statistics per station."""

    __tablename__ = "defect_summaries"

    summary_date: Mapped[str] = mapped_column(Date, nullable=False, index=True)
    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    total_inspected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pass_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    missing_component_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qr_error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sn_error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    antenna_error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return (
            f"<DefectSummary date={self.summary_date} station={self.station_id!r} "
            f"pass_rate={self.pass_rate}>"
        )
