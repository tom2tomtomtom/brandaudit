import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Target, 
  Download, 
  Eye, 
  Award,
  Star,
  Zap,
  Layers,
  Image,
  Maximize2,
  X,
  CheckCircle,
  AlertTriangle,
  Info,
  TrendingUp,
  Camera,
  Palette,
  Type,
  Layout,
  Grid3X3,
  Filter,
  Search
} from 'lucide-react'

const BrandAssetShowcase = ({ visualAnalysis, brandName }) => {
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [filterType, setFilterType] = useState('all') // 'all', 'logos', 'elements', 'typography'
  const [sortBy, setSortBy] = useState('quality') // 'quality', 'type', 'size'
  const [viewMode, setViewMode] = useState('grid') // 'grid', 'list'

  // Extract brand assets data
  const getBrandAssets = () => {
    if (!visualAnalysis) return null

    const logos = visualAnalysis.logos || []
    const brandAssets = visualAnalysis.brand_assets || {}
    const visualAssets = visualAnalysis.visual_assets || {}
    const screenshots = visualAnalysis.screenshots || {}
    const visualScores = visualAnalysis.visual_scores || {}

    // Process logos with enhanced data
    const processedLogos = logos.map((logo, index) => ({
      id: `logo_${index}`,
      type: 'logo',
      title: `Logo Detection ${index + 1}`,
      url: logo.extracted_path || logo.url,
      quality: logo.quality_score || 0,
      confidence: logo.confidence || 0,
      method: logo.detection_method || 'unknown',
      dimensions: logo.dimensions || {},
      position: logo.position || {},
      metadata: {
        area: logo.area || 0,
        aspectRatio: logo.aspect_ratio || 0,
        edgeDensity: logo.edge_density || 0,
        colorComplexity: logo.color_complexity || 0
      },
      analysis: {
        isClean: logo.quality_score > 0.7,
        isScalable: logo.aspect_ratio && logo.aspect_ratio > 0.2 && logo.aspect_ratio < 5,
        hasGoodContrast: logo.edge_density > 0.3
      }
    })).filter(logo => logo.url)

    // Process element captures
    const elementAssets = Object.entries(screenshots)
      .filter(([key]) => key.includes('element') || key.includes('header') || key.includes('hero'))
      .map(([key, url], index) => ({
        id: `element_${index}`,
        type: 'element',
        title: key.replace(/_/g, ' ').replace(/element|capture/gi, '').trim() || `Element ${index + 1}`,
        url,
        quality: 0.8, // Default quality for elements
        method: 'element_capture',
        elementType: key.includes('header') ? 'header' : key.includes('hero') ? 'hero' : 'element',
        analysis: {
          isClean: true,
          isScalable: true,
          hasGoodContrast: true
        }
      }))

    // Process typography assets (if available)
    const typographyAssets = visualAssets.typography ? [{
      id: 'typography_analysis',
      type: 'typography',
      title: 'Typography Analysis',
      fonts: visualAssets.typography.fonts_detected || [],
      consistency: visualAssets.typography.font_consistency || {},
      quality: visualAssets.typography.font_consistency?.overall_score || 0,
      analysis: {
        isConsistent: (visualAssets.typography.font_consistency?.overall_score || 0) > 0.7,
        varietyScore: visualAssets.typography.fonts_detected?.length || 0
      }
    }] : []

    const allAssets = [...processedLogos, ...elementAssets, ...typographyAssets]

    return {
      logos: processedLogos,
      elements: elementAssets,
      typography: typographyAssets,
      allAssets,
      totalAssets: allAssets.length,
      averageQuality: allAssets.length > 0 
        ? allAssets.reduce((sum, asset) => sum + (asset.quality || 0), 0) / allAssets.length 
        : 0,
      visualScores
    }
  }

  const brandAssets = getBrandAssets()

  // Filter and sort assets
  const getFilteredAssets = () => {
    if (!brandAssets) return []
    
    let filtered = brandAssets.allAssets
    
    if (filterType !== 'all') {
      filtered = filtered.filter(asset => asset.type === filterType)
    }
    
    // Sort assets
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'quality':
          return (b.quality || 0) - (a.quality || 0)
        case 'type':
          return a.type.localeCompare(b.type)
        case 'size':
          return (b.metadata?.area || 0) - (a.metadata?.area || 0)
        default:
          return 0
      }
    })
    
    return filtered
  }

  const filteredAssets = getFilteredAssets()

  const getQualityColor = (quality) => {
    if (quality >= 0.8) return 'text-green-600 bg-green-50 border-green-200'
    if (quality >= 0.6) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getQualityIcon = (quality) => {
    if (quality >= 0.8) return CheckCircle
    if (quality >= 0.6) return AlertTriangle
    return X
  }

  const downloadAsset = (url, filename) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const AssetCard = ({ asset }) => {
    const QualityIcon = getQualityIcon(asset.quality)
    
    return (
      <Card className="group hover:shadow-lg transition-all duration-200">
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* Asset Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {asset.type === 'logo' && <Target className="h-4 w-4 text-blue-600" />}
                {asset.type === 'element' && <Layout className="h-4 w-4 text-purple-600" />}
                {asset.type === 'typography' && <Type className="h-4 w-4 text-green-600" />}
                <h4 className="font-medium text-gray-900 capitalize">{asset.title}</h4>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => asset.url && downloadAsset(asset.url, `${brandName}-${asset.id}.png`)}
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                disabled={!asset.url}
              >
                <Download className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Asset Preview */}
            {asset.url ? (
              <div className="relative">
                <div className="relative overflow-hidden rounded-lg border shadow-sm hover:shadow-md transition-shadow">
                  <img 
                    src={asset.url}
                    alt={asset.title}
                    className="w-full h-32 object-contain bg-gray-50 cursor-pointer hover:scale-105 transition-transform duration-200"
                    onClick={() => setSelectedAsset(asset)}
                  />
                  
                  {/* Overlay with zoom icon */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                    <Maximize2 className="h-6 w-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              </div>
            ) : asset.type === 'typography' ? (
              <div className="h-32 bg-gray-50 rounded-lg border flex items-center justify-center">
                <div className="text-center">
                  <Type className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">Typography Analysis</p>
                  <p className="text-xs text-gray-500">{asset.fonts?.length || 0} fonts detected</p>
                </div>
              </div>
            ) : (
              <div className="h-32 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                <div className="text-center">
                  <Image className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">Asset not available</p>
                </div>
              </div>
            )}
            
            {/* Asset Metadata */}
            <div className="space-y-2">
              {/* Quality Score */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Quality</span>
                <div className="flex items-center gap-2">
                  <QualityIcon className={`h-4 w-4 ${getQualityColor(asset.quality).split(' ')[0]}`} />
                  <span className="text-sm font-medium">
                    {Math.round((asset.quality || 0) * 100)}%
                  </span>
                </div>
              </div>
              
              {/* Detection Method */}
              {asset.method && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Method</span>
                  <Badge variant="outline" className="text-xs">
                    {asset.method.replace(/_/g, ' ')}
                  </Badge>
                </div>
              )}
              
              {/* Asset Type Specific Info */}
              {asset.type === 'logo' && asset.metadata && (
                <div className="text-xs text-gray-500 space-y-1">
                  {asset.metadata.aspectRatio && (
                    <div className="flex justify-between">
                      <span>Aspect Ratio:</span>
                      <span>{asset.metadata.aspectRatio.toFixed(2)}</span>
                    </div>
                  )}
                  {asset.metadata.edgeDensity && (
                    <div className="flex justify-between">
                      <span>Edge Density:</span>
                      <span>{asset.metadata.edgeDensity.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              )}
              
              {asset.type === 'typography' && asset.fonts && (
                <div className="text-xs text-gray-500">
                  <div className="flex justify-between">
                    <span>Fonts Detected:</span>
                    <span>{asset.fonts.length}</span>
                  </div>
                  {asset.consistency?.overall_score && (
                    <div className="flex justify-between">
                      <span>Consistency:</span>
                      <span>{Math.round(asset.consistency.overall_score * 100)}%</span>
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {/* Analysis Indicators */}
            <div className="flex flex-wrap gap-1">
              {asset.analysis?.isClean && (
                <Badge variant="default" className="text-xs">
                  <CheckCircle className="h-2 w-2 mr-1" />
                  Clean
                </Badge>
              )}
              {asset.analysis?.isScalable && (
                <Badge variant="secondary" className="text-xs">
                  <Zap className="h-2 w-2 mr-1" />
                  Scalable
                </Badge>
              )}
              {asset.analysis?.hasGoodContrast && (
                <Badge variant="outline" className="text-xs">
                  <Eye className="h-2 w-2 mr-1" />
                  Good Contrast
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!brandAssets || brandAssets.totalAssets === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-gray-400" />
            Brand Asset Showcase
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Target className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No brand assets detected</p>
            <p className="text-sm text-gray-400">
              Visual processing required for logo detection and brand asset extraction
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Showcase Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              Brand Asset Showcase
              {brandName && <span className="text-sm font-normal text-gray-500">for {brandName}</span>}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="default" className="text-sm">
                <Image className="h-3 w-3 mr-1" />
                {brandAssets.totalAssets} Assets
              </Badge>
              {brandAssets.averageQuality > 0 && (
                <Badge variant="secondary" className="text-sm">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  Avg Quality: {Math.round(brandAssets.averageQuality * 100)}%
                </Badge>
              )}
            </div>
          </div>
          
          {/* Controls */}
          <div className="flex items-center justify-between pt-4">
            <div className="flex items-center gap-2">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-1 border rounded-md text-sm"
              >
                <option value="all">All Assets ({brandAssets.totalAssets})</option>
                <option value="logo">Logos ({brandAssets.logos.length})</option>
                <option value="element">Elements ({brandAssets.elements.length})</option>
                <option value="typography">Typography ({brandAssets.typography.length})</option>
              </select>
              
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-1 border rounded-md text-sm"
              >
                <option value="quality">Sort by Quality</option>
                <option value="type">Sort by Type</option>
                <option value="size">Sort by Size</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3X3 className="h-4 w-4 mr-1" />
                Grid
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Assets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAssets.map((asset) => (
          <AssetCard key={asset.id} asset={asset} />
        ))}
      </div>

      {/* Asset Detail Modal */}
      {selectedAsset && (
        <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
          <div className="relative max-w-4xl max-h-full bg-white rounded-lg overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <div className="flex items-center gap-2">
                {selectedAsset.type === 'logo' && <Target className="h-5 w-5 text-blue-600" />}
                {selectedAsset.type === 'element' && <Layout className="h-5 w-5 text-purple-600" />}
                {selectedAsset.type === 'typography' && <Type className="h-5 w-5 text-green-600" />}
                <h3 className="text-lg font-semibold">{selectedAsset.title}</h3>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedAsset(null)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Modal Content */}
            <div className="p-6 max-h-96 overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Asset Preview */}
                <div>
                  {selectedAsset.url ? (
                    <img
                      src={selectedAsset.url}
                      alt={selectedAsset.title}
                      className="w-full max-h-64 object-contain bg-gray-50 rounded-lg border"
                    />
                  ) : (
                    <div className="w-full h-64 bg-gray-50 rounded-lg border flex items-center justify-center">
                      <div className="text-center">
                        <Type className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-gray-600">Typography Analysis</p>
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Asset Details */}
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">Asset Information</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Type:</span>
                        <span className="capitalize">{selectedAsset.type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Quality Score:</span>
                        <span className="font-medium">{Math.round((selectedAsset.quality || 0) * 100)}%</span>
                      </div>
                      {selectedAsset.method && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Detection Method:</span>
                          <span className="capitalize">{selectedAsset.method.replace(/_/g, ' ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Type-specific details */}
                  {selectedAsset.type === 'logo' && selectedAsset.metadata && (
                    <div>
                      <h4 className="font-semibold mb-2">Logo Analysis</h4>
                      <div className="space-y-2 text-sm">
                        {selectedAsset.metadata.aspectRatio && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Aspect Ratio:</span>
                            <span>{selectedAsset.metadata.aspectRatio.toFixed(2)}</span>
                          </div>
                        )}
                        {selectedAsset.metadata.edgeDensity && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Edge Density:</span>
                            <span>{selectedAsset.metadata.edgeDensity.toFixed(2)}</span>
                          </div>
                        )}
                        {selectedAsset.metadata.colorComplexity && (
                          <div className="flex justify-between">
                            <span className="text-gray-600">Color Complexity:</span>
                            <span>{selectedAsset.metadata.colorComplexity.toFixed(2)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {selectedAsset.type === 'typography' && selectedAsset.fonts && (
                    <div>
                      <h4 className="font-semibold mb-2">Typography Details</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Fonts Detected:</span>
                          <span>{selectedAsset.fonts.length}</span>
                        </div>
                        {selectedAsset.fonts.length > 0 && (
                          <div>
                            <span className="text-gray-600">Font List:</span>
                            <ul className="mt-1 space-y-1">
                              {selectedAsset.fonts.slice(0, 5).map((font, index) => (
                                <li key={index} className="text-xs bg-gray-50 px-2 py-1 rounded">
                                  {font.name || font} {font.confidence && `(${Math.round(font.confidence * 100)}%)`}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Analysis Results */}
                  <div>
                    <h4 className="font-semibold mb-2">Analysis Results</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedAsset.analysis?.isClean && (
                        <Badge variant="default" className="text-xs">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Clean Design
                        </Badge>
                      )}
                      {selectedAsset.analysis?.isScalable && (
                        <Badge variant="secondary" className="text-xs">
                          <Zap className="h-3 w-3 mr-1" />
                          Scalable
                        </Badge>
                      )}
                      {selectedAsset.analysis?.hasGoodContrast && (
                        <Badge variant="outline" className="text-xs">
                          <Eye className="h-3 w-3 mr-1" />
                          Good Contrast
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BrandAssetShowcase
