#!/usr/bin/env python3
"""
Test script for visual analysis functionality
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.visual_analysis_service import VisualAnalysisService

async def test_visual_analysis():
    """Test visual analysis with a simple website"""
    print("🧪 Testing Visual Analysis Service")
    
    # Initialize the service
    service = VisualAnalysisService()
    
    # Check capabilities
    capabilities = service.get_capabilities()
    print(f"📊 Available capabilities: {capabilities}")
    
    # Test with a simple website
    test_brand = "Apple"
    test_url = "https://apple.com"
    
    print(f"🔍 Testing visual analysis for {test_brand} at {test_url}")
    
    try:
        results = await service.analyze_brand_visuals(test_brand, test_url)
        
        print(f"✅ Analysis completed!")
        print(f"📸 Screenshots captured: {len(results.get('visual_assets', {}).get('screenshots', {}))}")
        print(f"🎨 Colors extracted: {len(results.get('visual_assets', {}).get('color_palette', {}).get('primary_colors', []))}")
        print(f"📊 Visual scores: {list(results.get('visual_scores', {}).keys())}")
        print(f"❌ Errors: {len(results.get('errors', []))}")
        
        if results.get('errors'):
            print("⚠️ Errors encountered:")
            for error in results['errors']:
                print(f"  - {error}")
        
        return results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    # Run the test
    results = asyncio.run(test_visual_analysis())
    
    if results:
        print("\n🎉 Visual analysis test completed successfully!")
        print("✅ Visual processing is working and ready for integration")
    else:
        print("\n❌ Visual analysis test failed")
        print("⚠️ Check dependencies and configuration")
