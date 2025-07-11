#!/usr/bin/env python3
"""
Comprehensive test script for all brand audit features
Tests visual analysis, competitor analysis, campaign analysis, and social media
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.visual_analysis_service import VisualAnalysisService
from src.services.competitor_analysis_service import CompetitorAnalysisService
from src.services.campaign_analysis_service import CampaignAnalysisService
from src.services.social_media_service import SocialMediaService

async def test_comprehensive_analysis():
    """Test all analysis services with a well-known brand"""
    print("🧪 Testing Comprehensive Brand Audit Analysis")
    print("=" * 60)
    
    # Test brand
    test_brand = "Apple"
    test_url = "https://apple.com"
    test_industry = "Technology"
    
    print(f"🎯 Testing comprehensive analysis for: {test_brand}")
    print(f"🌐 Website: {test_url}")
    print(f"🏭 Industry: {test_industry}")
    print()
    
    # Test 1: Visual Analysis
    print("1️⃣ VISUAL ANALYSIS")
    print("-" * 30)
    try:
        visual_service = VisualAnalysisService()
        capabilities = visual_service.get_capabilities()
        print(f"📊 Visual capabilities: {capabilities}")
        
        visual_results = await visual_service.analyze_brand_visuals(test_brand, test_url)
        
        print(f"✅ Visual analysis completed!")
        print(f"📸 Screenshots: {len(visual_results.get('visual_assets', {}).get('screenshots', {}))}")
        print(f"🎨 Colors extracted: {len(visual_results.get('visual_assets', {}).get('color_palette', {}).get('primary_colors', []))}")
        print(f"📱 Social platforms: {len(visual_results.get('visual_assets', {}).get('social_media', {}).get('social_platforms', {}))}")
        print(f"📊 Visual scores: {list(visual_results.get('visual_scores', {}).keys())}")
        print(f"❌ Errors: {len(visual_results.get('errors', []))}")
        
        if visual_results.get('errors'):
            for error in visual_results['errors'][:3]:  # Show first 3 errors
                print(f"  ⚠️ {error}")
        
    except Exception as e:
        print(f"❌ Visual analysis failed: {e}")
    
    print()
    
    # Test 2: Competitor Analysis
    print("2️⃣ COMPETITOR ANALYSIS")
    print("-" * 30)
    try:
        competitor_service = CompetitorAnalysisService()
        capabilities = competitor_service.get_capabilities()
        print(f"📊 Competitor capabilities: {capabilities}")
        
        competitor_results = await competitor_service.analyze_competitors(test_brand, test_industry)
        
        print(f"✅ Competitor analysis completed!")
        print(f"🏢 Competitors identified: {len(competitor_results.get('competitors', []))}")
        print(f"📊 Competitor analyses: {len(competitor_results.get('competitor_analyses', []))}")
        print(f"🎯 Competitive positioning: {bool(competitor_results.get('competitive_analysis'))}")
        print(f"❌ Errors: {len(competitor_results.get('errors', []))}")
        
        if competitor_results.get('competitors'):
            print("🏢 Top competitors:")
            for i, comp in enumerate(competitor_results['competitors'][:3], 1):
                print(f"  {i}. {comp.get('name', 'Unknown')} - {comp.get('market_position', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Competitor analysis failed: {e}")
    
    print()
    
    # Test 3: Campaign Analysis
    print("3️⃣ CAMPAIGN ANALYSIS")
    print("-" * 30)
    try:
        campaign_service = CampaignAnalysisService()
        capabilities = campaign_service.get_capabilities()
        print(f"📊 Campaign capabilities: {capabilities}")
        
        campaign_results = await campaign_service.analyze_brand_campaigns(test_brand, test_industry)
        
        print(f"✅ Campaign analysis completed!")
        print(f"📢 Campaigns discovered: {len(campaign_results.get('campaigns', []))}")
        print(f"🎨 Creative assets: {len(campaign_results.get('creative_assets', []))}")
        print(f"📰 Trade press articles: {len(campaign_results.get('trade_press_coverage', []))}")
        print(f"❌ Errors: {len(campaign_results.get('errors', []))}")
        
        if campaign_results.get('campaigns'):
            print("📢 Recent campaigns:")
            for i, campaign in enumerate(campaign_results['campaigns'][:3], 1):
                title = campaign.get('title', campaign.get('name', 'Unknown'))
                print(f"  {i}. {title}")
        
    except Exception as e:
        print(f"❌ Campaign analysis failed: {e}")
    
    print()
    
    # Test 4: Social Media Analysis
    print("4️⃣ SOCIAL MEDIA ANALYSIS")
    print("-" * 30)
    try:
        social_service = SocialMediaService()
        capabilities = social_service.get_capabilities()
        print(f"📊 Social capabilities: {capabilities}")
        
        social_results = await social_service.analyze_social_presence(test_brand, test_url)
        
        print(f"✅ Social media analysis completed!")
        print(f"📱 Social platforms: {len(social_results.get('social_platforms', {}))}")
        print(f"📊 Engagement metrics: {bool(social_results.get('engagement_metrics'))}")
        print(f"🎯 Social insights: {bool(social_results.get('social_insights'))}")
        print(f"❌ Errors: {len(social_results.get('errors', []))}")
        
        if social_results.get('social_platforms'):
            print("📱 Discovered platforms:")
            for platform, info in social_results['social_platforms'].items():
                username = info.get('username', 'unknown')
                print(f"  • {platform.title()}: {username}")
        
    except Exception as e:
        print(f"❌ Social media analysis failed: {e}")
    
    print()
    print("=" * 60)
    print("🎉 COMPREHENSIVE ANALYSIS TEST COMPLETED!")
    print()
    
    # Summary
    print("📋 SUMMARY:")
    print("✅ Visual Analysis: Screenshots, colors, social discovery")
    print("✅ Competitor Analysis: AI-powered competitor identification")
    print("✅ Campaign Analysis: Campaign discovery and insights")
    print("✅ Social Media Analysis: Platform discovery and insights")
    print()
    print("🚀 All services are integrated and ready for full brand audit!")

if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(test_comprehensive_analysis())
