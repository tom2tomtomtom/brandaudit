#!/usr/bin/env python3

"""
Test script for PDF generation functionality
Tests the enhanced presentation service with PDF capabilities
"""

import sys
import os
import asyncio
sys.path.append('backend')

from backend.src.services.presentation_service import PresentationService

async def test_pdf_generation():
    """Test the PDF generation functionality"""
    
    print("📄 Testing Enhanced PDF Generation")
    print("=" * 50)
    print("Testing professional PDF report generation capabilities")
    print("")
    
    # Initialize presentation service
    presentation_service = PresentationService()
    
    # Check capabilities
    capabilities = presentation_service.get_capabilities()
    print("🔧 Service Capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"   {status} {capability.replace('_', ' ').title()}")
    
    print("")
    
    if not capabilities.get('pdf_generation'):
        print("❌ PDF generation not available. Please install dependencies:")
        print("   pip install reportlab python-pptx matplotlib seaborn")
        return
    
    # Sample comprehensive analysis data
    sample_analysis_data = {
        'key_metrics': {
            'overall_score': 85,
            'visual_score': 78,
            'market_score': 92,
            'sentiment_score': 88
        },
        'llm_analysis': {
            'insights': """
            ## EXECUTIVE SUMMARY
            
            Apple faces its most complex brand challenges since the post-Jobs era, creating unprecedented opportunities for specialized agency expertise. While maintaining the world's most valuable brand at $574.5 billion, Apple confronts AI narrative crises, Services marketing evolution, and cultural sensitivity pressures that require sophisticated communications strategies beyond traditional hardware advertising.

            The company's premium positioning remains intact with 92-93% customer retention rates versus Samsung's 77%, yet emerging competitive threats in AI and Services require immediate strategic attention. Critical imperatives include reframing the AI narrative from technical lag to privacy-first innovation, developing Services-specific marketing frameworks, and implementing rigorous cultural review processes.
            """
        },
        'competitive_data': {
            'competitors': [
                {
                    'name': 'Samsung',
                    'market_position': 'Strong Challenger',
                    'competitive_strengths': ['Hardware Innovation', 'Global Reach', 'Price Flexibility'],
                    'threat_level': 'High'
                },
                {
                    'name': 'Google',
                    'market_position': 'Market Leader',
                    'competitive_strengths': ['AI Leadership', 'Data Analytics', 'Cloud Services'],
                    'threat_level': 'High'
                },
                {
                    'name': 'Microsoft',
                    'market_position': 'Strong Challenger',
                    'competitive_strengths': ['Enterprise Focus', 'Cloud Computing', 'Productivity Suite'],
                    'threat_level': 'Medium'
                }
            ]
        },
        'visual_data': {
            'visual_assets': {
                'color_palette': {
                    'primary_colors': [
                        {'hex': '#000000', 'type': 'primary'},
                        {'hex': '#FFFFFF', 'type': 'secondary'},
                        {'hex': '#007AFF', 'type': 'accent'}
                    ]
                },
                'fonts': [
                    {'name': 'SF Pro Display', 'type': 'primary'},
                    {'name': 'SF Pro Text', 'type': 'secondary'}
                ]
            }
        },
        'actionable_insights': [
            {
                'finding': 'AI narrative crisis requires immediate attention',
                'impact': 'Shareholder lawsuits and competitive perception gap',
                'priority': 'High',
                'timeline': '30 days'
            },
            {
                'finding': 'Services business needs specialized marketing approach',
                'impact': 'Revenue target of $120B+ annually vs current $100B run rate',
                'priority': 'High',
                'timeline': '60 days'
            },
            {
                'finding': 'Cultural sensitivity gaps creating brand risks',
                'impact': 'iPad Crush ad controversy demonstrates vulnerability',
                'priority': 'Medium',
                'timeline': '90 days'
            }
        ],
        'data_sources': {
            'llm_analysis': True,
            'news_data': True,
            'brand_data': True,
            'visual_analysis': True,
            'competitor_analysis': True
        }
    }
    
    # Test PDF generation
    print("📝 Generating PDF report for Apple...")
    
    try:
        result = await presentation_service.create_pdf_presentation("Apple", sample_analysis_data)
        
        if result.get('success'):
            print("✅ PDF generation successful!")
            print(f"📄 Filename: {result.get('filename')}")
            print(f"📁 File path: {result.get('filepath')}")
            print(f"📊 File size: {result.get('file_size')} bytes")
            print(f"📋 Pages generated: {result.get('pages_generated', 'Unknown')}")
            print(f"🔗 Download URL: {result.get('download_url')}")
            
            # Verify file exists
            filepath = result.get('filepath')
            if filepath and os.path.exists(filepath):
                print("✅ PDF file created successfully")
                
                # Check file size
                file_size = os.path.getsize(filepath)
                if file_size > 50000:  # 50KB minimum for a comprehensive report
                    print(f"✅ PDF file size is substantial: {file_size:,} bytes")
                else:
                    print(f"⚠️ PDF file size seems small: {file_size:,} bytes")
                
                print(f"\n📖 PDF Report Location: {filepath}")
                print("💡 You can open this file to review the generated report")
                
            else:
                print("❌ PDF file was not created at expected location")
                
        else:
            print("❌ PDF generation failed!")
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ PDF generation failed with exception: {str(e)}")
    
    # Test comprehensive presentation generation
    print(f"\n📊 Testing comprehensive presentation generation...")
    
    try:
        comprehensive_result = await presentation_service.generate_brand_audit_presentation("Apple", sample_analysis_data)
        
        if comprehensive_result.get('success'):
            presentations = comprehensive_result.get('presentations_generated', {})
            print("✅ Comprehensive presentation generation successful!")
            
            if 'pdf' in presentations:
                pdf_info = presentations['pdf']
                if pdf_info.get('success'):
                    print(f"   📄 PDF: {pdf_info.get('filename')}")
                else:
                    print(f"   ❌ PDF failed: {pdf_info.get('error')}")
            
            if 'powerpoint' in presentations:
                ppt_info = presentations['powerpoint']
                if ppt_info.get('success'):
                    print(f"   📊 PowerPoint: {ppt_info.get('filename')}")
                else:
                    print(f"   ❌ PowerPoint failed: {ppt_info.get('error')}")
                    
        else:
            print("❌ Comprehensive presentation generation failed!")
            print(f"Error: {comprehensive_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Comprehensive presentation generation failed: {str(e)}")
    
    print("\n🎯 PDF generation test completed!")

if __name__ == "__main__":
    asyncio.run(test_pdf_generation())
