from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ProductTemplate(Base):
    """Defines expected components and formats for each product type."""

    __tablename__ = "product_templates"

    product_type: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    required_components: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # JSON array of component names, e.g. '["capacitor", "resistor", "ic_chip"]'

    component_positions: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON object mapping component name -> expected position region

    antenna_position: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON object with x, y, w, h for antenna region

    sn_format: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Regex pattern for valid serial number, e.g. r"^[A-Z]{2}\d{6}$"

    qr_format: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Regex pattern or expected QR content prefix

    def __repr__(self) -> str:
        return f"<ProductTemplate id={self.id} type={self.product_type!r}>"
