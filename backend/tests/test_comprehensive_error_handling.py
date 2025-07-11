"""
Comprehensive Error Handling Test Suite

Tests all error scenarios including API failures, network issues,
recovery mechanisms, fallback strategies, and monitoring.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests
import json

from src.services.error_management_service import (
    error_manager, 
    ErrorCategory, 
    ErrorSeverity, 
    RecoveryStrategy,
    ErrorContext,
    ErrorInfo
)
from src.services.enhanced_api_service import enhanced_api_service
from src.services.enhanced_retry_service import enhanced_retry_service, RetryConfig, CircuitBreakerConfig
from src.services.monitoring_service import monitoring_service
from src.services.fallback_service import fallback_service


class TestErrorManagementService:
    """Test the error management service"""
    
    def test_error_categorization(self):
        """Test error categorization logic"""
        # Network error
        network_error = requests.exceptions.ConnectionError("Connection failed")
        context = ErrorContext(api_name="test_api")
        error_info = error_manager.handle_error(network_error, context)
        
        assert error_info.category == ErrorCategory.NETWORK_ERROR
        assert error_info.severity in [ErrorSeverity.MEDIUM, ErrorSeverity.HIGH]
        assert "network" in error_info.user_message.lower()
    
    def test_authentication_error_handling(self):
        """Test authentication error handling"""
        auth_error = Exception("401 Unauthorized")
        context = ErrorContext(api_name="test_api")
        error_info = error_manager.handle_error(auth_error, context)
        
        assert error_info.category == ErrorCategory.AUTHENTICATION_ERROR
        assert error_info.recovery_strategy == RecoveryStrategy.USER_ACTION
        assert "authentication" in error_info.user_message.lower()
    
    def test_rate_limit_error_handling(self):
        """Test rate limit error handling"""
        rate_limit_error = Exception("429 Rate limit exceeded")
        context = ErrorContext(api_name="test_api")
        error_info = error_manager.handle_error(rate_limit_error, context)
        
        assert error_info.category == ErrorCategory.RATE_LIMIT_ERROR
        assert error_info.recovery_strategy == RecoveryStrategy.USER_ACTION
        assert "wait" in error_info.user_message.lower()
    
    def test_user_friendly_messages(self):
        """Test user-friendly error messages"""
        api_error = Exception("500 Internal Server Error")
        context = ErrorContext(api_name="brandfetch")
        error_info = error_manager.handle_error(api_error, context)
        
        # Should not expose technical details
        assert "500" not in error_info.user_message
        assert "Internal Server Error" not in error_info.user_message
        assert len(error_info.user_message) > 0
        assert error_info.user_message.endswith('.')
    
    def test_fallback_availability_check(self):
        """Test fallback availability checking"""
        context = ErrorContext(api_name="brandfetch")
        api_error = Exception("API Error")
        error_info = error_manager.handle_error(api_error, context)
        
        # Should detect fallback availability for brand data
        assert error_info.fallback_available == True
    
    def test_error_pattern_tracking(self):
        """Test error pattern tracking"""
        initial_patterns = len(error_manager.error_patterns)
        
        # Generate multiple similar errors
        for i in range(3):
            error = Exception(f"Test error {i}")
            context = ErrorContext(api_name="test_api")
            error_manager.handle_error(error, context)
        
        # Should track error patterns
        assert len(error_manager.error_patterns) > initial_patterns


class TestEnhancedRetryService:
    """Test the enhanced retry service"""
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation"""
        config = RetryConfig(
            base_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=10.0
        )
        
        # Test delay calculation
        delay_0 = enhanced_retry_service._calculate_delay(0, config)
        delay_1 = enhanced_retry_service._calculate_delay(1, config)
        delay_2 = enhanced_retry_service._calculate_delay(2, config)
        
        assert delay_0 >= 0.9 and delay_0 <= 1.1  # Base delay with jitter
        assert delay_1 >= 1.8 and delay_1 <= 2.2  # 2x base delay with jitter
        assert delay_2 >= 3.6 and delay_2 <= 4.4  # 4x base delay with jitter
    
    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions"""
        operation_name = "test_operation"
        config = CircuitBreakerConfig(failure_threshold=2)
        
        # Initially closed
        assert enhanced_retry_service.circuit_breakers.get(operation_name) is None
        
        # Simulate failures
        for i in range(3):
            try:
                enhanced_retry_service.execute_with_retry(
                    lambda: (_ for _ in ()).throw(Exception("Test error")),
                    operation_name,
                    RetryConfig(max_attempts=1),
                    config
                )
            except:
                pass
        
        # Should be open after threshold failures
        status = enhanced_retry_service.get_circuit_breaker_status(operation_name)
        assert operation_name in status
    
    def test_retry_with_non_retryable_exception(self):
        """Test that non-retryable exceptions don't trigger retries"""
        config = RetryConfig(
            max_attempts=3,
            non_retryable_exceptions=[ValueError]
        )
        
        call_count = 0
        def failing_operation():
            nonlocal call_count
            call_count += 1
            raise ValueError("Non-retryable error")
        
        with pytest.raises(Exception):
            enhanced_retry_service.execute_with_retry(
                failing_operation,
                "test_operation",
                config
            )
        
        # Should only be called once (no retries)
        assert call_count == 1
    
    def test_successful_retry_after_failures(self):
        """Test successful operation after initial failures"""
        call_count = 0
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = enhanced_retry_service.execute_with_retry(
            flaky_operation,
            "test_operation",
            RetryConfig(max_attempts=3)
        )
        
        assert result == "success"
        assert call_count == 3


