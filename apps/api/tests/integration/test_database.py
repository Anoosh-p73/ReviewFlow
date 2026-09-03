"""PostgreSQL integration tests for the Task 4 persistence boundary."""

from typing import Annotated, cast

import pytest
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool

from app.core.config import Settings
from app.db.engine import DatabaseResources
from app.db.session import get_db_session
from app.main import create_app

pytestmark = pytest.mark.integration


def test_session_executes_and_commit_and_rollback_are_transactional(
    db_session: Session,
) -> None:
    assert db_session.execute(text("SELECT 1")).scalar_one() == 1
    db_session.execute(text("CREATE TEMPORARY TABLE task4_probe (value INTEGER NOT NULL)"))
    db_session.execute(text("INSERT INTO task4_probe (value) VALUES (1)"))
    db_session.commit()
    assert db_session.execute(text("SELECT value FROM task4_probe")).scalar_one() == 1

    db_session.execute(text("INSERT INTO task4_probe (value) VALUES (2)"))
    db_session.rollback()
    assert db_session.execute(text("SELECT value FROM task4_probe")).scalars().all() == [1]


def test_readiness_succeeds_against_postgresql(database_settings: Settings) -> None:
    with TestClient(create_app(database_settings)) as client:
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "schema_version": "1"}


def test_request_sessions_close_on_success_and_failure(
    database_settings: Settings,
) -> None:
    application = create_app(database_settings)
    database = cast(DatabaseResources, application.state.database)
    assert isinstance(database.engine.pool, QueuePool)

    @application.get("/_test/db-success")
    def database_success(
        session: Annotated[Session, Depends(get_db_session)],
    ) -> dict[str, bool]:
        session.execute(text("SELECT 1"))
        return {"ok": True}

    @application.get("/_test/db-failure")
    def database_failure(
        session: Annotated[Session, Depends(get_db_session)],
    ) -> None:
        session.execute(text("SELECT 1"))
        raise HTTPException(status_code=409, detail="expected test failure")

    with TestClient(application) as client:
        assert client.get("/_test/db-success").status_code == 200
        assert database.engine.pool.checkedout() == 0
        assert client.get("/_test/db-failure").status_code == 409
        assert database.engine.pool.checkedout() == 0


def test_database_engine_uses_postgresql(database_engine: Engine) -> None:
    assert database_engine.dialect.name == "postgresql"
