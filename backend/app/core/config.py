import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"

class Settings(BaseModel):
    APP_NAME: str = "Advanced OCR with Layout Understanding"
    APP_SHORT_NAME: str = "AORL"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    
    # Storage paths
    STORAGE_PATH: Path = STORAGE_DIR
    UPLOAD_PATH: Path = STORAGE_DIR / "uploads"
    PROCESSED_PATH: Path = STORAGE_DIR / "processed"
    THUMBNAIL_PATH: Path = STORAGE_DIR / "thumbnails"
    EXPORT_PATH: Path = STORAGE_DIR / "exports"
    
    # Upload limits
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
    ALLOWED_MIME_TYPES: set[str] = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "application/pdf",
    }
    
    # OCR settings
    OCR_ENGINE: str = os.getenv("OCR_ENGINE", "paddleocr")
    OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "en")
    OCR_USE_GPU: bool = os.getenv("OCR_USE_GPU", "false").lower() == "true"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    LLM_API_KEY: str | None = os.getenv("LLM_API_KEY", None)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_BASE_URL: str | None = os.getenv("LLM_BASE_URL", None)
    
    # CORS
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"
        ).split(",")
    ]

settings = Settings()

# Ensure directories exist
for path in [
    settings.STORAGE_PATH,
    settings.UPLOAD_PATH,
    settings.PROCESSED_PATH,
    settings.THUMBNAIL_PATH,
    settings.EXPORT_PATH,
]:
    path.mkdir(parents=True, exist_ok=True)
