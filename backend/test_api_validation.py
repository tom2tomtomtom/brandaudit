#!/usr/bin/env python3
"""
Test script for API validation system
"""
import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.api_validation_service import api_validator
from src.services.llm_service import llm_service
from src.services.news_service import news_service
from src.services.brand_data_service import brand_data_service


def test_api_health_checks():
    """Test API health checks"""
    print("🔍 Testing API Health Checks...")
    print("=" * 50)
    
    # Test individual API health checks
    for api_name in ['openrouter', 'newsapi', 'brandfetch']:
        print(f"\n📊 Checking {api_name.upper()} API health...")
        try:
            health = api_validator.validate_api_connectivity(api_name, force_check=True)
            print(f"   Status: {health.status.value}")
            print(f"   Last Check: {health.last_check}")
            if health.response_time_ms:
                print(f"   Response Time: {health.response_time_ms:.1f}ms")
            if health.error_message:
                print(f"   Error: {health.error_message}")
            print(f"   Consecutive Failures: {health.consecutive_failures}")
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
    
    print("\n" + "=" * 50)


def test_system_health_summary():
    """Test system health summary"""
    print("🏥 Testing System Health Summary...")
    print("=" * 50)
    
    try:
        summary = api_validator.get_system_health_summary()
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Healthy APIs: {summary['healthy_apis']}/{summary['total_apis']}")
        
        print("\nAPI Health Details:")
        for api_name, health in summary['api_health'].items():
            print(f"  {api_name}: {health['status']} (Key: {'✓' if health['api_key_configured'] else '✗'})")
        
        print("\nMonitoring Summary:")
        for api_name, metrics in summary['monitoring_summary'].items():
            print(f"  {api_name}:")
            print(f"    Total Requests: {metrics['total_requests']}")
            print(f"    Success Rate: {metrics['success_rate']:.1f}%")
            print(f"    Avg Response Time: {metrics['avg_response_time']:.1f}ms")
            if metrics['active_alerts']:
                print(f"    Active Alerts: {', '.join(metrics['active_alerts'])}")
        
    except Exception as e:
        print(f"❌ System health summary failed: {e}")
    
    print("\n" + "=" * 50)


def test_service_integration():
    """Test service integration with validation"""
    print("🔧 Testing Service Integration...")
    print("=" * 50)
    
    # Test LLM Service
    print("\n🤖 Testing LLM Service...")
    try:
        result = llm_service.analyze_brand_sentiment("Apple is a great company with innovative products.", "Apple")
        if result['success']:
            print("   ✅ LLM service working with real API")
        else:
            print(f"   ❌ LLM service failed: {result['error']}")
    except Exception as e:
        print(f"   ❌ LLM service error: {e}")
    
    # Test News Service
    print("\n📰 Testing News Service...")
    try:
        result = news_service.search_news("Apple", days_back=7)
        if result['success']:
            print(f"   ✅ News service working - found {result['total_results']} articles")
        else:
            print(f"   ❌ News service failed: {result['error']}")
    except Exception as e:
        print(f"   ❌ News service error: {e}")
    
    # Test Brand Data Service
    print("\n🏢 Testing Brand Data Service...")
    try:
        result = brand_data_service.get_brand_assets("apple.com")
        if result['success']:
            print("   ✅ Brand data service working with real API")
        else:
            print(f"   ❌ Brand data service failed: {result['error']}")
    except Exception as e:
        print(f"   ❌ Brand data service error: {e}")
    
    print("\n" + "=" * 50)


def test_monitoring_data():
    """Test monitoring data collection"""
    print("📈 Testing Monitoring Data...")
    print("=" * 50)
    
    try:
        monitoring_data = api_validator.get_monitoring_data()
        
        for api_name, data in monitoring_data.items():
            print(f"\n{api_name.upper()} Metrics:")
            metrics = data['metrics']
            print(f"  Total Requests: {metrics['total_requests']}")
            print(f"  Successful Requests: {metrics['successful_requests']}")
            print(f"  Failed Requests: {metrics['failed_requests']}")
            print(f"  Average Response Time: {metrics['avg_response_time_ms']:.1f}ms")
            print(f"  24h Requests: {metrics['last_24h_requests']}")
            print(f"  24h Failures: {metrics['last_24h_failures']}")
            print(f"  Uptime: {metrics['uptime_percentage']:.1f}%")
            
            if data['alerts_active']:
                print(f"  Active Alerts: {', '.join(data['alerts_active'])}")
    
    except Exception as e:
        print(f"❌ Monitoring data test failed: {e}")
    
    print("\n" + "=" * 50)


def main():
    """Run all tests"""
    print("🚀 API Validation System Test Suite")
    print("=" * 50)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Check environment variables
    print("\n🔑 API Key Configuration:")
    apis = {
        'OpenRouter': 'OPENROUTER_API_KEY',
        'NewsAPI': 'NEWS_API_KEY', 
        'BrandFetch': 'BRANDFETCH_API_KEY'
    }
    
    for api_name, env_var in apis.items():
        key_configured = bool(os.getenv(env_var))
        print(f"  {api_name}: {'✅ Configured' if key_configured else '❌ Not Configured'}")
    
    print("\n" + "=" * 50)
    
    # Run tests
    test_api_health_checks()
    test_system_health_summary()
    test_service_integration()
    test_monitoring_data()
    
    print("✅ Test suite completed!")
    print("\nNote: This validation system ensures NO FAKE DATA is ever returned.")
    print("All services will fail gracefully if APIs are unavailable, maintaining data authenticity.")


if __name__ == "__main__":
    main()
