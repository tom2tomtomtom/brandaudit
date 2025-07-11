#!/usr/bin/env python3
"""
Test script for campaign analysis functionality
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.campaign_analysis_service import CampaignAnalysisService

async def test_campaign_analysis():
    """Test campaign analysis with a well-known brand"""
    print("🧪 Testing Campaign Analysis Service")
    
    # Initialize the service
    service = CampaignAnalysisService()
    
    # Check capabilities
    capabilities = service.get_capabilities()
    print(f"📊 Available capabilities: {capabilities}")
    
    # Test with a brand known for campaigns
    test_brand = "Nike"
    test_industry = "Sports & Apparel"
    
    print(f"🔍 Testing campaign analysis for {test_brand} in {test_industry}")
    
    try:
        results = await service.analyze_brand_campaigns(test_brand, test_industry)
        
        print(f"✅ Analysis completed!")
        print(f"📢 Campaigns discovered: {len(results.get('campaigns', []))}")
        print(f"🎨 Creative assets: {len(results.get('creative_assets', []))}")
        print(f"📰 Trade press articles: {len(results.get('trade_press_coverage', []))}")
        print(f"🎯 Advertising insights: {bool(results.get('advertising_research'))}")
        print(f"❌ Errors: {len(results.get('errors', []))}")
        
        if results.get('campaigns'):
            print("\n📢 Discovered Campaigns:")
            for i, campaign in enumerate(results['campaigns'][:3], 1):
                title = campaign.get('title', campaign.get('name', 'Unknown'))
                campaign_type = campaign.get('campaign_type', 'unknown')
                print(f"  {i}. {title} ({campaign_type})")
        
        if results.get('trade_press_coverage'):
            print(f"\n📰 Trade Press Coverage:")
            for i, article in enumerate(results['trade_press_coverage'][:3], 1):
                print(f"  {i}. {article.get('title', 'Unknown')} - {article.get('source', 'Unknown source')}")
        
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
    results = asyncio.run(test_campaign_analysis())
    
    if results and (results.get('campaigns') or results.get('trade_press_coverage')):
        print("\n🎉 Campaign analysis test completed successfully!")
        print("✅ Campaign discovery is working and ready for integration")
    else:
        print("\n❌ Campaign analysis test failed")
        print("⚠️ Check API keys and configuration")
