import React, { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Brain, 
  Search, 
  Lightbulb,
  TrendingUp,
  Target,
  AlertTriangle,
  CheckCircle,
  Zap,
  MessageSquare,
  Eye,
  Star,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Sparkles,
  Robot,
  BookOpen,
  Filter
} from 'lucide-react'

const AIInsightsEngine = ({ data, brandName, onInsightAction }) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [insights, setInsights] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState('')
  const [queryResults, setQueryResults] = useState(null)
  const [selectedInsightType, setSelectedInsightType] = useState('all')

  // AI-generated insights based on data
  const generateInsights = useMemo(() => {
    if (!data) return []

    const insights = []
    
    // Brand Health Insights
    if (data.brandHealth) {
      if (data.brandHealth.overall > 80) {
        insights.push({
          id: 'bh-1',
          type: 'positive',
          category: 'Brand Health',
          title: 'Exceptional Brand Performance',
          description: `Your brand health score of ${data.brandHealth.overall} places you in the top tier of brand performance. This indicates strong market positioning and customer perception.`,
          confidence: 0.92,
          impact: 'high',
          actionable: true,
          recommendation: 'Leverage this strong position to expand into new markets or launch premium product lines.',
          dataPoints: ['Brand Health Score', 'Market Position'],
          aiGenerated: true,
          timestamp: new Date().toISOString()
        })
      }
      
      if (data.brandHealth.visual < 70) {
        insights.push({
          id: 'bh-2',
          type: 'opportunity',
          category: 'Visual Identity',
          title: 'Visual Consistency Improvement Opportunity',
          description: `Visual consistency score of ${data.brandHealth.visual}% suggests room for improvement in brand visual elements across touchpoints.`,
          confidence: 0.85,
          impact: 'medium',
          actionable: true,
          recommendation: 'Conduct a comprehensive brand guidelines audit and implement consistent visual standards across all channels.',
          dataPoints: ['Visual Consistency Score', 'Brand Guidelines'],
          aiGenerated: true,
          timestamp: new Date().toISOString()
        })
      }
    }

    // Competitive Insights
    if (data.competitivePosition) {
      if (data.competitivePosition.ranking <= 3) {
        insights.push({
          id: 'cp-1',
          type: 'positive',
          category: 'Competitive Position',
          title: 'Strong Market Leadership',
          description: `Ranking #${data.competitivePosition.ranking} in the market demonstrates strong competitive positioning and market share.`,
          confidence: 0.88,
          impact: 'high',
          actionable: true,
          recommendation: 'Focus on defensive strategies to maintain market position while exploring adjacent market opportunities.',
          dataPoints: ['Market Ranking', 'Competitive Analysis'],
          aiGenerated: true,
          timestamp: new Date().toISOString()
        })
      }
    }

    // Sentiment Insights
    if (data.sentimentTrends) {
      if (data.sentimentTrends.change > 0.1) {
        insights.push({
          id: 'st-1',
          type: 'positive',
          category: 'Sentiment',
          title: 'Positive Sentiment Momentum',
          description: `Brand sentiment has improved by ${(data.sentimentTrends.change * 100).toFixed(1)}%, indicating positive market reception and customer satisfaction.`,
          confidence: 0.79,
          impact: 'medium',
          actionable: true,
          recommendation: 'Capitalize on positive sentiment with targeted marketing campaigns and customer engagement initiatives.',
          dataPoints: ['Sentiment Score', 'Trend Analysis'],
          aiGenerated: true,
          timestamp: new Date().toISOString()
        })
      }
    }

    return insights
  }, [data])

  // AI-generated recommendations
  const generateRecommendations = useMemo(() => {
    if (!data) return []

    const recommendations = []

    // Strategic recommendations based on data patterns
    recommendations.push({
      id: 'rec-1',
      category: 'Strategic',
      title: 'Brand Positioning Optimization',
      description: 'Based on competitive analysis and market trends, consider repositioning to emphasize unique value propositions.',
      priority: 'high',
      effort: 'medium',
      timeline: '3-6 months',
      expectedImpact: 'Increase brand differentiation by 15-20%',
      steps: [
        'Conduct customer perception research',
        'Analyze competitor positioning gaps',
        'Develop new positioning strategy',
        'Test messaging with target audience',
        'Implement across all touchpoints'
      ],
      aiGenerated: true,
      confidence: 0.84
    })

    recommendations.push({
      id: 'rec-2',
      category: 'Tactical',
      title: 'Digital Presence Enhancement',
      description: 'Strengthen digital brand presence through content marketing and social media optimization.',
      priority: 'medium',
      effort: 'low',
      timeline: '1-3 months',
      expectedImpact: 'Improve online sentiment by 10-15%',
      steps: [
        'Audit current digital presence',
        'Develop content strategy',
        'Optimize social media profiles',
        'Implement SEO improvements',
        'Monitor and adjust based on performance'
      ],
      aiGenerated: true,
      confidence: 0.76
    })

    return recommendations
  }, [data])

  // Natural language query processing
  const processNaturalLanguageQuery = async (query) => {
    setIsGenerating(true)
    
    try {
      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Mock AI response based on query
      const response = {
        query: query,
        answer: generateAIResponse(query),
        confidence: 0.82,
        sources: ['Brand Health Data', 'Competitive Analysis', 'Sentiment Trends'],
        relatedInsights: generateInsights.slice(0, 2),
        timestamp: new Date().toISOString()
      }
      
      setQueryResults(response)
    } catch (error) {
      console.error('Failed to process query:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  // Generate AI response based on query
  const generateAIResponse = (query) => {
    const lowerQuery = query.toLowerCase()
    
    if (lowerQuery.includes('brand health') || lowerQuery.includes('performance')) {
      return `Based on the current data, your brand health score is ${data?.brandHealth?.overall || 'N/A'}/100, which indicates ${data?.brandHealth?.overall > 80 ? 'excellent' : data?.brandHealth?.overall > 60 ? 'good' : 'moderate'} performance. Key strengths include visual consistency and market positioning, while opportunities exist in sentiment improvement and competitive differentiation.`
    }
    
    if (lowerQuery.includes('competitor') || lowerQuery.includes('competition')) {
      return `Your competitive position shows a ranking of #${data?.competitivePosition?.ranking || 'N/A'} in the market with ${data?.competitivePosition?.marketShare?.toFixed(1) || 'N/A'}% market share. This positions you ${data?.competitivePosition?.ranking <= 3 ? 'strongly' : 'moderately'} against competitors, with opportunities to leverage your brand health advantage.`
    }
    
    if (lowerQuery.includes('sentiment') || lowerQuery.includes('perception')) {
      return `Current brand sentiment stands at ${Math.round((data?.sentimentTrends?.current || 0) * 100)}% positive, with a recent ${data?.sentimentTrends?.change > 0 ? 'upward' : 'downward'} trend. This suggests ${data?.sentimentTrends?.change > 0 ? 'improving' : 'declining'} customer perception and market reception.`
    }
    
    if (lowerQuery.includes('recommend') || lowerQuery.includes('improve')) {
      return `Based on your brand analytics, I recommend focusing on: 1) Strengthening visual consistency across touchpoints, 2) Leveraging positive sentiment momentum through targeted campaigns, 3) Maintaining competitive position through defensive strategies, and 4) Exploring adjacent market opportunities for growth.`
    }
    
    return `Based on your brand analytics data, I can see several key patterns and opportunities. Your overall brand performance shows ${data?.brandHealth?.overall > 70 ? 'strong' : 'moderate'} health metrics with particular strengths in market positioning. Would you like me to elaborate on any specific aspect of your brand performance?`
  }

  // Filter insights by type
  const filteredInsights = useMemo(() => {
    if (selectedInsightType === 'all') return generateInsights
    return generateInsights.filter(insight => insight.type === selectedInsightType)
  }, [generateInsights, selectedInsightType])

  // Search insights
  const searchedInsights = useMemo(() => {
    if (!searchQuery) return filteredInsights
    return filteredInsights.filter(insight =>
      insight.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      insight.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      insight.category.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [filteredInsights, searchQuery])

  const InsightCard = ({ insight }) => {
    const getTypeIcon = () => {
      switch (insight.type) {
        case 'positive': return CheckCircle
        case 'opportunity': return Lightbulb
        case 'warning': return AlertTriangle
        default: return Brain
      }
    }

    const getTypeColor = () => {
      switch (insight.type) {
        case 'positive': return 'text-green-600'
        case 'opportunity': return 'text-blue-600'
        case 'warning': return 'text-yellow-600'
        default: return 'text-gray-600'
      }
    }

    const Icon = getTypeIcon()

    return (
      <Card className="relative">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <Icon className={`h-5 w-5 mt-0.5 ${getTypeColor()}`} />
              <div>
                <CardTitle className="text-lg">{insight.title}</CardTitle>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="outline">{insight.category}</Badge>
                  <Badge variant={insight.impact === 'high' ? 'destructive' : insight.impact === 'medium' ? 'default' : 'secondary'}>
                    {insight.impact} impact
                  </Badge>
                  {insight.aiGenerated && (
                    <Badge variant="outline" className="flex items-center gap-1">
                      <Sparkles className="h-3 w-3" />
                      AI Generated
                    </Badge>
                  )}
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {Math.round(insight.confidence * 100)}%
              </div>
              <div className="text-xs text-gray-500">confidence</div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <p className="text-gray-700">{insight.description}</p>
          
          {insight.recommendation && (
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Recommendation</span>
              </div>
              <p className="text-sm text-blue-800">{insight.recommendation}</p>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <div className="flex flex-wrap gap-1">
              {insight.dataPoints?.map(point => (
                <Badge key={point} variant="outline" className="text-xs">
                  {point}
                </Badge>
              ))}
            </div>
            
            <div className="flex gap-2">
              <Button variant="ghost" size="sm">
                <ThumbsUp className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <ThumbsDown className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const RecommendationCard = ({ recommendation }) => (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg">{recommendation.title}</CardTitle>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">{recommendation.category}</Badge>
              <Badge variant={recommendation.priority === 'high' ? 'destructive' : 'default'}>
                {recommendation.priority} priority
              </Badge>
            </div>
          </div>
          
          <div className="text-right text-sm">
            <div className="font-medium">{recommendation.timeline}</div>
            <div className="text-gray-500">{recommendation.effort} effort</div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <p className="text-gray-700">{recommendation.description}</p>
        
        <div className="p-3 bg-green-50 rounded-lg">
          <div className="text-sm font-medium text-green-900 mb-1">Expected Impact</div>
          <div className="text-sm text-green-800">{recommendation.expectedImpact}</div>
        </div>
        
        <div>
          <div className="text-sm font-medium text-gray-900 mb-2">Implementation Steps</div>
          <ol className="text-sm text-gray-700 space-y-1">
            {recommendation.steps.map((step, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-600 font-medium">{index + 1}.</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Confidence: {Math.round(recommendation.confidence * 100)}%
          </div>
          <Button size="sm">
            <Target className="h-4 w-4 mr-2" />
            Implement
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* AI Query Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Robot className="h-5 w-5 text-blue-600" />
            AI Analytics Assistant
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Input
                placeholder="Ask me anything about your brand analytics... (e.g., 'How is my brand performing?' or 'What should I improve?')"
                value={naturalLanguageQuery}
                onChange={(e) => setNaturalLanguageQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && processNaturalLanguageQuery(naturalLanguageQuery)}
              />
            </div>
            <Button 
              onClick={() => processNaturalLanguageQuery(naturalLanguageQuery)}
              disabled={isGenerating || !naturalLanguageQuery.trim()}
            >
              {isGenerating ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
            </Button>
          </div>
          
          {queryResults && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="h-4 w-4 text-blue-600" />
                <span className="font-medium text-gray-900">AI Response</span>
                <Badge variant="outline">{Math.round(queryResults.confidence * 100)}% confidence</Badge>
              </div>
              <p className="text-gray-700 mb-3">{queryResults.answer}</p>
              <div className="text-xs text-gray-500">
                Sources: {queryResults.sources.join(', ')}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Insights and Recommendations */}
      <Tabs defaultValue="insights" className="space-y-6">
        <TabsList>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            AI Insights ({generateInsights.length})
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Recommendations ({generateRecommendations.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="insights" className="space-y-6">
          {/* Insights Controls */}
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search insights..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="max-w-md"
              />
            </div>
            
            <select
              value={selectedInsightType}
              onChange={(e) => setSelectedInsightType(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              <option value="all">All Types</option>
              <option value="positive">Positive</option>
              <option value="opportunity">Opportunities</option>
              <option value="warning">Warnings</option>
            </select>
          </div>

          {/* Insights Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {searchedInsights.map(insight => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>

          {searchedInsights.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Brain className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No insights found matching your criteria</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {generateRecommendations.map(recommendation => (
              <RecommendationCard key={recommendation.id} recommendation={recommendation} />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default AIInsightsEngine
