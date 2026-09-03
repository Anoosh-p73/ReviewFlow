"""Alembic environment bound to ReviewFlow settings and shared metadata."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

from app.core.config import get_settings
from app.db.base import Base
from app.db.engine import create_database_engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Render migrations without opening a database connection."""
    database_url = get_settings().database_url.get_secret_value()
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_with_connection(connection: Connection) -> None:
    """Apply migrations through an existing connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations with the application's PostgreSQL engine settings."""
    engine = create_database_engine(get_settings(), apply_statement_timeout=False)
    try:
        with engine.connect() as connection:
            run_migrations_with_connection(connection)
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
