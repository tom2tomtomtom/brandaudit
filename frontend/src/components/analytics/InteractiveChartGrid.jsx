import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
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
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts'
import { 
  TrendingUp, 
  BarChart3, 
  PieChart as PieChartIcon,
  Activity,
  Target,
  Zap,
  Eye,
  Maximize2,
  Download,
  Filter,
  RefreshCw
} from 'lucide-react'

const InteractiveChartGrid = ({ data, filters, onDrillDown }) => {
  const [selectedChart, setSelectedChart] = useState(null)
  const [chartType, setChartType] = useState('line')
  const [timeframe, setTimeframe] = useState('30d')

  // Chart configuration
  const chartConfig = {
    brandHealth: {
      label: "Brand Health",
      color: "hsl(var(--chart-1))",
    },
    sentiment: {
      label: "Sentiment",
      color: "hsl(var(--chart-2))",
    },
    competition: {
      label: "Competition",
      color: "hsl(var(--chart-3))",
    },
    visual: {
      label: "Visual Score",
      color: "hsl(var(--chart-4))",
    },
    news: {
      label: "News Coverage",
      color: "hsl(var(--chart-5))",
    }
  }

  // Generate sample time series data
  const generateTimeSeriesData = (days = 30) => {
    const data = []
    const now = new Date()
    
    for (let i = days; i >= 0; i--) {
      const date = new Date(now)
      date.setDate(date.getDate() - i)
      
      data.push({
        date: date.toISOString().split('T')[0],
        brandHealth: Math.floor(Math.random() * 20) + 70 + Math.sin(i / 5) * 10,
        sentiment: Math.floor(Math.random() * 30) + 60 + Math.cos(i / 7) * 15,
        competition: Math.floor(Math.random() * 25) + 50 + Math.sin(i / 3) * 12,
        visual: Math.floor(Math.random() * 15) + 75 + Math.cos(i / 4) * 8,
        news: Math.floor(Math.random() * 35) + 45 + Math.sin(i / 6) * 20,
        mentions: Math.floor(Math.random() * 50) + 10,
        engagement: Math.floor(Math.random() * 1000) + 500
      })
    }
    
    return data
  }

  // Generate competitive positioning data
  const generateCompetitiveData = () => [
    { name: 'Your Brand', brandHealth: 85, marketShare: 15, sentiment: 78 },
    { name: 'Competitor A', brandHealth: 72, marketShare: 22, sentiment: 65 },
    { name: 'Competitor B', brandHealth: 68, marketShare: 18, sentiment: 70 },
    { name: 'Competitor C', brandHealth: 75, marketShare: 12, sentiment: 62 },
    { name: 'Competitor D', brandHealth: 63, marketShare: 8, sentiment: 58 },
    { name: 'Others', brandHealth: 55, marketShare: 25, sentiment: 60 }
  ]

  // Generate sentiment distribution data
  const generateSentimentData = () => [
    { name: 'Positive', value: 65, color: '#10B981' },
    { name: 'Neutral', value: 25, color: '#6B7280' },
    { name: 'Negative', value: 10, color: '#EF4444' }
  ]

  // Generate radar chart data for brand dimensions
  const generateRadarData = () => [
    {
      dimension: 'Brand Awareness',
      score: 85,
      industry: 72
    },
    {
      dimension: 'Visual Identity',
      score: 78,
      industry: 68
    },
    {
      dimension: 'Market Position',
      score: 82,
      industry: 75
    },
    {
      dimension: 'Customer Sentiment',
      score: 76,
      industry: 70
    },
    {
      dimension: 'Innovation',
      score: 88,
      industry: 65
    },
    {
      dimension: 'Trust & Reliability',
      score: 91,
      industry: 78
    }
  ]

  const timeSeriesData = useMemo(() => generateTimeSeriesData(30), [])
  const competitiveData = useMemo(() => generateCompetitiveData(), [])
  const sentimentData = useMemo(() => generateSentimentData(), [])
  const radarData = useMemo(() => generateRadarData(), [])

  const ChartCard = ({ title, children, icon: Icon, onExpand, chartId }) => (
    <Card className="relative group">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            {Icon && <Icon className="h-5 w-5 text-blue-600" />}
            {title}
          </CardTitle>
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onExpand?.(chartId)}
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDrillDown?.(chartId, data)}
            >
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {children}
      </CardContent>
    </Card>
  )

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2">{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-600">{entry.name}:</span>
              <span className="font-medium">{entry.value}</span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Chart Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
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
          
          <Badge variant="outline" className="flex items-center gap-1">
            <Activity className="h-3 w-3" />
            Live Data
          </Badge>
        </div>
        
        <Button variant="outline" size="sm">
          <Download className="h-4 w-4 mr-2" />
          Export Charts
        </Button>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Brand Health Trend */}
        <ChartCard 
          title="Brand Health Trend" 
          icon={TrendingUp}
          chartId="brand-health-trend"
          onExpand={setSelectedChart}
        >
          <ChartContainer config={chartConfig} className="h-64">
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis domain={[0, 100]} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line 
                type="monotone" 
                dataKey="brandHealth" 
                stroke="var(--color-brandHealth)" 
                strokeWidth={3}
                dot={{ fill: "var(--color-brandHealth)", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ChartContainer>
        </ChartCard>

        {/* Sentiment Analysis */}
        <ChartCard 
          title="Sentiment Distribution" 
          icon={PieChartIcon}
          chartId="sentiment-distribution"
          onExpand={setSelectedChart}
        >
          <ChartContainer config={chartConfig} className="h-64">
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend />
            </PieChart>
          </ChartContainer>
        </ChartCard>

        {/* Competitive Positioning */}
        <ChartCard 
          title="Competitive Positioning" 
          icon={Target}
          chartId="competitive-positioning"
          onExpand={setSelectedChart}
        >
          <ChartContainer config={chartConfig} className="h-64">
            <ScatterChart data={competitiveData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="marketShare" 
                name="Market Share"
                unit="%"
                domain={[0, 30]}
              />
              <YAxis 
                dataKey="brandHealth" 
                name="Brand Health"
                unit=""
                domain={[50, 90]}
              />
              <ChartTooltip 
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="bg-white p-3 border rounded-lg shadow-lg">
                        <p className="font-medium text-gray-900 mb-2">{data.name}</p>
                        <p className="text-sm text-gray-600">Market Share: {data.marketShare}%</p>
                        <p className="text-sm text-gray-600">Brand Health: {data.brandHealth}</p>
                        <p className="text-sm text-gray-600">Sentiment: {data.sentiment}%</p>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Scatter 
                dataKey="brandHealth" 
                fill="var(--color-competition)"
              />
            </ScatterChart>
          </ChartContainer>
        </ChartCard>

        {/* Brand Dimensions Radar */}
        <ChartCard 
          title="Brand Dimensions" 
          icon={Activity}
          chartId="brand-dimensions"
          onExpand={setSelectedChart}
        >
          <ChartContainer config={chartConfig} className="h-64">
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="dimension" />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]} 
                tick={false}
              />
              <Radar
                name="Your Brand"
                dataKey="score"
                stroke="var(--color-brandHealth)"
                fill="var(--color-brandHealth)"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              <Radar
                name="Industry Average"
                dataKey="industry"
                stroke="var(--color-competition)"
                fill="var(--color-competition)"
                fillOpacity={0.1}
                strokeWidth={2}
                strokeDasharray="5 5"
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Legend />
            </RadarChart>
          </ChartContainer>
        </ChartCard>
      </div>

      {/* Multi-metric Trend Chart */}
      <ChartCard 
        title="Multi-Metric Performance" 
        icon={BarChart3}
        chartId="multi-metric-performance"
        onExpand={setSelectedChart}
      >
        <ChartContainer config={chartConfig} className="h-80">
          <AreaChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis domain={[0, 100]} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Area
              type="monotone"
              dataKey="brandHealth"
              stackId="1"
              stroke="var(--color-brandHealth)"
              fill="var(--color-brandHealth)"
              fillOpacity={0.6}
            />
            <Area
              type="monotone"
              dataKey="sentiment"
              stackId="2"
              stroke="var(--color-sentiment)"
              fill="var(--color-sentiment)"
              fillOpacity={0.6}
            />
            <Area
              type="monotone"
              dataKey="visual"
              stackId="3"
              stroke="var(--color-visual)"
              fill="var(--color-visual)"
              fillOpacity={0.6}
            />
            <Legend />
          </AreaChart>
        </ChartContainer>
      </ChartCard>
    </div>
  )
}

export default InteractiveChartGrid
