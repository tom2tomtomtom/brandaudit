#!/usr/bin/env python3

"""
Test script for the complete enhanced analysis system with visual improvements
"""

import sys
import os
sys.path.append('backend')

from backend.simple_analysis import SimpleAnalyzer

def test_enhanced_analysis():
    """Test the complete analysis system with visual enhancements"""
    
    print("🚀 Testing Complete Enhanced Analysis System")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = SimpleAnalyzer()
    
    # Test with a well-known brand
    brand_name = "Tesla"
    print(f"🔍 Running enhanced analysis for {brand_name}...")
    
    # Run the analysis
    results = analyzer.analyze_brand(brand_name)
    
    if results and not results.get("error"):
        print("✅ Analysis completed successfully!")
        
        # Check visual analysis results
        visual_analysis = results.get('visual_analysis', {})
        print(f"\n🎨 Visual Analysis Results:")
        
        if visual_analysis and not visual_analysis.get('error'):
            visual_assets = visual_analysis.get('visual_assets', {})
            visual_scores = visual_analysis.get('visual_scores', {})
            
            # Count assets
            logos = visual_assets.get('logos', [])
            color_palette = visual_assets.get('color_palette', {})
            colors = color_palette.get('primary_colors', [])
            fonts = visual_assets.get('fonts', [])
            
            print(f"  🎯 Logos found: {len(logos)}")
            print(f"  🎨 Colors found: {len(colors)}")
            print(f"  🔤 Fonts found: {len(fonts)}")
            
            # Show visual scores
            print(f"\n📊 Visual Scores:")
            for score_name, score_value in visual_scores.items():
                print(f"  {score_name}: {score_value}")
            
            # Assessment
            total_visual_assets = len(logos) + len(colors) + len(fonts)
            print(f"\n📈 Visual Analysis Assessment:")
            print(f"  Total visual assets captured: {total_visual_assets}")
            
            if total_visual_assets >= 5:
                print("  ✅ EXCELLENT: Rich visual brand data captured!")
            elif total_visual_assets >= 3:
                print("  👍 GOOD: Decent visual brand data captured")
            elif total_visual_assets >= 1:
                print("  ⚠️ BASIC: Some visual brand data captured")
            else:
                print("  ❌ POOR: No visual brand data captured")
        else:
            print(f"  ❌ Visual analysis failed: {visual_analysis.get('error', 'Unknown error')}")
        
        # Check brand data (source of visual assets)
        brand_data = results.get('brand_data', {})
        print(f"\n🏢 Brand Data Results:")
        if brand_data and not brand_data.get('error'):
            print(f"  ✅ Brand data collected successfully")
            print(f"  📊 Logos in brand data: {len(brand_data.get('logos', []))}")
            print(f"  🎨 Colors in brand data: {len(brand_data.get('colors', []))}")
            print(f"  🔤 Fonts in brand data: {len(brand_data.get('fonts', []))}")
        else:
            print(f"  ❌ Brand data failed: {brand_data.get('error', 'Unknown error')}")
        
        # Check report generation
        markdown_report = results.get('markdown_report', {})
        print(f"\n📄 Report Generation:")
        if markdown_report and markdown_report.get('success'):
            print(f"  ✅ Markdown report generated successfully")
            print(f"  📁 File: {markdown_report.get('filename')}")
            print(f"  📊 Size: {markdown_report.get('file_size')} characters")
        else:
            print(f"  ❌ Report generation failed: {markdown_report.get('error', 'Unknown error')}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL SYSTEM ASSESSMENT:")
        
        # Count successful components
        successful_components = 0
        total_components = 5
        
        if results.get('llm_analysis', {}).get('success'):
            successful_components += 1
            print("  ✅ LLM Analysis: Working")
        else:
            print("  ❌ LLM Analysis: Failed")
        
        if results.get('news_analysis', {}).get('success'):
            successful_components += 1
            print("  ✅ News Analysis: Working")
        else:
            print("  ❌ News Analysis: Failed")
        
        if brand_data and not brand_data.get('error'):
            successful_components += 1
            print("  ✅ Brand Data Collection: Working")
        else:
            print("  ❌ Brand Data Collection: Failed")
        
        if visual_analysis and not visual_analysis.get('error'):
            successful_components += 1
            print("  ✅ Visual Analysis: Working")
        else:
            print("  ❌ Visual Analysis: Failed")
        
        if markdown_report and markdown_report.get('success'):
            successful_components += 1
            print("  ✅ Report Generation: Working")
        else:
            print("  ❌ Report Generation: Failed")
        
        success_rate = (successful_components / total_components) * 100
        print(f"\n📊 System Success Rate: {success_rate:.1f}% ({successful_components}/{total_components} components working)")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT: System is working well!")
        elif success_rate >= 60:
            print("👍 GOOD: System is mostly working")
        elif success_rate >= 40:
            print("⚠️ FAIR: System has some issues")
        else:
            print("❌ POOR: System needs significant fixes")
            
    else:
        print("❌ Analysis failed completely!")
        print(f"Error: {results.get('error') if results else 'No results returned'}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_enhanced_analysis()
