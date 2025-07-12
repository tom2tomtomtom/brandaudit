import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Heart,
  Eye,
  MessageSquare,
  Globe,
  Target,
  Award,
  AlertTriangle,
  CheckCircle,
  ArrowUpRight,
  ArrowDownRight,
  Activity
} from 'lucide-react'

const BrandHealthOverview = ({ data, layout = 'standard' }) => {
  if (!data) return null

  const { brandHealth, keyMetrics, sentimentTrends, competitivePosition } = data

  // Helper function to get trend icon and color
  const getTrendIndicator = (trend) => {
    if (trend > 5) return { icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-50' }
    if (trend < -5) return { icon: TrendingDown, color: 'text-red-500', bg: 'bg-red-50' }
    return { icon: Minus, color: 'text-gray-500', bg: 'bg-gray-50' }
  }

  // Helper function to get health score color
  const getHealthColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  // Helper function to get health status
  const getHealthStatus = (score) => {
    if (score >= 80) return { label: 'Excellent', color: 'bg-green-500' }
    if (score >= 60) return { label: 'Good', color: 'bg-yellow-500' }
    if (score >= 40) return { label: 'Fair', color: 'bg-orange-500' }
    return { label: 'Poor', color: 'bg-red-500' }
  }

  const MetricCard = ({ title, value, subtitle, trend, icon: Icon, score, format = 'number' }) => {
    const trendIndicator = getTrendIndicator(trend || 0)
    const TrendIcon = trendIndicator.icon

    const formatValue = (val) => {
      if (format === 'percentage') return `${val}%`
      if (format === 'currency') return `$${val.toLocaleString()}`
      if (format === 'number') return val.toLocaleString()
      return val
    }

    return (
      <Card className="relative overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {Icon && (
                <div className="p-2 rounded-lg bg-blue-50">
                  <Icon className="h-5 w-5 text-blue-600" />
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-600">{title}</p>
                <p className="text-2xl font-bold text-gray-900">{formatValue(value)}</p>
                {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
              </div>
            </div>
            
            {trend !== undefined && (
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${trendIndicator.bg}`}>
                <TrendIcon className={`h-4 w-4 ${trendIndicator.color}`} />
                <span className={`text-sm font-medium ${trendIndicator.color}`}>
                  {Math.abs(trend).toFixed(1)}%
                </span>
              </div>
            )}
          </div>
          
          {score !== undefined && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-500">Health Score</span>
                <span className={`text-sm font-medium ${getHealthColor(score)}`}>
                  {score}/100
                </span>
              </div>
              <Progress value={score} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const HealthScoreCard = () => {
    const status = getHealthStatus(brandHealth.overall)
    
    return (
      <Card className="col-span-full lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-500" />
            Overall Brand Health
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="text-4xl font-bold text-gray-900 mb-2">
                {brandHealth.overall}
                <span className="text-lg text-gray-500 ml-1">/100</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${status.color}`}></div>
                <span className="text-sm font-medium text-gray-600">{status.label}</span>
                {brandHealth.trend !== undefined && (
                  <Badge variant={brandHealth.trend > 0 ? 'default' : 'destructive'} className="ml-2">
                    {brandHealth.trend > 0 ? '+' : ''}{brandHealth.trend.toFixed(1)}%
                  </Badge>
                )}
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-sm text-gray-500 mb-1">vs. Industry Avg</div>
              <div className="flex items-center gap-1">
                {competitivePosition.brandScore > competitivePosition.avgCompetitorScore ? (
                  <ArrowUpRight className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm font-medium ${
                  competitivePosition.brandScore > competitivePosition.avgCompetitorScore 
                    ? 'text-green-600' 
                    : 'text-red-600'
                }`}>
                  {Math.abs(competitivePosition.brandScore - competitivePosition.avgCompetitorScore).toFixed(1)} pts
                </span>
              </div>
            </div>
          </div>

          {/* Health Score Breakdown */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Visual Identity</span>
                <span className="text-sm font-medium">{brandHealth.visual}%</span>
              </div>
              <Progress value={brandHealth.visual} className="h-2" />
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Brand Sentiment</span>
                <span className="text-sm font-medium">{brandHealth.sentiment}%</span>
              </div>
              <Progress value={brandHealth.sentiment} className="h-2" />
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">News Coverage</span>
                <span className="text-sm font-medium">{brandHealth.news}%</span>
              </div>
              <Progress value={brandHealth.news} className="h-2" />
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Market Position</span>
                <span className="text-sm font-medium">
                  #{competitivePosition.ranking}
                </span>
              </div>
              <Progress value={Math.max(0, 100 - (competitivePosition.ranking - 1) * 20)} className="h-2" />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const KeyInsightsCard = () => (
    <Card className="col-span-full lg:col-span-1">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-blue-500" />
          Key Insights
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Sentiment Insight */}
        <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-50">
          <div className="p-1 rounded-full bg-blue-100">
            {sentimentTrends.change > 0 ? (
              <CheckCircle className="h-4 w-4 text-blue-600" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-blue-600" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-blue-900">
              Sentiment {sentimentTrends.change > 0 ? 'Improving' : 'Declining'}
            </p>
            <p className="text-xs text-blue-700">
              {Math.abs(sentimentTrends.change * 100).toFixed(1)}% change from last period
            </p>
          </div>
        </div>

        {/* Competitive Position */}
        <div className="flex items-start gap-3 p-3 rounded-lg bg-green-50">
          <div className="p-1 rounded-full bg-green-100">
            <Target className="h-4 w-4 text-green-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-green-900">
              Market Position #{competitivePosition.ranking}
            </p>
            <p className="text-xs text-green-700">
              {competitivePosition.marketShare.toFixed(1)}% market share
            </p>
          </div>
        </div>

        {/* Visual Assets */}
        <div className="flex items-start gap-3 p-3 rounded-lg bg-purple-50">
          <div className="p-1 rounded-full bg-purple-100">
            <Eye className="h-4 w-4 text-purple-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-purple-900">
              {keyMetrics.visualAssets} Visual Assets
            </p>
            <p className="text-xs text-purple-700">
              Brand consistency score: {brandHealth.visual}%
            </p>
          </div>
        </div>

        {/* News Coverage */}
        <div className="flex items-start gap-3 p-3 rounded-lg bg-orange-50">
          <div className="p-1 rounded-full bg-orange-100">
            <MessageSquare className="h-4 w-4 text-orange-600" />
          </div>
          <div>
            <p className="text-sm font-medium text-orange-900">
              {keyMetrics.totalMentions} News Mentions
            </p>
            <p className="text-xs text-orange-700">
              {brandHealth.news}% positive coverage
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  if (layout === 'executive') {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <HealthScoreCard />
        <KeyInsightsCard />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Health Score */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <HealthScoreCard />
        <KeyInsightsCard />
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Brand Sentiment"
          value={Math.round(sentimentTrends.current * 100)}
          subtitle="Current sentiment score"
          trend={sentimentTrends.change * 100}
          icon={MessageSquare}
          score={brandHealth.sentiment}
          format="percentage"
        />
        
        <MetricCard
          title="Visual Consistency"
          value={brandHealth.visual}
          subtitle="Across all touchpoints"
          trend={brandHealth.trend}
          icon={Eye}
          score={brandHealth.visual}
          format="percentage"
        />
        
        <MetricCard
          title="Market Position"
          value={competitivePosition.ranking}
          subtitle={`${competitivePosition.marketShare.toFixed(1)}% market share`}
          icon={Target}
          score={Math.max(0, 100 - (competitivePosition.ranking - 1) * 20)}
        />
        
        <MetricCard
          title="News Coverage"
          value={keyMetrics.totalMentions}
          subtitle={`${brandHealth.news}% positive sentiment`}
          trend={brandHealth.trend}
          icon={Globe}
          score={brandHealth.news}
        />
      </div>
    </div>
  )
}

export default BrandHealthOverview
