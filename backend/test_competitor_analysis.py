#!/usr/bin/env python3
"""
Test script for competitor analysis functionality
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.competitor_analysis_service import CompetitorAnalysisService

async def test_competitor_analysis():
    """Test competitor analysis with a simple brand"""
    print("🧪 Testing Competitor Analysis Service")
    
    # Initialize the service
    service = CompetitorAnalysisService()
    
    # Check capabilities
    capabilities = service.get_capabilities()
    print(f"📊 Available capabilities: {capabilities}")
    
    # Test with a well-known brand
    test_brand = "Apple"
    test_industry = "Technology"
    
    print(f"🔍 Testing competitor analysis for {test_brand} in {test_industry}")
    
    try:
        results = await service.analyze_competitors(test_brand, test_industry)
        
        print(f"✅ Analysis completed!")
        print(f"🏢 Competitors identified: {len(results.get('competitors', []))}")
        print(f"📊 Competitor analyses: {len(results.get('competitor_analyses', []))}")
        print(f"🎯 Competitive positioning: {bool(results.get('competitive_analysis'))}")
        print(f"❌ Errors: {len(results.get('errors', []))}")
        
        if results.get('competitors'):
            print("\n🏢 Identified Competitors:")
            for i, comp in enumerate(results['competitors'][:3], 1):
                print(f"  {i}. {comp.get('name', 'Unknown')} - {comp.get('market_position', 'Unknown position')}")
        
        if results.get('errors'):
            print("\n⚠️ Errors encountered:")
            for error in results['errors']:
                print(f"  - {error}")
        
        return results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    # Run the test
    results = asyncio.run(test_competitor_analysis())
    
    if results and results.get('competitors'):
        print("\n🎉 Competitor analysis test completed successfully!")
        print("✅ Competitor identification is working and ready for integration")
    else:
        print("\n❌ Competitor analysis test failed")
        print("⚠️ Check API keys and configuration")
