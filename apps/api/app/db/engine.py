"""SQLAlchemy engine and session-factory construction."""

from dataclasses import dataclass

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


@dataclass(frozen=True, slots=True)
class DatabaseResources:
    """Database resources with one lifecycle owned by a FastAPI application."""

    engine: Engine
    session_factory: sessionmaker[Session]


def create_database_engine(
    settings: Settings,
    *,
    apply_statement_timeout: bool = True,
) -> Engine:
    """Build a lazy PostgreSQL engine with bounded connection and pool waits."""
    timeout_seconds = settings.database_timeout_seconds
    connect_args: dict[str, int | str] = {"connect_timeout": timeout_seconds}
    if apply_statement_timeout:
        connect_args["options"] = f"-c statement_timeout={timeout_seconds * 1000}"

    return create_engine(
        settings.database_url.get_secret_value(),
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_timeout=timeout_seconds,
    )


def create_database_resources(settings: Settings) -> DatabaseResources:
    """Build bounded application database resources without connecting."""
    engine = create_database_engine(settings)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return DatabaseResources(engine=engine, session_factory=factory)
