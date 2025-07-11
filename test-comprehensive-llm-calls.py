#!/usr/bin/env python3

"""
Test script for comprehensive LLM calls that deliver substantial content
"""

import sys
import os
sys.path.append('backend')

from backend.src.services.llm_service import LLMService

def test_comprehensive_llm_calls():
    """Test the enhanced LLM service with comprehensive content requirements"""
    
    print("🧠 Testing Comprehensive LLM Calls for Professional Content")
    print("=" * 65)
    print("Testing all enhanced prompts to ensure substantial, consulting-grade responses")
    print("")
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test data for Apple
    sample_brand_data = {
        'name': 'Apple',
        'industry': 'Technology',
        'description': 'Consumer electronics and software company',
        'founded': '1976',
        'website': 'apple.com',
        'news_articles': [
            {'title': 'Apple announces new AI features', 'content': 'Apple Intelligence...'},
            {'title': 'iPhone sales in China decline', 'content': 'Market challenges...'}
        ],
        'social_mentions': 1500000
    }
    
    print("📊 Testing Brand Insights Generation...")
    print("-" * 40)
    
    # Test 1: Brand Insights Generation
    insights_result = llm_service.generate_brand_insights(sample_brand_data)
    
    if insights_result.get('success'):
        insights_content = insights_result.get('insights', '')
        insights_length = len(insights_content)
        
        print(f"✅ Brand insights generated successfully")
        print(f"📏 Content length: {insights_length} characters")
        
        # Quality assessment
        if insights_length >= 2000:
            print("🎉 EXCELLENT: Comprehensive content (2000+ chars)")
        elif insights_length >= 1500:
            print("✅ GOOD: Substantial content (1500+ chars)")
        elif insights_length >= 1000:
            print("⚠️ FAIR: Moderate content (1000+ chars)")
        else:
            print("❌ POOR: Insufficient content (<1000 chars)")
        
        # Check for key sections
        has_exec_summary = "EXECUTIVE SUMMARY" in insights_content
        has_competitive = "COMPETITIVE INTELLIGENCE" in insights_content
        has_strategic_recs = "STRATEGIC RECOMMENDATIONS" in insights_content
        has_implementation = "IMPLEMENTATION ROADMAP" in insights_content
        
        sections_found = sum([has_exec_summary, has_competitive, has_strategic_recs, has_implementation])
        
        print(f"📋 Sections found: {sections_found}/4")
        print(f"   Executive Summary: {'✅' if has_exec_summary else '❌'}")
        print(f"   Competitive Intelligence: {'✅' if has_competitive else '❌'}")
        print(f"   Strategic Recommendations: {'✅' if has_strategic_recs else '❌'}")
        print(f"   Implementation Roadmap: {'✅' if has_implementation else '❌'}")
        
        # Show preview
        print(f"\n📖 Content Preview (first 500 chars):")
        print("-" * 50)
        print(insights_content[:500] + "..." if len(insights_content) > 500 else insights_content)
        print("-" * 50)
        
    else:
        print(f"❌ Brand insights generation failed: {insights_result.get('error')}")
    
    print("\n" + "=" * 65)
    print("📊 Testing Competitive Analysis...")
    print("-" * 40)
    
    # Test 2: Competitive Analysis
    competitor_data = [
        {'name': 'Samsung', 'description': 'Global electronics manufacturer'},
        {'name': 'Google', 'description': 'Technology and AI company'},
        {'name': 'Microsoft', 'description': 'Software and cloud services'}
    ]
    
    competitive_result = llm_service.analyze_competitive_landscape('Apple', competitor_data)
    
    if competitive_result.get('success'):
        competitive_content = str(competitive_result.get('insights', ''))
        competitive_length = len(competitive_content)
        
        print(f"✅ Competitive analysis generated successfully")
        print(f"📏 Content length: {competitive_length} characters")
        
        # Quality assessment
        if competitive_length >= 1500:
            print("🎉 EXCELLENT: Comprehensive competitive analysis")
        elif competitive_length >= 1000:
            print("✅ GOOD: Substantial competitive analysis")
        elif competitive_length >= 500:
            print("⚠️ FAIR: Moderate competitive analysis")
        else:
            print("❌ POOR: Insufficient competitive analysis")
        
        # Show preview
        print(f"\n📖 Competitive Analysis Preview (first 300 chars):")
        print("-" * 50)
        print(competitive_content[:300] + "..." if len(competitive_content) > 300 else competitive_content)
        print("-" * 50)
        
    else:
        print(f"❌ Competitive analysis failed: {competitive_result.get('error')}")
    
    print("\n" + "=" * 65)
    print("📊 Testing Executive Summary Generation...")
    print("-" * 40)
    
    # Test 3: Executive Summary
    analysis_data = {
        'brand_name': 'Apple',
        'key_metrics': {'overall_score': 85, 'visual_score': 78},
        'competitive_analysis': competitive_result,
        'brand_insights': insights_result
    }
    
    exec_summary_result = llm_service.generate_executive_summary(analysis_data)
    
    if exec_summary_result.get('success'):
        exec_content = str(exec_summary_result.get('insights', ''))
        exec_length = len(exec_content)
        
        print(f"✅ Executive summary generated successfully")
        print(f"📏 Content length: {exec_length} characters")
        
        # Quality assessment
        if exec_length >= 2000:
            print("🎉 EXCELLENT: Comprehensive executive summary")
        elif exec_length >= 1500:
            print("✅ GOOD: Substantial executive summary")
        elif exec_length >= 1000:
            print("⚠️ FAIR: Moderate executive summary")
        else:
            print("❌ POOR: Insufficient executive summary")
        
        # Show preview
        print(f"\n📖 Executive Summary Preview (first 400 chars):")
        print("-" * 50)
        print(exec_content[:400] + "..." if len(exec_content) > 400 else exec_content)
        print("-" * 50)
        
    else:
        print(f"❌ Executive summary failed: {exec_summary_result.get('error')}")
    
    # Overall Assessment
    print("\n" + "=" * 65)
    print("🎯 OVERALL LLM CONTENT QUALITY ASSESSMENT")
    print("=" * 65)
    
    total_tests = 3
    successful_tests = sum([
        insights_result.get('success', False),
        competitive_result.get('success', False),
        exec_summary_result.get('success', False)
    ])
    
    # Calculate content quality scores
    content_scores = []
    
    if insights_result.get('success'):
        insights_length = len(str(insights_result.get('insights', '')))
        if insights_length >= 2000:
            content_scores.append(100)
        elif insights_length >= 1500:
            content_scores.append(80)
        elif insights_length >= 1000:
            content_scores.append(60)
        else:
            content_scores.append(30)
    
    if competitive_result.get('success'):
        comp_length = len(str(competitive_result.get('insights', '')))
        if comp_length >= 1500:
            content_scores.append(100)
        elif comp_length >= 1000:
            content_scores.append(80)
        elif comp_length >= 500:
            content_scores.append(60)
        else:
            content_scores.append(30)
    
    if exec_summary_result.get('success'):
        exec_length = len(str(exec_summary_result.get('insights', '')))
        if exec_length >= 2000:
            content_scores.append(100)
        elif exec_length >= 1500:
            content_scores.append(80)
        elif exec_length >= 1000:
            content_scores.append(60)
        else:
            content_scores.append(30)
    
    avg_content_score = sum(content_scores) / len(content_scores) if content_scores else 0
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"📊 Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
    print(f"📏 Average Content Quality: {avg_content_score:.1f}%")
    
    if success_rate >= 100 and avg_content_score >= 80:
        print("🎉 OUTSTANDING: All LLM calls delivering comprehensive content!")
    elif success_rate >= 80 and avg_content_score >= 70:
        print("✅ EXCELLENT: LLM calls delivering professional content!")
    elif success_rate >= 60 and avg_content_score >= 60:
        print("👍 GOOD: LLM calls delivering decent content")
    else:
        print("⚠️ NEEDS IMPROVEMENT: LLM calls need enhancement")
    
    print("\n🎯 Comprehensive LLM test completed!")

if __name__ == "__main__":
    test_comprehensive_llm_calls()
