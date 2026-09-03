"""Process health routes."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse

from app.core.logging import get_logger
from app.db.session import DbSession

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)


class LivenessResponse(BaseModel):
    """Versioned contract proving that the API process can answer HTTP."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    schema_version: Literal["1"] = "1"


class ReadinessResponse(BaseModel):
    """Versioned contract reporting whether required dependencies are usable."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ready", "unavailable"]
    schema_version: Literal["1"] = "1"


@router.get("/live", response_model=LivenessResponse)
async def get_liveness() -> LivenessResponse:
    """Report process liveness without checking external dependencies."""
    return LivenessResponse()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse}},
)
def get_readiness(session: DbSession) -> ReadinessResponse | JSONResponse:
    """Probe PostgreSQL without exposing connection or failure details."""
    try:
        session.execute(text("SELECT 1")).scalar_one()
    except SQLAlchemyError as error:
        logger.warning(
            "database_readiness_failed",
            extra={"error_type": type(error).__name__},
        )
        response = ReadinessResponse(status="unavailable")
        return JSONResponse(status_code=503, content=response.model_dump())

    return ReadinessResponse(status="ready")
