#!/usr/bin/env python3
"""
Test script for brand asset detection functionality
Tests logo detection, typography analysis, and visual consistency
"""

import asyncio
import sys
import os
import logging

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.visual_analysis_service import VisualAnalysisService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_brand_asset_detection():
    """Test the brand asset detection functionality"""
    
    print("🔍 Testing Brand Asset Detection System")
    print("=" * 50)
    
    # Initialize the visual analysis service
    visual_service = VisualAnalysisService()
    
    # Check capabilities
    capabilities = visual_service.get_capabilities()
    print(f"📋 Available Capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"  {status} {capability.replace('_', ' ').title()}")
    
    if not capabilities.get('screenshot_capture'):
        print("\n⚠️ Screenshot capture not available - cannot test asset detection")
        return
    
    print(f"\n🎯 Testing Brand Asset Detection")
    
    # Test brands - using well-known brands with distinctive visual elements
    test_brands = [
        {
            'name': 'Apple',
            'website': 'https://www.apple.com',
            'expected_assets': ['logo', 'clean_typography', 'minimal_colors']
        },
        {
            'name': 'Nike',
            'website': 'https://www.nike.com',
            'expected_assets': ['swoosh_logo', 'bold_typography', 'brand_colors']
        }
    ]
    
    for i, brand in enumerate(test_brands, 1):
        print(f"\n{i}. Testing {brand['name']} ({brand['website']})")
        print("-" * 40)
        
        try:
            # Run visual analysis
            result = await visual_service.analyze_brand_visuals(
                brand['name'], 
                brand['website']
            )
            
            # Display results
            print_analysis_results(result, brand['name'])
            
        except Exception as e:
            print(f"❌ Analysis failed for {brand['name']}: {e}")
            logger.error(f"Brand analysis failed: {e}", exc_info=True)

def print_analysis_results(result: dict, brand_name: str):
    """Print formatted analysis results"""
    
    print(f"📊 Analysis Results for {brand_name}:")
    
    # Visual Assets
    visual_assets = result.get('visual_assets', {})
    
    # Screenshots
    screenshots = visual_assets.get('screenshots', {})
    if screenshots:
        print(f"  📸 Screenshots: {len(screenshots)} captured")
        for name, path in list(screenshots.items())[:3]:  # Show first 3
            print(f"    - {name}: {path}")
    
    # Logos
    logos = visual_assets.get('logos', [])
    print(f"  🏷️ Logos Detected: {len(logos)}")
    for i, logo in enumerate(logos[:5], 1):  # Show first 5
        print(f"    {i}. Type: {logo.get('type', 'unknown')}")
        print(f"       Method: {logo.get('detection_method', 'unknown')}")
        print(f"       Quality: {logo.get('quality_score', 0):.2f}")
        print(f"       Size: {logo.get('position', {}).get('width', 0)}x{logo.get('position', {}).get('height', 0)}")
    
    # Colors
    color_palette = visual_assets.get('color_palette', {})
    primary_colors = color_palette.get('primary_colors', [])
    print(f"  🎨 Colors Detected: {len(primary_colors)}")
    for i, color in enumerate(primary_colors[:5], 1):  # Show first 5
        if isinstance(color, dict):
            hex_color = color.get('hex', 'unknown')
            name = color.get('name', 'unnamed')
            print(f"    {i}. {hex_color} ({name})")
        else:
            print(f"    {i}. {color}")
    
    # Typography
    typography = visual_assets.get('typography', {})
    fonts_detected = typography.get('fonts_detected', [])
    print(f"  🔤 Fonts Detected: {len(fonts_detected)}")
    for i, font in enumerate(fonts_detected[:5], 1):  # Show first 5
        print(f"    {i}. {font.get('name', 'unknown')} ({font.get('type', 'unknown')})")
        print(f"       Source: {font.get('source', 'unknown')}")
        print(f"       Confidence: {font.get('confidence', 0):.2f}")
    
    # Visual Scores
    visual_scores = result.get('visual_scores', {})
    print(f"  📈 Visual Scores:")
    for score_name, score_value in visual_scores.items():
        print(f"    📊 {score_name.replace('_', ' ').title()}: {score_value}")
    
    # Visual Consistency
    visual_consistency = result.get('visual_consistency', {})
    if visual_consistency:
        overall_score = visual_consistency.get('overall_score', 0)
        print(f"  🎯 Overall Consistency Score: {overall_score}")
        
        recommendations = visual_consistency.get('recommendations', [])
        if recommendations:
            print(f"  💡 Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"    - {rec}")
    
    # Errors
    errors = result.get('errors', [])
    if errors:
        print(f"  ⚠️ Errors encountered:")
        for error in errors:
            print(f"    - {error}")
    else:
        print(f"  ✅ No errors encountered")
    
    print()

async def test_individual_methods():
    """Test individual detection methods"""
    
    print("\n🧪 Testing Individual Detection Methods")
    print("=" * 50)
    
    visual_service = VisualAnalysisService()
    
    # Test typography detection
    print("1. Testing Typography Detection")
    try:
        typography_result = await visual_service.detect_typography_patterns(
            {}, "https://www.apple.com"
        )
        print(f"   Fonts found: {len(typography_result.get('fonts_detected', []))}")
        print(f"   Consistency score: {typography_result.get('font_consistency', {}).get('overall_score', 0)}")
    except Exception as e:
        print(f"   ❌ Typography detection failed: {e}")
    
    print("\n2. Testing Visual Consistency Analysis")
    try:
        # Mock visual assets for testing
        mock_assets = {
            'color_palette': {
                'primary_colors': [
                    {'hex': '#007AFF', 'name': 'blue'},
                    {'hex': '#FFFFFF', 'name': 'white'},
                    {'hex': '#000000', 'name': 'black'}
                ]
            },
            'logos': [
                {
                    'type': 'contour_detected',
                    'quality_score': 0.85,
                    'detection_method': 'contour_analysis'
                }
            ],
            'typography': {
                'fonts_detected': [
                    {'name': 'San Francisco', 'type': 'sans-serif', 'confidence': 0.9}
                ],
                'font_consistency': {'overall_score': 0.8}
            }
        }
        
        consistency_result = await visual_service.analyze_visual_consistency(mock_assets)
        print(f"   Overall consistency: {consistency_result.get('overall_score', 0)}")
        print(f"   Recommendations: {len(consistency_result.get('recommendations', []))}")
        
    except Exception as e:
        print(f"   ❌ Consistency analysis failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Brand Asset Detection Tests")
    
    try:
        # Run main tests
        asyncio.run(test_brand_asset_detection())
        
        # Run individual method tests
        asyncio.run(test_individual_methods())
        
        print("\n✅ Testing completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        logger.error("Testing failed", exc_info=True)
