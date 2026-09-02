"""FastAPI composition root."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging, get_logger
from app.core.request_id import RequestIdMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the API after validating process configuration."""
    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings.log_level)
    logger = get_logger(__name__)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "application_started",
            extra={"environment": resolved_settings.environment.value},
        )
        yield
        logger.info("application_stopped")

    application = FastAPI(
        title="ReviewFlow API",
        version="0.1.0",
        debug=resolved_settings.environment.is_local,
        lifespan=lifespan,
    )
    application.add_middleware(RequestIdMiddleware)
    application.include_router(api_router)
    return application


app = create_app()
