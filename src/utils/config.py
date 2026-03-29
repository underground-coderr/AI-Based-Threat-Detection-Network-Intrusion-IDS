from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "AI Threat Detection System"
    app_version: str = "1.0.0"
    debug: bool = True

    # Paths
    data_raw_dir: Path = Path("data/raw")
    data_processed_dir: Path = Path("data/processed")
    models_dir: Path = Path("data/models")
    logs_dir: Path = Path("logs")

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/alerts.db"

    # ML
    random_seed: int = 42
    test_size: float = 0.2
    smote_enabled: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Alert thresholds
    alert_confidence_min: float = 0.75
    high_severity_threshold: float = 0.92

    def create_dirs(self):
        for d in [self.data_raw_dir, self.data_processed_dir,
                  self.models_dir, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.create_dirs()