class TestMonitoringService:
    """Test the monitoring service"""
    
    def test_performance_metric_recording(self):
        """Test performance metric recording"""
        with monitoring_service.track_performance("test_operation", correlation_id="test_123"):
            time.sleep(0.1)  # Simulate work
        
        # Check that metric was recorded
        summary = monitoring_service.get_performance_summary(hours=1)
        assert summary['total_operations'] > 0
        assert 'test_operation' in summary['operations']
        assert summary['operations']['test_operation']['avg_duration'] > 0.05
    
    def test_health_check_recording(self):
        """Test health check recording"""
        monitoring_service.record_health_check(
            service="test_service",
            status="healthy",
            response_time=100.0,
            details={"version": "1.0.0"}
        )
        
        health_status = monitoring_service.get_health_status()
        assert 'test_service' in health_status['services']
        assert health_status['services']['test_service']['status'] == 'healthy'
    
    def test_alert_creation_and_resolution(self):
        """Test alert creation and resolution"""
        from src.services.monitoring_service import AlertLevel
        
        alert_id = monitoring_service.create_alert(
            level=AlertLevel.WARNING,
            title="Test Alert",
            message="This is a test alert",
            service="test_service"
        )
        
        # Check alert was created
        active_alerts = monitoring_service.get_active_alerts()
        assert len(active_alerts) > 0
        assert any(alert['id'] == alert_id for alert in active_alerts)
        
        # Resolve alert
        monitoring_service.resolve_alert(alert_id)
        
        # Check alert was resolved
        active_alerts = monitoring_service.get_active_alerts()
        assert not any(alert['id'] == alert_id for alert in active_alerts)
    
    def test_metric_threshold_alerts(self):
        """Test automatic alert creation based on metric thresholds"""
        # Record a slow performance metric
        monitoring_service.record_performance_metric(
            monitoring_service.PerformanceMetric(
                operation="slow_operation",
                duration=15.0,  # Exceeds critical threshold
                success=True
            )
        )
        
        # Should create an alert
        active_alerts = monitoring_service.get_active_alerts()
        slow_alerts = [alert for alert in active_alerts if 'slow' in alert['title'].lower()]
        assert len(slow_alerts) > 0


