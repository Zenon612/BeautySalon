"""
Тесты для CRUD операций с мастерами (Masters).

Проверяет:
- Получение списка мастеров с пагинацией
- Получение мастера по ID
- Создание нового мастера (admin only)
- Обновление мастера (admin only)
- Деактивация мастера (admin only)
- Фильтрация по специализации
"""
import pytest


class TestMasterList:
    """Тесты получения списка мастеров."""
    
    @pytest.mark.asyncio
    async def test_list_masters_success(self, client, test_masters):
        """Тест: успешное получение списка мастеров."""
        response = await client.get("/api/v1/masters")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["items"]) == 3
    
    @pytest.mark.asyncio
    async def test_list_masters_pagination(self, client, test_masters):
        """Тест: пагинация списка мастеров."""
        response = await client.get("/api/v1/masters?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
    
    @pytest.mark.asyncio
    async def test_list_masters_filter_by_specialty(self, client, test_masters):
        """Тест: фильтрация мастеров по специализации."""
        response = await client.get("/api/v1/masters?specialty=hair")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["specialty"] == "hair"
    
    @pytest.mark.asyncio
    async def test_list_masters_empty_filter(self, client, test_masters):
        """Тест: фильтрация без результатов."""
        response = await client.get("/api/v1/masters?specialty=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestMasterGet:
    """Тесты получения мастера по ID."""
    
    @pytest.mark.asyncio
    async def test_get_master_by_id(self, client, test_masters):
        """Тест: успешное получение мастера по ID."""
        master = test_masters[0]
        response = await client.get(f"/api/v1/masters/{master.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == master.id
        assert data["name"] == master.name
    
    @pytest.mark.asyncio
    async def test_get_master_not_found(self, client):
        """Тест: мастер не найден."""
        response = await client.get("/api/v1/masters/9999")
        assert response.status_code == 404


class TestMasterCreate:
    """Тесты создания мастеров."""
    
    @pytest.mark.asyncio
    async def test_create_master_success(self, client, auth_headers):
        """Тест: успешное создание мастера."""
        response = await client.post(
            "/api/v1/masters",
            json={
                "name": "Кузнецова Анна",
                "specialty": "hair",
                "description": "Мастер-стилист международного класса",
                "photo_url": "/static/masters/anna.jpg"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Кузнецова Анна"
        assert data["specialty"] == "hair"
        assert data["is_active"] is True
        assert data["rating"] == 5.0
    
    @pytest.mark.asyncio
    async def test_create_master_duplicate_name(self, client, auth_headers, test_masters):
        """Тест: создание мастера с существующим именем."""
        response = await client.post(
            "/api/v1/masters",
            json={
                "name": "Иванова Мария",
                "specialty": "nails",
                "description": "Новый мастер",
                "photo_url": "/static/masters/new.jpg"
            },
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "уже существует" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_master_unauthorized(self, client):
        """Тест: создание мастера без авторизации."""
        response = await client.post(
            "/api/v1/masters",
            json={
                "name": "Unauthorized Master",
                "specialty": "hair"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_master_non_admin(self, client, user_auth_headers):
        """Тест: создание мастера обычным пользователем."""
        response = await client.post(
            "/api/v1/masters",
            json={
                "name": "Non-admin Master",
                "specialty": "hair"
            },
            headers=user_auth_headers
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_master_missing_name(self, client, auth_headers):
        """Тест: создание мастера без имени."""
        response = await client.post(
            "/api/v1/masters",
            json={
                "specialty": "hair",
                "description": "No name master"
            },
            headers=auth_headers
        )
        assert response.status_code == 422


class TestMasterUpdate:
    """Тесты обновления мастеров."""
    
    @pytest.mark.asyncio
    async def test_update_master_success(self, client, auth_headers, test_masters):
        """Тест: успешное обновление мастера."""
        master = test_masters[0]
        response = await client.put(
            f"/api/v1/masters/{master.id}",
            json={
                "name": "Иванова Мария (обновлено)",
                "rating": 5.0
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Иванова Мария (обновлено)"
        assert data["rating"] == 5.0
    
    @pytest.mark.asyncio
    async def test_update_master_invalid_rating(self, client, auth_headers, test_masters):
        """Тест: обновление с невалидным рейтингом."""
        master = test_masters[0]
        response = await client.put(
            f"/api/v1/masters/{master.id}",
            json={"rating": 6.0},
            headers=auth_headers
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_master_not_found(self, client, auth_headers):
        """Тест: обновление несуществующего мастера."""
        response = await client.put(
            "/api/v1/masters/9999",
            json={"name": "Updated Master"},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_master_unauthorized(self, client, test_masters):
        """Тест: обновление мастера без авторизации."""
        master = test_masters[0]
        response = await client.put(
            f"/api/v1/masters/{master.id}",
            json={"name": "Updated Master"}
        )
        assert response.status_code == 401


class TestMasterDeactivate:
    """Тесты деактивации мастеров."""
    
    @pytest.mark.asyncio
    async def test_deactivate_master_success(self, client, auth_headers, test_masters):
        """Тест: успешная деактивация мастера."""
        master = test_masters[0]
        response = await client.delete(
            f"/api/v1/masters/{master.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    
    @pytest.mark.asyncio
    async def test_deactivate_master_not_found(self, client, auth_headers):
        """Тест: деактивация несуществующего мастера."""
        response = await client.delete(
            "/api/v1/masters/9999",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_deactivate_master_unauthorized(self, client, test_masters):
        """Тест: деактивация мастера без авторизации."""
        master = test_masters[0]
        response = await client.delete(f"/api/v1/masters/{master.id}")
        assert response.status_code == 401
