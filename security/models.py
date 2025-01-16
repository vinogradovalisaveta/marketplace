from database import Base
from sqlalchemy import UUID, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
