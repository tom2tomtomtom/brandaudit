#!/usr/bin/env python3
"""
Demo script showing enhanced color palette extraction for brand audit
Demonstrates the complete workflow from screenshot capture to color analysis
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.visual_analysis_service import VisualAnalysisService

async def demo_brand_color_analysis():
    """Demonstrate complete brand color analysis workflow"""
    print("🎨 Brand Color Analysis Demo")
    print("=" * 60)
    
    # Initialize the service
    service = VisualAnalysisService()
    
    # Check capabilities
    capabilities = service.get_capabilities()
    print(f"📊 Available Capabilities:")
    for capability, available in capabilities.items():
        status = "✅" if available else "❌"
        print(f"  {status} {capability}")
    
    if not capabilities.get('screenshot_capture') or not capabilities.get('color_extraction'):
        print("\n❌ Required capabilities not available. Please install:")
        print("   pip install playwright Pillow colorthief webcolors")
        print("   playwright install")
        return
    
    # Demo brand analysis
    brand_name = "Apple"
    website_url = "https://apple.com"
    
    print(f"\n🔍 Analyzing Brand: {brand_name}")
    print(f"🌐 Website: {website_url}")
    print("-" * 40)
    
    try:
        # Perform complete visual analysis
        print("📸 Capturing screenshots...")
        visual_results = await service.analyze_brand_visuals(brand_name, website_url)
        
        # Display results
        print(f"\n✅ Analysis Complete!")
        print(f"   Timestamp: {visual_results.get('analysis_timestamp')}")
        print(f"   Screenshots captured: {len(visual_results.get('visual_assets', {}).get('screenshots', {}))}")
        
        # Color analysis results
        color_palette = visual_results.get('visual_assets', {}).get('color_palette', {})
        if color_palette and not color_palette.get('error'):
            print(f"\n🎨 Color Analysis Results:")
            print(f"   Primary colors: {len(color_palette.get('primary_colors', []))}")
            print(f"   Secondary colors: {len(color_palette.get('secondary_colors', []))}")
            print(f"   Accent colors: {len(color_palette.get('accent_colors', []))}")
            
            # Display color swatches
            swatches = color_palette.get('color_swatches', [])
            if swatches:
                print(f"\n🎯 Color Swatches ({len(swatches)} total):")
                for swatch in swatches[:8]:  # Show first 8 swatches
                    category = swatch['category'].upper()
                    hex_color = swatch['hex']
                    name = swatch['name']
                    consistency = swatch.get('consistency_score', 0)
                    print(f"   {category}: {hex_color} ({name}) - Consistency: {consistency}%")
            
            # Color analysis insights
            analysis = color_palette.get('color_analysis', {})
            if analysis:
                print(f"\n📊 Color Insights:")
                print(f"   Total unique colors: {analysis.get('total_unique_colors', 0)}")
                print(f"   Color diversity score: {analysis.get('color_diversity_score', 0)}/100")
                print(f"   Color temperature: {analysis.get('color_temperature', {}).get('temperature', 'unknown')}")
                print(f"   Color harmony: {analysis.get('color_harmony_type', 'unknown')}")
            
            # Consistency analysis
            consistency = color_palette.get('color_consistency', {})
            if consistency:
                print(f"\n🔄 Color Consistency Analysis:")
                print(f"   Overall score: {consistency.get('overall_score', 0)}/100")
                print(f"   Consistent colors: {consistency.get('consistent_colors_count', 0)}")
                print(f"   Screenshots analyzed: {consistency.get('screenshots_analyzed', 0)}")
                
                details = consistency.get('consistency_details', {})
                if details.get('highly_consistent'):
                    print("   ✅ Highly consistent color usage across brand assets")
                elif details.get('moderately_consistent'):
                    print("   ⚠️  Moderately consistent color usage")
                else:
                    print("   ❌ Low color consistency - consider brand guidelines review")
        
        else:
            print(f"\n❌ Color extraction failed: {color_palette.get('error', 'Unknown error')}")
        
        # Visual scores
        visual_scores = visual_results.get('visual_scores', {})
        if visual_scores:
            print(f"\n📈 Visual Analysis Scores:")
            for score_name, score_value in visual_scores.items():
                if isinstance(score_value, (int, float)):
                    print(f"   {score_name.replace('_', ' ').title()}: {score_value}/100")
        
        # Errors (if any)
        errors = visual_results.get('errors', [])
        if errors:
            print(f"\n⚠️  Warnings/Errors:")
            for error in errors:
                print(f"   • {error}")
        
        # Generate summary for frontend
        summary = generate_frontend_summary(visual_results)
        print(f"\n📋 Frontend Summary Generated:")
        print(f"   Color swatches: {len(summary.get('color_swatches', []))}")
        print(f"   Visual metrics: {len(summary.get('visual_metrics', []))}")
        print(f"   Screenshots: {len(summary.get('screenshots', []))}")
        
        # Save results to file for inspection
        output_file = f"color_analysis_{brand_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(visual_results, f, indent=2, default=str)
        print(f"\n💾 Full results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()

def generate_frontend_summary(visual_results):
    """Generate a summary suitable for frontend display"""
    color_palette = visual_results.get('visual_assets', {}).get('color_palette', {})
    
    summary = {
        'brand_name': visual_results.get('brand_name'),
        'analysis_timestamp': visual_results.get('analysis_timestamp'),
        'color_swatches': color_palette.get('color_swatches', []),
        'visual_metrics': [],
        'screenshots': [],
        'color_insights': {}
    }
    
    # Add visual metrics
    visual_scores = visual_results.get('visual_scores', {})
    for metric_name, score in visual_scores.items():
        if isinstance(score, (int, float)):
            summary['visual_metrics'].append({
                'name': metric_name.replace('_', ' ').title(),
                'value': score,
                'max_value': 100,
                'category': 'visual_analysis'
            })
    
    # Add screenshots info
    screenshots = visual_results.get('visual_assets', {}).get('screenshots', {})
    for name, path in screenshots.items():
        summary['screenshots'].append({
            'name': name,
            'path': path,
            'type': 'screenshot'
        })
    
    # Add color insights
    color_analysis = color_palette.get('color_analysis', {})
    consistency = color_palette.get('color_consistency', {})
    
    summary['color_insights'] = {
        'total_colors': color_analysis.get('total_unique_colors', 0),
        'color_temperature': color_analysis.get('color_temperature', {}).get('temperature', 'neutral'),
        'harmony_type': color_analysis.get('color_harmony_type', 'unknown'),
        'consistency_score': consistency.get('overall_score', 0),
        'primary_color_count': len(color_palette.get('primary_colors', [])),
        'secondary_color_count': len(color_palette.get('secondary_colors', [])),
        'accent_color_count': len(color_palette.get('accent_colors', []))
    }
    
    return summary

def display_color_swatch_example():
    """Show example of color swatch data structure for frontend"""
    print("\n🎨 Example Color Swatch Data Structure for Frontend:")
    print("-" * 50)
    
    example_swatch = {
        'id': 'primary_0',
        'category': 'primary',
        'hex': '#007AFF',
        'rgb': [0, 122, 255],
        'hsl': [211, 100, 50],
        'name': 'Blue',
        'brightness': 48,
        'frequency_score': 0.85,
        'consistency_score': 90,
        'appears_in': ['homepage', 'logo', 'header'],
        'is_dominant': True
    }
    
    print(json.dumps(example_swatch, indent=2))
    
    print("\n📱 Frontend Usage Example:")
    print("""
    // React component example
    const ColorSwatch = ({ swatch }) => (
      <div className="color-swatch">
        <div 
          className="color-preview" 
          style={{ backgroundColor: swatch.hex }}
        />
        <div className="color-info">
          <h4>{swatch.name}</h4>
          <p>{swatch.hex}</p>
          <p>Consistency: {swatch.consistency_score}%</p>
          <p>Appears in: {swatch.appears_in.join(', ')}</p>
        </div>
      </div>
    );
    """)

if __name__ == "__main__":
    print("🚀 Starting Brand Color Analysis Demo")
    print("=" * 60)
    
    # Show example data structure
    display_color_swatch_example()
    
    # Run the demo
    asyncio.run(demo_brand_color_analysis())
    
    print("\n✅ Demo completed!")
    print("=" * 60)
