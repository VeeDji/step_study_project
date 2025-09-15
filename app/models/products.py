from sqlalchemy import String, Float, Integer, Boolean, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.database import Base

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )
    seller: Mapped["User"] = relationship(
        "User",
        back_populates="products",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="product",
    )