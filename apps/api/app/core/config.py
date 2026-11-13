from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./careerpilot.db"
    jwt_secret_key: str = "development-only-change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./storage/uploads"
    max_upload_mb: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
if settings.app_env == "production" and len(settings.jwt_secret_key) < 32:
    raise RuntimeError("JWT_SECRET_KEY must be at least 32 characters in production.")
