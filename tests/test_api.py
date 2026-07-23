import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from core.database import Base, engine # Перевір, чи правильно імпортується engine та Base

@pytest.fixture(autouse=True)
async def setup_database():
    """Автоматично створює таблиці перед запуском тестів"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_solve_geometry_unauthorized_access(client):
    """Перевіряємо, що гість НЕ має доступу до преміум-фігур (curves)"""
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
    assert data["success"] is False
    assert "Ця фігура доступна лише зареєстрованим користувачам" in data["error"]


@pytest.mark.asyncio
async def test_solve_unknown_figure(client):
    """Перевіряємо реакцію на невідому фігуру (гість)"""
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
    assert "Ця фігура доступна лише зареєстрованим користувачам" in data["error"]


@pytest.mark.asyncio
async def test_solve_geometry_validation_error(client):
    """Перевіряємо валідацію помилкових параметрів"""
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


import uuid


@pytest.mark.asyncio
async def test_solve_geometry_success_authorized(client):
    """Перевіряємо успішний розв'язок для авторизованого користувача"""

    unique_username = f"testuser_{uuid.uuid4().hex[:6]}"

    # 1. РЕЄСТРАЦІЯ
    reg_response = await client.post(
        "/api/auth/register",
        json={"username": unique_username, "password": "testpassword1"}
    )
    assert reg_response.status_code in [200, 201], f"Помилка реєстрації: {reg_response.text}"

    # 2. ЛОГІН (Передаємо через json, але оскільки помилка вимагала словник/об'єкт,
    # переконайся, що твій роут логіну приймає JSON об'єкт)
    login_response = await client.post(
        "/api/auth/login",
        json={"username": unique_username, "password": "testpassword1"}
    )

    # На випадок, якщо твій роут логіну все ж таки за замовчуванням вимагає OAuth2 форму,
    # а не JSON, ми зробимо універсальну перевірку або передачу через json
    assert login_response.status_code == 200, f"Помилка логіну: {login_response.text}"

    # Витягуємо токен (перевір, чи ключ називається 'access_token', можливо у тебе просто 'token')
    token_data = login_response.json()
    token = token_data.get("access_token") or token_data.get("token")
    assert token is not None, f"Токен не знайдено у відповіді сервера: {token_data}"

    headers = {"Authorization": f"Bearer {token}"}

    # 3. РОЗВ'ЯЗАННЯ ЗАДАЧІ
    response = await client.post(
        "/api/solve",
        json={
            "figure": "curves",
            "task_type": "CIRCLE_RADIUS",
            "targets": ["area"],
            "params": {"radius": 2},
        },
        headers=headers
    )
    data = response.json()

    assert response.status_code == 200, f"Помилка розв'язання: {response.text}"
    assert data["success"] is True
    assert data["data"]["area"] == pytest.approx(12.57, rel=0.01)