"""FastAPI dependency for request-scoped SQLAlchemy sessions."""

from collections.abc import Iterator
from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db.engine import DatabaseResources


def get_db_session(request: Request) -> Iterator[Session]:
    """Yield one session and close it for every success or failure path."""
    database = cast(DatabaseResources, request.app.state.database)
    with database.session_factory() as session:
        yield session


DbSession = Annotated[Session, Depends(get_db_session)]
