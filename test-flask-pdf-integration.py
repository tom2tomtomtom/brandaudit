#!/usr/bin/env python3

"""
Test script for Flask PDF integration
Tests PDF generation within Flask application context
"""

import sys
import os
import asyncio
sys.path.append('backend')

def test_flask_pdf_integration():
    """Test PDF generation in Flask context"""
    
    print("🌐 Testing Flask PDF Integration")
    print("=" * 50)
    print("Testing PDF generation within Flask application context")
    print("")
    
    try:
        # Import Flask app and services
        from backend.src.services.presentation_service import PresentationService
        
        # Initialize presentation service
        presentation_service = PresentationService()
        
        # Check capabilities
        capabilities = presentation_service.get_capabilities()
        print("🔧 Service Capabilities in Flask Context:")
        for capability, available in capabilities.items():
            status = "✅" if available else "❌"
            print(f"   {status} {capability.replace('_', ' ').title()}")
        
        if not capabilities.get('pdf_generation'):
            print("❌ PDF generation not available in Flask context")
            return False
        
        # Test data
        test_data = {
            'key_metrics': {
                'overall_score': 85,
                'visual_score': 78,
                'market_score': 92,
                'sentiment_score': 88
            },
            'competitive_data': {
                'competitors': [
                    {
                        'name': 'Samsung',
                        'market_position': 'Strong Challenger',
                        'competitive_strengths': ['Hardware Innovation', 'Global Reach'],
                        'threat_level': 'High'
                    }
                ]
            },
            'actionable_insights': [
                {
                    'finding': 'Brand differentiation opportunity',
                    'impact': 'Market share growth potential',
                    'priority': 'High',
                    'timeline': '60 days'
                }
            ],
            'data_sources': {
                'llm_analysis': True,
                'brand_data': True,
                'visual_analysis': True
            }
        }
        
        # Test PDF generation
        print("\n📄 Testing PDF generation in Flask context...")
        
        async def run_pdf_test():
            result = await presentation_service.create_pdf_presentation("TestBrand", test_data)
            return result
        
        # Run async test
        result = asyncio.run(run_pdf_test())
        
        if result.get('success'):
            print("✅ PDF generation successful in Flask context!")
            print(f"📄 Filename: {result.get('filename')}")
            print(f"📊 File size: {result.get('file_size')} bytes")
            print(f"🔗 Download URL: {result.get('download_url')}")
            
            # Verify file exists
            filepath = result.get('filepath')
            if filepath and os.path.exists(filepath):
                print("✅ PDF file created and accessible")
                
                # Check if file is substantial
                file_size = os.path.getsize(filepath)
                if file_size > 5000:  # 5KB minimum
                    print(f"✅ PDF file has substantial content: {file_size:,} bytes")
                    return True
                else:
                    print(f"⚠️ PDF file seems small: {file_size:,} bytes")
                    return False
            else:
                print("❌ PDF file not found at expected location")
                return False
        else:
            print("❌ PDF generation failed in Flask context!")
            print(f"Error: {result.get('error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("   pip install reportlab python-pptx matplotlib seaborn")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_requirements_installation():
    """Test that all required packages are properly installed"""
    
    print("\n🔍 Testing Requirements Installation")
    print("-" * 40)
    
    required_packages = [
        ('reportlab', 'reportlab'),
        ('python-pptx', 'pptx'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn')
    ]
    
    all_installed = True
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} - Installed")
        except ImportError:
            print(f"❌ {package_name} - Not installed")
            all_installed = False
    
    if all_installed:
        print("✅ All required packages are installed")
    else:
        print("❌ Some packages are missing. Install with:")
        print("   pip install reportlab python-pptx matplotlib seaborn")
    
    return all_installed

def main():
    """Main test function"""
    
    print("🧪 Flask PDF Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Requirements installation
    requirements_ok = test_requirements_installation()
    
    if not requirements_ok:
        print("\n❌ Requirements test failed. Please install missing packages.")
        return False
    
    # Test 2: Flask PDF integration
    pdf_ok = test_flask_pdf_integration()
    
    # Overall results
    print("\n" + "=" * 60)
    print("🎯 OVERALL TEST RESULTS")
    print("=" * 60)
    
    tests_passed = sum([requirements_ok, pdf_ok])
    total_tests = 2
    
    print(f"📊 Tests Passed: {tests_passed}/{total_tests}")
    print(f"   {'✅' if requirements_ok else '❌'} Requirements Installation")
    print(f"   {'✅' if pdf_ok else '❌'} Flask PDF Integration")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! PDF generation is ready for production.")
        print("\n📋 Next Steps:")
        print("   1. PDF generation is now available in your Flask app")
        print("   2. Use PresentationService.create_pdf_presentation() to generate reports")
        print("   3. PDFs will be saved to src/static/presentations/")
        print("   4. Download URLs are provided for frontend integration")
        return True
    else:
        print(f"\n⚠️ {total_tests - tests_passed} test(s) failed. Please address the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
