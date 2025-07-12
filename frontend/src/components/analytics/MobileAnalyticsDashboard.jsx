import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet.jsx'
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
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  ResponsiveContainer
} from 'recharts'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Target,
  Activity,
  Eye,
  MessageSquare,
  Users,
  Award,
  Menu,
  Filter,
  Download,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  Smartphone,
  Tablet,
  Monitor
} from 'lucide-react'

const MobileAnalyticsDashboard = ({ 
  data, 
  brandName, 
  onRefresh,
  className = ""
}) => {
  const [activeMetric, setActiveMetric] = useState('brandHealth')
  const [expandedCard, setExpandedCard] = useState(null)
  const [viewMode, setViewMode] = useState('mobile') // mobile, tablet, desktop
  const [showFilters, setShowFilters] = useState(false)

  // Detect screen size and set view mode
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth
      if (width < 768) {
        setViewMode('mobile')
      } else if (width < 1024) {
        setViewMode('tablet')
      } else {
        setViewMode('desktop')
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Mock data for mobile display
  const mobileMetrics = {
    brandHealth: {
      value: 85,
      change: 5.2,
      status: 'excellent',
      trend: 'up'
    },
    sentiment: {
      value: 78,
      change: 3.1,
      status: 'good',
      trend: 'up'
    },
    marketShare: {
      value: 15.2,
      change: -0.8,
      status: 'good',
      trend: 'down'
    },
    awareness: {
      value: 82,
      change: 2.4,
      status: 'excellent',
      trend: 'up'
    }
  }

  const quickInsights = [
    {
      id: 1,
      type: 'positive',
      title: 'Brand Health Improving',
      description: 'Up 5.2% this month',
      icon: TrendingUp,
      color: 'text-green-600'
    },
    {
      id: 2,
      type: 'warning',
      title: 'Market Share Decline',
      description: 'Down 0.8% vs competitors',
      icon: TrendingDown,
      color: 'text-yellow-600'
    },
    {
      id: 3,
      type: 'info',
      title: 'Strong Awareness',
      description: '82% brand recognition',
      icon: Eye,
      color: 'text-blue-600'
    }
  ]

  const chartData = [
    { name: 'Jan', value: 75 },
    { name: 'Feb', value: 78 },
    { name: 'Mar', value: 82 },
    { name: 'Apr', value: 79 },
    { name: 'May', value: 85 },
    { name: 'Jun', value: 88 }
  ]

  const getTrendIcon = (trend) => {
    return trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Activity
  }

  const getTrendColor = (trend) => {
    return trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'excellent': return 'text-green-600'
      case 'good': return 'text-blue-600'
      case 'fair': return 'text-yellow-600'
      case 'poor': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  // Mobile-optimized metric card
  const MobileMetricCard = ({ title, metric, isActive, onClick }) => {
    const TrendIcon = getTrendIcon(metric.trend)
    
    return (
      <Card 
        className={`cursor-pointer transition-all ${
          isActive ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:shadow-md'
        }`}
        onClick={onClick}
      >
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">{title}</span>
            <TrendIcon className={`h-4 w-4 ${getTrendColor(metric.trend)}`} />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-gray-900">
              {metric.value}
              {title === 'Market Share' ? '%' : ''}
            </div>
            
            <div className={`text-sm font-medium ${getTrendColor(metric.trend)}`}>
              {metric.change > 0 ? '+' : ''}{metric.change.toFixed(1)}%
            </div>
          </div>
          
          <div className="mt-2">
            <Progress value={metric.value} className="h-2" />
          </div>
        </CardContent>
      </Card>
    )
  }

  // Expandable insight card
  const InsightCard = ({ insight, isExpanded, onToggle }) => {
    const Icon = insight.icon
    
    return (
      <Card className="cursor-pointer" onClick={onToggle}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Icon className={`h-5 w-5 ${insight.color}`} />
              <div>
                <h3 className="font-medium text-gray-900">{insight.title}</h3>
                <p className="text-sm text-gray-600">{insight.description}</p>
              </div>
            </div>
            
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-400" />
            )}
          </div>
          
          {isExpanded && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-700">
                Detailed analysis and recommendations would appear here with actionable insights
                and next steps for improvement.
              </p>
              <div className="flex gap-2 mt-3">
                <Button size="sm" variant="outline">
                  View Details
                </Button>
                <Button size="sm">
                  Take Action
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  // Mobile chart component
  const MobileChart = ({ data, type = 'line' }) => {
    const chartHeight = viewMode === 'mobile' ? 200 : 250
    
    return (
      <div style={{ height: chartHeight }}>
        <ResponsiveContainer width="100%" height="100%">
          {type === 'line' ? (
            <LineChart data={data}>
              <XAxis dataKey="name" />
              <YAxis />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          ) : type === 'area' ? (
            <AreaChart data={data}>
              <XAxis dataKey="name" />
              <YAxis />
              <Area
                type="monotone"
                dataKey="value"
                stroke="#3B82F6"
                fill="#3B82F6"
                fillOpacity={0.3}
              />
            </AreaChart>
          ) : (
            <BarChart data={data}>
              <XAxis dataKey="name" />
              <YAxis />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    )
  }

  // Mobile filters sheet
  const MobileFilters = () => (
    <Sheet open={showFilters} onOpenChange={setShowFilters}>
      <SheetContent side="bottom" className="h-[80vh]">
        <SheetHeader>
          <SheetTitle>Analytics Filters</SheetTitle>
        </SheetHeader>
        <div className="py-4 space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Time Period</label>
            <select className="w-full mt-1 p-2 border rounded-md">
              <option>Last 30 days</option>
              <option>Last 90 days</option>
              <option>Last 6 months</option>
              <option>Last year</option>
            </select>
          </div>
          
          <div>
            <label className="text-sm font-medium text-gray-700">Metrics</label>
            <div className="mt-2 space-y-2">
              {Object.keys(mobileMetrics).map(metric => (
                <label key={metric} className="flex items-center">
                  <input type="checkbox" className="mr-2" defaultChecked />
                  <span className="text-sm capitalize">{metric.replace(/([A-Z])/g, ' $1')}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="flex gap-3 pt-4">
            <Button className="flex-1" onClick={() => setShowFilters(false)}>
              Apply Filters
            </Button>
            <Button variant="outline" onClick={() => setShowFilters(false)}>
              Cancel
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Mobile Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{brandName} Analytics</h1>
          <p className="text-sm text-gray-600">Mobile Dashboard</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setShowFilters(true)}>
            <Filter className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={onRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Device Mode Indicator */}
      <div className="flex items-center gap-2 text-sm text-gray-600">
        {viewMode === 'mobile' && <Smartphone className="h-4 w-4" />}
        {viewMode === 'tablet' && <Tablet className="h-4 w-4" />}
        {viewMode === 'desktop' && <Monitor className="h-4 w-4" />}
        <span>Optimized for {viewMode}</span>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(mobileMetrics).map(([key, metric]) => (
          <MobileMetricCard
            key={key}
            title={key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
            metric={metric}
            isActive={activeMetric === key}
            onClick={() => setActiveMetric(key)}
          />
        ))}
      </div>

      {/* Active Metric Chart */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">
            {activeMetric.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())} Trend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <MobileChart data={chartData} type="line" />
        </CardContent>
      </Card>

      {/* Quick Insights */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Quick Insights</h2>
        <div className="space-y-3">
          {quickInsights.map(insight => (
            <InsightCard
              key={insight.id}
              insight={insight}
              isExpanded={expandedCard === insight.id}
              onToggle={() => setExpandedCard(expandedCard === insight.id ? null : insight.id)}
            />
          ))}
        </div>
      </div>

      {/* Mobile Tabs for Additional Views */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="compare">Compare</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Brand Health Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Overall Score</span>
                  <span className="text-lg font-bold text-gray-900">85/100</span>
                </div>
                <Progress value={85} className="h-3" />
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Visual Identity</span>
                    <div className="font-medium">78%</div>
                  </div>
                  <div>
                    <span className="text-gray-600">Market Position</span>
                    <div className="font-medium">#2</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">6-Month Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <MobileChart data={chartData} type="area" />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compare" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Competitive Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="font-medium">Your Brand</span>
                  <span className="text-lg font-bold text-blue-600">85</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">Competitor A</span>
                  <span className="text-lg font-bold text-gray-600">72</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">Competitor B</span>
                  <span className="text-lg font-bold text-gray-600">68</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Mobile Filters */}
      <MobileFilters />

      {/* Quick Actions */}
      <div className="fixed bottom-4 right-4 flex flex-col gap-2">
        <Button size="sm" className="rounded-full shadow-lg">
          <Download className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

export default MobileAnalyticsDashboard
