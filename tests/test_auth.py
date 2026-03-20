import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    """Тест: неверный пароль"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()