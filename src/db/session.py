import sys
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings


@lru_cache
def get_engine() -> Engine:
    database_url = get_settings().database_url
    if "pytest" in sys.modules:
        database_url = "sqlite:///./test_sync.db"
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with get_session_factory()() as session:
        yield session


def init_database() -> None:
    from src.db.base import Base
    from src.models import entities  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    _ensure_runtime_schema(engine)


def _ensure_runtime_schema(engine: Engine) -> None:
    """Best-effort compatibility for existing local/test DBs.

    Staging/production should use Alembic. This helper prevents local SQLite
    databases created before a nullable column was added from crashing during
    tests or development startup.
    """
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "conversations" not in table_names or "messages" not in table_names:
        return

    conversation_columns = {column["name"] for column in inspector.get_columns("conversations")}
    message_columns = {column["name"] for column in inspector.get_columns("messages")}

    statements: list[str] = []
    if "customer_id" not in conversation_columns:
        statements.append("ALTER TABLE conversations ADD COLUMN customer_id INTEGER")
    if "user_message_count" not in conversation_columns:
        statements.append("ALTER TABLE conversations ADD COLUMN user_message_count INTEGER DEFAULT 0")
    if "is_lead_captured" not in conversation_columns:
        statements.append("ALTER TABLE conversations ADD COLUMN is_lead_captured BOOLEAN DEFAULT 0")
    if "role" not in message_columns:
        statements.append("ALTER TABLE messages ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
    if "meta" not in message_columns:
        statements.append("ALTER TABLE messages ADD COLUMN meta JSON")

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
