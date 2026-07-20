import pytest
from pydantic import ValidationError

from src.config import Settings


def deployment_settings(**overrides) -> dict:
    values = {
        "app_env": "production",
        "database_url": "postgresql+psycopg://user:password@database:5432/app",
        "auto_create_tables": False,
        "jwt_secret_key": "a-unique-production-secret-with-32-characters",
        "admin_password": "a-unique-admin-password",
        "cors_origins": "https://example.com",
    }
    values.update(overrides)
    return values


def test_valid_production_configuration():
    settings = Settings(_env_file=None, **deployment_settings())

    assert settings.app_env == "production"
    assert settings.cors_origin_list == ["https://example.com"]


@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        ("jwt_secret_key", "development-only-change-me", "JWT_SECRET_KEY"),
        ("admin_password", "ChangeMe123!", "ADMIN_PASSWORD"),
        ("database_url", "sqlite:///./app.db", "PostgreSQL"),
        ("auto_create_tables", True, "AUTO_CREATE_TABLES"),
        ("cors_origins", "http://localhost:3000", "CORS_ORIGINS"),
    ],
)
def test_unsafe_production_configuration_is_rejected(field, value, expected_message):
    with pytest.raises(ValidationError, match=expected_message):
        Settings(_env_file=None, **deployment_settings(**{field: value}))


def test_staging_allows_staging_domain():
    settings = Settings(
        _env_file=None,
        **deployment_settings(
            app_env="staging",
            cors_origins="https://staging.example.com, https://api-staging.example.com",
        ),
    )

    assert settings.cors_origin_list == [
        "https://staging.example.com",
        "https://api-staging.example.com",
    ]
