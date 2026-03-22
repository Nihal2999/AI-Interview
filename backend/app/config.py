from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GROQ_API_KEY: str
    GROQ_MODEL: str

    # Ollama (local fallback - host.docker.internal reaches your host machine from Docker)
    OLLAMA_BASE_URL: str
    OLLAMA_MODEL: str

    class Config:
        env_file = ".env"

settings = Settings()
