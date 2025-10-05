from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_API_KEY: Optional[str] = None
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    
    DEFAULT_LLM_PROVIDER: str = "ollama"
    FALLBACK_LLM_PROVIDER: str = "gemini"
    
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    USE_LANGFUSE: bool = True
    
    APP_NAME: str = "EvidenceFirstResumeTailor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    MAX_FILE_SIZE_MB: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()