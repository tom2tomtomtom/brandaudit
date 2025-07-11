"""
Enhanced Configuration Management for the Brand Audit Tool
Provides secure, validated, and production-ready configuration management
"""

import os
import secrets
import logging
from typing import Optional, Type, Dict, Any
from .env_validator import validate_environment, ValidationError


class Config:
    """Enhanced base configuration class with validation"""

    def __init__(self):
        """Initialize configuration with environment validation"""
        self.logger = logging.getLogger(__name__)
        self._validated_config = {}
        self._load_and_validate_config()

    def _load_and_validate_config(self):
        """Load and validate environment configuration"""
        try:
            self._validated_config = validate_environment()
            self.logger.info("Environment configuration validated successfully")
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            # Fall back to basic configuration for critical settings
            self._load_fallback_config()

    def _load_fallback_config(self):
        """Load fallback configuration when validation fails"""
        self.logger.warning("Using fallback configuration - some features may be limited")
        self._validated_config = {
            "SECRET_KEY": os.environ.get("SECRET_KEY") or secrets.token_hex(32),
            "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY") or secrets.token_hex(32),
            "DATABASE_URL": os.environ.get("DATABASE_URL", "sqlite:///app.db"),
            "FLASK_ENV": os.environ.get("FLASK_ENV", "production"),
            "PORT": int(os.environ.get("PORT", 8080)),
            "DEBUG": False,
            "ALLOWED_ORIGINS": os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback"""
        return self._validated_config.get(key, default)

    # Security
    @property
    def SECRET_KEY(self) -> str:
        return self.get("SECRET_KEY") or secrets.token_hex(32)

    @property
    def JWT_SECRET_KEY(self) -> str:
        return self.get("JWT_SECRET_KEY") or secrets.token_hex(32)

    @property
    def JWT_ACCESS_TOKEN_EXPIRES(self) -> int:
        return self.get("JWT_ACCESS_TOKEN_EXPIRES", 3600)

    # CORS
    @property
    def ALLOWED_ORIGINS(self) -> list:
        origins = self.get("ALLOWED_ORIGINS", "http://localhost:3000")
        if isinstance(origins, str):
            return origins.split(",")
        return origins

    # Database with enhanced connection pooling
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.get("DATABASE_URL", "sqlite:///app.db")

    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self) -> bool:
        return False

    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> Dict[str, Any]:
        return {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_timeout": 20,
            "pool_size": 5,
            "max_overflow": 10,
        }

    # File Upload
    @property
    def UPLOAD_FOLDER(self) -> str:
        return self.get("UPLOAD_FOLDER", "uploads")

    @property
    def MAX_FILE_SIZE(self) -> int:
        return self.get("MAX_FILE_SIZE", 16 * 1024 * 1024)  # 16MB

    @property
    def ALLOWED_EXTENSIONS(self) -> set:
        return {"png", "jpg", "jpeg", "gif", "svg", "webp", "pdf"}

    # External APIs
    @property
    def OPENROUTER_API_KEY(self) -> Optional[str]:
        return self.get("OPENROUTER_API_KEY")

    @property
    def NEWS_API_KEY(self) -> Optional[str]:
        return self.get("NEWS_API_KEY")

    @property
    def BRANDFETCH_API_KEY(self) -> Optional[str]:
        return self.get("BRANDFETCH_API_KEY")

    @property
    def OPENCORPORATES_API_KEY(self) -> Optional[str]:
        return self.get("OPENCORPORATES_API_KEY")

    # Rate Limiting
    @property
    def RATELIMIT_STORAGE_URL(self) -> str:
        return self.get("RATE_LIMIT_STORAGE_URL", "memory://")

    @property
    def RATELIMIT_DEFAULT(self) -> str:
        return self.get("DEFAULT_RATE_LIMIT", "200 per day, 50 per hour")

    # Logging
    @property
    def LOG_LEVEL(self) -> str:
        return self.get("LOG_LEVEL", "INFO")

    @property
    def LOG_FORMAT(self) -> str:
        return "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Application
    @property
    def APP_NAME(self) -> str:
        return "AI Brand Audit Tool"

    @property
    def APP_VERSION(self) -> str:
        return "1.0.0"

    # Background Tasks
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    def init_app(self, app):
        """Initialize application with validated configuration"""
        # Set Flask configuration from validated environment
        for key, value in self._validated_config.items():
            if hasattr(self, key.upper()):
                setattr(app.config, key.upper(), value)

        # Log configuration status
        self.logger.info(f"Application initialized with {len(self._validated_config)} validated config values")

    def get_api_key_status(self) -> Dict[str, bool]:
        """Get status of API key configuration"""
        return {
            "openrouter": bool(self.OPENROUTER_API_KEY),
            "news_api": bool(self.NEWS_API_KEY),
            "brandfetch": bool(self.BRANDFETCH_API_KEY),
            "opencorporates": bool(self.OPENCORPORATES_API_KEY),
        }

    def is_production_ready(self) -> bool:
        """Check if configuration is ready for production"""
        required_keys = [
            self.SECRET_KEY,
            self.JWT_SECRET_KEY,
            self.OPENROUTER_API_KEY,
            self.NEWS_API_KEY,
            self.BRANDFETCH_API_KEY,
        ]
        return all(key for key in required_keys)


class DevelopmentConfig(Config):
    """Development configuration with enhanced debugging"""

    def __init__(self):
        super().__init__()
        self._development_overrides()

    def _development_overrides(self):
        """Apply development-specific overrides"""
        self._validated_config.update({
            "DEBUG": True,
            "TESTING": False,
            "LOG_LEVEL": "DEBUG",
            "FLASK_ENV": "development"
        })

    @property
    def DEBUG(self) -> bool:
        return True

    @property
    def TESTING(self) -> bool:
        return False


class ProductionConfig(Config):
    """Production configuration with enhanced security and performance"""

    def __init__(self):
        super().__init__()
        self._production_overrides()

    def _production_overrides(self):
        """Apply production-specific overrides"""
        self._validated_config.update({
            "DEBUG": False,
            "TESTING": False,
            "LOG_LEVEL": self.get("LOG_LEVEL", "INFO"),
            "FLASK_ENV": "production"
        })

    @property
    def DEBUG(self) -> bool:
        return False

    @property
    def TESTING(self) -> bool:
        return False

    # Enhanced security for production
    @property
    def SESSION_COOKIE_SECURE(self) -> bool:
        return True

    @property
    def SESSION_COOKIE_HTTPONLY(self) -> bool:
        return True

    @property
    def SESSION_COOKIE_SAMESITE(self) -> str:
        return "Lax"

    # Enhanced database connection pooling for production
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> Dict[str, Any]:
        return {
            "pool_size": 10,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
            "max_overflow": 20,
            "pool_timeout": 30,
            "echo": False,  # Disable SQL logging in production
        }

    def init_app(self, app):
        """Initialize production-specific settings"""
        super().init_app(app)

        # Enhanced logging for production
        import logging
        from logging import StreamHandler
        from logging.handlers import RotatingFileHandler

        # Console handler
        console_handler = StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter(self.LOG_FORMAT)
        )

        # File handler with rotation
        if not os.path.exists('logs'):
            os.makedirs('logs')

        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=10240000, backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter(self.LOG_FORMAT)
        )

        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

        # Validate production readiness
        if not self.is_production_ready():
            app.logger.warning("Application may not be production-ready - check API key configuration")


class TestingConfig(Config):
    """Testing configuration with isolated environment"""

    def __init__(self):
        super().__init__()
        self._testing_overrides()

    def _testing_overrides(self):
        """Apply testing-specific overrides"""
        self._validated_config.update({
            "TESTING": True,
            "DEBUG": True,
            "DATABASE_URL": "sqlite:///:memory:",
            "JWT_ACCESS_TOKEN_EXPIRES": 300,  # 5 minutes for testing
            "FLASK_ENV": "testing"
        })

    @property
    def TESTING(self) -> bool:
        return True

    @property
    def DEBUG(self) -> bool:
        return True

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return "sqlite:///:memory:"

    @property
    def WTF_CSRF_ENABLED(self) -> bool:
        return False


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name: Optional[str] = None) -> Type[Config]:
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    return config.get(config_name, config["default"])
