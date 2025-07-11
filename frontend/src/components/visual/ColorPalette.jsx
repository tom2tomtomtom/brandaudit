import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Palette, Eye, Droplets } from 'lucide-react'

const ColorPalette = ({ visualAnalysis, brandName }) => {
  // Extract color data from various sources
  const getColorData = () => {
    if (!visualAnalysis) return null

    // Check for enhanced visual analysis with multiple sources
    const combinedColors = visualAnalysis.combined_color_palette || []
    const extractedColors = visualAnalysis.extracted_colors || {}
    const brandfetchColors = visualAnalysis.brandfetch_colors || []

    // NEW: Check for enhanced color palette from visual assets
    const visualAssets = visualAnalysis.visual_assets || {}
    const enhancedColorPalette = visualAssets.color_palette || {}

    return {
      combinedColors,
      extractedColors,
      brandfetchColors,
      enhancedColorPalette, // NEW: Enhanced color data
      hasVisualProcessing: visualAnalysis.data_sources?.visual_processing,
      hasBrandfetch: visualAnalysis.data_sources?.brandfetch,
      hasEnhancedColors: !enhancedColorPalette.error && (
        enhancedColorPalette.primary_colors?.length > 0 ||
        enhancedColorPalette.color_swatches?.length > 0
      )
    }
  }

  const colorData = getColorData()

  if (!colorData || (!colorData.combinedColors.length && !colorData.extractedColors.primary_colors && !colorData.brandfetchColors.length && !colorData.hasEnhancedColors)) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-gray-400" />
            Brand Color Palette
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Palette className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No color data available</p>
            <p className="text-sm text-gray-400">
              Visual processing or Brandfetch API required for color analysis
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const ColorSwatch = ({ color, source, name }) => {
    // Handle different color formats
    const getColorStyle = (color) => {
      if (typeof color === 'string') {
        // Handle hex colors
        if (color.startsWith('#')) {
          return { backgroundColor: color }
        }
        // Handle named colors or other formats
        return { backgroundColor: color }
      } else if (color && color.hex) {
        // Handle color objects with hex property
        return { backgroundColor: color.hex }
      } else if (color && color.rgb) {
        // Handle RGB arrays
        return { backgroundColor: `rgb(${color.rgb.join(',')})` }
      }
      return { backgroundColor: '#cccccc' }
    }

    const getColorText = (color) => {
      if (typeof color === 'string') {
        return color.startsWith('#') ? color.toUpperCase() : color
      } else if (color && color.hex) {
        return color.hex.toUpperCase()
      } else if (color && color.rgb) {
        return `RGB(${color.rgb.join(', ')})`
      }
      return 'Unknown'
    }

    const getColorName = (color) => {
      if (color && color.name) {
        return color.name
      }
      return name || 'Color'
    }

    return (
      <div className="text-center group">
        <div 
          className="w-16 h-16 rounded-lg border-2 border-gray-200 mx-auto mb-2 shadow-sm group-hover:shadow-md transition-shadow cursor-pointer"
          style={getColorStyle(color)}
          title={`${getColorName(color)} - ${getColorText(color)}`}
        />
        <p className="text-xs font-mono text-gray-600 mb-1">
          {getColorText(color)}
        </p>
        {getColorName(color) !== 'Color' && (
          <p className="text-xs text-gray-500 capitalize">
            {getColorName(color)}
          </p>
        )}
        {source && (
          <Badge variant="outline" className="text-xs mt-1">
            {source}
          </Badge>
        )}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="h-5 w-5 text-blue-600" />
          Brand Color Palette
          {brandName && <span className="text-sm font-normal text-gray-500">for {brandName}</span>}
        </CardTitle>
        <div className="flex gap-2">
          {colorData.hasEnhancedColors && (
            <Badge variant="default" className="text-xs">
              <Palette className="h-3 w-3 mr-1" />
              Enhanced Analysis
            </Badge>
          )}
          {colorData.hasVisualProcessing && (
            <Badge variant="default" className="text-xs">
              <Eye className="h-3 w-3 mr-1" />
              Visual Processing
            </Badge>
          )}
          {colorData.hasBrandfetch && (
            <Badge variant="secondary" className="text-xs">
              <Droplets className="h-3 w-3 mr-1" />
              Brandfetch
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Enhanced Color Swatches (Priority Display) */}
          {colorData.hasEnhancedColors && colorData.enhancedColorPalette.color_swatches && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Palette className="h-4 w-4" />
                Enhanced Brand Colors
              </h4>

              {/* Primary Colors */}
              {colorData.enhancedColorPalette.color_swatches.filter(s => s.category === 'primary').length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Primary Colors</h5>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                    {colorData.enhancedColorPalette.color_swatches
                      .filter(s => s.category === 'primary')
                      .map((swatch, index) => (
                        <div key={`enhanced-primary-${index}`} className="text-center group cursor-pointer"
                             onClick={() => navigator.clipboard?.writeText(swatch.hex)}>
                          <div
                            className="w-16 h-16 rounded-lg border-2 border-gray-200 mx-auto mb-2 shadow-sm group-hover:shadow-md transition-shadow"
                            style={{ backgroundColor: swatch.hex }}
                            title={`${swatch.name} - ${swatch.hex} - Consistency: ${swatch.consistency_score}%`}
                          />
                          <p className="text-xs font-mono text-gray-600 mb-1">{swatch.hex}</p>
                          <p className="text-xs text-gray-500 capitalize">{swatch.name}</p>
                          {swatch.consistency_score && (
                            <Badge variant="outline" className="text-xs mt-1">
                              {swatch.consistency_score}% consistent
                            </Badge>
                          )}
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Secondary Colors */}
              {colorData.enhancedColorPalette.color_swatches.filter(s => s.category === 'secondary').length > 0 && (
                <div className="mb-4">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Secondary Colors</h5>
                  <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
                    {colorData.enhancedColorPalette.color_swatches
                      .filter(s => s.category === 'secondary')
                      .map((swatch, index) => (
                        <div key={`enhanced-secondary-${index}`} className="text-center group cursor-pointer"
                             onClick={() => navigator.clipboard?.writeText(swatch.hex)}>
                          <div
                            className="w-12 h-12 rounded-lg border-2 border-gray-200 mx-auto mb-1 shadow-sm group-hover:shadow-md transition-shadow"
                            style={{ backgroundColor: swatch.hex }}
                            title={`${swatch.name} - ${swatch.hex}`}
                          />
                          <p className="text-xs font-mono text-gray-600">{swatch.hex}</p>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Color Analysis Insights */}
              {colorData.enhancedColorPalette.color_analysis && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h5 className="font-medium text-blue-900 mb-2">Enhanced Color Analysis</h5>
                  <div className="text-sm text-blue-800 space-y-1">
                    <p>Total colors: {colorData.enhancedColorPalette.color_analysis.total_unique_colors}</p>
                    <p>Color temperature: {colorData.enhancedColorPalette.color_analysis.color_temperature?.temperature || 'neutral'}</p>
                    <p>Color harmony: {colorData.enhancedColorPalette.color_analysis.color_harmony_type || 'unknown'}</p>
                    {colorData.enhancedColorPalette.color_consistency && (
                      <p>Consistency score: {colorData.enhancedColorPalette.color_consistency.overall_score}/100</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Combined Colors (Primary Display) */}
          {colorData.combinedColors.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Brand Colors</h4>
              <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                {colorData.combinedColors.slice(0, 6).map((color, index) => (
                  <ColorSwatch 
                    key={`combined-${index}`}
                    color={color}
                    source="Combined"
                  />
                ))}
              </div>
            </div>
          )}

          {/* Extracted Colors from Visual Processing */}
          {colorData.extractedColors.primary_colors && colorData.extractedColors.primary_colors.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Extracted from Website
              </h4>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                {colorData.extractedColors.primary_colors.map((color, index) => (
                  <ColorSwatch 
                    key={`extracted-primary-${index}`}
                    color={color}
                    source="Extracted"
                    name={color.name}
                  />
                ))}
              </div>
              
              {/* Secondary Colors */}
              {colorData.extractedColors.secondary_colors && colorData.extractedColors.secondary_colors.length > 0 && (
                <div className="mt-4">
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Secondary Colors</h5>
                  <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
                    {colorData.extractedColors.secondary_colors.slice(0, 8).map((color, index) => (
                      <ColorSwatch 
                        key={`extracted-secondary-${index}`}
                        color={color}
                        source="Secondary"
                        name={color.name}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Brandfetch Colors */}
          {colorData.brandfetchColors.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Droplets className="h-4 w-4" />
                Brandfetch Data
              </h4>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                {colorData.brandfetchColors.map((color, index) => (
                  <ColorSwatch 
                    key={`brandfetch-${index}`}
                    color={color}
                    source="Brandfetch"
                  />
                ))}
              </div>
            </div>
          )}

          {/* Color Analysis Info */}
          {colorData.extractedColors.color_analysis && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-2">Color Analysis</h5>
              <div className="text-sm text-blue-800 space-y-1">
                {colorData.extractedColors.color_analysis.total_colors_extracted && (
                  <p>Total colors extracted: {colorData.extractedColors.color_analysis.total_colors_extracted}</p>
                )}
                {colorData.extractedColors.color_analysis.dominant_color_hex && (
                  <p>Dominant color: {colorData.extractedColors.color_analysis.dominant_color_hex}</p>
                )}
                {colorData.extractedColors.color_analysis.color_harmony && (
                  <p>Color harmony: {colorData.extractedColors.color_analysis.color_harmony}</p>
                )}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default ColorPalette
