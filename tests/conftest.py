import os
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Xóa DB test cũ để schema V2 luôn được tạo mới sạch (file cũ có thể còn
# bảng leads/sender từ schema trước, gây lỗi NOT NULL khi insert).
for _stale in ("test_sync.db", "test_async.db", "data/test_stable.db"):
    Path(_stale).unlink(missing_ok=True)

# Stable tests must never inherit production database settings from .env.
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./data/test_stable.db"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["RAG_PROVIDER"] = "legacy"
os.environ["RAG_EMBEDDING_PROVIDER"] = "local_hash"
os.environ.pop("LANGCHAIN_API_KEY", None)
os.environ.pop("LANGSMITH_API_KEY", None)

from src.config import get_settings  # noqa: E402

get_settings.cache_clear()
from src.main import app  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "live_llm: calls the real configured LLM provider; skipped by default",
    )


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_LIVE_LLM_TESTS") == "1":
        return

    skip_live = pytest.mark.skip(
        reason="live LLM tests are skipped unless RUN_LIVE_LLM_TESTS=1"
    )
    for item in items:
        if "live_llm" in item.keywords:
            item.add_marker(skip_live)


def pytest_sessionfinish(session, exitstatus):
    """Close DB resources so pytest can exit cleanly on Windows."""
    from src.db.session import get_engine

    get_engine().dispose()


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for testing API endpoints."""
    from src.db.seed import seed_catalog
    from src.db.seed_admin import seed_admin
    from src.db.seed_permissions import seed_permissions
    from src.db.session import get_session_factory, init_database

    init_database()
    with get_session_factory()() as session:
        seed_catalog(session)
        seed_admin(session, get_settings())
        seed_permissions(session)
        session.commit()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def stable_agent_mock(request, monkeypatch):
    """Mock LangGraph agent calls for stable tests; live tests opt out by marker."""
    if request.node.get_closest_marker("live_llm"):
        return
    if "test_api" not in str(request.node.path):
        return

    mock = AsyncMock()
    mock.return_value = {
        "response": "Mocked AI Response",
        "intent": "consult",
        "trigger_handover": False,
        "recommended_zones": [],
        "citations": [],
    }
    monkeypatch.setattr("src.api.agent_routes.agent.ainvoke", mock)


@pytest.fixture(autouse=True)
def reset_security_rate_limiters():
    """Prevent process-local security limiters from leaking across tests."""
    from src.api.agent_routes import (
        _CUSTOMER_SCORE_LIMITER,
        _IP_CHAT_LIMITER,
        _SESSION_CHAT_LIMITER,
    )
    from src.api.auth import _LOGIN_ACCOUNT_LIMITER, _LOGIN_IP_LIMITER

    limiters = (
        _CUSTOMER_SCORE_LIMITER,
        _IP_CHAT_LIMITER,
        _SESSION_CHAT_LIMITER,
        _LOGIN_ACCOUNT_LIMITER,
        _LOGIN_IP_LIMITER,
    )
    for limiter in limiters:
        limiter.clear()
    yield
    for limiter in limiters:
        limiter.clear()


@pytest.fixture
def mock_llm():
    """Mock LLM to avoid calling OpenAI during tests.

    Usage in test:
        def test_something(mock_llm):
            # LLM calls will return mock response instead of hitting OpenAI
            ...
    """
    mock = AsyncMock()
    mock.ainvoke.return_value = AsyncMock(content="Mocked LLM response")
    return mock
