import React, { useState, useMemo, memo, useCallback } from 'react'
import { usePerformanceOptimization, useIntersectionObserver } from '../hooks/usePerformanceOptimization'
import OptimizedImageDisplay from './OptimizedImageDisplay'
import PerformanceMonitor from './PerformanceMonitor'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import MarkdownRenderer from './MarkdownRenderer.jsx'
import {
  TrendingUp,
  Target,
  Brain,
  BarChart3,
  Lightbulb,
  Building2,
  Globe,
  Users,
  ArrowRight,
  Download,
  Star,
  CheckCircle,
  AlertTriangle,
  Info,
  DollarSign,
  Zap,
  Eye,
  Shield,
  Rocket,
  Award
} from 'lucide-react'

const StrategicIntelligenceBriefing = ({ analysisResults, brandName, onNewAnalysis }) => {
  const [activeTab, setActiveTab] = useState('executive')

  // Extract data from results with proper path mapping
  const llmAnalysis = analysisResults?.api_responses?.llm_analysis?.analysis || ''
  const competitors = analysisResults?.competitor_analysis?.competitors_identified?.competitors || []
  const campaigns = analysisResults?.campaign_analysis?.campaigns_discovered?.campaigns || []
  const strategicRecs = analysisResults?.strategic_synthesis?.strategic_recommendations || []
  const visualAnalysis = analysisResults?.visual_analysis || {}
  const keyMetrics = analysisResults?.key_metrics || {}
  const dataSources = analysisResults?.data_sources || {}

  // Parse LLM analysis into sections
  const parseAnalysisIntoSections = (analysis) => {
    if (!analysis) return {}
    
    const sections = {}
    const lines = analysis.split('\n')
    let currentSection = 'overview'
    let currentContent = []
    
    lines.forEach(line => {
      if (line.startsWith('##') || line.startsWith('###')) {
        // Save previous section
        if (currentContent.length > 0) {
          sections[currentSection] = currentContent.join('\n').trim()
        }
        // Start new section
        currentSection = line.replace(/#+\s*/, '').toLowerCase().replace(/\s+/g, '_')
        currentContent = []
      } else {
        currentContent.push(line)
      }
    })
    
    // Save last section
    if (currentContent.length > 0) {
      sections[currentSection] = currentContent.join('\n').trim()
    }
    
    return sections
  }

  const analysisSections = parseAnalysisIntoSections(llmAnalysis)

  const MetricCard = ({ title, value, icon: Icon, trend, color = "blue" }) => {
    const getColorClasses = (color) => {
      const colors = {
        blue: "bg-blue-50 border-blue-200 text-blue-700",
        green: "bg-green-50 border-green-200 text-green-700",
        yellow: "bg-yellow-50 border-yellow-200 text-yellow-700",
        red: "bg-red-50 border-red-200 text-red-700",
        purple: "bg-purple-50 border-purple-200 text-purple-700"
      }
      return colors[color] || colors.blue
    }

    return (
      <Card className={`${getColorClasses(color)} border-2`}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium opacity-80">{title}</p>
              <p className="text-2xl font-bold">{value}</p>
              {trend && (
                <p className="text-xs opacity-70 mt-1">{trend}</p>
              )}
            </div>
            <Icon className="h-8 w-8 opacity-80" />
          </div>
        </CardContent>
      </Card>
    )
  }

  const CompetitorCard = ({ competitor, index }) => (
    <Card key={index} className="hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
            {index + 1}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <h4 className="font-bold text-lg text-gray-900">{competitor.name}</h4>
              <Badge variant="outline" className="text-xs">
                {Math.round(competitor.confidence_score * 100)}% confidence
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {competitor.market_position}
              </Badge>
            </div>
            <p className="text-gray-600 mb-3 leading-relaxed">{competitor.description}</p>
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm font-medium text-blue-800 mb-1">Key Differentiator:</p>
              <p className="text-blue-700 text-sm">{competitor.key_differentiator}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const CampaignCard = ({ campaign, index }) => (
    <Card key={index} className="hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center text-white font-bold">
            {index + 1}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <h4 className="font-bold text-lg text-gray-900">{campaign.name}</h4>
              <Badge variant="outline" className="text-xs">
                {Math.round(campaign.confidence_score * 100)}% confidence
              </Badge>
              <Badge variant="secondary" className="text-xs">
                {campaign.campaign_type}
              </Badge>
            </div>
            <p className="text-gray-600 mb-3 leading-relaxed">{campaign.description}</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="bg-green-50 p-3 rounded-lg">
                <p className="text-sm font-medium text-green-800 mb-1">Key Messaging:</p>
                <p className="text-green-700 text-sm font-medium">"{campaign.key_messaging}"</p>
              </div>
              <div className="bg-purple-50 p-3 rounded-lg">
                <p className="text-sm font-medium text-purple-800 mb-1">Target Audience:</p>
                <p className="text-purple-700 text-sm">{campaign.target_audience}</p>
              </div>
            </div>
            {campaign.media_channels && (
              <div className="mt-3 flex flex-wrap gap-1">
                {campaign.media_channels.map((channel, i) => (
                  <Badge key={i} variant="outline" className="text-xs">
                    {channel}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const StrategicRecommendationCard = ({ recommendation, index }) => (
    <Card key={index} className="hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-full flex items-center justify-center text-white font-bold">
            {index + 1}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <h4 className="font-bold text-lg text-gray-900">{recommendation.title}</h4>
              <Badge 
                variant={recommendation.impact_level === 'high' ? 'default' : 'secondary'} 
                className="text-xs"
              >
                {recommendation.impact_level} impact
              </Badge>
            </div>
            <p className="text-gray-600 mb-3 leading-relaxed">{recommendation.description}</p>
            {recommendation.expected_outcome && (
              <div className="bg-orange-50 p-3 rounded-lg">
                <p className="text-sm font-medium text-orange-800 mb-1">Expected Outcome:</p>
                <p className="text-orange-700 text-sm">{recommendation.expected_outcome}</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white p-8 rounded-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Strategic Intelligence Briefing
            </h1>
            <p className="text-xl text-blue-100">
              Comprehensive brand analysis for <span className="font-semibold">{brandName}</span>
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-2 mb-2">
              <Award className="h-6 w-6" />
              <span className="text-lg font-semibold">Executive Grade Analysis</span>
            </div>
            <p className="text-blue-200">
              {Object.values(dataSources).filter(Boolean).length}/{Object.keys(dataSources).length} data sources active
            </p>
          </div>
        </div>
      </div>

      {/* Key Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Overall Brand Score"
          value={`${keyMetrics.overall_score || 'N/A'}/100`}
          icon={BarChart3}
          trend="vs industry avg"
          color="blue"
        />
        <MetricCard
          title="Competitive Position"
          value={competitors.length > 0 ? `${competitors.length} rivals` : 'N/A'}
          icon={Building2}
          trend="direct competitors"
          color="purple"
        />
        <MetricCard
          title="Campaign Intelligence"
          value={campaigns.length > 0 ? `${campaigns.length} campaigns` : 'N/A'}
          icon={Rocket}
          trend="discovered"
          color="green"
        />
        <MetricCard
          title="Strategic Recommendations"
          value={strategicRecs.length > 0 ? `${strategicRecs.length} priorities` : 'N/A'}
          icon={Target}
          trend="actionable insights"
          color="orange"
        />
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="executive" className="flex items-center gap-2">
            <Star className="h-4 w-4" />
            Executive
          </TabsTrigger>
          <TabsTrigger value="competitive" className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            Competitive
          </TabsTrigger>
          <TabsTrigger value="campaigns" className="flex items-center gap-2">
            <Rocket className="h-4 w-4" />
            Campaigns
          </TabsTrigger>
          <TabsTrigger value="strategic" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Strategic
          </TabsTrigger>
          <TabsTrigger value="intelligence" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            Intelligence
          </TabsTrigger>
          <TabsTrigger value="visual" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Visual
          </TabsTrigger>
        </TabsList>

        <TabsContent value="executive" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-500" />
                Executive Summary & Strategic Context
              </CardTitle>
            </CardHeader>
            <CardContent>
              {analysisSections.executive_intelligence_briefing || analysisSections.overview ? (
                <MarkdownRenderer 
                  content={analysisSections.executive_intelligence_briefing || analysisSections.overview}
                  className="text-gray-700 prose prose-lg max-w-none"
                />
              ) : (
                <div className="text-center py-8">
                  <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">Executive summary will appear here when analysis is complete.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="competitive" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">
              Competitive Intelligence
            </h2>
            <Badge variant="outline" className="text-lg px-3 py-1">
              {competitors.length} Competitors Analyzed
            </Badge>
          </div>
          
          {competitors.length > 0 ? (
            <div className="space-y-4">
              {competitors.map((competitor, index) => (
                <CompetitorCard key={index} competitor={competitor} index={index} />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  Competitive analysis will appear here when data is available.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">
              Campaign Intelligence
            </h2>
            <Badge variant="outline" className="text-lg px-3 py-1">
              {campaigns.length} Campaigns Discovered
            </Badge>
          </div>
          
          {campaigns.length > 0 ? (
            <div className="space-y-4">
              {campaigns.map((campaign, index) => (
                <CampaignCard key={index} campaign={campaign} index={index} />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Rocket className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  Campaign analysis will appear here when data is available.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="strategic" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">
              Strategic Recommendations
            </h2>
            <Badge variant="outline" className="text-lg px-3 py-1">
              {strategicRecs.length} Priority Actions
            </Badge>
          </div>
          
          {strategicRecs.length > 0 ? (
            <div className="space-y-4">
              {strategicRecs.map((recommendation, index) => (
                <StrategicRecommendationCard key={index} recommendation={recommendation} index={index} />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">
                  Strategic recommendations will appear here when analysis is complete.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="intelligence" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Full Strategic Intelligence Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {llmAnalysis ? (
                <MarkdownRenderer 
                  content={llmAnalysis}
                  className="text-gray-700 prose prose-lg max-w-none"
                />
              ) : (
                <div className="text-center py-8">
                  <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">
                    Comprehensive intelligence analysis will appear here.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="visual" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-900">
              Visual Brand Analysis
            </h2>
            <div className="flex gap-2">
              {visualAnalysis.screenshots && (
                <Badge variant="default" className="text-sm">
                  <Eye className="h-3 w-3 mr-1" />
                  Screenshots Available
                </Badge>
              )}
            </div>
          </div>

          {/* Visual content will be added here */}
          <Card>
            <CardContent className="p-8 text-center">
              <Eye className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">
                Visual analysis components will be integrated here.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex items-center justify-between p-6 bg-gray-50 rounded-lg">
        <div>
          <h3 className="font-semibold text-gray-900">Ready for strategic action?</h3>
          <p className="text-gray-600">Download your intelligence briefing or analyze another brand</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download Briefing
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

export default StrategicIntelligenceBriefing
