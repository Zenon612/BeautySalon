"""
Тесты для CRUD операций с услугами (Services).

Проверяет:
- Получение списка услуг с пагинацией
- Получение услуги по ID
- Создание новой услуги (admin only)
- Обновление услуги (admin only)
- Деактивация услуги (admin only)
- Фильтрация по категориям
"""
import pytest


class TestServiceList:
    """Тесты получения списка услуг."""
    
    @pytest.mark.asyncio
    async def test_list_services_success(self, client, test_services):
        """Тест: успешное получение списка услуг."""
        response = await client.get("/api/v1/services")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert data["total"] == 3  # 3 активные услуги
        assert len(data["items"]) == 3
    
    @pytest.mark.asyncio
    async def test_list_services_pagination(self, client, test_services):
        """Тест: пагинация списка услуг."""
        response = await client.get("/api/v1/services?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["pages"] == 2  # 3 услуги / 2 на страницу = 2 страницы
    
    @pytest.mark.asyncio
    async def test_list_services_filter_by_category(self, client, test_services):
        """Тест: фильтрация услуг по категории."""
        response = await client.get("/api/v1/services?category=hair")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "hair"
    
    @pytest.mark.asyncio
    async def test_list_services_invalid_category(self, client, test_services):
        """Тест: невалидная категория."""
        response = await client.get("/api/v1/services?category=invalid")
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_list_services_empty_result(self, client):
        """Тест: получение пустого списка (нет услуг)."""
        response = await client.get("/api/v1/services")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestServiceGet:
    """Тесты получения услуги по ID."""
    
    @pytest.mark.asyncio
    async def test_get_service_by_id(self, client, test_services):
        """Тест: успешное получение услуги по ID."""
        service = test_services[0]
        response = await client.get(f"/api/v1/services/{service.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == service.id
        assert data["name"] == service.name
    
    @pytest.mark.asyncio
    async def test_get_service_not_found(self, client):
        """Тест: услуга не найдена."""
        response = await client.get("/api/v1/services/9999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_inactive_service(self, client, db_session):
        """Тест: получение неактивной услуги."""
        from app.db.models.models import Service, ServiceCategory
        
        service = Service(
            name="Inactive Service",
            category=ServiceCategory.HAIR,
            price=1000,
            duration_minutes=30,
            is_active=False,
        )
        db_session.add(service)
        await db_session.commit()
        
        response = await client.get(f"/api/v1/services/{service.id}")
        assert response.status_code == 404


class TestServiceCreate:
    """Тесты создания услуг."""
    
    @pytest.mark.asyncio
    async def test_create_service_success(self, client, auth_headers):
        """Тест: успешное создание услуги администратором."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Новая услуга",
                "description": "Описание новой услуги",
                "category": "hair",
                "price": 2500,
                "duration_minutes": 60
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Новая услуга"
        assert data["price"] == 2500
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_create_service_duplicate_name(self, client, auth_headers, test_services):
        """Тест: создание услуги с существующим названием."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Стрижка женская",
                "category": "hair",
                "price": 1500,
                "duration_minutes": 45
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_service_unauthorized(self, client):
        """Тест: создание услуги без авторизации."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Unauthorized Service",
                "category": "hair",
                "price": 1000,
                "duration_minutes": 30
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_service_non_admin(self, client, user_auth_headers):
        """Тест: создание услуги обычным пользователем."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Non-admin Service",
                "category": "hair",
                "price": 1000,
                "duration_minutes": 30
            },
            headers=user_auth_headers
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_service_invalid_price(self, client, auth_headers):
        """Тест: создание услуги с отрицательной ценой."""
        response = await client.post(
            "/api/v1/services",
            json={
                "name": "Invalid Service",
                "category": "hair",
                "price": -100,
                "duration_minutes": 30
            },
            headers=auth_headers
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_service_missing_fields(self, client, auth_headers):
        """Тест: создание услуги без обязательных полей."""
        response = await client.post(
            "/api/v1/services",
            json={
                "category": "hair",
                "price": 1000
                # missing name and duration_minutes
            },
            headers=auth_headers
        )
        assert response.status_code == 422


class TestServiceUpdate:
    """Тесты обновления услуг."""
    
    @pytest.mark.asyncio
    async def test_update_service_success(self, client, auth_headers, test_services):
        """Тест: успешное обновление услуги."""
        service = test_services[0]
        response = await client.put(
            f"/api/v1/services/{service.id}",
            json={
                "name": "Обновлённая стрижка",
                "price": 2000
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Обновлённая стрижка"
        assert data["price"] == 2000
    
    @pytest.mark.asyncio
    async def test_update_service_not_found(self, client, auth_headers):
        """Тест: обновление несуществующей услуги."""
        response = await client.put(
            "/api/v1/services/9999",
            json={"name": "Updated Service"},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_service_unauthorized(self, client, test_services):
        """Тест: обновление услуги без авторизации."""
        service = test_services[0]
        response = await client.put(
            f"/api/v1/services/{service.id}",
            json={"name": "Updated Service"}
        )
        assert response.status_code == 401


class TestServiceDeactivate:
    """Тесты деактивации услуг."""
    
    @pytest.mark.asyncio
    async def test_deactivate_service_success(self, client, auth_headers, test_services):
        """Тест: успешная деактивация услуги."""
        service = test_services[0]
        response = await client.delete(
            f"/api/v1/services/{service.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    @pytest.mark.asyncio
    async def test_deactivate_service_not_found(self, client, auth_headers):
        """Тест: деактивация несуществующей услуги."""
        response = await client.delete(
            "/api/v1/services/9999",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_deactivate_service_unauthorized(self, client, test_services):
        """Тест: деактивация услуги без авторизации."""
        service = test_services[0]
        response = await client.delete(f"/api/v1/services/{service.id}")
        assert response.status_code == 401
