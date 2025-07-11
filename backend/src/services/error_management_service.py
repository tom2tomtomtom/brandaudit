"""
Centralized Error Management Service

This service provides comprehensive error handling, categorization, and user-friendly
error messages for the brand audit application. It integrates with the existing
API validation service to provide enhanced error management capabilities.
"""

import logging
import traceback
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
import json
import time
from collections import defaultdict, deque

from src.utils.logging_config import get_logger


class ErrorCategory(Enum):
    """Error categories for classification"""
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    DATA_ERROR = "data_error"
    SYSTEM_ERROR = "system_error"
    USER_ERROR = "user_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    DEGRADE = "degrade"
    FAIL = "fail"
    USER_ACTION = "user_action"


@dataclass
class ErrorContext:
    """Context information for errors"""
    user_id: Optional[str] = None
    analysis_id: Optional[str] = None
    api_name: Optional[str] = None
    operation: Optional[str] = None
    request_data: Optional[Dict] = None
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorInfo:
    """Comprehensive error information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    original_error: Exception
    user_message: str
    technical_message: str
    recovery_strategy: RecoveryStrategy
    context: ErrorContext
    retry_count: int = 0
    max_retries: int = 3
    can_retry: bool = True
    fallback_available: bool = False
    user_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FallbackStrategy:
    """Fallback strategy configuration"""
    name: str
    description: str
    handler: Callable
    priority: int
    conditions: List[str] = field(default_factory=list)
    enabled: bool = True


class ErrorManagementService:
    """Centralized error management service"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_history: deque = deque(maxlen=1000)  # Keep last 1000 errors
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.fallback_strategies: Dict[str, List[FallbackStrategy]] = {}
        self.user_friendly_messages: Dict[str, Dict[str, str]] = {}
        self.recovery_handlers: Dict[RecoveryStrategy, Callable] = {}
        
        self._initialize_error_mappings()
        self._initialize_fallback_strategies()
        self._initialize_recovery_handlers()
    
    def _initialize_error_mappings(self):
        """Initialize user-friendly error messages"""
        self.user_friendly_messages = {
            "api_error": {
                "brandfetch": "We're having trouble accessing brand information right now. Please try again in a few minutes.",
                "newsapi": "News data is temporarily unavailable. We'll continue with other analysis components.",
                "openrouter": "AI analysis is temporarily unavailable. Please try again shortly.",
                "opencorporates": "Company information lookup is experiencing issues. We'll use alternative sources."
            },
            "network_error": {
                "default": "Network connection issues detected. Please check your internet connection and try again.",
                "timeout": "The request is taking longer than expected. Please try again.",
                "dns": "Unable to reach our services. Please check your network connection."
            },
            "rate_limit_error": {
                "default": "We're processing many requests right now. Please wait a moment and try again.",
                "daily_limit": "Daily usage limit reached. Please try again tomorrow or upgrade your plan.",
                "hourly_limit": "Hourly usage limit reached. Please wait before trying again."
            },
            "authentication_error": {
                "default": "Authentication failed. Please check your credentials and try again.",
                "expired": "Your session has expired. Please log in again.",
                "invalid_key": "API configuration issue detected. Please contact support."
            },
            "validation_error": {
                "default": "Please check your input and try again.",
                "missing_field": "Required information is missing. Please complete all fields.",
                "invalid_format": "The information provided is not in the correct format."
            },
            "system_error": {
                "default": "We're experiencing technical difficulties. Our team has been notified.",
                "database": "Data storage is temporarily unavailable. Please try again shortly.",
                "memory": "System resources are currently limited. Please try again in a few minutes."
            }
        }
    
    def _initialize_fallback_strategies(self):
        """Initialize fallback strategies for different services"""
        self.fallback_strategies = {
            "brand_data": [
                FallbackStrategy(
                    name="wikipedia_fallback",
                    description="Use Wikipedia for basic brand information",
                    handler=self._wikipedia_fallback,
                    priority=1
                ),
                FallbackStrategy(
                    name="web_scraping_fallback",
                    description="Extract basic info from company website",
                    handler=self._web_scraping_fallback,
                    priority=2
                )
            ],
            "news_data": [
                FallbackStrategy(
                    name="rss_feeds_fallback",
                    description="Use RSS feeds for news data",
                    handler=self._rss_feeds_fallback,
                    priority=1
                ),
                FallbackStrategy(
                    name="social_media_fallback",
                    description="Extract news from social media",
                    handler=self._social_media_fallback,
                    priority=2
                )
            ],
            "ai_analysis": [
                FallbackStrategy(
                    name="cached_analysis_fallback",
                    description="Use cached analysis results",
                    handler=self._cached_analysis_fallback,
                    priority=1
                ),
                FallbackStrategy(
                    name="template_analysis_fallback",
                    description="Use template-based analysis",
                    handler=self._template_analysis_fallback,
                    priority=2
                )
            ]
        }
    
    def _initialize_recovery_handlers(self):
        """Initialize recovery strategy handlers"""
        self.recovery_handlers = {
            RecoveryStrategy.RETRY: self._handle_retry_recovery,
            RecoveryStrategy.FALLBACK: self._handle_fallback_recovery,
            RecoveryStrategy.DEGRADE: self._handle_degrade_recovery,
            RecoveryStrategy.FAIL: self._handle_fail_recovery,
            RecoveryStrategy.USER_ACTION: self._handle_user_action_recovery
        }
    
    def handle_error(self, 
                    error: Exception, 
                    context: ErrorContext,
                    operation_name: str = "unknown") -> ErrorInfo:
        """
        Main error handling method that categorizes errors and determines recovery strategy
        """
        error_id = str(uuid.uuid4())
        correlation_id = context.correlation_id or error_id
        
        # Categorize the error
        category = self._categorize_error(error, context)
        severity = self._determine_severity(error, category, context)
        
        # Generate user-friendly message
        user_message = self._generate_user_message(error, category, context)
        technical_message = self._generate_technical_message(error, context)
        
        # Determine recovery strategy
        recovery_strategy = self._determine_recovery_strategy(error, category, context)
        
        # Check for fallback availability
        fallback_available = self._check_fallback_availability(category, context)
        
        # Generate user actions
        user_actions = self._generate_user_actions(error, category, recovery_strategy)
        
        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            category=category,
            severity=severity,
            original_error=error,
            user_message=user_message,
            technical_message=technical_message,
            recovery_strategy=recovery_strategy,
            context=context,
            fallback_available=fallback_available,
            user_actions=user_actions
        )
        
        # Log the error
        self._log_error(error_info, operation_name)
        
        # Store in history for pattern analysis
        self.error_history.append(error_info)
        self._update_error_patterns(error_info)
        
        return error_info

    def _categorize_error(self, error: Exception, context: ErrorContext) -> ErrorCategory:
        """Categorize error based on type and context"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()

        # API-specific errors
        if context.api_name:
            if "401" in error_str or "403" in error_str or "unauthorized" in error_str:
                return ErrorCategory.AUTHENTICATION_ERROR
            elif "429" in error_str or "rate limit" in error_str:
                return ErrorCategory.RATE_LIMIT_ERROR
            elif "timeout" in error_str or "timed out" in error_str:
                return ErrorCategory.TIMEOUT_ERROR
            else:
                return ErrorCategory.API_ERROR

        # Network errors
        if any(term in error_str for term in ["connection", "network", "dns", "resolve"]):
            return ErrorCategory.NETWORK_ERROR

        # Validation errors
        if any(term in error_type for term in ["validation", "schema", "marshmallow"]):
            return ErrorCategory.VALIDATION_ERROR

        # System errors
        if any(term in error_str for term in ["memory", "disk", "database", "internal"]):
            return ErrorCategory.SYSTEM_ERROR

        # Default to external service error if we can't categorize
        return ErrorCategory.EXTERNAL_SERVICE_ERROR

    def _determine_severity(self, error: Exception, category: ErrorCategory, context: ErrorContext) -> ErrorSeverity:
        """Determine error severity based on category and context"""
        # Critical errors that affect core functionality
        if category in [ErrorCategory.SYSTEM_ERROR, ErrorCategory.AUTHENTICATION_ERROR]:
            return ErrorSeverity.CRITICAL

        # High severity for API errors that block analysis
        if category == ErrorCategory.API_ERROR and context.api_name in ["openrouter", "brandfetch"]:
            return ErrorSeverity.HIGH

        # Medium severity for rate limits and timeouts
        if category in [ErrorCategory.RATE_LIMIT_ERROR, ErrorCategory.TIMEOUT_ERROR]:
            return ErrorSeverity.MEDIUM

        # Low severity for validation and user errors
        if category in [ErrorCategory.VALIDATION_ERROR, ErrorCategory.USER_ERROR]:
            return ErrorSeverity.LOW

        return ErrorSeverity.MEDIUM

    def _generate_user_message(self, error: Exception, category: ErrorCategory, context: ErrorContext) -> str:
        """Generate user-friendly error message"""
        category_key = category.value

        # Try to get specific message for API
        if context.api_name and category_key in self.user_friendly_messages:
            api_messages = self.user_friendly_messages[category_key]
            if context.api_name in api_messages:
                return api_messages[context.api_name]

        # Try to get category-specific message
        if category_key in self.user_friendly_messages:
            messages = self.user_friendly_messages[category_key]
            if "default" in messages:
                return messages["default"]

        # Fallback message
        return "We encountered an issue while processing your request. Please try again or contact support if the problem persists."

    def _generate_technical_message(self, error: Exception, context: ErrorContext) -> str:
        """Generate technical error message for logging"""
        return f"{type(error).__name__}: {str(error)}"

    def _determine_recovery_strategy(self, error: Exception, category: ErrorCategory, context: ErrorContext) -> RecoveryStrategy:
        """Determine the best recovery strategy for the error"""
        error_str = str(error).lower()

        # Rate limit errors should wait, not retry immediately
        if category == ErrorCategory.RATE_LIMIT_ERROR:
            return RecoveryStrategy.USER_ACTION

        # Authentication errors need user action
        if category == ErrorCategory.AUTHENTICATION_ERROR:
            return RecoveryStrategy.USER_ACTION

        # Validation errors need user correction
        if category == ErrorCategory.VALIDATION_ERROR:
            return RecoveryStrategy.USER_ACTION

        # Network and timeout errors can be retried
        if category in [ErrorCategory.NETWORK_ERROR, ErrorCategory.TIMEOUT_ERROR]:
            return RecoveryStrategy.RETRY

        # API errors might have fallbacks
        if category == ErrorCategory.API_ERROR and self._check_fallback_availability(category, context):
            return RecoveryStrategy.FALLBACK

        # System errors should degrade gracefully
        if category == ErrorCategory.SYSTEM_ERROR:
            return RecoveryStrategy.DEGRADE

        return RecoveryStrategy.RETRY

    def _check_fallback_availability(self, category: ErrorCategory, context: ErrorContext) -> bool:
        """Check if fallback strategies are available"""
        if not context.api_name:
            return False

        # Map API names to fallback strategy keys
        api_fallback_map = {
            "brandfetch": "brand_data",
            "newsapi": "news_data",
            "openrouter": "ai_analysis"
        }

        fallback_key = api_fallback_map.get(context.api_name)
        if fallback_key and fallback_key in self.fallback_strategies:
            return any(strategy.enabled for strategy in self.fallback_strategies[fallback_key])

        return False

    def _generate_user_actions(self, error: Exception, category: ErrorCategory, recovery_strategy: RecoveryStrategy) -> List[str]:
        """Generate actionable steps for users"""
        actions = []

        if recovery_strategy == RecoveryStrategy.RETRY:
            actions.append("Try again in a few moments")
            if category == ErrorCategory.NETWORK_ERROR:
                actions.append("Check your internet connection")

        elif recovery_strategy == RecoveryStrategy.USER_ACTION:
            if category == ErrorCategory.RATE_LIMIT_ERROR:
                actions.append("Wait a few minutes before trying again")
            elif category == ErrorCategory.AUTHENTICATION_ERROR:
                actions.append("Check your login credentials")
                actions.append("Try logging out and back in")
            elif category == ErrorCategory.VALIDATION_ERROR:
                actions.append("Review and correct your input")

        elif recovery_strategy == RecoveryStrategy.FALLBACK:
            actions.append("We'll use alternative data sources")
            actions.append("Results may be limited but still useful")

        elif recovery_strategy == RecoveryStrategy.DEGRADE:
            actions.append("Some features may be temporarily unavailable")
            actions.append("Core functionality will continue to work")

        if not actions:
            actions.append("Contact support if the issue persists")

        return actions

    def _log_error(self, error_info: ErrorInfo, operation_name: str):
        """Log error with structured information"""
        log_data = {
            "error_id": error_info.error_id,
            "category": error_info.category.value,
            "severity": error_info.severity.value,
            "operation": operation_name,
            "user_id": error_info.context.user_id,
            "analysis_id": error_info.context.analysis_id,
            "api_name": error_info.context.api_name,
            "correlation_id": error_info.context.correlation_id,
            "recovery_strategy": error_info.recovery_strategy.value,
            "technical_message": error_info.technical_message,
            "timestamp": error_info.timestamp.isoformat()
        }

        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error in {operation_name}", extra=log_data)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error in {operation_name}", extra=log_data)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error in {operation_name}", extra=log_data)
        else:
            self.logger.info(f"Low severity error in {operation_name}", extra=log_data)

    def _update_error_patterns(self, error_info: ErrorInfo):
        """Update error pattern tracking for analysis"""
        pattern_key = f"{error_info.category.value}:{error_info.context.api_name or 'unknown'}"
        self.error_patterns[pattern_key] += 1

    # Recovery Strategy Handlers
    def _handle_retry_recovery(self, error_info: ErrorInfo, operation_func: Callable, *args, **kwargs):
        """Handle retry recovery strategy"""
        if error_info.retry_count >= error_info.max_retries:
            raise Exception(f"Max retries ({error_info.max_retries}) exceeded for operation")

        # Calculate exponential backoff with jitter
        base_delay = 1.0 * (2 ** error_info.retry_count)
        jitter = base_delay * 0.1 * (0.5 - time.time() % 1)
        delay = min(base_delay + jitter, 30.0)  # Max 30 seconds

        self.logger.info(f"Retrying operation after {delay:.1f}s (attempt {error_info.retry_count + 1})")
        time.sleep(delay)

        error_info.retry_count += 1
        return operation_func(*args, **kwargs)

    def _handle_fallback_recovery(self, error_info: ErrorInfo, fallback_key: str, *args, **kwargs):
        """Handle fallback recovery strategy"""
        if fallback_key not in self.fallback_strategies:
            raise Exception(f"No fallback strategies available for {fallback_key}")

        strategies = sorted(self.fallback_strategies[fallback_key], key=lambda x: x.priority)

        for strategy in strategies:
            if not strategy.enabled:
                continue

            try:
                self.logger.info(f"Attempting fallback strategy: {strategy.name}")
                result = strategy.handler(*args, **kwargs)
                self.logger.info(f"Fallback strategy {strategy.name} succeeded")
                return result
            except Exception as e:
                self.logger.warning(f"Fallback strategy {strategy.name} failed: {str(e)}")
                continue

        raise Exception("All fallback strategies failed")

    def _handle_degrade_recovery(self, error_info: ErrorInfo, *args, **kwargs):
        """Handle graceful degradation recovery strategy"""
        self.logger.info("Applying graceful degradation")
        return {
            "success": True,
            "degraded": True,
            "message": "Service is running with limited functionality",
            "available_features": self._get_available_features(error_info),
            "error_info": {
                "category": error_info.category.value,
                "user_message": error_info.user_message
            }
        }

    def _handle_fail_recovery(self, error_info: ErrorInfo, *args, **kwargs):
        """Handle fail recovery strategy"""
        self.logger.error(f"Operation failed with no recovery options: {error_info.technical_message}")
        raise error_info.original_error

    def _handle_user_action_recovery(self, error_info: ErrorInfo, *args, **kwargs):
        """Handle user action required recovery strategy"""
        return {
            "success": False,
            "requires_user_action": True,
            "user_message": error_info.user_message,
            "user_actions": error_info.user_actions,
            "error_category": error_info.category.value,
            "can_retry_after_action": error_info.can_retry
        }

    def _get_available_features(self, error_info: ErrorInfo) -> List[str]:
        """Get list of features still available during degraded operation"""
        all_features = ["brand_analysis", "competitive_analysis", "visual_analysis", "news_analysis"]

        # Remove features that depend on the failed service
        if error_info.context.api_name == "brandfetch":
            return [f for f in all_features if f != "visual_analysis"]
        elif error_info.context.api_name == "newsapi":
            return [f for f in all_features if f != "news_analysis"]
        elif error_info.context.api_name == "openrouter":
            return [f for f in all_features if f != "competitive_analysis"]

        return all_features

    # Fallback Strategy Implementations
    def _wikipedia_fallback(self, company_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Fallback to Wikipedia for basic brand information"""
        try:
            import wikipedia

            # Search for the company
            search_results = wikipedia.search(company_name, results=3)
            if not search_results:
                raise Exception("No Wikipedia results found")

            # Get the page content
            page = wikipedia.page(search_results[0])

            return {
                "success": True,
                "source": "wikipedia",
                "data": {
                    "name": company_name,
                    "description": page.summary[:500],
                    "url": page.url,
                    "categories": page.categories[:10] if hasattr(page, 'categories') else []
                },
                "fallback_used": True
            }
        except Exception as e:
            self.logger.warning(f"Wikipedia fallback failed: {str(e)}")
            raise e

    def _web_scraping_fallback(self, website_url: str, *args, **kwargs) -> Dict[str, Any]:
        """Fallback to basic web scraping for brand information"""
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(website_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic information
            title = soup.find('title')
            description = soup.find('meta', attrs={'name': 'description'})

            return {
                "success": True,
                "source": "web_scraping",
                "data": {
                    "title": title.text.strip() if title else "",
                    "description": description.get('content', '') if description else "",
                    "url": website_url
                },
                "fallback_used": True
            }
        except Exception as e:
            self.logger.warning(f"Web scraping fallback failed: {str(e)}")
            raise e

    def _rss_feeds_fallback(self, company_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Fallback to RSS feeds for news data"""
        try:
            import feedparser

            # Common RSS feed URLs for news
            rss_urls = [
                f"https://news.google.com/rss/search?q={company_name}&hl=en-US&gl=US&ceid=US:en",
                f"https://feeds.reuters.com/reuters/companyNews"
            ]

            articles = []
            for url in rss_urls:
                try:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:5]:  # Limit to 5 articles per feed
                        if company_name.lower() in entry.title.lower() or company_name.lower() in entry.summary.lower():
                            articles.append({
                                "title": entry.title,
                                "description": entry.summary,
                                "url": entry.link,
                                "published": entry.published if hasattr(entry, 'published') else ""
                            })
                except Exception as e:
                    self.logger.warning(f"RSS feed {url} failed: {str(e)}")
                    continue

            return {
                "success": True,
                "source": "rss_feeds",
                "data": {
                    "articles": articles[:10],  # Limit total articles
                    "total_results": len(articles)
                },
                "fallback_used": True
            }
        except Exception as e:
            self.logger.warning(f"RSS feeds fallback failed: {str(e)}")
            raise e

    def _social_media_fallback(self, company_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Fallback to social media for news data (placeholder implementation)"""
        # This would integrate with social media APIs in a real implementation
        self.logger.info(f"Social media fallback not implemented for {company_name}")
        raise Exception("Social media fallback not implemented")

    def _cached_analysis_fallback(self, analysis_data: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """Fallback to cached analysis results"""
        try:
            # This would check a cache/database for previous analysis results
            # For now, return a basic template
            return {
                "success": True,
                "source": "cached_analysis",
                "data": {
                    "analysis_type": "cached",
                    "message": "Using previously cached analysis results",
                    "limited_data": True
                },
                "fallback_used": True
            }
        except Exception as e:
            self.logger.warning(f"Cached analysis fallback failed: {str(e)}")
            raise e

    def _template_analysis_fallback(self, analysis_data: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """Fallback to template-based analysis"""
        try:
            company_name = analysis_data.get("company_name", "Unknown Company")

            return {
                "success": True,
                "source": "template_analysis",
                "data": {
                    "company_name": company_name,
                    "analysis": {
                        "brand_strength": "Analysis temporarily unavailable - please try again later",
                        "market_position": "Detailed analysis requires full API access",
                        "recommendations": [
                            "Monitor brand performance regularly",
                            "Engage with customer feedback",
                            "Maintain consistent brand messaging"
                        ]
                    },
                    "note": "This is a template response due to service limitations"
                },
                "fallback_used": True
            }
        except Exception as e:
            self.logger.warning(f"Template analysis fallback failed: {str(e)}")
            raise e

    # Utility Methods
    def get_error_statistics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_errors = [e for e in self.error_history if e.timestamp > cutoff_time]

        if not recent_errors:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "categories": {},
                "severities": {},
                "top_patterns": []
            }

        # Count by category
        categories = defaultdict(int)
        severities = defaultdict(int)

        for error in recent_errors:
            categories[error.category.value] += 1
            severities[error.severity.value] += 1

        # Get top error patterns
        top_patterns = sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_errors": len(recent_errors),
            "error_rate": len(recent_errors) / time_window_hours,
            "categories": dict(categories),
            "severities": dict(severities),
            "top_patterns": [{"pattern": pattern, "count": count} for pattern, count in top_patterns],
            "time_window_hours": time_window_hours
        }

    def get_system_health_impact(self) -> Dict[str, Any]:
        """Assess system health impact based on recent errors"""
        recent_errors = list(self.error_history)[-100:]  # Last 100 errors

        if not recent_errors:
            return {"status": "healthy", "impact": "none"}

        # Count critical and high severity errors
        critical_count = sum(1 for e in recent_errors if e.severity == ErrorSeverity.CRITICAL)
        high_count = sum(1 for e in recent_errors if e.severity == ErrorSeverity.HIGH)

        # Determine overall impact
        if critical_count > 5:
            status = "critical"
            impact = "severe"
        elif critical_count > 0 or high_count > 10:
            status = "degraded"
            impact = "moderate"
        elif high_count > 0:
            status = "warning"
            impact = "minor"
        else:
            status = "healthy"
            impact = "none"

        return {
            "status": status,
            "impact": impact,
            "critical_errors": critical_count,
            "high_severity_errors": high_count,
            "total_recent_errors": len(recent_errors)
        }

    def should_circuit_break(self, api_name: str, time_window_minutes: int = 10) -> bool:
        """Determine if circuit breaker should be triggered for an API"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        api_errors = [
            e for e in self.error_history
            if e.context.api_name == api_name
            and e.timestamp > cutoff_time
            and e.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
        ]

        # Circuit break if more than 5 high/critical errors in the time window
        return len(api_errors) > 5

    def get_recovery_suggestions(self, error_info: ErrorInfo) -> Dict[str, Any]:
        """Get detailed recovery suggestions for an error"""
        suggestions = {
            "immediate_actions": error_info.user_actions,
            "technical_steps": [],
            "prevention_tips": [],
            "escalation_needed": False
        }

        # Add technical steps based on category
        if error_info.category == ErrorCategory.API_ERROR:
            suggestions["technical_steps"].extend([
                "Check API key configuration",
                "Verify API endpoint availability",
                "Review rate limiting settings"
            ])
        elif error_info.category == ErrorCategory.NETWORK_ERROR:
            suggestions["technical_steps"].extend([
                "Test network connectivity",
                "Check DNS resolution",
                "Verify firewall settings"
            ])

        # Add prevention tips
        if error_info.category == ErrorCategory.RATE_LIMIT_ERROR:
            suggestions["prevention_tips"].extend([
                "Implement request throttling",
                "Use caching to reduce API calls",
                "Consider upgrading API plan"
            ])

        # Determine if escalation is needed
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            suggestions["escalation_needed"] = True

        return suggestions


# Global instance
error_manager = ErrorManagementService()
