from urllib.parse import urljoin

from pydantic import HttpUrl, SecretStr, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy import URL


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: SecretStr
    SQLALCHEMY_ECHO: bool = False

    AUTH_URL: HttpUrl
    AUTH_CLIENT_ID: str
    AUTH_CLIENT_SECRET: SecretStr
    AUTH_REALM: str

    @computed_field
    @property
    def DATABASE_URL(self) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    @computed_field
    @property
    def auth_token_url(self) -> str:
        return urljoin(
            urljoin(str(self.AUTH_URL), self.AUTH_REALM),
            "protocol/openid-connect/token",
        )


def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
