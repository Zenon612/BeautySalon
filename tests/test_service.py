import pytest

@pytest.mark.asyncio
async def test_list_services(client, test_services):
    response = await client.get("/api/v1/services")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Маникюр"

@pytest.mark.asyncio
async def test_list_services_with_category(client, test_services):
    response = await client.get("/api/v1/services?category=hair")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "hair"