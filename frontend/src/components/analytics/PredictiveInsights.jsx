import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent
} from '@/components/ui/chart.jsx'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer
} from 'recharts'
import { 
  Zap, 
  TrendingUp, 
  TrendingDown,
  Brain,
  Target,
  AlertTriangle,
  CheckCircle,
  Clock,
  Lightbulb,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Award,
  Eye,
  Download,
  RefreshCw
} from 'lucide-react'

const PredictiveInsights = ({ data, predictions }) => {
  const [forecastPeriod, setForecastPeriod] = useState('30d')
  const [confidenceThreshold, setConfidenceThreshold] = useState(70)
  const [selectedScenario, setSelectedScenario] = useState('optimistic')

  // Chart configuration
  const chartConfig = {
    actual: { label: "Actual", color: "hsl(var(--chart-1))" },
    predicted: { label: "Predicted", color: "hsl(var(--chart-2))" },
    confidence: { label: "Confidence", color: "hsl(var(--chart-3))" },
    optimistic: { label: "Optimistic", color: "hsl(var(--chart-4))" },
    pessimistic: { label: "Pessimistic", color: "hsl(var(--chart-5))" }
  }

  // Generate predictive data
  const predictiveData = useMemo(() => {
    const days = forecastPeriod === '30d' ? 30 : forecastPeriod === '90d' ? 90 : 180
    const historicalDays = 30
    const data = []
    
    // Historical data
    for (let i = historicalDays; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      data.push({
        date: date.toISOString().split('T')[0],
        actual: 75 + Math.sin(i / 5) * 8 + Math.random() * 5,
        type: 'historical'
      })
    }
    
    // Predicted data
    const lastActual = data[data.length - 1].actual
    for (let i = 1; i <= days; i++) {
      const date = new Date()
      date.setDate(date.getDate() + i)
      
      // Simple trend prediction with confidence intervals
      const trendFactor = 1 + (i / days) * 0.1 // Slight upward trend
      const seasonality = Math.sin(i / 7) * 2 // Weekly seasonality
      const noise = Math.random() * 3 - 1.5
      
      const predicted = lastActual * trendFactor + seasonality + noise
      const confidence = Math.max(50, 95 - (i / days) * 30) // Decreasing confidence over time
      
      data.push({
        date: date.toISOString().split('T')[0],
        predicted: Math.max(0, Math.min(100, predicted)),
        confidence: confidence,
        optimistic: Math.max(0, Math.min(100, predicted + 5)),
        pessimistic: Math.max(0, Math.min(100, predicted - 5)),
        type: 'predicted'
      })
    }
    
    return data
  }, [forecastPeriod])

  // Generate insights and recommendations
  const insights = useMemo(() => [
    {
      id: 1,
      type: 'opportunity',
      title: 'Brand Health Growth Opportunity',
      description: 'Current trends suggest a 12% improvement in brand health over the next 30 days.',
      confidence: 85,
      impact: 'high',
      timeframe: '30 days',
      recommendation: 'Increase content marketing efforts to capitalize on positive sentiment trends.',
      metrics: ['brandHealth', 'sentiment']
    },
    {
      id: 2,
      type: 'risk',
      title: 'Competitive Pressure Alert',
      description: 'Competitor A is showing strong momentum that could impact market share.',
      confidence: 72,
      impact: 'medium',
      timeframe: '45 days',
      recommendation: 'Consider defensive marketing strategies and monitor competitor campaigns.',
      metrics: ['marketShare', 'competition']
    },
    {
      id: 3,
      type: 'trend',
      title: 'Seasonal Sentiment Pattern',
      description: 'Historical data indicates sentiment typically increases by 8% in the coming quarter.',
      confidence: 91,
      impact: 'medium',
      timeframe: '90 days',
      recommendation: 'Prepare seasonal campaigns to maximize the positive sentiment window.',
      metrics: ['sentiment', 'engagement']
    },
    {
      id: 4,
      type: 'opportunity',
      title: 'Visual Identity Optimization',
      description: 'Improving visual consistency could boost brand health by 6-8%.',
      confidence: 78,
      impact: 'high',
      timeframe: '60 days',
      recommendation: 'Implement brand guidelines across all digital touchpoints.',
      metrics: ['visual', 'brandHealth']
    }
  ], [])

  // Generate scenario analysis
  const scenarios = useMemo(() => ({
    optimistic: {
      name: 'Optimistic Scenario',
      description: 'Best-case outcomes based on positive trend continuation',
      brandHealth: { current: 85, predicted: 92, change: 8.2 },
      sentiment: { current: 78, predicted: 86, change: 10.3 },
      marketShare: { current: 15.2, predicted: 17.1, change: 12.5 },
      probability: 25
    },
    realistic: {
      name: 'Realistic Scenario',
      description: 'Most likely outcomes based on current trends',
      brandHealth: { current: 85, predicted: 88, change: 3.5 },
      sentiment: { current: 78, predicted: 81, change: 3.8 },
      marketShare: { current: 15.2, predicted: 15.8, change: 3.9 },
      probability: 50
    },
    pessimistic: {
      name: 'Pessimistic Scenario',
      description: 'Conservative outcomes accounting for potential challenges',
      brandHealth: { current: 85, predicted: 82, change: -3.5 },
      sentiment: { current: 78, predicted: 74, change: -5.1 },
      marketShare: { current: 15.2, predicted: 14.1, change: -7.2 },
      probability: 25
    }
  }), [])

  const getInsightIcon = (type) => {
    switch (type) {
      case 'opportunity': return { icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-50' }
      case 'risk': return { icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-50' }
      case 'trend': return { icon: TrendingUp, color: 'text-blue-500', bg: 'bg-blue-50' }
      default: return { icon: Lightbulb, color: 'text-yellow-500', bg: 'bg-yellow-50' }
    }
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600'
    if (confidence >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getImpactBadge = (impact) => {
    const variants = {
      high: 'destructive',
      medium: 'default',
      low: 'secondary'
    }
    return variants[impact] || 'secondary'
  }

  const InsightCard = ({ insight }) => {
    const iconConfig = getInsightIcon(insight.type)
    const Icon = iconConfig.icon
    
    return (
      <Card className="relative overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-lg ${iconConfig.bg}`}>
                <Icon className={`h-5 w-5 ${iconConfig.color}`} />
              </div>
              <div>
                <CardTitle className="text-lg">{insight.title}</CardTitle>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant={getImpactBadge(insight.impact)}>
                    {insight.impact} impact
                  </Badge>
                  <Badge variant="outline">
                    <Clock className="h-3 w-3 mr-1" />
                    {insight.timeframe}
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <div className={`text-sm font-medium ${getConfidenceColor(insight.confidence)}`}>
                {insight.confidence}%
              </div>
              <div className="text-xs text-gray-500">confidence</div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <p className="text-gray-600">{insight.description}</p>
          
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium text-gray-900">Recommendation</span>
            </div>
            <p className="text-sm text-gray-700">{insight.recommendation}</p>
          </div>
          
          <div className="flex flex-wrap gap-1">
            {insight.metrics.map(metric => (
              <Badge key={metric} variant="outline" className="text-xs">
                {metric}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const ScenarioCard = ({ scenario, isSelected, onSelect }) => (
    <Card 
      className={`cursor-pointer transition-all ${isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:shadow-md'}`}
      onClick={onSelect}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{scenario.name}</CardTitle>
          <Badge variant="outline">{scenario.probability}% likely</Badge>
        </div>
        <p className="text-sm text-gray-600">{scenario.description}</p>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {Object.entries(scenario).filter(([key]) => 
          ['brandHealth', 'sentiment', 'marketShare'].includes(key)
        ).map(([metric, values]) => (
          <div key={metric} className="flex items-center justify-between">
            <span className="text-sm text-gray-600 capitalize">{metric}</span>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">
                {values.current} → {values.predicted}
              </span>
              <div className={`flex items-center gap-1 ${
                values.change > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {values.change > 0 ? (
                  <ArrowUpRight className="h-3 w-3" />
                ) : (
                  <ArrowDownRight className="h-3 w-3" />
                )}
                <span className="text-xs font-medium">
                  {Math.abs(values.change).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Select value={forecastPeriod} onValueChange={setForecastPeriod}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="30d">30 days</SelectItem>
              <SelectItem value="90d">90 days</SelectItem>
              <SelectItem value="180d">6 months</SelectItem>
            </SelectContent>
          </Select>
          
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Min Confidence:</span>
            <Select value={confidenceThreshold.toString()} onValueChange={(value) => setConfidenceThreshold(parseInt(value))}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="50">50%</SelectItem>
                <SelectItem value="70">70%</SelectItem>
                <SelectItem value="80">80%</SelectItem>
                <SelectItem value="90">90%</SelectItem>
              </SelectContent>
            </Select>
          </div>
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

      <Tabs defaultValue="forecast" className="space-y-6">
        <TabsList>
          <TabsTrigger value="forecast">Forecast</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
        </TabsList>

        <TabsContent value="forecast" className="space-y-6">
          {/* Predictive Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-600" />
                Brand Health Forecast - {forecastPeriod.toUpperCase()}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <LineChart data={predictiveData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis domain={[60, 100]} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="var(--color-actual)"
                    strokeWidth={3}
                    dot={{ fill: "var(--color-actual)", strokeWidth: 2, r: 3 }}
                    connectNulls={false}
                    name="Actual"
                  />
                  
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    stroke="var(--color-predicted)"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ fill: "var(--color-predicted)", strokeWidth: 2, r: 3 }}
                    connectNulls={false}
                    name="Predicted"
                  />
                  
                  <Area
                    type="monotone"
                    dataKey="optimistic"
                    stroke="var(--color-optimistic)"
                    fill="var(--color-optimistic)"
                    fillOpacity={0.1}
                    strokeWidth={1}
                    name="Optimistic"
                  />
                  
                  <Area
                    type="monotone"
                    dataKey="pessimistic"
                    stroke="var(--color-pessimistic)"
                    fill="var(--color-pessimistic)"
                    fillOpacity={0.1}
                    strokeWidth={1}
                    name="Pessimistic"
                  />
                </LineChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {insights
              .filter(insight => insight.confidence >= confidenceThreshold)
              .map(insight => (
                <InsightCard key={insight.id} insight={insight} />
              ))}
          </div>
        </TabsContent>

        <TabsContent value="scenarios" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {Object.entries(scenarios).map(([key, scenario]) => (
              <ScenarioCard
                key={key}
                scenario={scenario}
                isSelected={selectedScenario === key}
                onSelect={() => setSelectedScenario(key)}
              />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default PredictiveInsights
