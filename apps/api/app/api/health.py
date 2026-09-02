"""Process health routes."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/health", tags=["health"])


class LivenessResponse(BaseModel):
    """Versioned contract proving that the API process can answer HTTP."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    schema_version: Literal["1"] = "1"


@router.get("/live", response_model=LivenessResponse)
async def get_liveness() -> LivenessResponse:
    """Report process liveness without checking external dependencies."""
    return LivenessResponse()
