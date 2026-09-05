"""
Configuration management for WattWise EMS service.
Reads environment-specific config and secrets from system environment variables.
"""

import os
from typing import List


class EMSConfig:
    """EMS Service Configuration & Environment Variable Handler."""

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security Secrets & Keys
    EMS_API_KEY: str = os.getenv("EMS_API_KEY", "")  # Optional API secret for authenticating WattWise Backend
    
    # Safety Limits & System Parameters
    MAX_SYSTEM_LOAD_KW: float = float(os.getenv("MAX_SYSTEM_LOAD_KW", "10.0"))
    
    # CORS Origins (Comma-separated list of allowed origins)
    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def cors_origins(self) -> List[str]:
        if not self.CORS_ORIGINS_RAW or self.CORS_ORIGINS_RAW.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]


config = EMSConfig()
