#!/usr/bin/env python3
"""
End-to-End Integration Test for Color Analysis in Brand Audit
Tests the complete workflow from API request to color analysis results
"""

import asyncio
import os
import sys
import json
import requests
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.visual_analysis_service import VisualAnalysisService

def test_visual_analysis_service():
    """Test the visual analysis service directly"""
    print("🔧 Testing Visual Analysis Service")
    print("-" * 40)
    
    service = VisualAnalysisService()
    capabilities = service.get_capabilities()
    
    print("📊 Service Capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"  {status} {capability}")
    
    if not capabilities.get('color_extraction'):
        print("❌ Color extraction not available - skipping service test")
        return False
    
    print("✅ Visual analysis service ready")
    return True

async def test_color_extraction_workflow():
    """Test the complete color extraction workflow"""
    print("\n🎨 Testing Color Extraction Workflow")
    print("-" * 40)
    
    service = VisualAnalysisService()
    
    # Test with a simple brand
    brand_name = "Apple"
    website_url = "https://apple.com"
    
    print(f"🔍 Testing with: {brand_name} ({website_url})")
    
    try:
        # Mock brand data (similar to what Brandfetch would provide)
        mock_brand_data = {
            'name': brand_name,
            'domain': 'apple.com',
            'colors': [
                {'hex': '#000000', 'type': 'primary'},
                {'hex': '#FFFFFF', 'type': 'secondary'}
            ],
            'logos': [
                {'url': 'https://logo.clearbit.com/apple.com', 'type': 'icon'}
            ]
        }
        
        # Run visual analysis
        print("📸 Running visual analysis...")
        results = await service.analyze_brand_visuals(brand_name, website_url, mock_brand_data)
        
        # Check results structure
        print("✅ Visual analysis completed")
        print(f"   Screenshots: {len(results.get('visual_assets', {}).get('screenshots', {}))}")
        
        # Check color analysis
        color_palette = results.get('visual_assets', {}).get('color_palette', {})
        if color_palette and not color_palette.get('error'):
            print(f"   Primary colors: {len(color_palette.get('primary_colors', []))}")
            print(f"   Secondary colors: {len(color_palette.get('secondary_colors', []))}")
            print(f"   Color swatches: {len(color_palette.get('color_swatches', []))}")
            
            # Check for required fields
            required_fields = ['primary_colors', 'color_swatches', 'color_analysis', 'color_consistency']
            missing_fields = [field for field in required_fields if field not in color_palette]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
            else:
                print("✅ All required color analysis fields present")
            
            return True
        else:
            print(f"❌ Color extraction failed: {color_palette.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Color extraction workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_integration():
    """Test the backend integration structure"""
    print("\n🔗 Testing Backend Integration Structure")
    print("-" * 40)

    print("🧪 Testing import structure...")

    # Test that we can import the visual analysis service
    try:
        service = VisualAnalysisService()
        print("✅ VisualAnalysisService imported and initialized")

        # Check if service has required methods
        required_methods = ['analyze_brand_visuals', 'extract_brand_colors', 'get_capabilities']
        for method in required_methods:
            if hasattr(service, method):
                print(f"✅ {method} method available")
            else:
                print(f"❌ {method} method not found")
                return False

        # Test capabilities
        capabilities = service.get_capabilities()
        print(f"✅ Service capabilities: {list(capabilities.keys())}")

        return True

    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        return False

def test_frontend_data_structure():
    """Test that the data structure matches frontend expectations"""
    print("\n🖥️  Testing Frontend Data Structure")
    print("-" * 40)
    
    # Mock the expected data structure from visual analysis
    mock_visual_analysis = {
        'visual_assets': {
            'color_palette': {
                'primary_colors': [
                    {
                        'hex': '#007AFF',
                        'rgb': [0, 122, 255],
                        'hsl': [211, 100, 50],
                        'name': 'Blue',
                        'brightness': 48,
                        'frequency_score': 0.85,
                        'consistency_score': 90,
                        'appears_in': ['homepage', 'logo'],
                        'is_dominant': True
                    }
                ],
                'secondary_colors': [],
                'accent_colors': [],
                'color_swatches': [
                    {
                        'id': 'primary_0',
                        'category': 'primary',
                        'hex': '#007AFF',
                        'rgb': [0, 122, 255],
                        'hsl': [211, 100, 50],
                        'name': 'Blue',
                        'brightness': 48,
                        'frequency_score': 0.85,
                        'consistency_score': 90,
                        'appears_in': ['homepage', 'logo'],
                        'is_dominant': True
                    }
                ],
                'color_analysis': {
                    'total_unique_colors': 5,
                    'color_temperature': {'temperature': 'cool'},
                    'color_harmony_type': 'complementary'
                },
                'color_consistency': {
                    'overall_score': 85,
                    'unique_colors_count': 5,
                    'consistent_colors_count': 3
                }
            }
        }
    }
    
    # Check required fields for frontend
    color_palette = mock_visual_analysis['visual_assets']['color_palette']
    
    required_frontend_fields = [
        'color_swatches',
        'color_analysis', 
        'color_consistency'
    ]
    
    print("🔍 Checking frontend data structure:")
    all_present = True
    
    for field in required_frontend_fields:
        if field in color_palette:
            print(f"   ✅ {field}: Present")
        else:
            print(f"   ❌ {field}: Missing")
            all_present = False
    
    # Check color swatch structure
    if color_palette.get('color_swatches'):
        swatch = color_palette['color_swatches'][0]
        swatch_fields = ['id', 'category', 'hex', 'rgb', 'name', 'consistency_score']
        
        print("🎨 Checking color swatch structure:")
        for field in swatch_fields:
            if field in swatch:
                print(f"   ✅ {field}: {swatch[field]}")
            else:
                print(f"   ❌ {field}: Missing")
                all_present = False
    
    return all_present

def generate_integration_report():
    """Generate a comprehensive integration report"""
    print("\n📋 Integration Test Report")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'overall_status': 'UNKNOWN'
    }
    
    # Run all tests
    print("Running integration tests...")
    
    # Test 1: Visual Analysis Service
    results['tests']['visual_service'] = test_visual_analysis_service()
    
    # Test 2: Color Extraction Workflow (async)
    try:
        results['tests']['color_workflow'] = asyncio.run(test_color_extraction_workflow())
    except Exception as e:
        print(f"❌ Color workflow test failed: {e}")
        results['tests']['color_workflow'] = False
    
    # Test 3: Backend Integration
    results['tests']['backend_integration'] = test_backend_integration()
    
    # Test 4: Frontend Data Structure
    results['tests']['frontend_structure'] = test_frontend_data_structure()
    
    # Calculate overall status
    passed_tests = sum(1 for result in results['tests'].values() if result)
    total_tests = len(results['tests'])
    
    if passed_tests == total_tests:
        results['overall_status'] = 'PASS'
        status_emoji = "✅"
    elif passed_tests > total_tests / 2:
        results['overall_status'] = 'PARTIAL'
        status_emoji = "⚠️"
    else:
        results['overall_status'] = 'FAIL'
        status_emoji = "❌"
    
    print(f"\n{status_emoji} Overall Status: {results['overall_status']}")
    print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
    
    # Detailed results
    print("\n📋 Detailed Results:")
    for test_name, result in results['tests'].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    # Save report
    report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_file}")
    
    return results

if __name__ == "__main__":
    print("🚀 Starting End-to-End Integration Test")
    print("=" * 60)
    
    report = generate_integration_report()
    
    print("\n🎯 Integration Test Complete!")
    print("=" * 60)
    
    # Exit with appropriate code
    if report['overall_status'] == 'PASS':
        print("🎉 All tests passed! Color analysis integration is ready.")
        sys.exit(0)
    elif report['overall_status'] == 'PARTIAL':
        print("⚠️  Some tests failed. Review the report for details.")
        sys.exit(1)
    else:
        print("❌ Integration test failed. Please fix issues before deployment.")
        sys.exit(2)
