import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Docling LLM Converter"
    API_V1_STR: str = "/api/v1"
    # Folder to store temp uploads
    UPLOAD_DIR: str = "/tmp/doc_uploads"
    
    # Validation
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".doc"}

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure upload dir exists at startup
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)