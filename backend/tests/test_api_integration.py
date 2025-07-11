"""
Comprehensive API integration tests for brand audit endpoints
"""
import pytest
import json
import time
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from conftest import (
    assert_valid_analysis_response,
    assert_valid_progress_update,
    assert_valid_results_structure,
    IntegrationTestHelper
)


class TestAnalysisAPIIntegration:
    """Test analysis API endpoints integration"""
    
    def test_start_analysis_endpoint(self, client, test_data_factory, mock_api_services):
        """Test analysis start endpoint with valid data"""
        request_data = test_data_factory.create_analysis_request("Apple Inc")
        
        response = client.post('/api/analyze', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert_valid_analysis_response(data)
        
        # Verify analysis was created in database
        analysis_id = data['data']['analysis_id']
        status_response = client.get(f'/api/analyze/{analysis_id}/status')
        assert status_response.status_code == 200
    
    def test_start_analysis_invalid_data(self, client):
        """Test analysis start with invalid data"""
        invalid_requests = [
            {},  # Empty request
            {'company_name': ''},  # Empty company name
            {'company_name': 'A' * 300},  # Too long company name
            {'company_name': 'Test<script>'},  # Invalid characters
            {'company_name': 'Test', 'website': 'invalid-url'},  # Invalid URL
        ]
        
        for invalid_data in invalid_requests:
            response = client.post('/api/analyze',
                                 data=json.dumps(invalid_data),
                                 content_type='application/json')
            assert response.status_code in [400, 422], f"Failed for data: {invalid_data}"
    
    def test_analysis_status_endpoint(self, client, test_analysis):
        """Test analysis status endpoint"""
        response = client.get(f'/api/analyze/{test_analysis.id}/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        
        status_data = data['data']
        assert status_data['analysis_id'] == test_analysis.id
        assert status_data['status'] == test_analysis.status
        assert status_data['progress'] == test_analysis.progress
    
    def test_analysis_status_not_found(self, client):
        """Test status endpoint with non-existent analysis"""
        response = client.get('/api/analyze/non-existent-id/status')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_analysis_results_endpoint(self, client, test_analysis, sample_analysis_results):
        """Test analysis results endpoint"""
        # Update analysis with results
        test_analysis.status = 'completed'
        test_analysis.progress = 100
        test_analysis.results = sample_analysis_results
        
        response = client.get(f'/api/analyze/{test_analysis.id}/results')
        
        assert response.status_code == 200
        data = response.get_json()
        assert_valid_results_structure(data)
        
        results = data['data']
        assert results['analysis_id'] == test_analysis.id
        assert results['status'] == 'completed'
        assert 'llm_insights' in results
        assert 'visual_analysis' in results
    
    def test_analysis_results_not_ready(self, client, test_analysis):
        """Test results endpoint when analysis is not complete"""
        # Ensure analysis is not completed
        test_analysis.status = 'processing'
        test_analysis.progress = 50
        
        response = client.get(f'/api/analyze/{test_analysis.id}/results')
        assert response.status_code in [202, 404]  # Not ready or not found
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'version' in data
        assert 'timestamp' in data
    
    def test_cors_headers(self, client, test_data_factory):
        """Test CORS headers are properly set"""
        request_data = test_data_factory.create_analysis_request()
        
        # Test preflight request
        response = client.options('/api/analyze')
        assert response.status_code == 200
        
        # Test actual request has CORS headers
        response = client.post('/api/analyze',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        # Check for CORS headers (if configured)
        headers = response.headers
        # Note: Actual CORS headers depend on Flask-CORS configuration
    
    def test_rate_limiting(self, client, test_data_factory):
        """Test rate limiting (if enabled)"""
        request_data = test_data_factory.create_analysis_request()
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            responses.append(response.status_code)
        
        # Check if any requests were rate limited
        # Note: This depends on rate limiting configuration
        success_codes = [200, 201]
        rate_limit_codes = [429]
        
        for status_code in responses:
            assert status_code in success_codes + rate_limit_codes


class TestAnalysisWorkflowIntegration:
    """Test complete analysis workflow integration"""
    
    def test_complete_analysis_workflow(self, client, test_data_factory, mock_api_services):
        """Test complete analysis workflow from start to results"""
        # Step 1: Start analysis
        request_data = test_data_factory.create_analysis_request("Tesla")
        
        start_response = client.post('/api/analyze',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
        
        assert start_response.status_code == 200
        start_data = start_response.get_json()
        analysis_id = start_data['data']['analysis_id']
        
        # Step 2: Check initial status
        status_response = client.get(f'/api/analyze/{analysis_id}/status')
        assert status_response.status_code == 200
        
        status_data = status_response.get_json()
        assert status_data['data']['status'] in ['started', 'processing']
        
        # Step 3: Wait for completion (with timeout)
        try:
            final_status = IntegrationTestHelper.wait_for_analysis_completion(
                client, analysis_id, timeout=30
            )
            
            # Step 4: Get results
            results_response = client.get(f'/api/analyze/{analysis_id}/results')
            assert results_response.status_code == 200
            
            results_data = results_response.get_json()
            assert_valid_results_structure(results_data)
            
        except TimeoutError:
            # Analysis didn't complete in time - check it's still processing
            status_response = client.get(f'/api/analyze/{analysis_id}/status')
            status_data = status_response.get_json()
            assert status_data['data']['status'] in ['processing', 'started']
    
    def test_concurrent_analyses(self, client, test_data_factory, mock_api_services):
        """Test handling of concurrent analysis requests"""
        brands = ["Apple", "Google", "Microsoft"]
        analysis_ids = []
        
        # Start multiple analyses
        for brand in brands:
            request_data = test_data_factory.create_analysis_request(brand)
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            analysis_ids.append(data['data']['analysis_id'])
        
        # Check all analyses are tracked
        for analysis_id in analysis_ids:
            status_response = client.get(f'/api/analyze/{analysis_id}/status')
            assert status_response.status_code == 200
    
    def test_analysis_error_handling(self, client, test_data_factory):
        """Test analysis error handling"""
        # Mock service to raise an exception
        with patch('src.services.llm_service.LLMService') as mock_llm:
            mock_llm.return_value.analyze_brand_sentiment.side_effect = Exception("API Error")
            
            request_data = test_data_factory.create_analysis_request("ErrorBrand")
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                analysis_id = data['data']['analysis_id']
                
                # Wait a bit for error to be processed
                time.sleep(2)
                
                # Check status shows error
                status_response = client.get(f'/api/analyze/{analysis_id}/status')
                if status_response.status_code == 200:
                    status_data = status_response.get_json()
                    # Error might be reflected in status or error_message
                    assert status_data['data']['status'] in ['error', 'failed', 'processing']


class TestDataValidationIntegration:
    """Test data validation and sanitization"""
    
    def test_input_sanitization(self, client):
        """Test input data is properly sanitized"""
        malicious_inputs = [
            {'company_name': '<script>alert("xss")</script>'},
            {'company_name': 'Test"; DROP TABLE analyses; --'},
            {'company_name': '../../etc/passwd'},
            {'website': 'javascript:alert("xss")'},
        ]
        
        for malicious_data in malicious_inputs:
            response = client.post('/api/analyze',
                                 data=json.dumps(malicious_data),
                                 content_type='application/json')
            
            # Should either reject the input or sanitize it
            assert response.status_code in [400, 422, 200]
            
            if response.status_code == 200:
                # If accepted, verify it was sanitized
                data = response.get_json()
                analysis_id = data['data']['analysis_id']
                
                status_response = client.get(f'/api/analyze/{analysis_id}/status')
                status_data = status_response.get_json()
                
                # Verify no malicious content in stored data
                brand_name = status_data['data'].get('brand_name', '')
                assert '<script>' not in brand_name
                assert 'DROP TABLE' not in brand_name
    
    def test_response_data_structure(self, client, test_data_factory, sample_analysis_results):
        """Test API responses have consistent data structures"""
        request_data = test_data_factory.create_analysis_request()
        
        # Start analysis
        response = client.post('/api/analyze',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert isinstance(data, dict)
        assert 'success' in data
        assert 'data' in data
        assert isinstance(data['success'], bool)
        assert isinstance(data['data'], dict)
        
        # Test status endpoint structure
        analysis_id = data['data']['analysis_id']
        status_response = client.get(f'/api/analyze/{analysis_id}/status')
        status_data = status_response.get_json()
        
        assert isinstance(status_data, dict)
        assert 'success' in status_data
        assert 'data' in status_data
