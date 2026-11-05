# app/models.py
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Identity,
    Index,
    Text,
    UniqueConstraint,
    func,
    text,
    String
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint(
            "status IN ('applied', 'interview', 'offer', 'rejected')",
            name="applications_status_check",
        ),
    )

    id: Mapped[int] = mapped_column(
        Identity(always=True),
        primary_key=True,
    )
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    applied_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
    )
    status: Mapped[str] = mapped_column(
        Text,
        index=True,
        nullable=False,
        server_default=text("'applied'"),
    )
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Identity(always=True),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(Text, nullable=False)
    hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

Index("uq_ix_email_lower", func.lower(User.email), unique=True)