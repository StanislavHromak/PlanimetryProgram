import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_solve_geometry_success(client):
    response = await client.post(
        "/api/solve",
        json={
            "figure": "curves",
            "task_type": "CIRCLE_RADIUS",
            "targets": ["area"],
            "params": {"radius": 2},
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["data"]["area"] == pytest.approx(12.57, rel=0.01)


@pytest.mark.asyncio
async def test_solve_geometry_validation_error(client):
    response = await client.post(
        "/api/solve",
        json={
            "figure": "curves",
            "task_type": "CIRCLE_RADIUS",
            "targets": ["area"],
            "params": {"radius": -1},
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "error" in data


@pytest.mark.asyncio
async def test_solve_unknown_figure(client):
    response = await client.post(
        "/api/solve",
        json={
            "figure": "nonexistent",
            "task_type": "CIRCLE_RADIUS",
            "targets": ["area"],
            "params": {"radius": 1},
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "Фабрика не знає" in data["error"]
