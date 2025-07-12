import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { 
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent
} from '@/components/ui/chart.jsx'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer
} from 'recharts'
import { 
  Target, 
  TrendingUp, 
  TrendingDown,
  Award,
  AlertTriangle,
  Eye,
  MessageSquare,
  Globe,
  Users,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react'

const CompetitiveIntelligence = ({ data, competitorData, brandName }) => {
  const [selectedMetric, setSelectedMetric] = useState('brandHealth')
  const [timeframe, setTimeframe] = useState('30d')
  const [viewType, setViewType] = useState('overview')

  // Chart configuration
  const chartConfig = {
    brandHealth: { label: "Brand Health", color: "hsl(var(--chart-1))" },
    sentiment: { label: "Sentiment", color: "hsl(var(--chart-2))" },
    marketShare: { label: "Market Share", color: "hsl(var(--chart-3))" },
    awareness: { label: "Awareness", color: "hsl(var(--chart-4))" },
    engagement: { label: "Engagement", color: "hsl(var(--chart-5))" }
  }

  // Generate competitive data
  const competitiveMetrics = useMemo(() => {
    const competitors = [
      { 
        name: brandName, 
        brandHealth: 85, 
        sentiment: 78, 
        marketShare: 15.2, 
        awareness: 82, 
        engagement: 4.2,
        trend: 5.2,
        isYourBrand: true
      },
      { 
        name: 'Competitor A', 
        brandHealth: 72, 
        sentiment: 65, 
        marketShare: 22.1, 
        awareness: 75, 
        engagement: 3.8,
        trend: -2.1
      },
      { 
        name: 'Competitor B', 
        brandHealth: 68, 
        sentiment: 70, 
        marketShare: 18.5, 
        awareness: 68, 
        engagement: 3.5,
        trend: 1.8
      },
      { 
        name: 'Competitor C', 
        brandHealth: 75, 
        sentiment: 62, 
        marketShare: 12.3, 
        awareness: 71, 
        engagement: 4.0,
        trend: -0.5
      },
      { 
        name: 'Competitor D', 
        brandHealth: 63, 
        sentiment: 58, 
        marketShare: 8.9, 
        awareness: 59, 
        engagement: 2.9,
        trend: -3.2
      }
    ]
    
    return competitors.sort((a, b) => b[selectedMetric] - a[selectedMetric])
  }, [selectedMetric, brandName])

  // Generate trend data
  const trendData = useMemo(() => {
    const days = 30
    const data = []
    
    for (let i = days; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      data.push({
        date: date.toISOString().split('T')[0],
        yourBrand: 85 + Math.sin(i / 5) * 5 + Math.random() * 3,
        competitorA: 72 + Math.cos(i / 7) * 4 + Math.random() * 2,
        competitorB: 68 + Math.sin(i / 6) * 3 + Math.random() * 2,
        competitorC: 75 + Math.cos(i / 4) * 6 + Math.random() * 2
      })
    }
    
    return data
  }, [])

  // Market positioning data
  const positioningData = useMemo(() => 
    competitiveMetrics.map(comp => ({
      name: comp.name,
      x: comp.marketShare,
      y: comp.brandHealth,
      size: comp.awareness,
      isYourBrand: comp.isYourBrand
    }))
  , [competitiveMetrics])

  const getTrendIcon = (trend) => {
    if (trend > 2) return { icon: TrendingUp, color: 'text-green-500' }
    if (trend < -2) return { icon: TrendingDown, color: 'text-red-500' }
    return { icon: Minus, color: 'text-gray-500' }
  }

  const getMetricColor = (value, metric) => {
    const thresholds = {
      brandHealth: { good: 75, fair: 60 },
      sentiment: { good: 70, fair: 50 },
      marketShare: { good: 15, fair: 10 },
      awareness: { good: 75, fair: 60 },
      engagement: { good: 4, fair: 3 }
    }
    
    const threshold = thresholds[metric] || { good: 75, fair: 60 }
    
    if (value >= threshold.good) return 'text-green-600'
    if (value >= threshold.fair) return 'text-yellow-600'
    return 'text-red-600'
  }

  const CompetitorCard = ({ competitor, rank }) => {
    const trendIndicator = getTrendIcon(competitor.trend)
    const TrendIcon = trendIndicator.icon
    
    return (
      <Card className={`${competitor.isYourBrand ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                rank === 1 ? 'bg-yellow-100 text-yellow-800' :
                rank === 2 ? 'bg-gray-100 text-gray-800' :
                rank === 3 ? 'bg-orange-100 text-orange-800' :
                'bg-gray-50 text-gray-600'
              }`}>
                #{rank}
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{competitor.name}</h3>
                {competitor.isYourBrand && (
                  <Badge variant="default" className="text-xs">Your Brand</Badge>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              <TrendIcon className={`h-4 w-4 ${trendIndicator.color}`} />
              <span className={`text-sm font-medium ${trendIndicator.color}`}>
                {competitor.trend > 0 ? '+' : ''}{competitor.trend.toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Brand Health</span>
              <span className={`text-sm font-medium ${getMetricColor(competitor.brandHealth, 'brandHealth')}`}>
                {competitor.brandHealth}
              </span>
            </div>
            <Progress value={competitor.brandHealth} className="h-2" />
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Sentiment</span>
                <div className={`font-medium ${getMetricColor(competitor.sentiment, 'sentiment')}`}>
                  {competitor.sentiment}%
                </div>
              </div>
              <div>
                <span className="text-gray-600">Market Share</span>
                <div className={`font-medium ${getMetricColor(competitor.marketShare, 'marketShare')}`}>
                  {competitor.marketShare}%
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const MarketPositioningChart = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-blue-600" />
          Market Positioning Map
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-80">
          <ScatterChart data={positioningData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="x" 
              name="Market Share"
              unit="%"
              domain={[0, 25]}
            />
            <YAxis 
              dataKey="y" 
              name="Brand Health"
              domain={[50, 90]}
            />
            <ChartTooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload
                  return (
                    <div className="bg-white p-3 border rounded-lg shadow-lg">
                      <p className="font-medium text-gray-900 mb-2">{data.name}</p>
                      <p className="text-sm text-gray-600">Market Share: {data.x}%</p>
                      <p className="text-sm text-gray-600">Brand Health: {data.y}</p>
                      <p className="text-sm text-gray-600">Awareness: {data.size}%</p>
                    </div>
                  )
                }
                return null
              }}
            />
            <Scatter 
              dataKey="y" 
              fill={(entry) => entry.isYourBrand ? '#3B82F6' : '#6B7280'}
            />
          </ScatterChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )

  const CompetitiveTrendsChart = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-green-600" />
          Competitive Trends
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-80">
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis domain={[60, 90]} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Line 
              type="monotone" 
              dataKey="yourBrand" 
              stroke="#3B82F6" 
              strokeWidth={3}
              name={brandName}
            />
            <Line 
              type="monotone" 
              dataKey="competitorA" 
              stroke="#6B7280" 
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Competitor A"
            />
            <Line 
              type="monotone" 
              dataKey="competitorB" 
              stroke="#9CA3AF" 
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Competitor B"
            />
            <Line 
              type="monotone" 
              dataKey="competitorC" 
              stroke="#D1D5DB" 
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Competitor C"
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Select value={selectedMetric} onValueChange={setSelectedMetric}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="brandHealth">Brand Health</SelectItem>
              <SelectItem value="sentiment">Sentiment Score</SelectItem>
              <SelectItem value="marketShare">Market Share</SelectItem>
              <SelectItem value="awareness">Brand Awareness</SelectItem>
              <SelectItem value="engagement">Engagement Rate</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 3 months</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <Tabs value={viewType} onValueChange={setViewType} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="positioning">Positioning</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Competitive Rankings */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Competitive Rankings - {chartConfig[selectedMetric]?.label}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {competitiveMetrics.map((competitor, index) => (
                <CompetitorCard 
                  key={competitor.name} 
                  competitor={competitor} 
                  rank={index + 1} 
                />
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="positioning" className="space-y-6">
          <MarketPositioningChart />
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <CompetitiveTrendsChart />
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5 text-green-600" />
                  Competitive Advantages
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3 p-3 rounded-lg bg-green-50">
                  <div className="p-1 rounded-full bg-green-100">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-green-900">
                      Leading Brand Health Score
                    </p>
                    <p className="text-xs text-green-700">
                      13 points above nearest competitor
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 rounded-lg bg-blue-50">
                  <div className="p-1 rounded-full bg-blue-100">
                    <Eye className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-blue-900">
                      Strong Brand Awareness
                    </p>
                    <p className="text-xs text-blue-700">
                      82% awareness vs 68% industry average
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-orange-600" />
                  Areas for Improvement
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3 p-3 rounded-lg bg-orange-50">
                  <div className="p-1 rounded-full bg-orange-100">
                    <Target className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-orange-900">
                      Market Share Gap
                    </p>
                    <p className="text-xs text-orange-700">
                      7% behind market leader
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 rounded-lg bg-yellow-50">
                  <div className="p-1 rounded-full bg-yellow-100">
                    <MessageSquare className="h-4 w-4 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-yellow-900">
                      Sentiment Opportunity
                    </p>
                    <p className="text-xs text-yellow-700">
                      Room for improvement in customer sentiment
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default CompetitiveIntelligence
