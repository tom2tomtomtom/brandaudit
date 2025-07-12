#!/usr/bin/env python3
"""
Test script for Professional Report Generation System
Tests all templates, themes, and export formats
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.presentation_service import ProfessionalPresentationService, ReportTemplate, ReportTheme

# Sample analysis data for testing
SAMPLE_ANALYSIS_DATA = {
    "key_metrics": {
        "overall_score": 78,
        "visual_score": 82,
        "market_score": 75,
        "sentiment_score": 80
    },
    "competitor_analysis": {
        "competitors_identified": {
            "competitors": [
                {
                    "name": "Apple",
                    "market_position": "Premium leader",
                    "threat_level": "High",
                    "competitive_strengths": ["Innovation", "Brand loyalty"]
                },
                {
                    "name": "Samsung",
                    "market_position": "Technology innovator",
                    "threat_level": "High",
                    "competitive_strengths": ["R&D", "Global reach"]
                },
                {
                    "name": "Google",
                    "market_position": "Software ecosystem",
                    "threat_level": "Medium",
                    "competitive_strengths": ["AI", "Data analytics"]
                }
            ]
        }
    },
    "visual_analysis": {
        "screenshots": {
            "homepage": "screenshot1.png",
            "products": "screenshot2.png",
            "about": "screenshot3.png"
        },
        "extracted_colors": {
            "primary_colors": [
                {"hex": "#1f4e79", "type": "primary"},
                {"hex": "#2e5984", "type": "secondary"},
                {"hex": "#4472a8", "type": "accent"}
            ]
        }
    },
    "actionable_insights": [
        {
            "finding": "Enhance visual brand consistency across digital touchpoints",
            "priority": "High",
            "timeline": "60 days",
            "impact": "High"
        },
        {
            "finding": "Strengthen competitive positioning in premium segment",
            "priority": "High",
            "timeline": "90 days",
            "impact": "Medium"
        },
        {
            "finding": "Optimize social media engagement strategy",
            "priority": "Medium",
            "timeline": "45 days",
            "impact": "Medium"
        },
        {
            "finding": "Implement comprehensive brand measurement framework",
            "priority": "Medium",
            "timeline": "120 days",
            "impact": "High"
        },
        {
            "finding": "Develop strategic partnership opportunities",
            "priority": "Low",
            "timeline": "180 days",
            "impact": "Medium"
        }
    ],
    "llm_analysis": {
        "insights": """
        ## Strategic Brand Assessment

        This comprehensive analysis reveals significant opportunities for brand enhancement and market positioning optimization. The brand demonstrates strong foundational elements with clear opportunities for strategic advancement.

        ### Key Strategic Findings

        **Brand Positioning**: The current market position shows strong potential with room for differentiation enhancement. Competitive analysis indicates opportunities for strategic positioning improvements.

        **Visual Identity**: Brand visual consistency demonstrates professional standards with opportunities for enhanced cohesion across digital touchpoints.

        **Market Opportunity**: Analysis reveals untapped market segments and strategic expansion possibilities that align with brand capabilities.

        ### Strategic Recommendations

        Priority initiatives should focus on brand differentiation, competitive response strategies, and market expansion opportunities that leverage existing brand strengths while addressing identified gaps.
        """
    },
    "data_sources": {
        "llm_analysis": True,
        "news_data": True,
        "brand_data": True,
        "visual_analysis": True,
        "competitor_analysis": True
    }
}

async def test_professional_report_generation():
    """Test the professional report generation system"""
    print("🚀 Testing Professional Report Generation System")
    print("=" * 60)
    
    # Initialize the service
    service = ProfessionalPresentationService()
    
    # Test brand name
    brand_name = "Tesla"
    
    # Get capabilities
    capabilities = service.get_capabilities()
    print(f"📊 Service Capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"   {status} {capability}")
    print()
    
    # Test all template and theme combinations
    templates_to_test = [
        ReportTemplate.EXECUTIVE_SUMMARY,
        ReportTemplate.DETAILED_ANALYSIS,
        ReportTemplate.PRESENTATION_DECK,
        ReportTemplate.CONSULTING_REPORT,
        ReportTemplate.STRATEGIC_BRIEF
    ]
    
    themes_to_test = [
        ReportTheme.CORPORATE_BLUE,
        ReportTheme.MODERN_MINIMAL,
        ReportTheme.CONSULTING_PREMIUM
    ]
    
    export_formats = ['pdf', 'html']
    if capabilities.get('powerpoint_generation'):
        export_formats.append('pptx')
    
    results = []
    
    for template in templates_to_test:
        for theme in themes_to_test:
            print(f"🎨 Testing: {template.value} with {theme.value}")
            
            try:
                result = await service.generate_professional_report(
                    brand_name=brand_name,
                    analysis_data=SAMPLE_ANALYSIS_DATA,
                    template=template,
                    theme=theme,
                    export_formats=export_formats
                )
                
                if result.get('errors'):
                    print(f"   ⚠️  Warnings: {len(result['errors'])} issues")
                    for error in result['errors'][:2]:  # Show first 2 errors
                        print(f"      - {error}")
                
                reports_generated = result.get('reports_generated', {})
                charts_generated = result.get('charts_generated', [])
                
                print(f"   📄 Reports: {len(reports_generated)} formats")
                print(f"   📊 Charts: {len(charts_generated)} visualizations")
                
                for format_type, report_data in reports_generated.items():
                    if report_data.get('success'):
                        file_size = report_data.get('file_size', 0)
                        print(f"      ✅ {format_type.upper()}: {report_data.get('filename')} ({file_size} bytes)")
                    else:
                        print(f"      ❌ {format_type.upper()}: {report_data.get('error', 'Unknown error')}")
                
                results.append({
                    'template': template.value,
                    'theme': theme.value,
                    'success': len(reports_generated) > 0,
                    'reports_count': len(reports_generated),
                    'charts_count': len(charts_generated),
                    'errors_count': len(result.get('errors', []))
                })
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                results.append({
                    'template': template.value,
                    'theme': theme.value,
                    'success': False,
                    'error': str(e)
                })
            
            print()
    
    # Test chart generation separately
    print("📊 Testing Chart Generation")
    print("-" * 30)
    
    try:
        charts = await service.generate_dynamic_charts(
            brand_name=brand_name,
            analysis_data=SAMPLE_ANALYSIS_DATA,
            theme=ReportTheme.CORPORATE_BLUE
        )
        
        print(f"✅ Generated {len(charts)} charts:")
        for chart in charts:
            print(f"   - {chart.get('title', 'Unknown')}: {chart.get('filename', 'No file')}")
    
    except Exception as e:
        print(f"❌ Chart generation failed: {str(e)}")
    
    print()
    
    # Summary
    print("📋 Test Summary")
    print("=" * 30)
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        avg_reports = sum(r.get('reports_count', 0) for r in results if r.get('success')) / successful_tests
        avg_charts = sum(r.get('charts_count', 0) for r in results if r.get('success')) / successful_tests
        print(f"📊 Average reports per test: {avg_reports:.1f}")
        print(f"📈 Average charts per test: {avg_charts:.1f}")
    
    # Show any failures
    failures = [r for r in results if not r.get('success', False)]
    if failures:
        print(f"\n❌ Failed Tests:")
        for failure in failures:
            print(f"   - {failure['template']} + {failure['theme']}: {failure.get('error', 'Unknown error')}")
    
    print(f"\n🎉 Professional Report Generation System Test Complete!")
    return results

if __name__ == "__main__":
    # Run the test
    results = asyncio.run(test_professional_report_generation())
    
    # Save results to file
    with open('test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)
    
    print(f"📁 Test results saved to test_results.json")