class TestFallbackService:
    """Test the fallback service"""
    
    @pytest.mark.asyncio
    async def test_brand_data_fallback(self):
        """Test brand data fallback strategies"""
        with patch('wikipedia.search') as mock_search, \
             patch('wikipedia.page') as mock_page:
            
            # Mock Wikipedia response
            mock_search.return_value = ['Apple Inc.']
            mock_page_obj = Mock()
            mock_page_obj.summary = "Apple Inc. is a technology company"
            mock_page_obj.url = "https://en.wikipedia.org/wiki/Apple_Inc."
            mock_page_obj.content = "Apple Inc. was founded in 1976"
            mock_page.return_value = mock_page_obj
            
            result = await fallback_service.get_brand_data_with_fallback("Apple Inc.")
            
            assert result.success == True
            assert result.source == "wikipedia"
            assert result.quality_score > 0
            assert "Apple Inc." in result.data['name']
    
    @pytest.mark.asyncio
    async def test_news_data_fallback(self):
        """Test news data fallback strategies"""
        with patch('feedparser.parse') as mock_parse:
            # Mock RSS feed response
            mock_feed = Mock()
            mock_entry = Mock()
            mock_entry.title = "Apple announces new product"
            mock_entry.summary = "Apple has announced a new product line"
            mock_entry.link = "https://example.com/news/1"
            mock_entry.published = "2024-01-01"
            mock_feed.entries = [mock_entry]
            mock_parse.return_value = mock_feed
            
            result = await fallback_service.get_news_data_with_fallback("Apple Inc.")
            
            assert result.success == True
            assert result.source == "rss_feeds"
            assert len(result.data['articles']) > 0
    
    @pytest.mark.asyncio
    async def test_ai_analysis_fallback(self):
        """Test AI analysis fallback strategies"""
        result = await fallback_service.get_ai_analysis_with_fallback(
            "Brand analysis context", 
            "Apple Inc."
        )
        
        assert result.success == True
        assert result.source == "template_analysis"
        assert 'brand_perception' in result.data
        assert 'competitive_analysis' in result.data
    
    def test_fallback_caching(self):
        """Test fallback result caching"""
        test_data = {"test": "data"}
        cache_key = "test_cache_key"
        
        # Cache data
        fallback_service.cache_result(cache_key, test_data)
        
        # Should be in cache
        assert cache_key in fallback_service.fallback_cache
        assert fallback_service.fallback_cache[cache_key]['data'] == test_data
    
    def test_cache_cleanup(self):
        """Test cache cleanup functionality"""
        # Add expired entry
        expired_key = "expired_key"
        fallback_service.fallback_cache[expired_key] = {
            'data': {"old": "data"},
            'timestamp': datetime.utcnow() - timedelta(hours=2)
        }
        
        # Trigger cleanup
        fallback_service._cleanup_cache()
        
        # Expired entry should be removed
        assert expired_key not in fallback_service.fallback_cache


class TestIntegratedErrorHandling:
    """Test integrated error handling across services"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_error_recovery(self):
        """Test complete error recovery flow"""
        # Simulate API failure with fallback recovery
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
            
            # This should trigger fallback mechanisms
            result = await fallback_service.get_brand_data_with_fallback("Test Company")
            
            # Should succeed with fallback data
            assert result.success == True
            assert result.fallback_used == True
            assert len(result.limitations) > 0
    
    def test_circuit_breaker_integration(self):
        """Test circuit breaker integration with error management"""
        operation_name = "integration_test"
        
        # Simulate multiple failures to open circuit breaker
        for i in range(5):
            try:
                enhanced_retry_service.execute_with_retry(
                    lambda: (_ for _ in ()).throw(Exception("Persistent error")),
                    operation_name,
                    RetryConfig(max_attempts=1),
                    CircuitBreakerConfig(failure_threshold=3)
                )
            except:
                pass
        
        # Circuit breaker should be open
        status = enhanced_retry_service.get_circuit_breaker_status(operation_name)
        assert operation_name in status
    
    def test_monitoring_integration(self):
        """Test monitoring integration with error handling"""
        # Generate an error that should trigger monitoring
        error = Exception("Test monitoring error")
        context = ErrorContext(
            api_name="test_api",
            operation="test_operation",
            correlation_id="test_correlation_123"
        )
        
        error_info = error_manager.handle_error(error, context)
        
        # Should have correlation ID for tracking
        assert error_info.context.correlation_id == "test_correlation_123"
        
        # Should be trackable in monitoring
        assert error_info.error_id is not None


class TestErrorRecoveryScenarios:
    """Test specific error recovery scenarios"""
    
    def test_network_timeout_recovery(self):
        """Test recovery from network timeout"""
        timeout_error = requests.exceptions.Timeout("Request timed out")
        context = ErrorContext(api_name="test_api")
        error_info = error_manager.handle_error(timeout_error, context)
        
        assert error_info.category == ErrorCategory.TIMEOUT_ERROR
        assert error_info.recovery_strategy == RecoveryStrategy.RETRY
        assert error_info.can_retry == True
    
    def test_service_degradation_handling(self):
        """Test graceful service degradation"""
        # Simulate partial service failure
        context = ErrorContext(api_name="brandfetch")
        service_error = Exception("Service temporarily unavailable")
        error_info = error_manager.handle_error(service_error, context)
        
        # Should suggest degraded operation
        if error_info.recovery_strategy == RecoveryStrategy.DEGRADE:
            recovery_result = error_manager._handle_degrade_recovery(error_info)
            assert recovery_result['success'] == True
            assert recovery_result['degraded'] == True
            assert 'available_features' in recovery_result
    
    def test_authentication_recovery_flow(self):
        """Test authentication error recovery flow"""
        auth_error = Exception("401 Authentication failed")
        context = ErrorContext(api_name="test_api", user_id="test_user")
        error_info = error_manager.handle_error(auth_error, context)
        
        assert error_info.recovery_strategy == RecoveryStrategy.USER_ACTION
        assert "log in" in error_info.user_message.lower()
        assert len(error_info.user_actions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
