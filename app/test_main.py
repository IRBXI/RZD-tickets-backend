import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.config import settings


@pytest.mark.anyio
async def test_get_station_code():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=settings.API_V1_STR
    ) as ac:
        response = await ac.get(f"/stations?name=Москва")

        assert response.status_code == 200
        assert response.json == "2000000"

        response = await ac.get(f"/stations?name=Санкт-Петербург")

        assert response.status_code == 200
        assert response.json == "2004000"
