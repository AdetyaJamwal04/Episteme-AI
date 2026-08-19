"""Tests for System Health and OpenAPI Documentation."""

import pytest
from httpx import ASGITransport, AsyncClient

from verifact.api.app import create_app


@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    """Verify GET /api/v1/health returns healthy status."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["database_connected"] is True
        assert data["redis_connected"] is True


@pytest.mark.asyncio
async def test_openapi_schema_generation() -> None:
    """Verify OpenAPI JSON schema is generated with registered endpoints."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema
        assert "/api/v1/check" in schema["paths"]
        assert "/api/v1/research" in schema["paths"]
        assert "/api/v1/health" in schema["paths"]


@pytest.mark.asyncio
async def test_web_dashboard_root_serving() -> None:
    """Verify GET / returns the HTML5 web dashboard."""
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "VeriFact" in response.text
        assert "claim-input" in response.text
