from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    customer_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    order_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    product: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    complaint_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="RECEIVED",
    )

    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    assigned_team: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )