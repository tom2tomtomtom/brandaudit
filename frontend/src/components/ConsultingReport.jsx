import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Download, 
  FileText, 
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Building2,
  TrendingUp,
  Target,
  Lightbulb,
  Users,
  Globe,
  Zap
} from 'lucide-react'

const ConsultingReport = ({ analysisResults }) => {
  const [activeSection, setActiveSection] = useState('executive')
  const [showFullReport, setShowFullReport] = useState(false)

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  // Use pre-parsed LLM sections from backend (no need to parse again)
  const llmSections = analysisResults?.parsed_sections || analysisResults?.llm_sections || {}

  const ExpandableSection = ({ title, icon: Icon, sectionKey, children, defaultExpanded = false }) => {
    const isExpanded = expandedSections[sectionKey]
    
    return (
      <Card className="mb-6">
        <CardHeader 
          className="cursor-pointer hover:bg-gray-50 transition-colors"
          onClick={() => toggleSection(sectionKey)}
        >
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Icon className="h-6 w-6 text-blue-600" />
              <span className="text-xl font-semibold">{title}</span>
            </div>
            {isExpanded ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </CardTitle>
        </CardHeader>
        {isExpanded && (
          <CardContent className="pt-0">
            {children}
          </CardContent>
        )}
      </Card>
    )
  }

  const ExecutiveSummary = () => {
    const executiveContent = llmSections.executive_summary || llmSections.executivesummary || 'Executive summary not available'
    const insights = analysisResults?.actionable_insights || []
    
    return (
      <div className="space-y-6">
        {/* Key Strategic Findings */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
          <h4 className="font-semibold text-blue-900 mb-3">Key Strategic Findings</h4>
          <div className="prose text-blue-800 whitespace-pre-line">
            {executiveContent.split('\n').slice(0, 6).join('\n')}
          </div>
        </div>
        
        {/* Strategic Insights Grid */}
        {insights.length > 0 && (
          <div className="grid md:grid-cols-2 gap-4">
            {insights.slice(0, 4).map((insight, idx) => (
              <div key={idx} className="border rounded-lg p-4 bg-white shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={insight.priority === 'High' ? 'destructive' : 'default'}>
                    {insight.priority}
                  </Badge>
                  <Badge variant="outline">{insight.timeline}</Badge>
                </div>
                <h5 className="font-medium mb-2">{insight.finding}</h5>
                <p className="text-sm text-gray-600 mb-2">{insight.impact}</p>
                <p className="text-sm font-medium text-blue-600">{insight.recommendation}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  const CompetitiveIntelligence = () => {
    const competitiveContent = llmSections.competitive_intelligence || llmSections.competitiveintelligence || 'Competitive analysis not available'
    
    return (
      <div className="space-y-6">
        <div className="prose max-w-none">
          <div className="whitespace-pre-line text-gray-800 leading-relaxed">
            {competitiveContent}
          </div>
        </div>
        
        {/* Key Competitive Metrics */}
        {analysisResults?.competitive_intelligence && (
          <div className="grid md:grid-cols-3 gap-4 mt-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <h5 className="font-medium text-green-800 mb-2">Competitive Strengths</h5>
              <p className="text-sm text-green-700">
                {analysisResults.competitive_intelligence.analysis_note || 'Competitive advantages identified in analysis'}
              </p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h5 className="font-medium text-yellow-800 mb-2">Market Position</h5>
              <p className="text-sm text-yellow-700">
                {analysisResults.competitive_intelligence.market_positioning || 'Market positioning analysis available'}
              </p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <h5 className="font-medium text-red-800 mb-2">Competitive Threats</h5>
              <p className="text-sm text-red-700">
                {analysisResults.competitive_intelligence.competitive_landscape || 'Competitive landscape evaluation'}
              </p>
            </div>
          </div>
        )}
      </div>
    )
  }

  const StrategicRecommendations = () => {
    const recommendationsContent = llmSections.strategic_recommendations || llmSections.strategicrecommendations || 'Strategic recommendations not available'
    
    return (
      <div className="space-y-6">
        <div className="prose max-w-none">
          <div className="whitespace-pre-line text-gray-800 leading-relaxed">
            {recommendationsContent}
          </div>
        </div>
        
        {/* Implementation Timeline */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h4 className="font-semibold mb-4">Implementation Roadmap</h4>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="font-medium">Immediate Actions (0-6 months)</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="font-medium">Medium-term Strategy (6-18 months)</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="font-medium">Long-term Vision (18+ months)</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Report Header */}
      <Card className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                Brand Strategic Analysis
              </h1>
              <p className="text-blue-100 text-lg">
                Comprehensive consulting report for {analysisResults?.brand_name || 'Brand'}
              </p>
              <div className="flex items-center gap-4 mt-4">
                <Badge variant="secondary" className="bg-white/20 text-white">
                  McKinsey-Level Analysis
                </Badge>
                <Badge variant="secondary" className="bg-white/20 text-white">
                  Real Data Integration
                </Badge>
                <Badge variant="secondary" className="bg-white/20 text-white">
                  AI-Powered Insights
                </Badge>
              </div>
            </div>
            <CheckCircle className="h-16 w-16 text-green-300" />
          </div>
        </CardContent>
      </Card>

      {/* Data Sources Quality Indicator */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Analysis Data Sources</h3>
            <div className="flex gap-4">
              {analysisResults?.data_sources && Object.entries(analysisResults.data_sources).map(([source, available]) => (
                <div key={source} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${available ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <span className="text-sm capitalize">{source.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Executive Summary */}
      <ExpandableSection 
        title="Executive Summary" 
        icon={Lightbulb} 
        sectionKey="executive"
        defaultExpanded={true}
      >
        <ExecutiveSummary />
      </ExpandableSection>

      {/* Brand Positioning Analysis */}
      <ExpandableSection 
        title="Brand Positioning Analysis" 
        icon={Target} 
        sectionKey="positioning"
      >
        <div className="prose max-w-none">
          <div className="whitespace-pre-line text-gray-800 leading-relaxed">
            {llmSections.brand_positioning_analysis || llmSections.brandpositioninganalysis || 'Brand positioning analysis not available'}
          </div>
        </div>
      </ExpandableSection>

      {/* Competitive Intelligence */}
      <ExpandableSection 
        title="Competitive Intelligence" 
        icon={Building2} 
        sectionKey="competitive"
      >
        <CompetitiveIntelligence />
      </ExpandableSection>

      {/* Market Performance & Dynamics */}
      <ExpandableSection 
        title="Market Performance & Dynamics" 
        icon={TrendingUp} 
        sectionKey="market"
      >
        <div className="space-y-6">
          <div className="prose max-w-none">
            <div className="whitespace-pre-line text-gray-800 leading-relaxed">
              {llmSections.market_performance_and_dynamics || llmSections.marketperformancedynamics || 'Market performance analysis not available'}
            </div>
          </div>
          
          {/* Real News Data Integration */}
          {analysisResults?.media_analysis?.media_presence && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-3">Real Market Data</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {analysisResults.media_analysis.media_presence.total_mentions_12mo || 0}
                  </div>
                  <div className="text-sm text-gray-600">Media Mentions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {analysisResults.brand_perception?.market_sentiment?.positive_percentage || 'N/A'}%
                  </div>
                  <div className="text-sm text-gray-600">Positive Sentiment</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {analysisResults.media_analysis.media_presence.estimated_reach || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-600">Estimated Reach</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600 capitalize">
                    {analysisResults.media_analysis.media_presence.momentum_trend || 'Stable'}
                  </div>
                  <div className="text-sm text-gray-600">Trend</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ExpandableSection>

      {/* Brand Equity Assessment */}
      <ExpandableSection 
        title="Brand Equity Assessment" 
        icon={Users} 
        sectionKey="equity"
      >
        <div className="prose max-w-none">
          <div className="whitespace-pre-line text-gray-800 leading-relaxed">
            {llmSections.brand_equity_assessment || llmSections.brandequityassessment || 'Brand equity assessment not available'}
          </div>
        </div>
      </ExpandableSection>

      {/* Digital Ecosystem Analysis */}
      <ExpandableSection 
        title="Digital Ecosystem Analysis" 
        icon={Globe} 
        sectionKey="digital"
      >
        <div className="prose max-w-none">
          <div className="whitespace-pre-line text-gray-800 leading-relaxed">
            {llmSections.digital_ecosystem_analysis || llmSections.digitalecosystemanalysis || 'Digital ecosystem analysis not available'}
          </div>
        </div>
      </ExpandableSection>

      {/* Strategic Recommendations */}
      <ExpandableSection 
        title="Strategic Recommendations" 
        icon={Zap} 
        sectionKey="recommendations"
        defaultExpanded={true}
      >
        <StrategicRecommendations />
      </ExpandableSection>

      {/* Professional Export Options */}
      <Card>
        <CardContent className="p-6">
          <h3 className="font-semibold mb-4">Professional Report Export</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="flex flex-col gap-2 h-20">
              <Download className="h-5 w-5" />
              <span className="text-sm">Executive Summary PDF</span>
            </Button>
            <Button variant="outline" className="flex flex-col gap-2 h-20">
              <FileText className="h-5 w-5" />
              <span className="text-sm">Full Report PDF</span>
            </Button>
            <Button variant="outline" className="flex flex-col gap-2 h-20">
              <Building2 className="h-5 w-5" />
              <span className="text-sm">Strategic Brief</span>
            </Button>
            <Button variant="outline" className="flex flex-col gap-2 h-20">
              <TrendingUp className="h-5 w-5" />
              <span className="text-sm">Competitive Analysis</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ConsultingReport