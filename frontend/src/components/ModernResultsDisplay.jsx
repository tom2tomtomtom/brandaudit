import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import MarkdownRenderer from './MarkdownRenderer.jsx'
import VisualMetrics from './visual/VisualMetrics.jsx'
import CompetitorComparison from './competitor/CompetitorComparison.jsx'
import CampaignAnalysis from './campaign/CampaignAnalysis.jsx'
// Enhanced Visual Components
import VisualAnalysisDashboard from './visual/VisualAnalysisDashboard.jsx'
import EnhancedVisualGallery from './visual/EnhancedVisualGallery.jsx'
import InteractiveColorPalette from './visual/InteractiveColorPalette.jsx'
import BrandAssetShowcase from './visual/BrandAssetShowcase.jsx'
import {
  TrendingUp,
  Target,
  Brain,
  BarChart3,
  Lightbulb,
  Building2,
  Globe,
  Palette,
  ArrowRight,
  Download,
  Star,
  CheckCircle,
  AlertTriangle,
  Info,
  Camera,
  Eye
} from 'lucide-react'

const ModernResultsDisplay = ({ analysisResults, brandName, onNewAnalysis }) => {
  const [activeTab, setActiveTab] = useState('overview')

  // Extract data from results
  const metrics = analysisResults?.key_metrics || {}
  const insights = analysisResults?.actionable_insights || []
  const llmSections = analysisResults?.llm_sections || {}
  const brandHealth = analysisResults?.brand_health_dashboard || {}
  const dataSources = analysisResults?.data_sources || {}
  const visualAnalysis = analysisResults?.visual_analysis || {}
  const competitorAnalysis = analysisResults?.competitor_analysis || {}
  const campaignAnalysis = analysisResults?.campaign_analysis || {}

  // Extract website URL for screenshots
  const websiteUrl = analysisResults?.api_responses?.brand_data?.domain
    ? `https://${analysisResults.api_responses.brand_data.domain}`
    : null

  // Calculate working APIs
  const workingAPIs = Object.values(dataSources).filter(Boolean).length
  const totalAPIs = Object.keys(dataSources).length

  const ScoreCard = ({ title, score, icon: Icon, color = "blue" }) => {
    const getScoreColor = (score) => {
      if (score >= 70) return "text-green-600"
      if (score >= 40) return "text-yellow-600"
      return "text-red-600"
    }

    const getScoreBackground = (score) => {
      if (score >= 70) return "bg-green-50 border-green-200"
      if (score >= 40) return "bg-yellow-50 border-yellow-200"
      return "bg-red-50 border-red-200"
    }

    return (
      <Card className={`${getScoreBackground(score)} border-2`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{title}</p>
              <p className={`text-3xl font-bold ${getScoreColor(score)}`}>
                {score}/100
              </p>
            </div>
            <Icon className={`h-8 w-8 ${getScoreColor(score)}`} />
          </div>
        </CardContent>
      </Card>
    )
  }

  const InsightCard = ({ insight, index }) => {
    const getPriorityColor = (priority) => {
      switch (priority?.toLowerCase()) {
        case 'high': return 'bg-red-100 text-red-800 border-red-200'
        case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
        case 'low': return 'bg-green-100 text-green-800 border-green-200'
        default: return 'bg-blue-100 text-blue-800 border-blue-200'
      }
    }

    return (
      <Card key={index} className="hover:shadow-lg transition-shadow duration-200">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-blue-600 font-semibold text-sm">{index + 1}</span>
            </div>
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <Badge className={`${getPriorityColor(insight.priority)} border`}>
                  {insight.priority} Priority
                </Badge>
                {insight.timeline && (
                  <Badge variant="outline">{insight.timeline}</Badge>
                )}
                {insight.effort && (
                  <Badge variant="outline">{insight.effort} Effort</Badge>
                )}
              </div>
              <h4 className="font-semibold text-lg text-gray-900 mb-2">
                {insight.finding || insight.recommendation}
              </h4>
              {insight.impact && (
                <p className="text-gray-600 mb-3">{insight.impact}</p>
              )}
              {insight.recommendation && insight.finding && (
                <div className="flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                  <ArrowRight className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <p className="text-blue-800 font-medium">{insight.recommendation}</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Brand Analysis Complete
            </h1>
            <p className="text-xl text-blue-100">
              Professional AI-powered audit for <span className="font-semibold">{brandName}</span>
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="h-6 w-6" />
              <span className="text-lg font-semibold">Analysis Complete</span>
            </div>
            <p className="text-blue-200">
              {workingAPIs}/{totalAPIs} data sources active
            </p>
          </div>
        </div>
      </div>

      {/* Key Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(metrics).map(([key, value]) => (
          <ScoreCard
            key={key}
            title={key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            score={value}
            icon={key.includes('overall') ? BarChart3 : key.includes('visual') ? Palette : TrendingUp}
          />
        ))}
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="visual" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Visual
          </TabsTrigger>
          <TabsTrigger value="visual-dashboard" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Insights
          </TabsTrigger>
          <TabsTrigger value="analysis" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            AI Analysis
          </TabsTrigger>
          <TabsTrigger value="competitive" className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            Competitive
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Executive Summary */}
          {brandHealth.executive_summary && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-500" />
                  Executive Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-lg text-gray-700 leading-relaxed">
                    {brandHealth.executive_summary.overview}
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <h4 className="font-semibold text-green-700 mb-2">Top Strengths</h4>
                      <ul className="space-y-1">
                        {brandHealth.executive_summary.top_strengths?.map((strength, i) => (
                          <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {strength}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-yellow-700 mb-2">Improvement Areas</h4>
                      <ul className="space-y-1">
                        {brandHealth.executive_summary.improvement_areas?.map((area, i) => (
                          <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                            <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                            {area}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-blue-700 mb-2">Strategic Recommendations</h4>
                      <ul className="space-y-1">
                        {brandHealth.executive_summary.strategic_recommendations?.map((rec, i) => (
                          <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                            <Target className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Data Sources Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Data Sources & Reliability
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(dataSources).map(([source, working]) => (
                  <div key={source} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <div className={`w-3 h-3 rounded-full ${working ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className="font-medium capitalize">
                      {source.replace('_', ' ')}
                    </span>
                    <Badge variant={working ? "default" : "secondary"} className="ml-auto">
                      {working ? "Active" : "Offline"}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="visual" className="space-y-6">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Visual Brand Analysis
              </h2>
              <div className="flex gap-2">
                {dataSources.visual_analysis && (
                  <Badge variant="default" className="text-sm">
                    <Camera className="h-3 w-3 mr-1" />
                    Enhanced Visual Analysis
                  </Badge>
                )}
                {!dataSources.visual_analysis && (
                  <Badge variant="secondary" className="text-sm">
                    <Camera className="h-3 w-3 mr-1" />
                    Visual Processing Offline
                  </Badge>
                )}
              </div>
            </div>

            {/* Enhanced Visual Components */}
            <div className="space-y-6">
              {/* Visual Metrics */}
              <VisualMetrics
                visualAnalysis={visualAnalysis}
                brandName={brandName}
              />

              {/* Enhanced Screenshot Gallery */}
              <EnhancedVisualGallery
                visualAnalysis={visualAnalysis}
                brandName={brandName}
                websiteUrl={websiteUrl}
              />

              {/* Interactive Color Palette */}
              <InteractiveColorPalette
                visualAnalysis={visualAnalysis}
                brandName={brandName}
              />

              {/* Brand Asset Showcase */}
              <BrandAssetShowcase
                visualAnalysis={visualAnalysis}
                brandName={brandName}
              />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="visual-dashboard" className="space-y-6">
          <VisualAnalysisDashboard
            analysisResults={analysisResults}
            brandName={brandName}
            competitorAnalysis={competitorAnalysis}
            websiteUrl={websiteUrl}
          />
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Strategic Insights & Recommendations
              </h2>
              <Badge variant="outline" className="text-lg px-3 py-1">
                {insights.length} Insights
              </Badge>
            </div>
            
            {/* Campaign Analysis */}
            <CampaignAnalysis
              campaignAnalysis={campaignAnalysis}
              brandName={brandName}
            />

            {/* Strategic Insights */}
            {insights.length > 0 ? (
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-gray-900">AI-Generated Strategic Insights</h3>
                {insights.map((insight, index) => (
                  <InsightCard key={index} insight={insight} index={index} />
                ))}
              </div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5" />
                    AI Strategic Insights
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-8 text-center">
                  <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">
                    No specific insights available. This may be due to limited data sources.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          {llmSections['EXECUTIVE SUMMARY'] && (
            <Card>
              <CardHeader>
                <CardTitle>AI Strategic Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <MarkdownRenderer 
                  content={llmSections['EXECUTIVE SUMMARY']}
                  className="text-gray-700"
                />
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="competitive" className="space-y-6">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                Competitive Analysis
              </h2>
              <div className="flex gap-2">
                {dataSources.competitor_analysis && (
                  <Badge variant="default" className="text-sm">
                    <Building2 className="h-3 w-3 mr-1" />
                    Competitor Data Available
                  </Badge>
                )}
                {!dataSources.competitor_analysis && (
                  <Badge variant="secondary" className="text-sm">
                    <Building2 className="h-3 w-3 mr-1" />
                    Competitor Analysis Offline
                  </Badge>
                )}
              </div>
            </div>

            {/* Enhanced Competitor Comparison */}
            <CompetitorComparison
              competitorAnalysis={competitorAnalysis}
              brandName={brandName}
            />

            {/* AI-Generated Competitive Intelligence */}
            {llmSections['COMPETITIVE INTELLIGENCE'] && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5" />
                    AI Competitive Intelligence
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <MarkdownRenderer
                    content={llmSections['COMPETITIVE INTELLIGENCE']}
                    className="text-gray-700"
                  />
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex items-center justify-between p-6 bg-gray-50 rounded-lg">
        <div>
          <h3 className="font-semibold text-gray-900">Ready for the next step?</h3>
          <p className="text-gray-600">Download your report or analyze another brand</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download Report
          </Button>
          <Button onClick={onNewAnalysis}>
            <ArrowRight className="h-4 w-4 mr-2" />
            New Analysis
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ModernResultsDisplay
