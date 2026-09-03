"""PostgreSQL fixtures that cannot target the normal development database."""

import os
from collections.abc import Iterator

import pytest
from pydantic import SecretStr
from sqlalchemy import Engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import Environment, Settings
from app.db.engine import create_database_engine

_DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg://reviewflow:reviewflow-local-only@127.0.0.1:5432/reviewflow_test"
)


@pytest.fixture(scope="session")
def database_settings() -> Settings:
    """Return settings for the dedicated database and reject unsafe targets."""
    raw_url = os.getenv("REVIEWFLOW_TEST_DATABASE_URL", _DEFAULT_TEST_DATABASE_URL)
    try:
        parsed_url = make_url(raw_url)
    except ArgumentError:
        pytest.fail(
            "REVIEWFLOW_TEST_DATABASE_URL must be a valid database URL",
            pytrace=False,
        )
    if parsed_url.database != "reviewflow_test":
        pytest.fail(
            "REVIEWFLOW_TEST_DATABASE_URL must target the dedicated reviewflow_test database",
            pytrace=False,
        )
    return Settings(environment=Environment.TEST, database_url=SecretStr(raw_url))


@pytest.fixture(scope="session")
def database_engine(database_settings: Settings) -> Iterator[Engine]:
    """Own one PostgreSQL engine for the integration-test session."""
    engine = create_database_engine(database_settings)
    database_available = True
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
    except SQLAlchemyError:
        engine.dispose()
        database_available = False

    if not database_available:
        pytest.fail(
            "Cannot connect to the dedicated reviewflow_test database; run pnpm db:up",
            pytrace=False,
        )
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(database_engine: Engine) -> Iterator[Session]:
    """Roll back every test, including changes committed by its sessions."""
    with database_engine.connect() as connection:
        outer_transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            outer_transaction.rollback()
