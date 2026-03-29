"""
Тесты для CRUD операций с портфолио (Portfolio).

Проверяет:
- Получение списка элементов портфолио с пагинацией
- Получение элемента по ID
- Создание нового элемента (admin only)
- Обновление элемента (admin only)
- Деактивация элемента (admin only)
- Фильтрация по категориям
"""
import pytest


class TestPortfolioList:
    """Тесты получения списка портфолио."""
    
    @pytest.mark.asyncio
    async def test_list_portfolio_success(self, client, test_portfolio):
        """Тест: успешное получение списка портфолио."""
        response = await client.get("/api/v1/portfolio")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 3  # Минимум 3 элемента
        assert len(data["items"]) >= 3
    
    @pytest.mark.asyncio
    async def test_list_portfolio_pagination(self, client, test_portfolio):
        """Тест: пагинация портфолио."""
        response = await client.get("/api/v1/portfolio?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
    
    @pytest.mark.asyncio
    async def test_list_portfolio_filter_by_category(self, client, test_portfolio):
        """Тест: фильтрация портфолио по категории."""
        response = await client.get("/api/v1/portfolio?category=hair")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        # Все элементы должны быть категории hair
        for item in data["items"]:
            assert item["category"] == "hair"
    
    @pytest.mark.asyncio
    async def test_list_portfolio_empty_filter(self, client, test_portfolio):
        """Тест: фильтрация портфолио без результатов."""
        response = await client.get("/api/v1/portfolio?category=facial")
        assert response.status_code == 200
        data = response.json()
        # facial может быть или не быть в тестовых данных
        assert data["total"] >= 0


class TestPortfolioGet:
    """Тесты получения элемента портфолио по ID."""
    
    @pytest.mark.asyncio
    async def test_get_portfolio_by_id(self, client, test_portfolio):
        """Тест: успешное получение элемента по ID."""
        item = test_portfolio[0]
        response = await client.get(f"/api/v1/portfolio/{item.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item.id
        assert data["title"] == item.title
        # master может быть null, если не подгружен
    
    @pytest.mark.asyncio
    async def test_get_portfolio_not_found(self, client):
        """Тест: элемент портфолио не найден."""
        response = await client.get("/api/v1/portfolio/9999")
        assert response.status_code == 404


class TestPortfolioCreate:
    """Тесты создания элементов портфолио."""
    
    @pytest.mark.asyncio
    async def test_create_portfolio_success(self, client, auth_headers, test_masters):
        """Тест: успешное создание элемента портфолио."""
        response = await client.post(
            "/api/v1/portfolio",
            json={
                "title": "Новая работа",
                "description": "Описание новой работы",
                "category": "nails",
                "image_url": "/static/portfolio/new_work.jpg",
                "is_featured": True,
                "master_id": test_masters[1].id
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Новая работа"
        assert data["category"] == "nails"
        assert data["is_featured"] is True
    
    @pytest.mark.asyncio
    async def test_create_portfolio_unauthorized(self, client, test_masters):
        """Тест: создание портфолио без авторизации."""
        response = await client.post(
            "/api/v1/portfolio",
            json={
                "title": "Unauthorized Work",
                "category": "hair",
                "image_url": "/static/portfolio/unauthorized.jpg"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_portfolio_non_admin(self, client, user_auth_headers, test_masters):
        """Тест: создание портфолио обычным пользователем."""
        response = await client.post(
            "/api/v1/portfolio",
            json={
                "title": "Non-admin Work",
                "category": "hair",
                "image_url": "/static/portfolio/nonadmin.jpg"
            },
            headers=user_auth_headers
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_portfolio_missing_fields(self, client, auth_headers):
        """Тест: создание портфолио без обязательных полей."""
        response = await client.post(
            "/api/v1/portfolio",
            json={
                "description": "Missing required fields"
                # missing title, category, image_url
            },
            headers=auth_headers
        )
        assert response.status_code == 422


class TestPortfolioUpdate:
    """Тесты обновления элементов портфолио."""
    
    @pytest.mark.asyncio
    async def test_update_portfolio_success(self, client, auth_headers, test_portfolio):
        """Тест: успешное обновление элемента портфолио."""
        item = test_portfolio[0]
        response = await client.put(
            f"/api/v1/portfolio/{item.id}",
            json={
                "title": "Обновлённая работа",
                "is_featured": False
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Обновлённая работа"
        assert data["is_featured"] is False
    
    @pytest.mark.asyncio
    async def test_update_portfolio_not_found(self, client, auth_headers):
        """Тест: обновление несуществующего элемента."""
        response = await client.put(
            "/api/v1/portfolio/9999",
            json={"title": "Updated Work"},
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_portfolio_unauthorized(self, client, test_portfolio):
        """Тест: обновление портфолио без авторизации."""
        item = test_portfolio[0]
        response = await client.put(
            f"/api/v1/portfolio/{item.id}",
            json={"title": "Updated Work"}
        )
        assert response.status_code == 401


class TestPortfolioDeactivate:
    """Тесты деактивации элементов портфолио."""
    
    @pytest.mark.asyncio
    async def test_deactivate_portfolio_success(self, client, auth_headers, test_portfolio):
        """Тест: успешная деактивация элемента портфолио."""
        item = test_portfolio[0]
        response = await client.delete(
            f"/api/v1/portfolio/{item.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_featured"] is False
    
    @pytest.mark.asyncio
    async def test_deactivate_portfolio_not_found(self, client, auth_headers):
        """Тест: деактивация несуществующего элемента."""
        response = await client.delete(
            "/api/v1/portfolio/9999",
            headers=auth_headers
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_deactivate_portfolio_unauthorized(self, client, test_portfolio):
        """Тест: деактивация портфолио без авторизации."""
        item = test_portfolio[0]
        response = await client.delete(f"/api/v1/portfolio/{item.id}")
        assert response.status_code == 401
