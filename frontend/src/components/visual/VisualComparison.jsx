import React, { useState, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  ArrowLeftRight, 
  Eye, 
  TrendingUp,
  TrendingDown,
  Minus,
  Plus,
  Target,
  Palette,
  Monitor,
  Smartphone,
  Layers,
  BarChart3,
  Award,
  AlertTriangle,
  CheckCircle,
  Info,
  Maximize2,
  Download,
  RefreshCw,
  Split,
  Grid2X2,
  Zap
} from 'lucide-react'

const VisualComparison = ({ 
  primaryAnalysis, 
  competitorAnalysis, 
  brandName, 
  comparisonType = 'competitive' // 'competitive', 'temporal', 'variant'
}) => {
  const [comparisonMode, setComparisonMode] = useState('side-by-side') // 'side-by-side', 'overlay', 'slider'
  const [selectedMetric, setSelectedMetric] = useState('overall')
  const [showDifferences, setShowDifferences] = useState(true)
  const [selectedView, setSelectedView] = useState('desktop') // 'desktop', 'mobile', 'both'
  const sliderRef = useRef(null)

  // Extract comparison data
  const getComparisonData = () => {
    if (!primaryAnalysis) return null

    const primary = {
      name: brandName || 'Primary Brand',
      screenshots: primaryAnalysis.screenshots || {},
      colors: primaryAnalysis.visual_assets?.color_palette || primaryAnalysis.extracted_colors || {},
      logos: primaryAnalysis.logos || [],
      scores: primaryAnalysis.visual_scores || {},
      assets: primaryAnalysis.visual_assets || {}
    }

    const competitor = competitorAnalysis ? {
      name: competitorAnalysis.brand_name || 'Competitor',
      screenshots: competitorAnalysis.screenshots || {},
      colors: competitorAnalysis.visual_assets?.color_palette || competitorAnalysis.extracted_colors || {},
      logos: competitorAnalysis.logos || [],
      scores: competitorAnalysis.visual_scores || {},
      assets: competitorAnalysis.visual_assets || {}
    } : null

    return { primary, competitor }
  }

  const comparisonData = getComparisonData()

  // Calculate comparison metrics
  const getComparisonMetrics = () => {
    if (!comparisonData?.competitor) return null

    const { primary, competitor } = comparisonData

    const metrics = {
      overall: {
        primary: primary.scores.overall_visual_score || 0,
        competitor: competitor.scores.overall_visual_score || 0,
        label: 'Overall Visual Score'
      },
      colorConsistency: {
        primary: primary.scores.color_consistency || 0,
        competitor: competitor.scores.color_consistency || 0,
        label: 'Color Consistency'
      },
      logoQuality: {
        primary: primary.scores.logo_quality || 0,
        competitor: competitor.scores.logo_quality || 0,
        label: 'Logo Quality'
      },
      assetCount: {
        primary: Object.keys(primary.screenshots).length + primary.logos.length,
        competitor: Object.keys(competitor.screenshots).length + competitor.logos.length,
        label: 'Total Assets'
      },
      colorCount: {
        primary: (primary.colors.primary_colors?.length || 0) + (primary.colors.secondary_colors?.length || 0),
        competitor: (competitor.colors.primary_colors?.length || 0) + (competitor.colors.secondary_colors?.length || 0),
        label: 'Color Palette Size'
      }
    }

    return metrics
  }

  const metrics = getComparisonMetrics()

  const getScoreDifference = (primaryScore, competitorScore) => {
    const diff = primaryScore - competitorScore
    return {
      value: Math.abs(diff),
      direction: diff > 0 ? 'better' : diff < 0 ? 'worse' : 'equal',
      percentage: competitorScore > 0 ? ((diff / competitorScore) * 100) : 0
    }
  }

  const getScoreColor = (difference) => {
    switch (difference.direction) {
      case 'better': return 'text-green-600 bg-green-50 border-green-200'
      case 'worse': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getScoreIcon = (difference) => {
    switch (difference.direction) {
      case 'better': return TrendingUp
      case 'worse': return TrendingDown
      default: return Minus
    }
  }

  const MetricCard = ({ metricKey, metric }) => {
    const difference = getScoreDifference(metric.primary, metric.competitor)
    const ScoreIcon = getScoreIcon(difference)
    
    return (
      <Card className={`${selectedMetric === metricKey ? 'ring-2 ring-blue-500' : ''} cursor-pointer transition-all`}
             onClick={() => setSelectedMetric(metricKey)}>
        <CardContent className="p-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">{metric.label}</h4>
              <ScoreIcon className={`h-4 w-4 ${getScoreColor(difference).split(' ')[0]}`} />
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{comparisonData.primary.name}:</span>
                <span className="font-semibold">{typeof metric.primary === 'number' ? metric.primary.toFixed(1) : metric.primary}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{comparisonData.competitor.name}:</span>
                <span className="font-semibold">{typeof metric.competitor === 'number' ? metric.competitor.toFixed(1) : metric.competitor}</span>
              </div>
            </div>
            
            {difference.direction !== 'equal' && (
              <div className={`text-xs px-2 py-1 rounded ${getScoreColor(difference)}`}>
                {difference.direction === 'better' ? '+' : '-'}{difference.value.toFixed(1)} 
                {difference.percentage !== 0 && ` (${Math.abs(difference.percentage).toFixed(1)}%)`}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  const ScreenshotComparison = ({ primaryUrl, competitorUrl, title }) => {
    return (
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900 flex items-center gap-2">
          {selectedView === 'desktop' ? <Monitor className="h-4 w-4" /> : <Smartphone className="h-4 w-4" />}
          {title}
        </h4>
        
        {comparisonMode === 'side-by-side' && (
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">{comparisonData.primary.name}</p>
              {primaryUrl ? (
                <img 
                  src={primaryUrl}
                  alt={`${comparisonData.primary.name} ${title}`}
                  className="w-full h-48 object-cover object-top rounded-lg border shadow-sm"
                />
              ) : (
                <div className="w-full h-48 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                  <p className="text-sm text-gray-500">No screenshot available</p>
                </div>
              )}
            </div>
            
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">{comparisonData.competitor.name}</p>
              {competitorUrl ? (
                <img 
                  src={competitorUrl}
                  alt={`${comparisonData.competitor.name} ${title}`}
                  className="w-full h-48 object-cover object-top rounded-lg border shadow-sm"
                />
              ) : (
                <div className="w-full h-48 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                  <p className="text-sm text-gray-500">No screenshot available</p>
                </div>
              )}
            </div>
          </div>
        )}
        
        {comparisonMode === 'overlay' && (
          <div className="relative">
            <div className="relative w-full h-64 rounded-lg overflow-hidden border shadow-sm">
              {primaryUrl && (
                <img 
                  src={primaryUrl}
                  alt={`${comparisonData.primary.name} ${title}`}
                  className="absolute inset-0 w-full h-full object-cover object-top"
                />
              )}
              {competitorUrl && (
                <img 
                  src={competitorUrl}
                  alt={`${comparisonData.competitor.name} ${title}`}
                  className="absolute inset-0 w-full h-full object-cover object-top opacity-50 hover:opacity-75 transition-opacity"
                />
              )}
            </div>
            <div className="absolute bottom-2 left-2 right-2 flex justify-between">
              <Badge variant="default" className="text-xs">
                {comparisonData.primary.name}
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {comparisonData.competitor.name} (Overlay)
              </Badge>
            </div>
          </div>
        )}
      </div>
    )
  }

  const ColorComparison = () => {
    const primaryColors = comparisonData.primary.colors.primary_colors || []
    const competitorColors = comparisonData.competitor.colors.primary_colors || []
    
    return (
      <div className="space-y-4">
        <h4 className="font-medium text-gray-900 flex items-center gap-2">
          <Palette className="h-4 w-4" />
          Color Palette Comparison
        </h4>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">{comparisonData.primary.name}</p>
            <div className="flex flex-wrap gap-2">
              {primaryColors.slice(0, 6).map((color, index) => (
                <div key={index} className="text-center">
                  <div 
                    className="w-12 h-12 rounded-lg border-2 border-gray-200 shadow-sm"
                    style={{ backgroundColor: typeof color === 'string' ? color : color.hex || color.value }}
                  />
                  <p className="text-xs font-mono mt-1">
                    {(typeof color === 'string' ? color : color.hex || color.value || '#000').toUpperCase()}
                  </p>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">{comparisonData.competitor.name}</p>
            <div className="flex flex-wrap gap-2">
              {competitorColors.slice(0, 6).map((color, index) => (
                <div key={index} className="text-center">
                  <div 
                    className="w-12 h-12 rounded-lg border-2 border-gray-200 shadow-sm"
                    style={{ backgroundColor: typeof color === 'string' ? color : color.hex || color.value }}
                  />
                  <p className="text-xs font-mono mt-1">
                    {(typeof color === 'string' ? color : color.hex || color.value || '#000').toUpperCase()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!comparisonData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowLeftRight className="h-5 w-5 text-gray-400" />
            Visual Comparison
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <ArrowLeftRight className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No comparison data available</p>
            <p className="text-sm text-gray-400">
              Competitor analysis required for visual comparisons
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Comparison Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <ArrowLeftRight className="h-5 w-5 text-blue-600" />
              Visual Comparison
              <Badge variant="outline" className="text-sm capitalize">
                {comparisonType}
              </Badge>
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="default" className="text-sm">
                <Eye className="h-3 w-3 mr-1" />
                {comparisonData.primary.name} vs {comparisonData.competitor?.name || 'Competitor'}
              </Badge>
            </div>
          </div>
          
          {/* Comparison Controls */}
          <div className="flex items-center justify-between pt-4">
            <div className="flex items-center gap-2">
              <Button
                variant={comparisonMode === 'side-by-side' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setComparisonMode('side-by-side')}
              >
                <Split className="h-4 w-4 mr-1" />
                Side by Side
              </Button>
              <Button
                variant={comparisonMode === 'overlay' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setComparisonMode('overlay')}
              >
                <Layers className="h-4 w-4 mr-1" />
                Overlay
              </Button>
            </div>
            
            <div className="flex items-center gap-2">
              <select
                value={selectedView}
                onChange={(e) => setSelectedView(e.target.value)}
                className="px-3 py-1 border rounded-md text-sm"
              >
                <option value="desktop">Desktop View</option>
                <option value="mobile">Mobile View</option>
                <option value="both">Both Views</option>
              </select>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDifferences(!showDifferences)}
              >
                <BarChart3 className="h-4 w-4 mr-1" />
                {showDifferences ? 'Hide' : 'Show'} Metrics
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Comparison Metrics */}
      {showDifferences && metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(metrics).map(([key, metric]) => (
            <MetricCard key={key} metricKey={key} metric={metric} />
          ))}
        </div>
      )}

      {/* Visual Comparisons */}
      <div className="space-y-6">
        {/* Screenshot Comparisons */}
        {(selectedView === 'desktop' || selectedView === 'both') && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Monitor className="h-5 w-5 text-blue-600" />
                Desktop Comparison
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <ScreenshotComparison
                primaryUrl={comparisonData.primary.screenshots.homepage_desktop || comparisonData.primary.screenshots.homepage}
                competitorUrl={comparisonData.competitor?.screenshots.homepage_desktop || comparisonData.competitor?.screenshots.homepage}
                title="Homepage"
              />
            </CardContent>
          </Card>
        )}

        {(selectedView === 'mobile' || selectedView === 'both') && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smartphone className="h-5 w-5 text-purple-600" />
                Mobile Comparison
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <ScreenshotComparison
                primaryUrl={comparisonData.primary.screenshots.homepage_mobile}
                competitorUrl={comparisonData.competitor?.screenshots.homepage_mobile}
                title="Mobile Homepage"
              />
            </CardContent>
          </Card>
        )}

        {/* Color Comparison */}
        {comparisonData.competitor && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-green-600" />
                Brand Colors
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ColorComparison />
            </CardContent>
          </Card>
        )}

        {/* Summary Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-yellow-600" />
              Comparison Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {metrics && Object.entries(metrics).map(([key, metric]) => {
                const difference = getScoreDifference(metric.primary, metric.competitor)
                if (difference.direction === 'equal') return null
                
                return (
                  <div key={key} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    {difference.direction === 'better' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <p className="font-medium">
                        {metric.label}: {comparisonData.primary.name} performs {difference.direction} than {comparisonData.competitor.name}
                      </p>
                      <p className="text-sm text-gray-600">
                        Difference of {difference.value.toFixed(1)} 
                        {difference.percentage !== 0 && ` (${Math.abs(difference.percentage).toFixed(1)}%)`}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default VisualComparison
