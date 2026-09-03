"""HTTP contract tests for the API shell."""

from uuid import UUID

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Environment, Settings
from app.core.request_id import REQUEST_ID_HEADER
from app.main import create_app


def build_client() -> TestClient:
    """Create a test client with explicit non-local settings."""
    settings = Settings(environment=Environment.TEST)
    return TestClient(create_app(settings))


def test_liveness_returns_versioned_response() -> None:
    with build_client() as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "schema_version": "1"}


def test_request_id_is_generated_and_returned() -> None:
    with build_client() as client:
        first_response = client.get("/health/live")
        second_response = client.get("/health/live")

    first_request_id = first_response.headers[REQUEST_ID_HEADER]
    second_request_id = second_response.headers[REQUEST_ID_HEADER]
    assert UUID(first_request_id).version == 4
    assert UUID(second_request_id).version == 4
    assert first_request_id != second_request_id


def test_valid_caller_request_id_is_propagated() -> None:
    caller_request_id = "reviewflow-test:1234"

    with build_client() as client:
        response = client.get(
            "/health/live",
            headers={REQUEST_ID_HEADER: caller_request_id},
        )

    assert response.headers[REQUEST_ID_HEADER] == caller_request_id


def test_invalid_caller_request_id_is_replaced() -> None:
    invalid_request_id = "contains spaces and cannot be logged safely"

    with build_client() as client:
        response = client.get(
            "/health/live",
            headers={REQUEST_ID_HEADER: invalid_request_id},
        )

    assert response.headers[REQUEST_ID_HEADER] != invalid_request_id
    assert UUID(response.headers[REQUEST_ID_HEADER]).version == 4


def test_unknown_route_uses_fastapi_default_not_found_response() -> None:
    with build_client() as client:
        response = client.get("/not-a-route")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    assert REQUEST_ID_HEADER in response.headers


def test_readiness_failure_is_non_sensitive_and_does_not_change_liveness() -> None:
    settings = Settings(
        environment=Environment.TEST,
        database_url=SecretStr("postgresql+psycopg://user:secret@127.0.0.1:1/unavailable"),
        database_timeout_seconds=1,
    )

    with TestClient(create_app(settings)) as client:
        readiness = client.get("/health/ready")
        liveness = client.get("/health/live")

    assert readiness.status_code == 503
    assert readiness.json() == {"status": "unavailable", "schema_version": "1"}
    assert "secret" not in readiness.text
    assert liveness.status_code == 200


def test_unexpected_exception_does_not_expose_detail_in_production() -> None:
    application = create_app(Settings(environment=Environment.PRODUCTION))

    @application.get("/unexpected-failure")
    async def raise_unexpected_failure() -> None:
        raise RuntimeError("confidential diagnostic detail")

    with TestClient(application, raise_server_exceptions=False) as client:
        response = client.get("/unexpected-failure")

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert "confidential diagnostic detail" not in response.text
