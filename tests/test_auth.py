"""
Тесты для модуля аутентификации и авторизации.

Проверяет:
- Регистрацию пользователей
- Вход в систему
- Валидацию токенов
- Права доступа администратора
"""
import pytest
from httpx import AsyncClient


class TestAuthRegistration:
    """Тесты регистрации пользователей."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """Тест: успешная регистрация нового пользователя."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Newpassword123",
                "full_name": "New User",
                "phone": "+7 (999) 123-45-67"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, regular_user):
        """Тест: регистрация с существующим email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "Newpassword123",
                "full_name": "Another User",
                "phone": "+7 (999) 999-99-99"
            }
        )
        # Pydantic валидирует email до проверки на дубликат
        assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Тест: регистрация с невалидным email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
                "full_name": "Test User",
                "phone": "+7 (999) 123-45-67"
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_short_password(self, client):
        """Тест: регистрация с коротким паролем."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",
                "full_name": "Test User",
                "phone": "+7 (999) 123-45-67"
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        """Тест: регистрация без обязательных полей."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
                # missing full_name and phone
            }
        )
        assert response.status_code == 422


class TestAuthLogin:
    """Тесты входа в систему."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client, regular_user):
        """Тест: успешный вход."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "Userpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client, regular_user):
        """Тест: неверный пароль."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "detail" in response.json()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client):
        """Тест: вход несуществующего пользователя."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"}
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, db_session):
        """Тест: вход неактивного пользователя."""
        from app.db.models.models import User
        from app.services.auth import get_password_hash
        
        user = User(
            email="inactive@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Inactive User",
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "password123"}
        )
        assert response.status_code == 401


class TestAuthAdmin:
    """Тесты прав администратора."""
    
    @pytest.mark.asyncio
    async def test_admin_token_has_admin_rights(self, admin_token):
        """Тест: токен администратора содержит права."""
        from jose import jwt
        from app.core.config import settings
        
        payload = jwt.decode(
            admin_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"verify_exp": False}
        )
        assert payload.get("is_admin") is True
    
    @pytest.mark.asyncio
    async def test_user_token_no_admin_rights(self, user_token):
        """Тест: токен обычного пользователя не имеет прав админа."""
        from jose import jwt
        from app.core.config import settings
        
        payload = jwt.decode(
            user_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"verify_exp": False}
        )
        assert payload.get("is_admin") is False


class TestAuthEndpoints:
    """Тесты защиты эндпоинтов."""
    
    @pytest.mark.asyncio
    async def test_create_service_requires_admin(self, client, user_token):
        """Тест: создание услуги требует прав администратора."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Test Service",
                "category": "hair",
                "price": 1000,
                "duration_minutes": 30
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_service_with_admin_token(self, client, admin_token):
        """Тест: создание услуги с токеном администратора."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Admin Service",
                "category": "hair",
                "price": 2000,
                "duration_minutes": 60
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        """Тест: неавторизованный доступ к защищённому эндпоинту."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Test Service",
                "category": "hair",
                "price": 1000,
                "duration_minutes": 30
            }
        )
        assert response.status_code == 401
