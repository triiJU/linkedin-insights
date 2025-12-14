import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_root():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_list_pages_empty():
    """Test listing pages when empty"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/pages")
        assert response.status_code == 200
        data = response.json()
        assert "pages" in data
        assert "total" in data
        assert isinstance(data["pages"], list)

@pytest.mark.asyncio
async def test_list_pages_with_pagination():
    """Test pagination parameters"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/pages?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5

@pytest.mark.asyncio
async def test_list_pages_with_filters():
    """Test filter parameters"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/pages?min_followers=1000&industry=Tech")
        assert response.status_code == 200
