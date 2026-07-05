from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    base_url: str = "http://localhost:8000"
    model_config = {"env_file": ".env"}


settings = Settings()