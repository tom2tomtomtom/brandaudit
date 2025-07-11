"""
Environment Variable Validation and Management System
Provides comprehensive validation, type checking, and secure handling of environment variables
"""

import os
import re
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Validation levels for environment variables"""
    REQUIRED = "required"
    OPTIONAL = "optional"
    DEPRECATED = "deprecated"


class ValidationError(Exception):
    """Custom exception for environment variable validation errors"""
    pass


@dataclass
class EnvVarConfig:
    """Configuration for environment variable validation"""
    name: str
    validation_level: ValidationLevel
    var_type: type = str
    default: Any = None
    validator: Optional[Callable[[Any], bool]] = None
    description: str = ""
    sensitive: bool = False
    pattern: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    choices: Optional[List[str]] = None


class EnvironmentValidator:
    """Comprehensive environment variable validator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_errors: List[str] = []
        self.warnings: List[str] = []
        
        # Define environment variable configurations
        self.env_configs = [
            # Security
            EnvVarConfig(
                name="SECRET_KEY",
                validation_level=ValidationLevel.REQUIRED,
                description="Flask secret key for session management",
                sensitive=True,
                min_length=32
            ),
            EnvVarConfig(
                name="JWT_SECRET_KEY",
                validation_level=ValidationLevel.REQUIRED,
                description="JWT token signing key",
                sensitive=True,
                min_length=32
            ),
            
            # Database
            EnvVarConfig(
                name="DATABASE_URL",
                validation_level=ValidationLevel.OPTIONAL,
                description="Database connection URL",
                default="sqlite:///app.db",
                pattern=r"^(sqlite|postgresql|mysql)://.*"
            ),
            
            # API Keys
            EnvVarConfig(
                name="OPENROUTER_API_KEY",
                validation_level=ValidationLevel.REQUIRED,
                description="OpenRouter API key for AI analysis",
                sensitive=True,
                pattern=r"^sk-or-.*"
            ),
            EnvVarConfig(
                name="NEWS_API_KEY",
                validation_level=ValidationLevel.REQUIRED,
                description="News API key for news data",
                sensitive=True,
                min_length=32
            ),
            EnvVarConfig(
                name="BRANDFETCH_API_KEY",
                validation_level=ValidationLevel.REQUIRED,
                description="BrandFetch API key for brand assets",
                sensitive=True
            ),
            EnvVarConfig(
                name="OPENCORPORATES_API_KEY",
                validation_level=ValidationLevel.OPTIONAL,
                description="OpenCorporates API key for company data",
                sensitive=True
            ),
            
            # Application Settings
            EnvVarConfig(
                name="FLASK_ENV",
                validation_level=ValidationLevel.OPTIONAL,
                description="Flask environment mode",
                default="production",
                choices=["development", "production", "testing"]
            ),
            EnvVarConfig(
                name="PORT",
                validation_level=ValidationLevel.OPTIONAL,
                var_type=int,
                description="Application port",
                default=8080,
                validator=lambda x: 1024 <= x <= 65535
            ),
            EnvVarConfig(
                name="DEBUG",
                validation_level=ValidationLevel.OPTIONAL,
                var_type=bool,
                description="Enable debug mode",
                default=False
            ),
            
            # CORS
            EnvVarConfig(
                name="ALLOWED_ORIGINS",
                validation_level=ValidationLevel.OPTIONAL,
                description="Comma-separated list of allowed CORS origins",
                default="http://localhost:3000,http://localhost:5173"
            ),
            
            # File Upload
            EnvVarConfig(
                name="UPLOAD_FOLDER",
                validation_level=ValidationLevel.OPTIONAL,
                description="Directory for file uploads",
                default="uploads"
            ),
            EnvVarConfig(
                name="MAX_FILE_SIZE",
                validation_level=ValidationLevel.OPTIONAL,
                var_type=int,
                description="Maximum file upload size in bytes",
                default=16777216,  # 16MB
                validator=lambda x: x > 0
            ),
            
            # Rate Limiting
            EnvVarConfig(
                name="RATE_LIMIT_STORAGE_URL",
                validation_level=ValidationLevel.OPTIONAL,
                description="Rate limiting storage backend URL",
                default="memory://"
            ),
            EnvVarConfig(
                name="DEFAULT_RATE_LIMIT",
                validation_level=ValidationLevel.OPTIONAL,
                description="Default rate limit configuration",
                default="200 per day, 50 per hour"
            ),
            
            # Logging
            EnvVarConfig(
                name="LOG_LEVEL",
                validation_level=ValidationLevel.OPTIONAL,
                description="Logging level",
                default="INFO",
                choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            ),
            
            # Redis/Celery (optional)
            EnvVarConfig(
                name="CELERY_BROKER_URL",
                validation_level=ValidationLevel.OPTIONAL,
                description="Celery broker URL",
                default="redis://localhost:6379/0"
            ),
            EnvVarConfig(
                name="CELERY_RESULT_BACKEND",
                validation_level=ValidationLevel.OPTIONAL,
                description="Celery result backend URL",
                default="redis://localhost:6379/0"
            ),
        ]
    
    def _convert_type(self, value: str, target_type: type) -> Any:
        """Convert string value to target type"""
        if target_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        else:
            return value
    
    def _validate_pattern(self, value: str, pattern: str) -> bool:
        """Validate value against regex pattern"""
        return bool(re.match(pattern, value))
    
    def _validate_length(self, value: str, min_length: Optional[int], max_length: Optional[int]) -> bool:
        """Validate string length"""
        if min_length and len(value) < min_length:
            return False
        if max_length and len(value) > max_length:
            return False
        return True
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate all environment variables and return validated configuration"""
        validated_config = {}
        self.validation_errors.clear()
        self.warnings.clear()
        
        for config in self.env_configs:
            try:
                value = self._validate_single_var(config)
                if value is not None:
                    validated_config[config.name] = value
            except ValidationError as e:
                self.validation_errors.append(str(e))
        
        # Log results
        if self.validation_errors:
            for error in self.validation_errors:
                self.logger.error(f"Environment validation error: {error}")
        
        if self.warnings:
            for warning in self.warnings:
                self.logger.warning(f"Environment validation warning: {warning}")
        
        return validated_config
    
    def _validate_single_var(self, config: EnvVarConfig) -> Any:
        """Validate a single environment variable"""
        raw_value = os.environ.get(config.name)
        
        # Handle missing values
        if raw_value is None:
            if config.validation_level == ValidationLevel.REQUIRED:
                raise ValidationError(f"Required environment variable '{config.name}' is not set")
            elif config.default is not None:
                return config.default
            else:
                return None
        
        # Type conversion
        try:
            value = self._convert_type(raw_value, config.var_type)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid type for '{config.name}': {e}")
        
        # Pattern validation
        if config.pattern and isinstance(value, str):
            if not self._validate_pattern(value, config.pattern):
                raise ValidationError(f"'{config.name}' does not match required pattern")
        
        # Length validation
        if isinstance(value, str):
            if not self._validate_length(value, config.min_length, config.max_length):
                raise ValidationError(f"'{config.name}' length validation failed")
        
        # Choices validation
        if config.choices and value not in config.choices:
            raise ValidationError(f"'{config.name}' must be one of: {config.choices}")
        
        # Custom validator
        if config.validator and not config.validator(value):
            raise ValidationError(f"'{config.name}' failed custom validation")
        
        return value
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report"""
        return {
            "errors": self.validation_errors,
            "warnings": self.warnings,
            "is_valid": len(self.validation_errors) == 0,
            "configured_vars": [
                {
                    "name": config.name,
                    "required": config.validation_level == ValidationLevel.REQUIRED,
                    "configured": os.environ.get(config.name) is not None,
                    "description": config.description,
                    "sensitive": config.sensitive
                }
                for config in self.env_configs
            ]
        }
    
    def generate_env_template(self) -> str:
        """Generate .env template file content"""
        template_lines = [
            "# Environment Configuration for AI Brand Audit Tool",
            "# Copy this file to .env and fill in your values",
            ""
        ]
        
        categories = {
            "Security": ["SECRET_KEY", "JWT_SECRET_KEY"],
            "Database": ["DATABASE_URL"],
            "API Keys": ["OPENROUTER_API_KEY", "NEWS_API_KEY", "BRANDFETCH_API_KEY", "OPENCORPORATES_API_KEY"],
            "Application": ["FLASK_ENV", "PORT", "DEBUG"],
            "CORS": ["ALLOWED_ORIGINS"],
            "File Upload": ["UPLOAD_FOLDER", "MAX_FILE_SIZE"],
            "Rate Limiting": ["RATE_LIMIT_STORAGE_URL", "DEFAULT_RATE_LIMIT"],
            "Logging": ["LOG_LEVEL"],
            "Background Tasks": ["CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"]
        }
        
        for category, var_names in categories.items():
            template_lines.append(f"# {category}")
            for var_name in var_names:
                config = next((c for c in self.env_configs if c.name == var_name), None)
                if config:
                    if config.validation_level == ValidationLevel.REQUIRED:
                        template_lines.append(f"{var_name}=  # REQUIRED: {config.description}")
                    else:
                        default_str = f"={config.default}" if config.default is not None else "="
                        template_lines.append(f"{var_name}{default_str}  # OPTIONAL: {config.description}")
            template_lines.append("")
        
        return "\n".join(template_lines)


# Global validator instance
env_validator = EnvironmentValidator()


def validate_environment() -> Dict[str, Any]:
    """Validate environment variables and return configuration"""
    return env_validator.validate_environment()


def get_validation_report() -> Dict[str, Any]:
    """Get environment validation report"""
    return env_validator.get_validation_report()


def generate_env_template() -> str:
    """Generate environment template"""
    return env_validator.generate_env_template()
