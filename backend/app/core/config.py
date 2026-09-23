import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """ALIAS application configuration."""
    APP_NAME: str = "ALIAS"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "AI-assisted Login Anomaly Investigation System"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./alias.db")
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174,https://yukith-hub.vercel.app").split(",")
    
    # Phase 4: Anomaly Engine Settings
    ANOMALY_TEMPORAL_ENABLED: bool = True
    ANOMALY_DEVICE_ENABLED: bool = True
    ANOMALY_LOCATION_ENABLED: bool = True
    ANOMALY_NETWORK_ENABLED: bool = True
    ANOMALY_AUTH_ENABLED: bool = True
    ANOMALY_ACCESS_ENABLED: bool = True
    
    # Thresholds
    IMPOSSIBLE_TRAVEL_SPEED_KMH: float = 1000.0  # e.g., commercial flights top out ~900km/h
    AUTH_FAILURE_WINDOW_MINUTES: int = 15
    AUTH_FAILURE_MULTIPLIER: float = 3.0
    MIN_HISTORY_FOR_DETECTION: int = 5
    
    # Phase 5: Risk Engine Settings
    RISK_ENGINE_VERSION: str = "risk_engine_v1"
    CORRELATION_WINDOW_MINUTES: int = 30
    
    # Risk Base Weights
    WEIGHT_DEVICE: float = 15.0
    WEIGHT_LOCATION: float = 20.0
    WEIGHT_NETWORK: float = 10.0
    WEIGHT_TEMPORAL: float = 5.0
    WEIGHT_AUTH: float = 25.0
    WEIGHT_ACCESS: float = 15.0
    
    # Risk Severity Thresholds
    SEVERITY_MODERATE: float = 25.0
    SEVERITY_HIGH: float = 50.0
    SEVERITY_CRITICAL: float = 75.0

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "none")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def __init__(self):
        # Re-read from env to ensure latest values
        for attr in ['APP_NAME', 'APP_VERSION', 'ENVIRONMENT', 'HOST', 'DATABASE_URL',
                     'JWT_SECRET', 'JWT_ALGORITHM', 'LLM_PROVIDER', 'LLM_MODEL',
                     'LLM_API_KEY', 'LOG_LEVEL']:
            env_val = os.getenv(attr)
            if env_val is not None:
                setattr(self, attr, env_val)
        port = os.getenv('PORT')
        if port:
            self.PORT = int(port)
        expire = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
        if expire:
            self.ACCESS_TOKEN_EXPIRE_MINUTES = int(expire)
        cors = os.getenv('CORS_ORIGINS')
        if cors:
            self.CORS_ORIGINS = [o.strip() for o in cors.split(',')]

@lru_cache()
def get_settings() -> Settings:
    return Settings()
