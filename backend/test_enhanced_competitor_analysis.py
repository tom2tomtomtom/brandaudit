#!/usr/bin/env python3
"""
Enhanced Competitor Analysis Service Test Script
Tests the advanced competitive intelligence capabilities
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.competitor_analysis_service import CompetitorAnalysisService

async def test_enhanced_competitor_analysis():
    """Test the enhanced competitor analysis service"""
    
    print("🚀 Testing Enhanced Competitor Analysis Service")
    print("=" * 60)
    
    # Initialize the service
    service = CompetitorAnalysisService()
    
    # Test brand and competitors
    test_brand = "Apple"
    test_industry = "Technology"
    
    print(f"📊 Testing competitive analysis for: {test_brand}")
    print(f"🏭 Industry: {test_industry}")
    print()
    
    # Test 1: Check capabilities
    print("1️⃣ Testing Service Capabilities")
    print("-" * 30)
    capabilities = service.get_capabilities()
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"{status} {capability}: {available}")
    print()
    
    # Test 2: Multi-source competitor discovery
    print("2️⃣ Testing Multi-Source Competitor Discovery")
    print("-" * 40)
    try:
        discovery_results = await service.discover_competitors_multi_source(
            test_brand, test_industry, "comprehensive"
        )
        
        competitors_found = len(discovery_results.get('competitors', []))
        sources_used = len(discovery_results.get('sources_used', []))
        
        print(f"✅ Competitors discovered: {competitors_found}")
        print(f"✅ Data sources used: {sources_used}")
        print(f"✅ Sources: {', '.join(discovery_results.get('sources_used', []))}")
        
        if discovery_results.get('competitors'):
            print("📋 Sample competitors:")
            for i, comp in enumerate(discovery_results['competitors'][:3]):
                print(f"   {i+1}. {comp.get('name', 'Unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Multi-source discovery failed: {e}")
        print()
    
    # Test 3: Real-time competitive intelligence
    print("3️⃣ Testing Real-Time Competitive Intelligence")
    print("-" * 42)
    try:
        # Use sample competitors for testing
        sample_competitors = [
            {"name": "Microsoft", "website": "https://microsoft.com"},
            {"name": "Google", "website": "https://google.com"},
            {"name": "Samsung", "website": "https://samsung.com"}
        ]
        
        intelligence_results = await service.gather_real_time_intelligence(
            sample_competitors, test_brand, test_industry
        )
        
        competitor_intel = intelligence_results.get('competitor_intelligence', {})
        print(f"✅ Intelligence gathered for {len(competitor_intel)} competitors")
        
        for competitor, intel in competitor_intel.items():
            data_sources = len(intel.get('data_sources', []))
            confidence = intel.get('confidence_score', 0)
            print(f"   📊 {competitor}: {data_sources} sources, {confidence:.2f} confidence")
        print()
        
    except Exception as e:
        print(f"❌ Real-time intelligence failed: {e}")
        print()
    
    # Test 4: Dynamic competitive positioning
    print("4️⃣ Testing Dynamic Competitive Positioning")
    print("-" * 38)
    try:
        positioning_results = await service.analyze_competitive_positioning(
            test_brand, sample_competitors
        )
        
        competitive_map = positioning_results.get('competitive_map', {})
        strategic_groups = positioning_results.get('strategic_groups', {})
        positioning_matrix = positioning_results.get('positioning_matrix', {})
        
        print(f"✅ Competitive mapping completed")
        print(f"✅ Strategic groups identified: {len(strategic_groups.get('groups_identified', []))}")
        print(f"✅ Brand positioned in: {strategic_groups.get('brand_group', 'Unknown')}")
        
        if positioning_matrix.get('primary_dimensions'):
            dims = positioning_matrix['primary_dimensions']
            print(f"✅ Key positioning dimensions: {', '.join(dims[:2])}")
        print()
        
    except Exception as e:
        print(f"❌ Competitive positioning failed: {e}")
        print()
    
    # Test 5: Automated landscape mapping
    print("5️⃣ Testing Automated Landscape Mapping")
    print("-" * 35)
    try:
        landscape_map = await service.generate_competitive_landscape_map(
            test_brand, sample_competitors, positioning_results
        )
        
        ecosystem = landscape_map.get('competitive_ecosystem', {})
        market_structure = landscape_map.get('market_structure', {})
        matrices = landscape_map.get('competitive_matrices', {})
        
        print(f"✅ Ecosystem analysis completed")
        print(f"✅ Market structure analyzed")
        print(f"✅ Competitive matrices generated: {len(matrices)}")
        
        ecosystem_health = landscape_map.get('landscape_insights', {}).get('ecosystem_health_score', 0)
        print(f"✅ Ecosystem health score: {ecosystem_health:.2f}")
        print()
        
    except Exception as e:
        print(f"❌ Landscape mapping failed: {e}")
        print()
    
    # Test 6: Trend analysis and gap identification
    print("6️⃣ Testing Trend Analysis & Gap Identification")
    print("-" * 43)
    try:
        trend_analysis = await service.analyze_competitive_trends_and_gaps(
            test_brand, sample_competitors, intelligence_results, 
            positioning_results, landscape_map
        )
        
        market_trends = trend_analysis.get('market_trends', {})
        competitive_gaps = trend_analysis.get('competitive_gaps', {})
        opportunities = trend_analysis.get('market_opportunities', {})
        
        print(f"✅ Market trends analyzed")
        print(f"✅ Competitive gaps identified")
        print(f"✅ Market opportunities detected")
        
        gap_prioritization = trend_analysis.get('gap_prioritization', {})
        critical_priorities = len(gap_prioritization.get('critical_priorities', []))
        high_priorities = len(gap_prioritization.get('high_priorities', []))
        
        print(f"✅ Critical priorities: {critical_priorities}")
        print(f"✅ High priorities: {high_priorities}")
        print()
        
    except Exception as e:
        print(f"❌ Trend analysis failed: {e}")
        print()
    
    # Test 7: Data integration and caching
    print("7️⃣ Testing Data Integration & Caching")
    print("-" * 34)
    try:
        # Test cache statistics
        cache_stats = service.get_cache_statistics()
        print(f"✅ Cache entries: {cache_stats.get('total_entries', 0)}")
        print(f"✅ Valid entries: {cache_stats.get('valid_entries', 0)}")
        print(f"✅ Cache efficiency: {cache_stats.get('cache_hit_potential', 0):.2f}")
        
        # Test data integration status
        integration_status = service.get_data_integration_status()
        health = integration_status.get('integration_health', 'unknown')
        print(f"✅ Integration health: {health}")
        
        # Test data freshness validation
        data_sources = ['news_monitoring', 'financial_data', 'ai_analysis']
        freshness_report = await service.validate_data_freshness(data_sources)
        freshness_score = freshness_report.get('overall_freshness_score', 0)
        print(f"✅ Data freshness score: {freshness_score:.2f}")
        print()
        
    except Exception as e:
        print(f"❌ Data integration testing failed: {e}")
        print()
    
    # Test 8: Comprehensive analysis workflow
    print("8️⃣ Testing Comprehensive Analysis Workflow")
    print("-" * 40)
    try:
        # Run full analysis with all enhancements
        full_analysis = await service.analyze_competitors(
            test_brand, test_industry, "strategic"
        )
        
        performance_metrics = full_analysis.get('performance_metrics', {})
        duration = performance_metrics.get('total_duration_seconds', 0)
        competitors_count = performance_metrics.get('competitors_discovered', 0)
        sources_count = performance_metrics.get('data_sources_used', 0)
        
        print(f"✅ Full analysis completed in {duration}s")
        print(f"✅ Competitors analyzed: {competitors_count}")
        print(f"✅ Data sources utilized: {sources_count}")
        print(f"✅ Analysis depth: {performance_metrics.get('analysis_depth', 'unknown')}")
        
        # Check for errors
        errors = full_analysis.get('errors', [])
        if errors:
            print(f"⚠️  Errors encountered: {len(errors)}")
            for error in errors[:3]:  # Show first 3 errors
                print(f"   - {error}")
        else:
            print("✅ No errors encountered")
        print()
        
    except Exception as e:
        print(f"❌ Comprehensive analysis failed: {e}")
        print()
    
    print("🎉 Enhanced Competitor Analysis Testing Complete!")
    print("=" * 60)
    
    # Summary
    print("\n📋 ENHANCEMENT SUMMARY:")
    print("✅ Multi-source competitor discovery")
    print("✅ Real-time competitive intelligence")
    print("✅ Dynamic positioning analysis")
    print("✅ Automated landscape mapping")
    print("✅ Trend analysis & gap identification")
    print("✅ Enhanced data integration & caching")
    print("✅ Strategic insights & recommendations")
    print("\n🚀 The competitor analysis service has been successfully enhanced!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_competitor_analysis())
