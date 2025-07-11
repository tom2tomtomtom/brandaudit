"""
Comprehensive error handling validation tests
"""
import pytest
import json
import time
from unittest.mock import patch, Mock, side_effect
from requests.exceptions import RequestException, Timeout, ConnectionError
from sqlalchemy.exc import SQLAlchemyError

from conftest import IntegrationTestHelper


class TestAPIErrorHandling:
    """Test API error handling scenarios"""
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON in request"""
        invalid_json_requests = [
            '{"company_name": "Test"',  # Incomplete JSON
            '{"company_name": }',  # Invalid syntax
            'not json at all',  # Not JSON
            '',  # Empty request
        ]
        
        for invalid_json in invalid_json_requests:
            response = client.post('/api/analyze',
                                 data=invalid_json,
                                 content_type='application/json')
            
            assert response.status_code in [400, 422]
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        invalid_requests = [
            {},  # No fields
            {'website': 'https://test.com'},  # Missing company_name
            {'company_name': ''},  # Empty company_name
            {'company_name': None},  # Null company_name
        ]
        
        for invalid_data in invalid_requests:
            response = client.post('/api/analyze',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json')
            
            assert response.status_code in [400, 422]
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data
    
    def test_field_validation_errors(self, client):
        """Test field validation error handling"""
        invalid_requests = [
            {'company_name': 'A' * 300},  # Too long
            {'company_name': 'Test<script>'},  # Invalid characters
            {'company_name': 'Test', 'website': 'not-a-url'},  # Invalid URL
            {'company_name': 'Test', 'analysis_options': 'not-a-dict'},  # Wrong type
        ]
        
        for invalid_data in invalid_requests:
            response = client.post('/api/analyze',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json')
            
            assert response.status_code in [400, 422]
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data
    
    def test_database_error_handling(self, client, test_data_factory):
        """Test database error handling"""
        request_data = test_data_factory.create_analysis_request()
        
        # Mock database error
        with patch('src.extensions.db.session.add') as mock_add:
            mock_add.side_effect = SQLAlchemyError("Database connection failed")
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data
    
    def test_analysis_not_found(self, client):
        """Test handling of non-existent analysis requests"""
        non_existent_id = 'non-existent-analysis-id'
        
        # Test status endpoint
        response = client.get(f'/api/analyze/{non_existent_id}/status')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        
        # Test results endpoint
        response = client.get(f'/api/analyze/{non_existent_id}/results')
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_malformed_analysis_id(self, client):
        """Test handling of malformed analysis IDs"""
        malformed_ids = [
            '../../../etc/passwd',  # Path traversal
            '<script>alert("xss")</script>',  # XSS attempt
            'DROP TABLE analyses; --',  # SQL injection attempt
            '',  # Empty ID
            'a' * 1000,  # Too long
        ]
        
        for malformed_id in malformed_ids:
            # Test status endpoint
            response = client.get(f'/api/analyze/{malformed_id}/status')
            assert response.status_code in [400, 404, 422]
            
            # Test results endpoint
            response = client.get(f'/api/analyze/{malformed_id}/results')
            assert response.status_code in [400, 404, 422]


class TestServiceErrorHandling:
    """Test service-level error handling"""
    
    def test_llm_service_error(self, client, test_data_factory):
        """Test LLM service error handling"""
        request_data = test_data_factory.create_analysis_request()
        
        with patch('src.services.llm_service.LLMService') as mock_llm:
            # Test different types of LLM errors
            error_scenarios = [
                RequestException("API request failed"),
                Timeout("Request timed out"),
                ConnectionError("Connection failed"),
                Exception("Unexpected error")
            ]
            
            for error in error_scenarios:
                mock_llm.return_value.analyze_brand_sentiment.side_effect = error
                
                response = client.post('/api/analyze',
                                     data=json.dumps(request_data),
                                     content_type='application/json')
                
                # Should either handle gracefully or return error
                assert response.status_code in [200, 500]
                
                if response.status_code == 200:
                    # If analysis started, check it handles the error
                    data = response.get_json()
                    analysis_id = data['data']['analysis_id']
                    
                    # Wait for error to be processed
                    time.sleep(2)
                    
                    status_response = client.get(f'/api/analyze/{analysis_id}/status')
                    if status_response.status_code == 200:
                        status_data = status_response.get_json()
                        # Should show error or still be processing with fallback
                        assert status_data['data']['status'] in ['error', 'failed', 'processing']
    
    def test_news_service_error(self, client, test_data_factory):
        """Test news service error handling"""
        request_data = test_data_factory.create_analysis_request()
        
        with patch('src.services.news_service.NewsService') as mock_news:
            mock_news.return_value.get_recent_news.side_effect = Exception("News API failed")
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should handle news service error gracefully
            assert response.status_code in [200, 500]
    
    def test_visual_analysis_service_error(self, client, test_data_factory):
        """Test visual analysis service error handling"""
        request_data = test_data_factory.create_analysis_request()
        
        with patch('src.services.visual_analysis_service.VisualAnalysisService') as mock_visual:
            mock_visual.return_value.analyze_brand_visuals.side_effect = Exception("Visual analysis failed")
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should handle visual analysis error gracefully
            assert response.status_code in [200, 500]
    
    def test_multiple_service_failures(self, client, test_data_factory):
        """Test handling when multiple services fail"""
        request_data = test_data_factory.create_analysis_request()
        
        with patch('src.services.llm_service.LLMService') as mock_llm, \
             patch('src.services.news_service.NewsService') as mock_news, \
             patch('src.services.visual_analysis_service.VisualAnalysisService') as mock_visual:
            
            # All services fail
            mock_llm.return_value.analyze_brand_sentiment.side_effect = Exception("LLM failed")
            mock_news.return_value.get_recent_news.side_effect = Exception("News failed")
            mock_visual.return_value.analyze_brand_visuals.side_effect = Exception("Visual failed")
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should handle gracefully even when all services fail
            assert response.status_code in [200, 500]
            
            if response.status_code == 200:
                data = response.get_json()
                analysis_id = data['data']['analysis_id']
                
                # Wait for processing
                time.sleep(3)
                
                # Check final status
                status_response = client.get(f'/api/analyze/{analysis_id}/status')
                if status_response.status_code == 200:
                    status_data = status_response.get_json()
                    # Should indicate error or provide partial results
                    assert status_data['data']['status'] in ['error', 'failed', 'completed']


class TestNetworkErrorHandling:
    """Test network-related error handling"""
    
    def test_timeout_handling(self, client, test_data_factory):
        """Test request timeout handling"""
        request_data = test_data_factory.create_analysis_request()
        
        with patch('src.services.llm_service.LLMService') as mock_llm:
            # Simulate timeout
            def slow_response(*args, **kwargs):
                time.sleep(10)  # Longer than typical timeout
                return {'analysis': 'Slow response'}
            
            mock_llm.return_value.analyze_brand_sentiment.side_effect = slow_response
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should handle timeout gracefully
            assert response.status_code in [200, 500, 504]
    
    def test_rate_limit_handling(self, client, test_data_factory):
        """Test rate limit error handling"""
        request_data = test_data_factory.create_analysis_request()
        
        # Make multiple rapid requests
        responses = []
        for i in range(20):  # More than typical rate limit
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            responses.append(response.status_code)
        
        # Should handle rate limiting
        rate_limited = any(status == 429 for status in responses)
        successful = any(status == 200 for status in responses)
        
        # Either rate limiting is working or all requests succeeded
        assert rate_limited or successful
    
    def test_connection_error_recovery(self, client, test_data_factory):
        """Test recovery from connection errors"""
        request_data = test_data_factory.create_analysis_request()
        
        with patch('src.services.llm_service.LLMService') as mock_llm:
            # First call fails, second succeeds
            mock_llm.return_value.analyze_brand_sentiment.side_effect = [
                ConnectionError("Connection failed"),
                {'analysis': 'Success after retry', 'sentiment_score': 0.8}
            ]
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should handle connection error and potentially retry
            assert response.status_code in [200, 500]


class TestDataValidationErrorHandling:
    """Test data validation and sanitization error handling"""
    
    def test_xss_prevention(self, client):
        """Test XSS attack prevention"""
        xss_payloads = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src="x" onerror="alert(1)">',
            '"><script>alert("xss")</script>',
        ]
        
        for payload in xss_payloads:
            request_data = {
                'company_name': payload,
                'analysis_options': {'brandPerception': True}
            }
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should either reject or sanitize
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                # If accepted, verify it was sanitized
                data = response.get_json()
                analysis_id = data['data']['analysis_id']
                
                status_response = client.get(f'/api/analyze/{analysis_id}/status')
                if status_response.status_code == 200:
                    status_data = status_response.get_json()
                    brand_name = status_data['data'].get('brand_name', '')
                    
                    # Should not contain script tags
                    assert '<script>' not in brand_name.lower()
                    assert 'javascript:' not in brand_name.lower()
    
    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention"""
        sql_payloads = [
            "'; DROP TABLE analyses; --",
            "' OR '1'='1",
            "'; INSERT INTO analyses VALUES ('malicious'); --",
            "' UNION SELECT * FROM users; --",
        ]
        
        for payload in sql_payloads:
            request_data = {
                'company_name': payload,
                'analysis_options': {'brandPerception': True}
            }
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should handle safely
            assert response.status_code in [200, 400, 422]
            
            # Database should still be intact
            health_response = client.get('/api/health')
            assert health_response.status_code == 200
    
    def test_path_traversal_prevention(self, client):
        """Test path traversal attack prevention"""
        path_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '/etc/shadow',
            '....//....//....//etc/passwd',
        ]
        
        for payload in path_payloads:
            # Test in analysis ID
            response = client.get(f'/api/analyze/{payload}/status')
            assert response.status_code in [400, 404, 422]
            
            # Test in request data
            request_data = {
                'company_name': payload,
                'analysis_options': {'brandPerception': True}
            }
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should handle safely
            assert response.status_code in [200, 400, 422]


