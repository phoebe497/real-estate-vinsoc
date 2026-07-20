from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from src.config import get_settings


def test_migrations_upgrade_and_downgrade(tmp_path, monkeypatch):
    database_path = tmp_path / "migration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    get_settings.cache_clear()
    config = Config("alembic.ini")

    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    tables = set(inspect(engine).get_table_names())
    assert {
        "subdivisions",
        "apartment_specs",
        "amenities",
        "sales_policies",
        "customers",
        "customer_notes",
        "purchase_history",
        "sale_awards",
        "permissions",
        "user_permissions",
        "user_subdivisions",
        "conversations",
        "messages",
        "fallback_rules",
    }.issubset(tables)
    assert "leads" not in tables
    assert "customer_accounts" not in tables

    engine.dispose()
    command.downgrade(config, "base")
    get_settings.cache_clear()
