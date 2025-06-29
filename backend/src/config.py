"""
Configuration management for the Brand Audit Tool
"""
import os
import secrets
from typing import Optional


class Config:
    """Base configuration class"""
    
    # Security
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hour
    
    # CORS
    ALLOWED_ORIGINS: list = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # File Upload
    UPLOAD_FOLDER: str = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_FILE_SIZE: int = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'pdf'}
    
    # External APIs
    OPENROUTER_API_KEY: Optional[str] = os.environ.get('OPENROUTER_API_KEY')
    NEWS_API_KEY: Optional[str] = os.environ.get('NEWS_API_KEY')
    BRANDFETCH_API_KEY: Optional[str] = os.environ.get('BRANDFETCH_API_KEY')
    OPENCORPORATES_API_KEY: Optional[str] = os.environ.get('OPENCORPORATES_API_KEY')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL: str = os.environ.get('RATE_LIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT: str = os.environ.get('DEFAULT_RATE_LIMIT', '200 per day, 50 per hour')
    
    # Logging
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Application
    APP_NAME: str = 'AI Brand Audit Tool'
    APP_VERSION: str = '1.0.0'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG: bool = True
    TESTING: bool = False
    LOG_LEVEL: str = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG: bool = False
    TESTING: bool = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = 'Lax'
    
    # Database connection pooling for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings"""
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        
        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)


class TestingConfig(Config):
    """Testing configuration"""
    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED: bool = False
    JWT_ACCESS_TOKEN_EXPIRES: int = 300  # 5 minutes for testing


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])

