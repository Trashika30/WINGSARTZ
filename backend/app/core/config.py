import os
from dotenv import load_dotenv
from typing import List

# Load env file if it exists
load_dotenv()

class Settings:
    PROJECT_NAME: str = "WingsArtz API"
    API_V1_STR: str = "/api/v1"
    
    # JWT security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    
    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./wingsartz.db"
    )
    
    # Vector DB settings
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", 8001))
    
    # AI API keys — Gemini (primary) → Groq (fallback 1) → OpenAI (fallback 2)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "mock-key-for-development")
    
    # CORS Allowed Origins
    # null is required for local file:// HTML access
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:8000,null"
        ).split(",")
        if origin.strip()
    ]

settings = Settings()

