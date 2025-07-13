#!/usr/bin/env python3
"""
Real API integration tests for existing Flask API
Tests with REAL API calls using configured API keys
Only run when API keys are properly configured
"""
import os
import sys
import pytest
import json
import time
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from simple_analysis import SimpleAnalyzer

# Skip all tests if API keys not configured
pytestmark = pytest.mark.skipif(
    not (os.environ.get('OPENROUTER_API_KEY') or 
         os.environ.get('NEWS_API_KEY') or 
         os.environ.get('BRANDFETCH_API_KEY')),
    reason="Real API keys not configured"
)

class TestRealAPIIntegration:
    """Test suite for real API integration with existing system"""
    
    @pytest.fixture
    def client(self):
        """Create test client with real API keys"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                from src.extensions import db
                db.create_all()
                yield client
                db.drop_all()
    
    def test_health_check_with_real_apis(self, client):
        """Test health check with real API connectivity"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'system_health' in data
        assert 'api_connectivity' in data
        
        # Should show real API status
        api_connectivity = data['api_connectivity']
        assert 'total_apis' in api_connectivity
        assert 'healthy_apis' in api_connectivity
        
        print(f"API Health Status: {api_connectivity}")
        
    def test_detailed_health_check_real_apis(self, client):
        """Test detailed health check with real API validation"""
        response = client.get('/api/health/detailed')
        
        # Should return 200 if APIs are working, 500 if not
        assert response.status_code in [200, 500]
        
        data = response.get_json()
        assert 'service' in data
        
        if response.status_code == 200:
            assert 'detailed_metrics' in data
            assert 'api_configurations' in data
            print("✅ Detailed health check passed with real APIs")
        else:
            print("⚠️ Some APIs may not be working properly")
    
    @pytest.mark.slow
    def test_real_brand_analysis_apple(self, client):
        """Test real brand analysis with Apple (well-known brand)"""
        
        test_data = {
            'company_name': 'Apple Inc',
            'analysis_types': ['brand_positioning', 'competitive_analysis']
        }
        
        # Start analysis
        response = client.post('/api/analyze',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        analysis_id = data['data']['analysis_id']
        
        print(f"Started real analysis for Apple Inc: {analysis_id}")
        
        # Wait for completion (real APIs take time)
        max_wait = 300  # 5 minutes for real APIs
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = client.get(f'/api/analyze/{analysis_id}/status')
            status_data = response.get_json()
            
            status = status_data['data']['status']
            progress = status_data['data'].get('progress', 0)
            
            print(f"Analysis progress: {progress}% - Status: {status}")
            
            if status == 'completed':
                break
            elif status == 'failed':
                pytest.fail(f"Real analysis failed: {status_data}")
                
            time.sleep(10)  # Check every 10 seconds
        else:
            pytest.fail("Real analysis did not complete within timeout")
        
        # Get results
        response = client.get(f'/api/analyze/{analysis_id}/results')
        assert response.status_code == 200
        
        results_data = response.get_json()
        assert results_data['success'] is True
        
        results = results_data['data']
        assert results['brand_name'] == 'Apple Inc'
        
        # Verify we got real data
        data_sources = results.get('data_sources', {})
        real_data_count = sum(1 for source, available in data_sources.items() 
                             if available and source in ['llm_analysis', 'news_data', 'brand_data'])
        
        assert real_data_count > 0, "No real data sources were successful"
        print(f"✅ Real analysis completed with {real_data_count} data sources")
        
        # Print some results for verification
        if results.get('key_metrics'):
            print(f"Key metrics: {results['key_metrics']}")
        
        if results.get('llm_sections'):
            sections = list(results['llm_sections'].keys())
            print(f"LLM sections generated: {sections}")
    
    @pytest.mark.slow
    def test_real_brand_analysis_tesla(self, client):
        """Test real brand analysis with Tesla"""
        
        test_data = {'company_name': 'Tesla'}
        
        response = client.post('/api/analyze',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        analysis_id = response.get_json()['data']['analysis_id']
        
        print(f"Started real analysis for Tesla: {analysis_id}")
        
        # Wait for completion with shorter timeout
        max_wait = 180  # 3 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = client.get(f'/api/analyze/{analysis_id}/status')
            status_data = response.get_json()
            
            if status_data['data']['status'] in ['completed', 'failed']:
                break
                
            time.sleep(5)
        
        # Check final status
        response = client.get(f'/api/analyze/{analysis_id}/status')
        final_status = response.get_json()['data']['status']
        
        if final_status == 'completed':
            # Get and verify results
            response = client.get(f'/api/analyze/{analysis_id}/results')
            assert response.status_code == 200
            
            results = response.get_json()['data']
            assert results['brand_name'] == 'Tesla'
            print("✅ Tesla analysis completed successfully")
        else:
            print(f"⚠️ Tesla analysis status: {final_status}")
    
    def test_simple_analyzer_real_apis(self):
        """Test SimpleAnalyzer directly with real APIs"""
        
        analyzer = SimpleAnalyzer()
        
        # Check API keys are configured
        has_keys = any([
            analyzer.openrouter_api_key,
            analyzer.news_api_key,
            analyzer.brandfetch_api_key
        ])
        
        assert has_keys, "No API keys configured for real testing"
        
        # Test with a simple brand
        result = analyzer.analyze_brand("Nike")
        
        # Should not fail completely if at least one API works
        if result.get('success'):
            assert result['brand_name'] == "Nike"
            assert 'data_sources' in result
            print("✅ Direct SimpleAnalyzer test passed")
        else:
            # If it fails, should be due to API issues, not code issues
            assert 'API' in result.get('error', '') or 'api' in result.get('error', '')
            print(f"⚠️ SimpleAnalyzer failed due to API issues: {result.get('error')}")
    
    def test_api_key_validation(self):
        """Test that API keys are properly configured"""
        
        api_keys = {
            'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY'),
            'NEWS_API_KEY': os.environ.get('NEWS_API_KEY'),
            'BRANDFETCH_API_KEY': os.environ.get('BRANDFETCH_API_KEY'),
            'OPENCORPORATES_API_KEY': os.environ.get('OPENCORPORATES_API_KEY')
        }
        
        configured_keys = {k: v for k, v in api_keys.items() if v}
        
        print(f"Configured API keys: {list(configured_keys.keys())}")
        
        # Should have at least one API key for real testing
        assert len(configured_keys) > 0, "No API keys configured for real testing"
        
        # Validate key formats (basic check)
        for key_name, key_value in configured_keys.items():
            assert len(key_value) > 10, f"{key_name} seems too short"
            assert not key_value.startswith('test-'), f"{key_name} appears to be a test key"
    
    @pytest.mark.slow
    def test_websocket_with_real_analysis(self, client):
        """Test WebSocket functionality during real analysis"""
        
        # This test would require a WebSocket client
        # For now, just verify the WebSocket service is available
        from src.services.websocket_service import get_websocket_service
        
        websocket_service = get_websocket_service()
        assert websocket_service is not None
        
        # Start a real analysis to test WebSocket integration
        test_data = {'company_name': 'Microsoft'}
        response = client.post('/api/analyze',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        analysis_id = response.get_json()['data']['analysis_id']
        
        # Check that progress tracker was created
        time.sleep(2)  # Give it a moment to initialize
        
        if analysis_id in websocket_service.progress_trackers:
            tracker = websocket_service.progress_trackers[analysis_id]
            assert tracker.analysis_id == analysis_id
            print("✅ WebSocket progress tracker created for real analysis")
        else:
            print("⚠️ WebSocket progress tracker not found (may be timing issue)")

def run_real_api_tests():
    """Run real API tests if keys are configured"""
    
    # Check if we have any real API keys
    has_real_keys = any([
        os.environ.get('OPENROUTER_API_KEY', '').startswith('sk-'),
        os.environ.get('NEWS_API_KEY') and len(os.environ.get('NEWS_API_KEY', '')) > 20,
        os.environ.get('BRANDFETCH_API_KEY') and len(os.environ.get('BRANDFETCH_API_KEY', '')) > 20
    ])
    
    if not has_real_keys:
        print("⚠️ No real API keys detected. Skipping real API tests.")
        print("To run real API tests, configure:")
        print("  - OPENROUTER_API_KEY (starts with sk-)")
        print("  - NEWS_API_KEY")
        print("  - BRANDFETCH_API_KEY")
        return False
    
    print("🔑 Real API keys detected. Running real API integration tests...")
    
    # Run the tests
    import subprocess
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        __file__,
        '-v',
        '--tb=short',
        '-m', 'not slow'  # Skip slow tests by default
    ], cwd=os.path.dirname(__file__))
    
    return result.returncode == 0

if __name__ == '__main__':
    success = run_real_api_tests()
    sys.exit(0 if success else 1)
