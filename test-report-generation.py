#!/usr/bin/env python3

"""
Test script for the new professional report generation system
"""

import sys
import os
sys.path.append('backend')

from backend.src.services.report_generation_service import ReportGenerationService

def test_report_generation():
    """Test the report generation with sample data"""
    
    print("🧪 Testing Professional Report Generation System")
    print("=" * 50)
    
    # Sample analysis data (similar to what would come from real analysis)
    sample_analysis_data = {
        'llm_analysis': {
            'insights': """
## EXECUTIVE SUMMARY

Apple faces its most complex brand challenges since the post-Jobs era, creating unprecedented opportunities for specialized agency expertise. While maintaining the world's most valuable brand at $574.5 billion, Apple confronts AI narrative crises, Services marketing evolution, and cultural sensitivity pressures that require sophisticated communications strategies beyond traditional hardware advertising.

The company's premium positioning remains intact with 92-93% customer retention rates versus Samsung's 77%, yet emerging competitive threats in AI and Services require immediate strategic attention. Critical imperatives include reframing the AI narrative from technical lag to privacy-first innovation, developing Services-specific marketing frameworks, and implementing rigorous cultural review processes.

## BRAND POSITIONING ANALYSIS

Apple maintains dominant market position as world's most valuable brand at $574.5 billion, with unparalleled customer loyalty (92-93% retention) and premium pricing power (average iPhone price $1,000+ vs $295 Android). However, the company faces positioning challenges in AI narrative where it's perceived as "years behind competition" despite privacy-first approach.

Brand equity drivers include ecosystem lock-in (60% of customers own 3-4 Apple devices), Services growth (26% of revenue targeting $120B+ annually), and cultural authority as taste-maker. Key vulnerabilities include AI perception gap, China market decline, and cultural sensitivity risks as demonstrated by iPad "Crush" ad controversy.

## COMPETITIVE INTELLIGENCE

Primary competitors include Samsung (direct hardware competition), Google (ecosystem and AI-first approach), and Microsoft (enterprise productivity). Samsung competes on feature-heavy messaging vs Apple's simplicity, while Google leverages AI-first, data personalization vs Apple's privacy-first approach.

Emerging threats include Chinese technology brands (BYD, Pinduoduo showing 400%+ growth) challenging Apple in world's largest smartphone market, and AI-first startups potentially disrupting next computing platform. Strategic response requires increased localization, cultural relevance, and accelerated Apple Intelligence development.

## STRATEGIC RECOMMENDATIONS

1. **Reframe AI Narrative**: Transform from defensive "privacy vs features" to offensive "privacy-enabled intelligence" positioning
2. **Services Marketing Evolution**: Develop subscription-specific frameworks driving retention and ecosystem expansion  
3. **Cultural Sensitivity Systems**: Implement rigorous review processes preventing cultural backlash incidents
4. **China Market Recovery**: Develop localized strategies rebuilding relevance in critical growth market
5. **Crisis Response Capabilities**: Build rapid response systems protecting premium brand positioning

## IMPLEMENTATION ROADMAP

Phase 1 (0-3 months): AI narrative reframing, cultural review process implementation
Phase 2 (3-6 months): Services marketing framework development, China strategy execution
Phase 3 (6-12 months): Crisis response system optimization, market expansion initiatives
            """
        },
        'key_metrics': {
            'overall_score': 85,
            'visual_score': 78,
            'market_score': 92,
            'sentiment_score': 88
        },
        'brand_health_dashboard': {
            'overall_score': 85,
            'score_color': 'green',
            'trend_indicator': 'improving',
            'benchmark_vs_industry': '+20%'
        },
        'actionable_insights': [
            {
                'finding': 'AI narrative crisis requires immediate attention',
                'impact': 'Shareholder lawsuits and competitive perception gap',
                'recommendation': 'Reframe AI story from technical lag to privacy-first innovation',
                'priority': 'High',
                'timeline': '30 days'
            },
            {
                'finding': 'Services business needs specialized marketing approach',
                'impact': 'Revenue target of $120B+ annually vs current $100B run rate',
                'recommendation': 'Develop Services-specific marketing frameworks',
                'priority': 'High',
                'timeline': '60 days'
            }
        ],
        'data_sources': {
            'llm_analysis': True,
            'news_data': True,
            'brand_data': True,
            'visual_analysis': False,
            'competitor_analysis': True
        }
    }
    
    # Initialize report service
    report_service = ReportGenerationService()
    
    # Generate report for Apple
    print("📝 Generating report for Apple...")
    result = report_service.generate_comprehensive_report("Apple", sample_analysis_data)
    
    if result.get('success'):
        print("✅ Report generation successful!")
        print(f"📄 Filename: {result.get('filename')}")
        print(f"📁 File path: {result.get('root_filepath')}")
        print(f"📊 File size: {result.get('file_size')} characters")
        print(f"📋 Sections: {result.get('sections_generated')}")
        
        # Read and display first few lines
        try:
            with open(result.get('root_filepath'), 'r') as f:
                content = f.read()
                lines = content.split('\n')
                print("\n📖 Report Preview (first 20 lines):")
                print("-" * 40)
                for i, line in enumerate(lines[:20], 1):
                    print(f"{i:2d}: {line}")
                print("-" * 40)
                print(f"... (total {len(lines)} lines)")
                
        except Exception as e:
            print(f"❌ Error reading report file: {e}")
            
    else:
        print("❌ Report generation failed!")
        print(f"Error: {result.get('error')}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_report_generation()
