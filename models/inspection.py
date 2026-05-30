from sqlalchemy import Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Inspection(Base):
    """Record of a single product inspection."""

    __tablename__ = "inspections"
    __table_args__ = (
        Index("ix_inspections_created_at", "created_at"),
    )

    product_serial: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    product_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    batch_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    overall_result: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # "pass", "fail", "pending"

    missing_components: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON array of missing component names

    qr_result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # "pass", "fail", "not_found"

    sn_result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # "pass", "fail", "not_found"

    antenna_result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # "pass", "fail", "not_found"

    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    inference_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Inspection id={self.id} serial={self.product_serial!r} "
            f"result={self.overall_result!r}>"
        )
