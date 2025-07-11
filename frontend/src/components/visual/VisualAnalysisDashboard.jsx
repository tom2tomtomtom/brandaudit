import React, { useState, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import EnhancedVisualGallery from './EnhancedVisualGallery.jsx'
import InteractiveColorPalette from './InteractiveColorPalette.jsx'
import BrandAssetShowcase from './BrandAssetShowcase.jsx'
import VisualComparison from './VisualComparison.jsx'
import VisualMetrics from './VisualMetrics.jsx'
import { 
  Eye, 
  Download, 
  Share2, 
  Printer,
  FileText,
  BarChart3,
  Target,
  Palette,
  Layers,
  ArrowLeftRight,
  Camera,
  Award,
  TrendingUp,
  Zap,
  CheckCircle,
  AlertTriangle,
  Info,
  ExternalLink,
  Maximize2,
  Settings,
  Filter,
  Grid3X3,
  List,
  PieChart,
  Activity
} from 'lucide-react'

const VisualAnalysisDashboard = ({ 
  analysisResults, 
  brandName, 
  competitorAnalysis = null,
  websiteUrl = null 
}) => {
  const [activeTab, setActiveTab] = useState('overview')
  const [exportFormat, setExportFormat] = useState('pdf')
  const [showExportOptions, setShowExportOptions] = useState(false)
  const [dashboardLayout, setDashboardLayout] = useState('comprehensive') // 'comprehensive', 'executive', 'technical'
  const dashboardRef = useRef(null)

  // Extract visual analysis data
  const visualAnalysis = analysisResults?.visual_analysis || {}
  const visualScores = visualAnalysis.visual_scores || {}
  const hasVisualData = Object.keys(visualAnalysis).length > 0

  // Calculate dashboard metrics
  const getDashboardMetrics = () => {
    if (!hasVisualData) return null

    const screenshots = visualAnalysis.screenshots || {}
    const logos = visualAnalysis.logos || []
    const colors = visualAnalysis.visual_assets?.color_palette || visualAnalysis.extracted_colors || {}
    
    const totalAssets = Object.keys(screenshots).length + logos.length
    const colorCount = (colors.primary_colors?.length || 0) + 
                      (colors.secondary_colors?.length || 0) + 
                      (colors.accent_colors?.length || 0)
    
    const overallScore = visualScores.overall_visual_score || 0
    const colorConsistency = visualScores.color_consistency || 0
    const logoQuality = visualScores.logo_quality || 0

    return {
      totalAssets,
      colorCount,
      overallScore,
      colorConsistency,
      logoQuality,
      screenshotCount: Object.keys(screenshots).length,
      logoCount: logos.length,
      hasScreenshots: Object.keys(screenshots).length > 0,
      hasLogos: logos.length > 0,
      hasColors: colorCount > 0
    }
  }

  const metrics = getDashboardMetrics()

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getScoreIcon = (score) => {
    if (score >= 80) return CheckCircle
    if (score >= 60) return AlertTriangle
    return Info
  }

  const handleExport = async (format) => {
    // In a real implementation, this would generate and download the report
    console.log(`Exporting visual analysis report as ${format}`)
    
    // Mock export functionality
    const exportData = {
      brandName,
      analysisDate: new Date().toISOString(),
      metrics,
      visualScores,
      format
    }
    
    // Create a blob and download link
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${brandName}-visual-analysis.${format === 'pdf' ? 'json' : format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    setShowExportOptions(false)
  }

  const MetricCard = ({ title, value, subtitle, icon: Icon, score, trend }) => {
    const ScoreIcon = score ? getScoreIcon(score) : Icon
    
    return (
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{title}</p>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
              {subtitle && (
                <p className="text-sm text-gray-500">{subtitle}</p>
              )}
            </div>
            <div className="flex flex-col items-end gap-2">
              <ScoreIcon className={`h-8 w-8 ${score ? getScoreColor(score).split(' ')[0] : 'text-blue-600'}`} />
              {score && (
                <Badge variant="outline" className="text-xs">
                  {Math.round(score)}%
                </Badge>
              )}
              {trend && (
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-3 w-3 text-green-600" />
                  <span className="text-xs text-green-600">+{trend}%</span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const DashboardOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Overall Visual Score"
          value={metrics?.overallScore ? `${Math.round(metrics.overallScore)}%` : 'N/A'}
          subtitle="Brand visual quality"
          score={metrics?.overallScore}
          trend={5}
        />
        <MetricCard
          title="Total Assets"
          value={metrics?.totalAssets || 0}
          subtitle={`${metrics?.screenshotCount || 0} screenshots, ${metrics?.logoCount || 0} logos`}
          icon={Camera}
        />
        <MetricCard
          title="Color Palette"
          value={metrics?.colorCount || 0}
          subtitle="Brand colors detected"
          icon={Palette}
          score={metrics?.colorConsistency}
        />
        <MetricCard
          title="Logo Quality"
          value={metrics?.logoQuality ? `${Math.round(metrics.logoQuality * 100)}%` : 'N/A'}
          subtitle="Logo detection score"
          score={metrics?.logoQuality ? metrics.logoQuality * 100 : 0}
          icon={Target}
        />
      </div>

      {/* Quick Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-600" />
            Visual Analysis Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Strengths</h4>
              <div className="space-y-2">
                {metrics?.hasScreenshots && (
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Website screenshots captured successfully</span>
                  </div>
                )}
                {metrics?.hasColors && (
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Brand color palette identified</span>
                  </div>
                )}
                {metrics?.hasLogos && (
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Logo assets detected and extracted</span>
                  </div>
                )}
                {metrics?.overallScore >= 70 && (
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span>Strong overall visual consistency</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Opportunities</h4>
              <div className="space-y-2">
                {!metrics?.hasScreenshots && (
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span>Website screenshots not available</span>
                  </div>
                )}
                {!metrics?.hasColors && (
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span>Color palette analysis incomplete</span>
                  </div>
                )}
                {!metrics?.hasLogos && (
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span>Logo detection needs improvement</span>
                  </div>
                )}
                {metrics?.overallScore < 70 && (
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span>Visual consistency could be enhanced</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  if (!hasVisualData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-gray-400" />
            Visual Analysis Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-16">
            <Eye className="h-20 w-20 text-gray-300 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Visual Data Available</h3>
            <p className="text-gray-500 mb-4">
              Visual processing is required to generate comprehensive brand analysis
            </p>
            <div className="space-y-2 text-sm text-gray-400">
              <p>• Website screenshot capture</p>
              <p>• Color palette extraction</p>
              <p>• Logo detection and analysis</p>
              <p>• Brand asset identification</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div ref={dashboardRef} className="space-y-6">
      {/* Dashboard Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-6 w-6 text-blue-600" />
                Visual Analysis Dashboard
                {brandName && <span className="text-lg font-normal text-gray-500">for {brandName}</span>}
              </CardTitle>
              <p className="text-gray-600 mt-1">
                Comprehensive visual brand analysis and insights
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowExportOptions(!showExportOptions)}
              >
                <Download className="h-4 w-4 mr-1" />
                Export
              </Button>
              
              {websiteUrl && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(websiteUrl, '_blank')}
                >
                  <ExternalLink className="h-4 w-4 mr-1" />
                  Visit Site
                </Button>
              )}
            </div>
          </div>
          
          {/* Export Options */}
          {showExportOptions && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-3">Export Options</h4>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('pdf')}
                >
                  <FileText className="h-4 w-4 mr-1" />
                  PDF Report
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('json')}
                >
                  <Download className="h-4 w-4 mr-1" />
                  Raw Data
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.print()}
                >
                  <Printer className="h-4 w-4 mr-1" />
                  Print
                </Button>
              </div>
            </div>
          )}
        </CardHeader>
      </Card>

      {/* Dashboard Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview" className="flex items-center gap-1">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="gallery" className="flex items-center gap-1">
            <Camera className="h-4 w-4" />
            Gallery
          </TabsTrigger>
          <TabsTrigger value="colors" className="flex items-center gap-1">
            <Palette className="h-4 w-4" />
            Colors
          </TabsTrigger>
          <TabsTrigger value="assets" className="flex items-center gap-1">
            <Target className="h-4 w-4" />
            Assets
          </TabsTrigger>
          <TabsTrigger value="metrics" className="flex items-center gap-1">
            <Award className="h-4 w-4" />
            Metrics
          </TabsTrigger>
          <TabsTrigger value="comparison" className="flex items-center gap-1">
            <ArrowLeftRight className="h-4 w-4" />
            Compare
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <DashboardOverview />
        </TabsContent>

        <TabsContent value="gallery" className="space-y-6">
          <EnhancedVisualGallery
            visualAnalysis={visualAnalysis}
            brandName={brandName}
            websiteUrl={websiteUrl}
          />
        </TabsContent>

        <TabsContent value="colors" className="space-y-6">
          <InteractiveColorPalette
            visualAnalysis={visualAnalysis}
            brandName={brandName}
          />
        </TabsContent>

        <TabsContent value="assets" className="space-y-6">
          <BrandAssetShowcase
            visualAnalysis={visualAnalysis}
            brandName={brandName}
          />
        </TabsContent>

        <TabsContent value="metrics" className="space-y-6">
          <VisualMetrics
            visualAnalysis={visualAnalysis}
            brandName={brandName}
          />
        </TabsContent>

        <TabsContent value="comparison" className="space-y-6">
          <VisualComparison
            primaryAnalysis={visualAnalysis}
            competitorAnalysis={competitorAnalysis}
            brandName={brandName}
            comparisonType="competitive"
          />
        </TabsContent>
      </Tabs>

      {/* Dashboard Footer */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-4">
              <span>Analysis completed: {new Date().toLocaleDateString()}</span>
              <span>•</span>
              <span>{metrics?.totalAssets || 0} assets analyzed</span>
              <span>•</span>
              <span>Overall score: {metrics?.overallScore ? `${Math.round(metrics.overallScore)}%` : 'N/A'}</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs">
                <Zap className="h-3 w-3 mr-1" />
                AI-Powered Analysis
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default VisualAnalysisDashboard
