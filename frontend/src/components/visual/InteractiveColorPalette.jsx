import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Palette, 
  Copy, 
  Download, 
  Eye, 
  Droplets,
  Star,
  Award,
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  Info,
  Zap,
  Target,
  Layers,
  Contrast,
  Accessibility
} from 'lucide-react'

const InteractiveColorPalette = ({ visualAnalysis, brandName }) => {
  const [selectedColor, setSelectedColor] = useState(null)
  const [showColorDetails, setShowColorDetails] = useState(false)
  const [copiedColor, setCopiedColor] = useState(null)
  const [colorHarmony, setColorHarmony] = useState(null)

  // Extract comprehensive color data
  const getColorData = () => {
    if (!visualAnalysis) return null

    const combinedColors = visualAnalysis.combined_color_palette || []
    const extractedColors = visualAnalysis.extracted_colors || {}
    const brandfetchColors = visualAnalysis.brandfetch_colors || []
    const visualAssets = visualAnalysis.visual_assets || {}
    const enhancedColorPalette = visualAssets.color_palette || {}
    const colorScores = visualAnalysis.visual_scores || {}

    return {
      primaryColors: enhancedColorPalette.primary_colors || extractedColors.primary_colors || [],
      secondaryColors: enhancedColorPalette.secondary_colors || extractedColors.secondary_colors || [],
      accentColors: enhancedColorPalette.accent_colors || extractedColors.accent_colors || [],
      combinedColors,
      brandfetchColors,
      colorAnalysis: enhancedColorPalette.color_analysis || {},
      colorConsistency: enhancedColorPalette.color_consistency || {},
      colorSwatches: enhancedColorPalette.color_swatches || [],
      consistencyScore: colorScores.color_consistency || 0,
      hasEnhancedColors: Object.keys(enhancedColorPalette).length > 0,
      extractionMethod: enhancedColorPalette.extraction_method || 'basic'
    }
  }

  const colorData = getColorData()

  // Color utility functions
  const hexToRgb = (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }

  const rgbToHsl = (r, g, b) => {
    r /= 255; g /= 255; b /= 255
    const max = Math.max(r, g, b), min = Math.min(r, g, b)
    let h, s, l = (max + min) / 2

    if (max === min) {
      h = s = 0
    } else {
      const d = max - min
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break
        case g: h = (b - r) / d + 2; break
        case b: h = (r - g) / d + 4; break
      }
      h /= 6
    }

    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100)
    }
  }

  const getColorLuminance = (hex) => {
    const rgb = hexToRgb(hex)
    if (!rgb) return 0
    
    const { r, g, b } = rgb
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    })
    
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
  }

  const getContrastRatio = (color1, color2) => {
    const lum1 = getColorLuminance(color1)
    const lum2 = getColorLuminance(color2)
    const brightest = Math.max(lum1, lum2)
    const darkest = Math.min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)
  }

  const getAccessibilityScore = (color) => {
    const whiteContrast = getContrastRatio(color, '#FFFFFF')
    const blackContrast = getContrastRatio(color, '#000000')
    
    const wcagAA = Math.max(whiteContrast, blackContrast) >= 4.5
    const wcagAAA = Math.max(whiteContrast, blackContrast) >= 7
    
    return {
      whiteContrast: whiteContrast.toFixed(2),
      blackContrast: blackContrast.toFixed(2),
      wcagAA,
      wcagAAA,
      score: wcagAAA ? 100 : wcagAA ? 75 : 50
    }
  }

  const getColorName = (hex) => {
    // Basic color naming - in a real app, you'd use a color naming library
    const rgb = hexToRgb(hex)
    if (!rgb) return 'Unknown'
    
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b)
    
    if (hsl.s < 10) {
      if (hsl.l > 90) return 'White'
      if (hsl.l < 10) return 'Black'
      return 'Gray'
    }
    
    const hue = hsl.h
    if (hue < 15 || hue >= 345) return 'Red'
    if (hue < 45) return 'Orange'
    if (hue < 75) return 'Yellow'
    if (hue < 105) return 'Yellow Green'
    if (hue < 135) return 'Green'
    if (hue < 165) return 'Green Cyan'
    if (hue < 195) return 'Cyan'
    if (hue < 225) return 'Blue'
    if (hue < 255) return 'Blue Magenta'
    if (hue < 285) return 'Magenta'
    if (hue < 315) return 'Red Magenta'
    return 'Red'
  }

  const copyToClipboard = async (text, colorKey) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedColor(colorKey)
      setTimeout(() => setCopiedColor(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const generateColorHarmony = (baseColor) => {
    const rgb = hexToRgb(baseColor)
    if (!rgb) return null
    
    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b)
    
    // Generate complementary, triadic, and analogous colors
    const complementary = { ...hsl, h: (hsl.h + 180) % 360 }
    const triadic1 = { ...hsl, h: (hsl.h + 120) % 360 }
    const triadic2 = { ...hsl, h: (hsl.h + 240) % 360 }
    const analogous1 = { ...hsl, h: (hsl.h + 30) % 360 }
    const analogous2 = { ...hsl, h: (hsl.h - 30 + 360) % 360 }
    
    return {
      base: baseColor,
      complementary: hslToHex(complementary),
      triadic: [hslToHex(triadic1), hslToHex(triadic2)],
      analogous: [hslToHex(analogous1), hslToHex(analogous2)]
    }
  }

  const hslToHex = (hsl) => {
    const { h, s, l } = hsl
    const hDecimal = h / 360
    const sDecimal = s / 100
    const lDecimal = l / 100
    
    const c = (1 - Math.abs(2 * lDecimal - 1)) * sDecimal
    const x = c * (1 - Math.abs((hDecimal * 6) % 2 - 1))
    const m = lDecimal - c / 2
    
    let r, g, b
    
    if (hDecimal < 1/6) {
      r = c; g = x; b = 0
    } else if (hDecimal < 2/6) {
      r = x; g = c; b = 0
    } else if (hDecimal < 3/6) {
      r = 0; g = c; b = x
    } else if (hDecimal < 4/6) {
      r = 0; g = x; b = c
    } else if (hDecimal < 5/6) {
      r = x; g = 0; b = c
    } else {
      r = c; g = 0; b = x
    }
    
    r = Math.round((r + m) * 255)
    g = Math.round((g + m) * 255)
    b = Math.round((b + m) * 255)
    
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
  }

  const ColorSwatch = ({ color, label, source, isPrimary = false, index }) => {
    const colorHex = typeof color === 'string' ? color : color.hex || color.value || '#000000'
    const colorName = getColorName(colorHex)
    const accessibility = getAccessibilityScore(colorHex)
    const isSelected = selectedColor === `${source}_${index}`
    
    return (
      <div 
        className={`relative group cursor-pointer transition-all duration-200 ${
          isSelected ? 'ring-2 ring-blue-500 ring-offset-2' : ''
        }`}
        onClick={() => {
          setSelectedColor(`${source}_${index}`)
          setColorHarmony(generateColorHarmony(colorHex))
          setShowColorDetails(true)
        }}
      >
        <div className="text-center">
          <div 
            className={`w-20 h-20 rounded-xl border-2 border-gray-200 mx-auto mb-3 shadow-sm group-hover:shadow-lg transition-all duration-200 ${
              isPrimary ? 'ring-2 ring-blue-400 ring-offset-1' : ''
            }`}
            style={{ backgroundColor: colorHex }}
          />
          
          <div className="space-y-1">
            <p className="text-xs font-mono text-gray-700 font-medium">
              {colorHex.toUpperCase()}
            </p>
            <p className="text-xs text-gray-500 capitalize">
              {colorName}
            </p>
            {label && (
              <p className="text-xs text-gray-400">
                {label}
              </p>
            )}
          </div>
          
          {/* Accessibility indicator */}
          <div className="flex items-center justify-center mt-2 gap-1">
            {accessibility.wcagAAA ? (
              <Badge variant="default" className="text-xs px-1 py-0">
                <Accessibility className="h-2 w-2 mr-1" />
                AAA
              </Badge>
            ) : accessibility.wcagAA ? (
              <Badge variant="secondary" className="text-xs px-1 py-0">
                <Accessibility className="h-2 w-2 mr-1" />
                AA
              </Badge>
            ) : (
              <Badge variant="outline" className="text-xs px-1 py-0">
                <AlertTriangle className="h-2 w-2 mr-1" />
                Low
              </Badge>
            )}
          </div>
          
          {/* Copy button */}
          <Button
            variant="ghost"
            size="sm"
            className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity p-1 h-6 w-6"
            onClick={(e) => {
              e.stopPropagation()
              copyToClipboard(colorHex, `${source}_${index}`)
            }}
          >
            {copiedColor === `${source}_${index}` ? (
              <CheckCircle className="h-3 w-3 text-green-600" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
          </Button>
          
          {source && (
            <Badge variant="outline" className="text-xs mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
              {source}
            </Badge>
          )}
        </div>
      </div>
    )
  }

  if (!colorData || (!colorData.primaryColors.length && !colorData.combinedColors.length && !colorData.brandfetchColors.length)) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-gray-400" />
            Interactive Color Palette
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Palette className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No color data available</p>
            <p className="text-sm text-gray-400">
              Visual processing or Brandfetch API required for color analysis
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Color Palette Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Palette className="h-5 w-5 text-blue-600" />
              Interactive Color Palette
              {brandName && <span className="text-sm font-normal text-gray-500">for {brandName}</span>}
            </CardTitle>
            <div className="flex items-center gap-2">
              {colorData.hasEnhancedColors && (
                <Badge variant="default" className="text-sm">
                  <Zap className="h-3 w-3 mr-1" />
                  Enhanced Analysis
                </Badge>
              )}
              {colorData.consistencyScore > 0 && (
                <Badge variant="secondary" className="text-sm">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Consistency: {Math.round(colorData.consistencyScore)}%
                </Badge>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-8">
          {/* Primary Colors */}
          {colorData.primaryColors.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Star className="h-4 w-4 text-yellow-500" />
                <h3 className="font-semibold text-gray-900">Primary Colors</h3>
                <Badge variant="outline" className="text-xs">
                  {colorData.primaryColors.length} colors
                </Badge>
              </div>
              <div className="flex flex-wrap gap-6">
                {colorData.primaryColors.map((color, index) => (
                  <ColorSwatch
                    key={`primary_${index}`}
                    color={color}
                    source="Primary"
                    isPrimary={true}
                    index={index}
                  />
                ))}
              </div>
            </div>
          )}
          
          {/* Secondary Colors */}
          {colorData.secondaryColors.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Layers className="h-4 w-4 text-blue-500" />
                <h3 className="font-semibold text-gray-900">Secondary Colors</h3>
                <Badge variant="outline" className="text-xs">
                  {colorData.secondaryColors.length} colors
                </Badge>
              </div>
              <div className="flex flex-wrap gap-6">
                {colorData.secondaryColors.map((color, index) => (
                  <ColorSwatch
                    key={`secondary_${index}`}
                    color={color}
                    source="Secondary"
                    index={index}
                  />
                ))}
              </div>
            </div>
          )}
          
          {/* Accent Colors */}
          {colorData.accentColors.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Target className="h-4 w-4 text-purple-500" />
                <h3 className="font-semibold text-gray-900">Accent Colors</h3>
                <Badge variant="outline" className="text-xs">
                  {colorData.accentColors.length} colors
                </Badge>
              </div>
              <div className="flex flex-wrap gap-6">
                {colorData.accentColors.map((color, index) => (
                  <ColorSwatch
                    key={`accent_${index}`}
                    color={color}
                    source="Accent"
                    index={index}
                  />
                ))}
              </div>
            </div>
          )}
          
          {/* Combined/Extracted Colors */}
          {colorData.combinedColors.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Eye className="h-4 w-4 text-green-500" />
                <h3 className="font-semibold text-gray-900">Extracted Colors</h3>
                <Badge variant="outline" className="text-xs">
                  {colorData.combinedColors.length} colors
                </Badge>
              </div>
              <div className="flex flex-wrap gap-6">
                {colorData.combinedColors.map((color, index) => (
                  <ColorSwatch
                    key={`combined_${index}`}
                    color={color}
                    source="Extracted"
                    index={index}
                  />
                ))}
              </div>
            </div>
          )}
          
          {/* Brandfetch Colors */}
          {colorData.brandfetchColors.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Droplets className="h-4 w-4 text-indigo-500" />
                <h3 className="font-semibold text-gray-900">Brand Database Colors</h3>
                <Badge variant="outline" className="text-xs">
                  {colorData.brandfetchColors.length} colors
                </Badge>
              </div>
              <div className="flex flex-wrap gap-6">
                {colorData.brandfetchColors.map((color, index) => (
                  <ColorSwatch
                    key={`brandfetch_${index}`}
                    color={color}
                    source="Brandfetch"
                    index={index}
                  />
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Color Details Modal/Panel */}
      {showColorDetails && selectedColor && colorHarmony && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5 text-blue-600" />
                Color Analysis
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowColorDetails(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Base Color Info */}
              <div className="space-y-4">
                <h3 className="font-semibold">Color Information</h3>
                <div className="flex items-center gap-4">
                  <div 
                    className="w-16 h-16 rounded-lg border-2 border-gray-200"
                    style={{ backgroundColor: colorHarmony.base }}
                  />
                  <div>
                    <p className="font-mono text-lg">{colorHarmony.base.toUpperCase()}</p>
                    <p className="text-gray-600">{getColorName(colorHarmony.base)}</p>
                  </div>
                </div>
                
                {/* Accessibility Scores */}
                <div className="space-y-2">
                  <h4 className="font-medium">Accessibility</h4>
                  {(() => {
                    const accessibility = getAccessibilityScore(colorHarmony.base)
                    return (
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span>vs White:</span>
                          <span className="font-mono">{accessibility.whiteContrast}:1</span>
                        </div>
                        <div className="flex justify-between">
                          <span>vs Black:</span>
                          <span className="font-mono">{accessibility.blackContrast}:1</span>
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant={accessibility.wcagAAA ? "default" : accessibility.wcagAA ? "secondary" : "outline"}>
                            WCAG {accessibility.wcagAAA ? "AAA" : accessibility.wcagAA ? "AA" : "Fail"}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            Score: {accessibility.score}/100
                          </span>
                        </div>
                      </div>
                    )
                  })()}
                </div>
              </div>
              
              {/* Color Harmony */}
              <div className="space-y-4">
                <h3 className="font-semibold">Color Harmony</h3>
                
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium mb-2">Complementary</h4>
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-8 h-8 rounded border"
                        style={{ backgroundColor: colorHarmony.complementary }}
                      />
                      <span className="font-mono text-sm">{colorHarmony.complementary.toUpperCase()}</span>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium mb-2">Triadic</h4>
                    <div className="flex items-center gap-2">
                      {colorHarmony.triadic.map((color, index) => (
                        <div key={index} className="flex items-center gap-1">
                          <div 
                            className="w-8 h-8 rounded border"
                            style={{ backgroundColor: color }}
                          />
                          <span className="font-mono text-xs">{color.toUpperCase()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium mb-2">Analogous</h4>
                    <div className="flex items-center gap-2">
                      {colorHarmony.analogous.map((color, index) => (
                        <div key={index} className="flex items-center gap-1">
                          <div 
                            className="w-8 h-8 rounded border"
                            style={{ backgroundColor: color }}
                          />
                          <span className="font-mono text-xs">{color.toUpperCase()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default InteractiveColorPalette
