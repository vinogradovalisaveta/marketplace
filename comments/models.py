from sqlalchemy import Integer, ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from users.models import User


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    user: Mapped["User"] = relationship("User", back_populates="comments")
    product: Mapped["Product"] = relationship("Product", back_populates="comments")
