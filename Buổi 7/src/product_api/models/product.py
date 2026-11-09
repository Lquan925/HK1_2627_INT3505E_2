from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_cents >= 0", name="price_nonnegative"),
        CheckConstraint("qty_in_stock >= 0", name="stock_nonnegative"),
        CheckConstraint("length(sku) BETWEEN 3 AND 32", name="sku_length"),
        CheckConstraint("length(name) BETWEEN 1 AND 255", name="name_length"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    price_cents: Mapped[int] = mapped_column(Integer)
    qty_in_stock: Mapped[int] = mapped_column(Integer, default=0)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
