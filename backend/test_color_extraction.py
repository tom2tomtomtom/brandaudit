#!/usr/bin/env python3
"""
Test script for color extraction functionality
Tests the enhanced color palette extraction from the visual analysis service
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.visual_analysis_service import VisualAnalysisService

async def test_color_extraction():
    """Test the color extraction functionality"""
    print("🎨 Testing Enhanced Color Extraction")
    print("=" * 50)
    
    # Initialize the service
    service = VisualAnalysisService()
    
    # Check capabilities
    capabilities = service.get_capabilities()
    print(f"📊 Service Capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"  {status} {capability}: {available}")
    
    if not capabilities.get('color_extraction'):
        print("\n❌ Color extraction not available. Please install required dependencies:")
        print("   pip install Pillow colorthief webcolors")
        return
    
    print(f"\n🔍 Testing Color Analysis Methods:")
    
    # Test RGB to HEX conversion
    test_rgb = (255, 0, 0)
    hex_color = service.rgb_to_hex(test_rgb)
    print(f"  RGB {test_rgb} → HEX {hex_color}")
    
    # Test RGB to HSL conversion
    hsl_color = service.rgb_to_hsl(test_rgb)
    print(f"  RGB {test_rgb} → HSL {hsl_color}")
    
    # Test brightness calculation
    brightness = service.calculate_brightness(test_rgb)
    print(f"  RGB {test_rgb} → Brightness {brightness}")
    
    # Test color name detection
    color_name = service.get_color_name(test_rgb)
    print(f"  RGB {test_rgb} → Name '{color_name}'")
    
    # Test color harmony analysis
    test_palette = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    harmony = service.analyze_color_harmony(test_palette)
    print(f"  Palette {test_palette} → Harmony '{harmony}'")
    
    print(f"\n🎯 Color extraction test completed!")
    print(f"   Timestamp: {datetime.now().isoformat()}")

def test_color_swatches():
    """Test color swatch generation"""
    print("\n🎨 Testing Color Swatch Generation")
    print("-" * 30)
    
    service = VisualAnalysisService()
    
    # Mock color data
    mock_colors_data = {
        'primary_colors': [
            {
                'hex': '#FF0000',
                'rgb': (255, 0, 0),
                'hsl': [0, 100, 50],
                'name': 'Red',
                'brightness': 76,
                'frequency_score': 0.8,
                'consistency_score': 80,
                'appears_in': ['homepage', 'logo'],
                'is_dominant': True
            }
        ],
        'secondary_colors': [
            {
                'hex': '#00FF00',
                'rgb': (0, 255, 0),
                'hsl': [120, 100, 50],
                'name': 'Green',
                'brightness': 87,
                'frequency_score': 0.6,
                'consistency_score': 60,
                'appears_in': ['homepage']
            }
        ],
        'accent_colors': [
            {
                'hex': '#0000FF',
                'rgb': (0, 0, 255),
                'hsl': [240, 100, 50],
                'name': 'Blue',
                'brightness': 29,
                'frequency_score': 0.3,
                'consistency_score': 40,
                'appears_in': ['header']
            }
        ]
    }
    
    # Generate swatches
    swatches = service._generate_color_swatches(mock_colors_data)
    
    print(f"Generated {len(swatches)} color swatches:")
    for swatch in swatches:
        print(f"  {swatch['category'].upper()}: {swatch['hex']} ({swatch['name']})")
        print(f"    RGB: {swatch['rgb']}, HSL: {swatch['hsl']}")
        print(f"    Brightness: {swatch['brightness']}, Frequency: {swatch['frequency_score']}")
        print(f"    Appears in: {', '.join(swatch.get('appears_in', []))}")
        print()

def test_color_consistency():
    """Test color consistency calculation"""
    print("\n📊 Testing Color Consistency Calculation")
    print("-" * 40)
    
    service = VisualAnalysisService()
    
    # Mock screenshot colors data
    mock_screenshot_colors = {
        'homepage': {
            'extraction_success': True,
            'raw_colors': [
                {'hex': '#FF0000', 'weight': 0.8},
                {'hex': '#00FF00', 'weight': 0.6},
                {'hex': '#0000FF', 'weight': 0.4}
            ]
        },
        'about': {
            'extraction_success': True,
            'raw_colors': [
                {'hex': '#FF0000', 'weight': 0.7},  # Same red
                {'hex': '#FFFF00', 'weight': 0.5},  # Different color
                {'hex': '#0000FF', 'weight': 0.3}   # Same blue
            ]
        }
    }
    
    consistency = service._calculate_color_consistency_advanced(mock_screenshot_colors)
    
    print(f"Color Consistency Analysis:")
    print(f"  Overall Score: {consistency['overall_score']}/100")
    print(f"  Unique Colors: {consistency['unique_colors_count']}")
    print(f"  Consistent Colors: {consistency['consistent_colors_count']}")
    print(f"  Cross-Screenshot Consistency: {consistency['cross_screenshot_consistency']:.1f}%")
    print(f"  Screenshots Analyzed: {consistency['screenshots_analyzed']}")
    
    details = consistency['consistency_details']
    if details['highly_consistent']:
        print("  ✅ Brand has highly consistent color usage")
    elif details['moderately_consistent']:
        print("  ⚠️  Brand has moderately consistent color usage")
    else:
        print("  ❌ Brand has low color consistency")

if __name__ == "__main__":
    print("🚀 Starting Color Extraction Tests")
    print("=" * 60)
    
    # Run async test
    asyncio.run(test_color_extraction())
    
    # Run sync tests
    test_color_swatches()
    test_color_consistency()
    
    print("\n✅ All tests completed!")
    print("=" * 60)
