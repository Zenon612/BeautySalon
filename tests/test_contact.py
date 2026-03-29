"""
Тесты для CRUD операций с контактной информацией (Contact).

Проверяет:
- Получение контактной информации
- Создание контактной информации (admin only)
- Обновление контактной информации (admin only)
- Обработка случая, когда контакт не найден
"""
import pytest


class TestContactGet:
    """Тесты получения контактной информации."""
    
    @pytest.mark.asyncio
    async def test_z_get_contact_not_found(self, client):
        """Тест: контактная информация не найдена (чистая БД)."""
        response = await client.get("/api/v1/contact")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_z_get_contact_success(self, client, test_contact):
        """Тест: успешное получение контактной информации."""
        response = await client.get("/api/v1/contact")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_contact.id
        assert data["address"] == test_contact.address
        assert data["phone"] == test_contact.phone
        assert data["email"] == test_contact.email


class ATestContactCreate:
    """Тесты создания контактной информации."""
    
    @pytest.mark.asyncio
    async def test_create_contact_success(self, client, auth_headers):
        """Тест: успешное создание контактной информации."""
        # Сначала проверяем, что контакта нет
        get_response = await client.get("/api/v1/contact")
        assert get_response.status_code == 404
        
        # Создаём контакт
        response = await client.post(
            "/api/v1/contact",
            json={
                "address": "г. Москва, ул. Новая, д. 10",
                "phone": "+7 (495) 999-88-77",
                "email": "newinfo@beautysalon.ru",
                "working_hours": "Пн-Вс: 09:00 - 21:00",
                "latitude": 55.7500,
                "longitude": 37.6200,
                "social_telegram": "https://t.me/newbeautysalon",
                "social_vk": "https://vk.com/newbeautysalon"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["address"] == "г. Москва, ул. Новая, д. 10"
        assert data["email"] == "newinfo@beautysalon.ru"
    
    @pytest.mark.asyncio
    async def test_create_contact_duplicate(self, client, auth_headers, test_contact):
        """Тест: создание дублирующейся контактной информации."""
        response = await client.post(
            "/api/v1/contact",
            json={
                "address": "Duplicate Address",
                "phone": "+7 (999) 000-00-00",
                "email": "duplicate@example.com"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_contact_unauthorized(self, client):
        """Тест: создание контакта без авторизации."""
        response = await client.post(
            "/api/v1/contact",
            json={
                "address": "Unauthorized Address",
                "phone": "+7 (999) 000-00-00"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_contact_non_admin(self, client, user_auth_headers):
        """Тест: создание контакта обычным пользователем."""
        response = await client.post(
            "/api/v1/contact",
            json={
                "address": "Non-admin Address",
                "phone": "+7 (999) 000-00-00"
            },
            headers=user_auth_headers
        )
        assert response.status_code == 401


class TestContactUpdate:
    """Тесты обновления контактной информации."""
    
    @pytest.mark.asyncio
    async def test_update_contact_success(self, client, auth_headers, test_contact):
        """Тест: успешное обновление контактной информации."""
        response = await client.put(
            "/api/v1/contact",
            json={
                "address": "Обновлённый адрес",
                "phone": "+7 (495) 111-22-33",
                "email": "updated@beautysalon.ru"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == "Обновлённый адрес"
        assert data["phone"] == "+7 (495) 111-22-33"
        assert data["email"] == "updated@beautysalon.ru"
    
    @pytest.mark.asyncio
    async def test_update_contact_partial(self, client, auth_headers, test_contact):
        """Тест: частичное обновление контактной информации."""
        response = await client.put(
            "/api/v1/contact",
            json={
                "phone": "+7 (495) 555-44-33"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+7 (495) 555-44-33"
        # Остальные поля должны сохраниться
        assert data["address"] == test_contact.address
    
    @pytest.mark.asyncio
    async def test_update_contact_not_found(self, client, auth_headers):
        """Тест: обновление несуществующей контактной информации."""
        response = await client.put(
            "/api/v1/contact",
            json={"address": "Updated Address"},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_contact_unauthorized(self, client, test_contact):
        """Тест: обновление контакта без авторизации."""
        response = await client.put(
            "/api/v1/contact",
            json={"address": "Unauthorized Address"}
        )
        assert response.status_code == 401


class ATestContactEndpoints:
    """Интеграционные тесты для контактной информации."""
    
    @pytest.mark.asyncio
    async def test_contact_workflow(self, client, auth_headers):
        """Тест: полный цикл работы с контактной информацией."""
        # 1. Сначала проверяем, что контакта нет
        get_response = await client.get("/api/v1/contact")
        assert get_response.status_code == 404
        
        # 2. Создание
        create_response = await client.post(
            "/api/v1/contact",
            json={
                "address": "Test Address",
                "phone": "+7 (999) 111-22-33",
                "email": "test@example.com",
                "working_hours": "10:00 - 20:00"
            },
            headers=auth_headers
        )
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]
        
        # 3. Получение
        get_response = await client.get("/api/v1/contact")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == created_id
        
        # 4. Обновление
        update_response = await client.put(
            "/api/v1/contact",
            json={"phone": "+7 (999) 999-88-77"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["phone"] == "+7 (999) 999-88-77"
        
        # 5. Проверка обновления
        final_response = await client.get("/api/v1/contact")
        assert final_response.json()["phone"] == "+7 (999) 999-88-77"
