#!/usr/bin/env python3

"""
Test script for the enhanced visual analysis with Brandfetch integration
"""

import sys
import os
sys.path.append('backend')

import asyncio
from backend.src.services.visual_analysis_service import VisualAnalysisService

async def test_visual_analysis():
    """Test the visual analysis with sample Brandfetch data"""
    
    print("🎨 Testing Enhanced Visual Analysis with Brandfetch Integration")
    print("=" * 60)
    
    # Sample Brandfetch data (similar to what would come from real API)
    sample_brand_data = {
        'name': 'Apple',
        'domain': 'apple.com',
        'logos': [
            {
                'url': 'https://logo.clearbit.com/apple.com',
                'type': 'icon',
                'format': 'png'
            },
            {
                'url': 'https://logo.clearbit.com/apple.com',
                'type': 'logo',
                'format': 'svg'
            }
        ],
        'colors': [
            {
                'hex': '#000000',
                'type': 'primary'
            },
            {
                'hex': '#FFFFFF', 
                'type': 'secondary'
            },
            {
                'hex': '#007AFF',
                'type': 'accent'
            }
        ],
        'fonts': [
            {
                'name': 'SF Pro Display',
                'type': 'primary'
            },
            {
                'name': 'SF Pro Text',
                'type': 'secondary'
            }
        ],
        'success': True
    }
    
    # Initialize visual analysis service
    visual_service = VisualAnalysisService()
    
    # Test visual analysis with Brandfetch data
    print("🔍 Running visual analysis for Apple with Brandfetch data...")
    result = await visual_service.analyze_brand_visuals(
        "Apple", 
        "https://apple.com", 
        sample_brand_data
    )
    
    if result and not result.get('error'):
        print("✅ Visual analysis successful!")
        
        # Check visual assets
        visual_assets = result.get('visual_assets', {})
        print(f"\n📊 Visual Assets Found:")
        
        logos = visual_assets.get('logos', [])
        print(f"  🎯 Logos: {len(logos)}")
        for i, logo in enumerate(logos[:3], 1):
            print(f"    {i}. {logo.get('type', 'unknown')} - {logo.get('format', 'unknown')}")
        
        colors = visual_assets.get('color_palette', {}).get('primary_colors', [])
        print(f"  🎨 Colors: {len(colors)}")
        for i, color in enumerate(colors[:5], 1):
            print(f"    {i}. {color.get('hex', 'unknown')} ({color.get('type', 'unknown')})")
        
        fonts = visual_assets.get('fonts', [])
        print(f"  🔤 Fonts: {len(fonts)}")
        for i, font in enumerate(fonts[:3], 1):
            print(f"    {i}. {font.get('name', 'unknown')} ({font.get('type', 'unknown')})")
        
        # Check visual scores
        visual_scores = result.get('visual_scores', {})
        print(f"\n📈 Visual Scores:")
        for score_name, score_value in visual_scores.items():
            print(f"  📊 {score_name.replace('_', ' ').title()}: {score_value}")
        
        # Check for errors
        errors = result.get('errors', [])
        if errors:
            print(f"\n⚠️ Errors encountered:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"\n✅ No errors encountered")
            
        # Overall assessment
        total_assets = len(logos) + len(colors) + len(fonts)
        print(f"\n🎯 Overall Assessment:")
        print(f"  📦 Total Visual Assets: {total_assets}")
        print(f"  🎨 Brand Visual Completeness: {'High' if total_assets >= 5 else 'Medium' if total_assets >= 3 else 'Low'}")
        
        if total_assets >= 5:
            print("  ✅ Excellent visual brand data captured!")
        elif total_assets >= 3:
            print("  👍 Good visual brand data captured")
        else:
            print("  ⚠️ Limited visual brand data captured")
            
    else:
        print("❌ Visual analysis failed!")
        print(f"Error: {result.get('error') if result else 'No result returned'}")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_visual_analysis())
