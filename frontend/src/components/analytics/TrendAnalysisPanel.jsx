import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent
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
  TrendingUp, 
  TrendingDown,
  Calendar,
  Activity,
  BarChart3,
  Zap,
  Target,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Download,
  Filter
} from 'lucide-react'

const TrendAnalysisPanel = ({ data, historicalData, dateRange }) => {
  const [selectedMetrics, setSelectedMetrics] = useState(['brandHealth', 'sentiment'])
  const [trendPeriod, setTrendPeriod] = useState('30d')
  const [analysisType, setAnalysisType] = useState('comparative')

  // Chart configuration
  const chartConfig = {
    brandHealth: { label: "Brand Health", color: "hsl(var(--chart-1))" },
    sentiment: { label: "Sentiment", color: "hsl(var(--chart-2))" },
    awareness: { label: "Awareness", color: "hsl(var(--chart-3))" },
    engagement: { label: "Engagement", color: "hsl(var(--chart-4))" },
    marketShare: { label: "Market Share", color: "hsl(var(--chart-5))" }
  }

  // Generate trend data
  const trendData = useMemo(() => {
    const days = trendPeriod === '7d' ? 7 : trendPeriod === '30d' ? 30 : trendPeriod === '90d' ? 90 : 365
    const data = []
    
    for (let i = days; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      // Generate realistic trend data with some seasonality
      const baseHealth = 75
      const healthTrend = Math.sin(i / 10) * 5 + Math.random() * 8
      const sentimentBase = 65
      const sentimentTrend = Math.cos(i / 15) * 10 + Math.random() * 6
      
      data.push({
        date: date.toISOString().split('T')[0],
        brandHealth: Math.max(0, Math.min(100, baseHealth + healthTrend)),
        sentiment: Math.max(0, Math.min(100, sentimentBase + sentimentTrend)),
        awareness: Math.max(0, Math.min(100, 70 + Math.sin(i / 8) * 8 + Math.random() * 5)),
        engagement: Math.max(0, Math.min(10, 3.5 + Math.cos(i / 12) * 1.5 + Math.random() * 0.5)),
        marketShare: Math.max(0, Math.min(30, 15 + Math.sin(i / 20) * 3 + Math.random() * 2)),
        mentions: Math.floor(Math.random() * 50) + 20,
        reach: Math.floor(Math.random() * 10000) + 5000
      })
    }
    
    return data
  }, [trendPeriod])

  // Calculate trend statistics
  const trendStats = useMemo(() => {
    if (trendData.length < 2) return {}
    
    const calculateTrend = (metric) => {
      const recent = trendData.slice(-7).reduce((sum, item) => sum + item[metric], 0) / 7
      const previous = trendData.slice(-14, -7).reduce((sum, item) => sum + item[metric], 0) / 7
      const change = ((recent - previous) / previous) * 100
      
      return {
        current: recent,
        previous: previous,
        change: change,
        direction: change > 2 ? 'up' : change < -2 ? 'down' : 'stable'
      }
    }
    
    return {
      brandHealth: calculateTrend('brandHealth'),
      sentiment: calculateTrend('sentiment'),
      awareness: calculateTrend('awareness'),
      engagement: calculateTrend('engagement'),
      marketShare: calculateTrend('marketShare')
    }
  }, [trendData])

  // Seasonal analysis
  const seasonalData = useMemo(() => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.map((month, index) => ({
      month,
      brandHealth: 75 + Math.sin(index / 2) * 10 + Math.random() * 5,
      sentiment: 65 + Math.cos(index / 3) * 12 + Math.random() * 6,
      engagement: 3.5 + Math.sin(index / 4) * 1.2 + Math.random() * 0.3
    }))
  }, [])

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up': return { icon: TrendingUp, color: 'text-green-500' }
      case 'down': return { icon: TrendingDown, color: 'text-red-500' }
      default: return { icon: Minus, color: 'text-gray-500' }
    }
  }

  const TrendCard = ({ title, metric, icon: Icon }) => {
    const trend = trendStats[metric]
    if (!trend) return null
    
    const trendIndicator = getTrendIcon(trend.direction)
    const TrendIcon = trendIndicator.icon
    
    return (
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Icon className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-600">{title}</span>
            </div>
            <div className="flex items-center gap-1">
              <TrendIcon className={`h-4 w-4 ${trendIndicator.color}`} />
              <span className={`text-sm font-medium ${trendIndicator.color}`}>
                {trend.change > 0 ? '+' : ''}{trend.change.toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {metric === 'engagement' ? trend.current.toFixed(1) : Math.round(trend.current)}
            {metric === 'engagement' ? '' : metric === 'marketShare' ? '%' : ''}
          </div>
          
          <div className="text-xs text-gray-500">
            vs. previous period: {Math.round(trend.previous)}
          </div>
        </CardContent>
      </Card>
    )
  }

  const MetricToggle = ({ metric, label }) => {
    const isSelected = selectedMetrics.includes(metric)
    
    return (
      <Button
        variant={isSelected ? "default" : "outline"}
        size="sm"
        onClick={() => {
          if (isSelected) {
            setSelectedMetrics(prev => prev.filter(m => m !== metric))
          } else {
            setSelectedMetrics(prev => [...prev, metric])
          }
        }}
        className="text-xs"
      >
        {label}
      </Button>
    )
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Select value={trendPeriod} onValueChange={setTrendPeriod}>
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
          
          <Select value={analysisType} onValueChange={setAnalysisType}>
            <SelectTrigger className="w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="comparative">Comparative</SelectItem>
              <SelectItem value="seasonal">Seasonal</SelectItem>
              <SelectItem value="correlation">Correlation</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Trend Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <TrendCard title="Brand Health" metric="brandHealth" icon={Activity} />
        <TrendCard title="Sentiment" metric="sentiment" icon={TrendingUp} />
        <TrendCard title="Awareness" metric="awareness" icon={Target} />
        <TrendCard title="Engagement" metric="engagement" icon={Zap} />
        <TrendCard title="Market Share" metric="marketShare" icon={BarChart3} />
      </div>

      {/* Metric Selection */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Select Metrics to Compare</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <MetricToggle metric="brandHealth" label="Brand Health" />
            <MetricToggle metric="sentiment" label="Sentiment" />
            <MetricToggle metric="awareness" label="Awareness" />
            <MetricToggle metric="engagement" label="Engagement" />
            <MetricToggle metric="marketShare" label="Market Share" />
          </div>
        </CardContent>
      </Card>

      <Tabs value={analysisType} onValueChange={setAnalysisType} className="space-y-6">
        <TabsContent value="comparative" className="space-y-6">
          {/* Multi-Metric Trend Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                Trend Analysis - {trendPeriod.toUpperCase()}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-96">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <ChartLegend content={<ChartLegendContent />} />
                  
                  {selectedMetrics.map((metric) => (
                    <Line
                      key={metric}
                      type="monotone"
                      dataKey={metric}
                      stroke={chartConfig[metric]?.color}
                      strokeWidth={2}
                      dot={{ fill: chartConfig[metric]?.color, strokeWidth: 2, r: 3 }}
                      activeDot={{ r: 5 }}
                      name={chartConfig[metric]?.label}
                    />
                  ))}
                </LineChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Area Chart for Volume Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-green-600" />
                Volume & Reach Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-64">
                <AreaChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Area
                    type="monotone"
                    dataKey="mentions"
                    stackId="1"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                    name="Mentions"
                  />
                  <Area
                    type="monotone"
                    dataKey="reach"
                    stackId="2"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.6}
                    name="Reach"
                  />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="seasonal" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-purple-600" />
                Seasonal Patterns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <BarChart data={seasonalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="brandHealth" fill="var(--color-brandHealth)" name="Brand Health" />
                  <Bar dataKey="sentiment" fill="var(--color-sentiment)" name="Sentiment" />
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="correlation" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-orange-600" />
                Metric Correlations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-900">Strong Correlations</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="text-sm font-medium">Brand Health ↔ Sentiment</span>
                      <Badge variant="default">0.87</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <span className="text-sm font-medium">Awareness ↔ Market Share</span>
                      <Badge variant="default">0.72</Badge>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-900">Weak Correlations</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium">Engagement ↔ Market Share</span>
                      <Badge variant="outline">0.23</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium">Sentiment ↔ Engagement</span>
                      <Badge variant="outline">0.31</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default TrendAnalysisPanel
