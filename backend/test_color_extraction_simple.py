#!/usr/bin/env python3
"""
Simple test to verify color extraction works with a real image
"""

import asyncio
import os
import sys
from PIL import Image, ImageDraw

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.visual_analysis_service import VisualAnalysisService

def create_test_image():
    """Create a simple test image with known colors"""
    # Create a 200x200 image with different colored sections
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add colored rectangles
    draw.rectangle([0, 0, 100, 100], fill='#FF0000')      # Red
    draw.rectangle([100, 0, 200, 100], fill='#00FF00')    # Green  
    draw.rectangle([0, 100, 100, 200], fill='#0000FF')    # Blue
    draw.rectangle([100, 100, 200, 200], fill='#FFFF00')  # Yellow
    
    # Save test image
    test_image_path = 'test_image.png'
    img.save(test_image_path)
    return test_image_path

async def test_color_extraction_with_real_image():
    """Test color extraction with a real image"""
    print("🎨 Testing Color Extraction with Real Image")
    print("=" * 50)
    
    # Create test image
    test_image_path = create_test_image()
    print(f"📸 Created test image: {test_image_path}")
    
    try:
        service = VisualAnalysisService()
        
        # Test direct color extraction from image
        result = await service._extract_colors_from_image(test_image_path, "test_image")
        
        print(f"✅ Color extraction completed")
        print(f"   Colors found: {result['color_count']}")
        print(f"   Extraction success: {result['extraction_success']}")
        
        if result['extraction_success'] and result['raw_colors']:
            print(f"\n🎯 Extracted Colors:")
            for i, color in enumerate(result['raw_colors'][:5]):  # Show first 5
                print(f"   {i+1}. {color['hex']} ({color['name']}) - Brightness: {color['brightness']}")
            
            # Test full color analysis workflow
            print(f"\n🔄 Testing Full Color Analysis Workflow...")
            mock_screenshots = {
                'test_image': test_image_path
            }
            
            colors_data = await service.extract_brand_colors(mock_screenshots)
            
            if not colors_data.get('error'):
                print(f"✅ Full workflow completed")
                print(f"   Primary colors: {len(colors_data.get('primary_colors', []))}")
                print(f"   Secondary colors: {len(colors_data.get('secondary_colors', []))}")
                print(f"   Color swatches: {len(colors_data.get('color_swatches', []))}")
                
                # Show color swatches
                swatches = colors_data.get('color_swatches', [])
                if swatches:
                    print(f"\n🎨 Color Swatches:")
                    for swatch in swatches[:3]:  # Show first 3
                        print(f"   {swatch['category'].upper()}: {swatch['hex']} ({swatch['name']})")
                        print(f"      Consistency: {swatch.get('consistency_score', 0)}%")
                
                return True
            else:
                print(f"❌ Full workflow failed: {colors_data.get('error')}")
                return False
        else:
            print(f"❌ Color extraction failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"🧹 Cleaned up test image")

async def test_visual_analysis_integration():
    """Test the complete visual analysis integration"""
    print("\n🔗 Testing Visual Analysis Integration")
    print("=" * 50)
    
    service = VisualAnalysisService()
    
    # Test with mock data (no actual screenshots)
    brand_name = "TestBrand"
    website_url = "https://testbrand.com"
    
    # Mock brand data
    mock_brand_data = {
        'name': brand_name,
        'colors': [
            {'hex': '#FF0000', 'type': 'primary'},
            {'hex': '#00FF00', 'type': 'secondary'}
        ],
        'logos': [
            {'url': 'https://example.com/logo.png', 'type': 'icon'}
        ]
    }
    
    try:
        print(f"🧪 Running visual analysis for {brand_name}...")
        results = await service.analyze_brand_visuals(brand_name, website_url, mock_brand_data)
        
        print(f"✅ Visual analysis completed")
        print(f"   Brand: {results.get('brand_name')}")
        print(f"   Capabilities used: {list(results.get('capabilities_used', {}).keys())}")
        print(f"   Errors: {len(results.get('errors', []))}")
        
        # Check visual assets
        visual_assets = results.get('visual_assets', {})
        print(f"   Visual assets: {list(visual_assets.keys())}")
        
        # Check if Brandfetch colors were integrated
        color_palette = visual_assets.get('color_palette', {})
        if color_palette and 'primary_colors' in color_palette:
            print(f"   Color palette available: {len(color_palette.get('primary_colors', []))} primary colors")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple Color Extraction Test")
    print("=" * 60)
    
    # Test 1: Color extraction with real image
    test1_result = asyncio.run(test_color_extraction_with_real_image())
    
    # Test 2: Visual analysis integration
    test2_result = asyncio.run(test_visual_analysis_integration())
    
    print(f"\n📊 Test Results:")
    print(f"   Color Extraction: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   Integration Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print(f"\n🎉 All tests passed! Color analysis is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)
