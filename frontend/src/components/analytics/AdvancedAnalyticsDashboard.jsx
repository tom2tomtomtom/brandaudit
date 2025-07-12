import React, { useState, useEffect, useMemo } from 'react'
import analyticsApi from '../../services/analyticsApi.js'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { DatePickerWithRange } from '@/components/ui/date-picker.jsx'
import { 
  BarChart3, 
  TrendingUp, 
  Target, 
  Users, 
  Eye, 
  Filter,
  Download,
  Settings,
  RefreshCw,
  Calendar,
  Zap,
  Brain,
  Globe,
  Award,
  AlertTriangle,
  CheckCircle,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from 'lucide-react'

// Import analytics components
import BrandHealthOverview from './BrandHealthOverview.jsx'
import InteractiveChartGrid from './InteractiveChartGrid.jsx'
import CompetitiveIntelligence from './CompetitiveIntelligence.jsx'
import TrendAnalysisPanel from './TrendAnalysisPanel.jsx'
import PredictiveInsights from './PredictiveInsights.jsx'
import CustomizableDashboard from './CustomizableDashboard.jsx'
import AnalyticsFilters from './AnalyticsFilters.jsx'
import RealTimeAnalyticsPanel from './RealTimeAnalyticsPanel.jsx'
import ExportDialog from './ExportDialog.jsx'
import PerformanceMonitor from './PerformanceMonitor.jsx'
import AIInsightsEngine from './AIInsightsEngine.jsx'
import MobileAnalyticsDashboard from './MobileAnalyticsDashboard.jsx'

const AdvancedAnalyticsDashboard = ({ 
  analysisResults, 
  brandName, 
  historicalData = [],
  competitorData = [],
  onExport,
  onRefresh,
  className = ""
}) => {
  // State management
  const [activeView, setActiveView] = useState('overview')
  const [dateRange, setDateRange] = useState({ from: null, to: null })
  const [filters, setFilters] = useState({
    analysisTypes: [],
    sentimentRange: [0, 100],
    competitorFilter: 'all',
    timeframe: '30d'
  })
  const [dashboardLayout, setDashboardLayout] = useState('standard')
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [apiData, setApiData] = useState(null)
  const [error, setError] = useState(null)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Check for mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Fetch analytics data from API
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      if (!brandName) return

      setIsLoading(true)
      setError(null)

      try {
        const dashboardData = await analyticsApi.getDashboardData(brandName, filters.timeframe)
        setApiData(dashboardData)
        setLastUpdated(new Date())
      } catch (err) {
        console.error('Failed to fetch analytics data:', err)
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }

    fetchAnalyticsData()
  }, [brandName, filters.timeframe])

  // Computed analytics data
  const analyticsData = useMemo(() => {
    if (!analysisResults) return null

    return {
      brandHealth: calculateBrandHealth(analysisResults),
      sentimentTrends: calculateSentimentTrends(analysisResults, historicalData),
      competitivePosition: calculateCompetitivePosition(analysisResults, competitorData),
      keyMetrics: extractKeyMetrics(analysisResults),
      insights: generateInsights(analysisResults, historicalData),
      predictions: generatePredictions(analysisResults, historicalData)
    }
  }, [analysisResults, historicalData, competitorData, filters])

  // Helper functions for data processing
  const calculateBrandHealth = (results) => {
    const baseScore = results?.brand_health_score || 0
    const visualScore = results?.visual_analysis?.visual_scores?.overall_score || 0
    const sentimentScore = results?.llm_insights?.sentiment_score || 0
    const newsScore = results?.news_analysis?.sentiment_score || 0

    return {
      overall: Math.round((baseScore + visualScore + sentimentScore * 100 + newsScore * 100) / 4),
      visual: Math.round(visualScore),
      sentiment: Math.round(sentimentScore * 100),
      news: Math.round(newsScore * 100),
      trend: calculateTrend(baseScore, historicalData)
    }
  }

  const calculateSentimentTrends = (results, historical) => {
    const currentSentiment = results?.llm_insights?.sentiment_score || 0
    const trends = historical.map(item => ({
      date: item.date,
      sentiment: item.sentiment_score || 0,
      volume: item.mention_volume || 0
    }))

    return {
      current: currentSentiment,
      historical: trends,
      change: calculateChange(currentSentiment, historical)
    }
  }

  const calculateCompetitivePosition = (results, competitors) => {
    const brandScore = results?.brand_health_score || 0
    const competitorScores = competitors.map(comp => comp.health_score || 0)
    const avgCompetitorScore = competitorScores.reduce((a, b) => a + b, 0) / competitorScores.length || 0

    return {
      brandScore,
      avgCompetitorScore,
      ranking: calculateRanking(brandScore, competitorScores),
      marketShare: calculateMarketShare(results, competitors)
    }
  }

  const extractKeyMetrics = (results) => {
    return {
      totalMentions: results?.news_analysis?.total_articles || 0,
      sentimentScore: results?.llm_insights?.sentiment_score || 0,
      visualAssets: results?.visual_analysis?.total_assets || 0,
      competitorCount: results?.competitive_analysis?.competitors?.length || 0,
      campaignCount: results?.campaign_analysis?.campaigns?.length || 0,
      lastAnalysis: results?.created_at || new Date().toISOString()
    }
  }

  const generateInsights = (results, historical) => {
    const insights = []
    
    // Brand health insights
    if (results?.brand_health_score > 80) {
      insights.push({
        type: 'positive',
        category: 'Brand Health',
        title: 'Strong Brand Performance',
        description: 'Your brand shows excellent health metrics across all dimensions.',
        confidence: 0.9
      })
    }

    // Sentiment insights
    const sentimentTrend = calculateTrend(results?.llm_insights?.sentiment_score, historical)
    if (sentimentTrend > 0.1) {
      insights.push({
        type: 'positive',
        category: 'Sentiment',
        title: 'Improving Brand Sentiment',
        description: 'Brand sentiment has shown consistent improvement over time.',
        confidence: 0.8
      })
    }

    // Competitive insights
    if (results?.competitive_analysis?.market_position === 'leader') {
      insights.push({
        type: 'positive',
        category: 'Competition',
        title: 'Market Leadership Position',
        description: 'Your brand maintains a strong competitive position in the market.',
        confidence: 0.85
      })
    }

    return insights
  }

  const generatePredictions = (results, historical) => {
    // Simple prediction logic - can be enhanced with ML models
    const predictions = []
    
    const sentimentTrend = calculateTrend(results?.llm_insights?.sentiment_score, historical)
    if (sentimentTrend > 0) {
      predictions.push({
        metric: 'Brand Sentiment',
        prediction: 'Positive growth expected',
        confidence: 0.75,
        timeframe: '30 days',
        impact: 'high'
      })
    }

    return predictions
  }

  // Utility functions
  const calculateTrend = (current, historical) => {
    if (!historical || historical.length < 2) return 0
    const previous = historical[historical.length - 2]?.value || current
    return ((current - previous) / previous) * 100
  }

  const calculateChange = (current, historical) => {
    if (!historical || historical.length === 0) return 0
    const previous = historical[historical.length - 1]?.sentiment_score || current
    return current - previous
  }

  const calculateRanking = (brandScore, competitorScores) => {
    const allScores = [brandScore, ...competitorScores].sort((a, b) => b - a)
    return allScores.indexOf(brandScore) + 1
  }

  const calculateMarketShare = (results, competitors) => {
    // Simplified market share calculation
    const totalMentions = competitors.reduce((sum, comp) => sum + (comp.mentions || 0), 0)
    const brandMentions = results?.news_analysis?.total_articles || 0
    return totalMentions > 0 ? (brandMentions / (totalMentions + brandMentions)) * 100 : 0
  }

  const handleRefresh = async () => {
    if (!brandName) return

    setIsLoading(true)
    setError(null)

    try {
      const dashboardData = await analyticsApi.getDashboardData(brandName, filters.timeframe)
      setApiData(dashboardData)
      setLastUpdated(new Date())
      onRefresh?.()
    } catch (err) {
      console.error('Failed to refresh analytics data:', err)
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleExport = async (format) => {
    try {
      const exportData = {
        view: activeView,
        filters,
        dateRange,
        data: analyticsData
      }

      const result = await analyticsApi.exportData(exportData, format, 'dashboard')

      // Create download link
      if (result.download_url) {
        const link = document.createElement('a')
        link.href = result.download_url
        link.download = result.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }

      onExport?.(format, exportData)
    } catch (err) {
      console.error('Export failed:', err)
      setError('Export failed: ' + err.message)
    }
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-600 mb-2">Failed to load analytics data</p>
          <p className="text-gray-500 text-sm mb-4">{error}</p>
          <Button onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Retry
          </Button>
        </div>
      </div>
    )
  }

  if (!analyticsData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No analytics data available</p>
        </div>
      </div>
    )
  }

  // Show mobile dashboard on small screens
  if (isMobile) {
    return (
      <MobileAnalyticsDashboard
        data={analyticsData}
        brandName={brandName}
        onRefresh={handleRefresh}
        className={className}
      />
    )
  }

  return (
    <div id="analytics-dashboard" className={`space-y-6 ${className}`}>
      {/* Dashboard Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Advanced insights for {brandName} • Last updated {lastUpdated.toLocaleTimeString()}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Select value={dashboardLayout} onValueChange={setDashboardLayout}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="standard">Standard</SelectItem>
              <SelectItem value="executive">Executive</SelectItem>
              <SelectItem value="detailed">Detailed</SelectItem>
              <SelectItem value="competitive">Competitive</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowExportDialog(true)}
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Analytics Filters */}
      <AnalyticsFilters
        filters={filters}
        onFiltersChange={setFilters}
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
      />

      {/* Main Dashboard Content */}
      <Tabs value={activeView} onValueChange={setActiveView} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            <span className="hidden sm:inline">Overview</span>
          </TabsTrigger>
          <TabsTrigger value="realtime" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            <span className="hidden sm:inline">Real-time</span>
          </TabsTrigger>
          <TabsTrigger value="trends" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            <span className="hidden sm:inline">Trends</span>
          </TabsTrigger>
          <TabsTrigger value="competitive" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            <span className="hidden sm:inline">Competitive</span>
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2 hidden lg:flex">
            <Brain className="h-4 w-4" />
            AI Insights
          </TabsTrigger>
          <TabsTrigger value="predictions" className="flex items-center gap-2 hidden lg:flex">
            <Zap className="h-4 w-4" />
            Predictions
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center gap-2 hidden lg:flex">
            <Activity className="h-4 w-4" />
            Performance
          </TabsTrigger>
          <TabsTrigger value="custom" className="flex items-center gap-2 hidden lg:flex">
            <Settings className="h-4 w-4" />
            Custom
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <BrandHealthOverview
            data={analyticsData}
            layout={dashboardLayout}
          />
          <InteractiveChartGrid
            data={analyticsData}
            filters={filters}
            onDrillDown={(metric, data) => console.log('Drill down:', metric, data)}
          />
        </TabsContent>

        <TabsContent value="realtime" className="space-y-6">
          <RealTimeAnalyticsPanel
            brandId={brandName}
            onDataUpdate={(data) => {
              console.log('Real-time data update:', data)
              // Update analytics data with real-time updates
            }}
          />
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <TrendAnalysisPanel 
            data={analyticsData}
            historicalData={historicalData}
            dateRange={dateRange}
          />
        </TabsContent>

        <TabsContent value="competitive" className="space-y-6">
          <CompetitiveIntelligence 
            data={analyticsData}
            competitorData={competitorData}
            brandName={brandName}
          />
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <AIInsightsEngine
            data={analyticsData}
            brandName={brandName}
            onInsightAction={(action, insight) => console.log('Insight action:', action, insight)}
          />
        </TabsContent>

        <TabsContent value="predictions" className="space-y-6">
          <PredictiveInsights
            data={analyticsData}
            predictions={analyticsData.predictions}
          />
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <PerformanceMonitor />
        </TabsContent>

        <TabsContent value="custom" className="space-y-6">
          <CustomizableDashboard
            data={analyticsData}
            layout={dashboardLayout}
            onLayoutChange={setDashboardLayout}
          />
        </TabsContent>
      </Tabs>

      {/* Export Dialog */}
      <ExportDialog
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        data={analyticsData}
        brandName={brandName}
        dashboardElementId="analytics-dashboard"
      />
    </div>
  )
}

export default AdvancedAnalyticsDashboard
