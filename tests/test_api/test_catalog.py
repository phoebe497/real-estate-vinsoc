import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.db.seed import seed_catalog
from src.db.session import get_db
from src.main import app


@pytest_asyncio.fixture
async def catalog_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        assert seed_catalog(session) == 12

    def override_get_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.asyncio
async def test_list_seeded_subdivisions(catalog_client):
    response = await catalog_client.get("/api/v1/subdivisions")

    assert response.status_code == 200
    assert len(response.json()) == 12
    assert response.json()[0]["slug"] == "the-sapphire"


@pytest.mark.asyncio
async def test_get_subdivision_detail(catalog_client):
    response = await catalog_client.get("/api/v1/subdivisions/the-zenpark")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "The Zenpark"
    assert payload["apartment_specs"]
    assert {item["scope"] for item in payload["amenities"]} == {"internal", "external"}


@pytest.mark.asyncio
async def test_create_contact(catalog_client):
    response = await catalog_client.post(
        "/api/v1/contact",
        json={
            "name": "Nguyễn An",
            "phone": "0912 345 678",
            "email": "an@example.com",
            "preferred_bedrooms": "2PN",
            "subdivision_slug": "the-zenpark",
            "message": "Muốn nhận bảng giá mới",
        },
    )

    assert response.status_code == 201
    assert response.json()["customer_id"] > 0


@pytest.mark.asyncio
async def test_reject_invalid_phone(catalog_client):
    response = await catalog_client.post("/api/v1/contact", json={"phone": "123"})

    assert response.status_code == 422
