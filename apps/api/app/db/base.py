"""Shared SQLAlchemy declarative metadata for domain-owned tables."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class whose metadata is consumed by Alembic."""
