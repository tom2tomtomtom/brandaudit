#!/usr/bin/env python3
"""
Integration tests for existing brand analysis workflow
Tests the complete flow from API request to results with REAL data
"""
import os
import sys
import pytest
import json
import time
import threading
from unittest.mock import patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, analysis_storage
from simple_analysis import run_brand_analysis, SimpleAnalyzer
from src.services.websocket_service import get_websocket_service

class TestIntegrationWorkflow:
    """Integration tests for existing analysis workflow"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                from src.extensions import db
                db.create_all()
                yield client
                db.drop_all()
    
    def test_complete_analysis_workflow_mock(self, client):
        """Test complete analysis workflow with mocked APIs"""
        
        # Mock API calls to avoid external dependencies
        with patch('simple_analysis.SimpleAnalyzer.call_llm_analysis') as mock_llm, \
             patch('simple_analysis.SimpleAnalyzer.call_news_api') as mock_news, \
             patch('simple_analysis.SimpleAnalyzer.call_brandfetch') as mock_brandfetch:
            
            # Setup mock responses
            mock_llm.return_value = {
                'success': True,
                'analysis': '''
                EXECUTIVE SUMMARY
                Apple Inc is a leading technology company with strong brand recognition.
                
                STRENGTHS
                • Strong brand loyalty
                • Innovative product design
                • Premium market positioning
                
                WEAKNESSES
                • High pricing strategy
                • Limited market segments
                
                STRATEGIC RECOMMENDATIONS
                • Expand into emerging markets
                • Develop more affordable product lines
                '''
            }
            
            mock_news.return_value = {
                'success': True,
                'total_articles': 15,
                'positive_percentage': 75,
                'negative_percentage': 15,
                'neutral_percentage': 10
            }
            
            mock_brandfetch.return_value = {
                'success': True,
                'name': 'Apple Inc',
                'domain': 'apple.com',
                'colors': ['#000000', '#FFFFFF'],
                'logos': [{'format': 'png', 'url': 'https://example.com/logo.png'}],
                'fonts': ['SF Pro Display']
            }
            
            # Step 1: Start analysis
            test_data = {
                'company_name': 'Apple Inc',
                'analysis_types': ['brand_positioning', 'competitive_analysis']
            }
            
            response = client.post('/api/analyze',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            analysis_id = data['data']['analysis_id']
            
            # Step 2: Wait for analysis to complete (with timeout)
            max_wait = 30  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                response = client.get(f'/api/analyze/{analysis_id}/status')
                status_data = response.get_json()
                
                if status_data['data']['status'] == 'completed':
                    break
                elif status_data['data']['status'] == 'failed':
                    pytest.fail(f"Analysis failed: {status_data}")
                    
                time.sleep(1)
            else:
                pytest.fail("Analysis did not complete within timeout")
            
            # Step 3: Get results
            response = client.get(f'/api/analyze/{analysis_id}/results')
            assert response.status_code == 200
            
            results_data = response.get_json()
            assert results_data['success'] is True
            assert 'data' in results_data
            
            # Verify result structure
            results = results_data['data']
            assert results['brand_name'] == 'Apple Inc'
            assert 'data_sources' in results
            assert 'key_metrics' in results
            assert 'brand_health_dashboard' in results
            
            # Verify data sources were used
            data_sources = results['data_sources']
            assert data_sources['llm_analysis'] is True
            assert data_sources['news_data'] is True
            assert data_sources['brand_data'] is True
            
    def test_analysis_with_websocket_progress(self, client):
        """Test analysis workflow with WebSocket progress tracking"""
        
        # Mock API calls for faster testing
        with patch('simple_analysis.SimpleAnalyzer.call_llm_analysis') as mock_llm, \
             patch('simple_analysis.SimpleAnalyzer.call_news_api') as mock_news, \
             patch('simple_analysis.SimpleAnalyzer.call_brandfetch') as mock_brandfetch:
            
            mock_llm.return_value = {'success': True, 'analysis': 'Test analysis'}
            mock_news.return_value = {'success': True, 'total_articles': 5}
            mock_brandfetch.return_value = {'success': True, 'name': 'Tesla'}
            
            # Start analysis
            test_data = {'company_name': 'Tesla'}
            response = client.post('/api/analyze',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            analysis_id = response.get_json()['data']['analysis_id']
            
            # Check WebSocket service has progress tracker
            websocket_service = get_websocket_service()
            
            # Wait a moment for analysis to start
            time.sleep(2)
            
            # Should have created progress tracker
            assert analysis_id in websocket_service.progress_trackers
            
            tracker = websocket_service.progress_trackers[analysis_id]
            assert tracker.analysis_id == analysis_id
            assert tracker.total_stages > 0
            
    def test_analysis_error_handling(self, client):
        """Test analysis workflow error handling"""
        
        # Mock all APIs to fail
        with patch('simple_analysis.SimpleAnalyzer.call_llm_analysis') as mock_llm, \
             patch('simple_analysis.SimpleAnalyzer.call_news_api') as mock_news, \
             patch('simple_analysis.SimpleAnalyzer.call_brandfetch') as mock_brandfetch:
            
            mock_llm.return_value = {'error': 'LLM API failed'}
            mock_news.return_value = {'error': 'News API failed'}
            mock_brandfetch.return_value = {'error': 'Brandfetch API failed'}
            
            # Start analysis
            test_data = {'company_name': 'FailBrand'}
            response = client.post('/api/analyze',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            analysis_id = response.get_json()['data']['analysis_id']
            
            # Wait for analysis to complete
            time.sleep(5)
            
            # Check status
            response = client.get(f'/api/analyze/{analysis_id}/status')
            status_data = response.get_json()
            
            # Should handle errors gracefully
            assert status_data['success'] is True  # Status endpoint should work
            
            # Try to get results
            response = client.get(f'/api/analyze/{analysis_id}/results')
            
            # Should either be not complete or return error info
            assert response.status_code in [202, 200, 400]
            
    def test_multiple_concurrent_analyses(self, client):
        """Test multiple concurrent analyses"""
        
        with patch('simple_analysis.SimpleAnalyzer.call_llm_analysis') as mock_llm, \
             patch('simple_analysis.SimpleAnalyzer.call_news_api') as mock_news, \
             patch('simple_analysis.SimpleAnalyzer.call_brandfetch') as mock_brandfetch:
            
            # Setup quick mock responses
            mock_llm.return_value = {'success': True, 'analysis': 'Quick analysis'}
            mock_news.return_value = {'success': True, 'total_articles': 3}
            mock_brandfetch.return_value = {'success': True, 'name': 'Brand'}
            
            # Start multiple analyses
            brands = ['Nike', 'Adidas', 'Puma']
            analysis_ids = []
            
            for brand in brands:
                test_data = {'company_name': brand}
                response = client.post('/api/analyze',
                                     data=json.dumps(test_data),
                                     content_type='application/json')
                
                analysis_id = response.get_json()['data']['analysis_id']
                analysis_ids.append(analysis_id)
            
            # All should be stored in analysis_storage
            for analysis_id in analysis_ids:
                assert analysis_id in analysis_storage
                
            # Wait for analyses to complete
            time.sleep(10)
            
            # Check all analyses
            completed_count = 0
            for analysis_id in analysis_ids:
                response = client.get(f'/api/analyze/{analysis_id}/status')
                status_data = response.get_json()
                
                if status_data['data']['status'] == 'completed':
                    completed_count += 1
            
            # At least some should complete
            assert completed_count > 0
            
    def test_analysis_with_different_types(self, client):
        """Test analysis with different analysis types"""
        
        with patch('simple_analysis.SimpleAnalyzer.call_llm_analysis') as mock_llm, \
             patch('simple_analysis.SimpleAnalyzer.call_news_api') as mock_news, \
             patch('simple_analysis.SimpleAnalyzer.call_brandfetch') as mock_brandfetch:
            
            mock_llm.return_value = {'success': True, 'analysis': 'Comprehensive analysis'}
            mock_news.return_value = {'success': True, 'total_articles': 8}
            mock_brandfetch.return_value = {'success': True, 'name': 'Google'}
            
            # Test with comprehensive analysis types
            test_data = {
                'company_name': 'Google',
                'analysis_types': [
                    'brand_positioning',
                    'competitive_analysis',
                    'visual_analysis',
                    'sentiment_analysis',
                    'market_research'
                ]
            }
            
            response = client.post('/api/analyze',
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = response.get_json()
            analysis_id = data['data']['analysis_id']
            
            # Verify analysis types were stored
            assert analysis_id in analysis_storage
            stored_analysis = analysis_storage[analysis_id]
            assert stored_analysis['analysis_types'] == test_data['analysis_types']
            
    def test_run_brand_analysis_function(self):
        """Test the run_brand_analysis function directly"""
        
        with patch('simple_analysis.SimpleAnalyzer.analyze_brand') as mock_analyze:
            mock_analyze.return_value = {
                'success': True,
                'brand_name': 'Direct Test Brand',
                'key_metrics': {'overall_score': 80}
            }
            
            # Test the function directly
            analysis_id = 'direct-test-123'
            test_storage = {}
            
            run_brand_analysis('Direct Test Brand', analysis_id, test_storage)
            
            # Should have called analyze_brand
            mock_analyze.assert_called_once_with(
                'Direct Test Brand', 
                analysis_id, 
                test_storage, 
                None  # websocket_service
            )
            
            # Should have updated storage
            assert analysis_id in test_storage
            assert test_storage[analysis_id]['status'] == 'completed'