class TestErrorRecoveryAndResilience:
    """Test error recovery and system resilience"""
    
    def test_partial_failure_handling(self, client, test_data_factory):
        """Test handling when some services succeed and others fail"""
        request_data = test_data_factory.create_analysis_request()
        
        with patch('src.services.llm_service.LLMService') as mock_llm, \
             patch('src.services.news_service.NewsService') as mock_news:
            
            # LLM succeeds, News fails
            mock_llm.return_value.analyze_brand_sentiment.return_value = {
                'analysis': 'LLM analysis successful',
                'sentiment_score': 0.8
            }
            mock_news.return_value.get_recent_news.side_effect = Exception("News service failed")
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            analysis_id = data['data']['analysis_id']
            
            # Wait for processing
            time.sleep(3)
            
            # Should complete with partial results
            results_response = client.get(f'/api/analyze/{analysis_id}/results')
            if results_response.status_code == 200:
                results_data = results_response.get_json()
                results = results_data['data']
                
                # Should have LLM results but not news results
                assert 'llm_insights' in results
                # News analysis might be missing or have error indicator
    
    def test_graceful_degradation(self, client, test_data_factory):
        """Test graceful degradation when services are unavailable"""
        request_data = test_data_factory.create_analysis_request()
        
        # Mock all external services to fail
        with patch('src.services.llm_service.LLMService') as mock_llm, \
             patch('src.services.news_service.NewsService') as mock_news, \
             patch('src.services.visual_analysis_service.VisualAnalysisService') as mock_visual:
            
            mock_llm.return_value.analyze_brand_sentiment.side_effect = Exception("Service unavailable")
            mock_news.return_value.get_recent_news.side_effect = Exception("Service unavailable")
            mock_visual.return_value.analyze_brand_visuals.side_effect = Exception("Service unavailable")
            
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            # Should still accept the request
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.get_json()
                analysis_id = data['data']['analysis_id']
                
                # Should track the analysis even if services fail
                status_response = client.get(f'/api/analyze/{analysis_id}/status')
                assert status_response.status_code == 200
    
    def test_error_message_consistency(self, client, test_data_factory):
        """Test that error messages are consistent and informative"""
        # Test various error scenarios and verify message format
        error_scenarios = [
            ({'company_name': ''}, 'validation'),
            ({'company_name': 'A' * 300}, 'validation'),
            ({}, 'missing_field'),
        ]
        
        for invalid_data, error_type in error_scenarios:
            response = client.post('/api/analyze',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json')
            
            assert response.status_code in [400, 422]
            data = response.get_json()
            
            # Verify error response structure
            assert 'success' in data
            assert data['success'] is False
            assert 'error' in data
            assert isinstance(data['error'], str)
            assert len(data['error']) > 0
            
            # Error message should be informative but not expose internals
            error_message = data['error'].lower()
            assert 'traceback' not in error_message
            assert 'exception' not in error_message
            assert 'internal' not in error_message or 'server error' in error_message
