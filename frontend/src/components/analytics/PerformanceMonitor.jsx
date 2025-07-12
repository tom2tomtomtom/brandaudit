import React, { useState, useEffect, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
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
  Activity, 
  Clock, 
  Database,
  Server,
  Zap,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Cpu,
  HardDrive,
  Wifi,
  Users,
  Eye,
  RefreshCw
} from 'lucide-react'

const PerformanceMonitor = ({ className = "" }) => {
  const [performanceData, setPerformanceData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Chart configuration
  const chartConfig = {
    responseTime: { label: "Response Time", color: "hsl(var(--chart-1))" },
    throughput: { label: "Throughput", color: "hsl(var(--chart-2))" },
    errorRate: { label: "Error Rate", color: "hsl(var(--chart-3))" },
    cacheHitRate: { label: "Cache Hit Rate", color: "hsl(var(--chart-4))" },
    activeUsers: { label: "Active Users", color: "hsl(var(--chart-5))" }
  }

  // Generate mock performance data
  const generatePerformanceData = () => {
    const now = new Date()
    const data = []
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000)
      data.push({
        time: time.toISOString(),
        hour: time.getHours(),
        responseTime: 150 + Math.random() * 100 + Math.sin(i / 4) * 50,
        throughput: 800 + Math.random() * 400 + Math.cos(i / 6) * 200,
        errorRate: Math.random() * 2 + Math.sin(i / 8) * 1,
        cacheHitRate: 85 + Math.random() * 10 + Math.cos(i / 5) * 5,
        activeUsers: 50 + Math.random() * 100 + Math.sin(i / 3) * 30,
        cpuUsage: 30 + Math.random() * 40 + Math.sin(i / 7) * 20,
        memoryUsage: 60 + Math.random() * 20 + Math.cos(i / 9) * 10,
        diskUsage: 45 + Math.random() * 10
      })
    }
    
    return data
  }

  // System metrics
  const systemMetrics = useMemo(() => {
    if (!performanceData) return null
    
    const latest = performanceData[performanceData.length - 1]
    const previous = performanceData[performanceData.length - 2]
    
    return {
      responseTime: {
        current: latest.responseTime,
        change: latest.responseTime - (previous?.responseTime || latest.responseTime),
        status: latest.responseTime < 200 ? 'good' : latest.responseTime < 500 ? 'warning' : 'critical'
      },
      throughput: {
        current: latest.throughput,
        change: latest.throughput - (previous?.throughput || latest.throughput),
        status: latest.throughput > 800 ? 'good' : latest.throughput > 500 ? 'warning' : 'critical'
      },
      errorRate: {
        current: latest.errorRate,
        change: latest.errorRate - (previous?.errorRate || latest.errorRate),
        status: latest.errorRate < 1 ? 'good' : latest.errorRate < 3 ? 'warning' : 'critical'
      },
      cacheHitRate: {
        current: latest.cacheHitRate,
        change: latest.cacheHitRate - (previous?.cacheHitRate || latest.cacheHitRate),
        status: latest.cacheHitRate > 90 ? 'good' : latest.cacheHitRate > 80 ? 'warning' : 'critical'
      },
      activeUsers: {
        current: latest.activeUsers,
        change: latest.activeUsers - (previous?.activeUsers || latest.activeUsers),
        status: 'info'
      },
      systemHealth: {
        cpu: latest.cpuUsage,
        memory: latest.memoryUsage,
        disk: latest.diskUsage
      }
    }
  }, [performanceData])

  // Fetch performance data
  const fetchPerformanceData = async () => {
    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      const data = generatePerformanceData()
      setPerformanceData(data)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Failed to fetch performance data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-refresh effect
  useEffect(() => {
    fetchPerformanceData()
    
    if (autoRefresh) {
      const interval = setInterval(fetchPerformanceData, 30000) // Every 30 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const getStatusColor = (status) => {
    switch (status) {
      case 'good': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'critical': return 'text-red-600'
      default: return 'text-blue-600'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'good': return CheckCircle
      case 'warning': return AlertTriangle
      case 'critical': return AlertTriangle
      default: return Activity
    }
  }

  const MetricCard = ({ title, value, unit, change, status, icon: Icon }) => {
    const StatusIcon = getStatusIcon(status)
    const TrendIcon = change > 0 ? TrendingUp : change < 0 ? TrendingDown : Activity
    
    return (
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {Icon && <Icon className="h-4 w-4 text-blue-600" />}
              <span className="text-sm font-medium text-gray-600">{title}</span>
            </div>
            <StatusIcon className={`h-4 w-4 ${getStatusColor(status)}`} />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-gray-900">
              {typeof value === 'number' ? value.toFixed(1) : value}{unit}
            </div>
            
            {change !== undefined && (
              <div className={`flex items-center gap-1 ${
                change > 0 ? 'text-green-500' : change < 0 ? 'text-red-500' : 'text-gray-500'
              }`}>
                <TrendIcon className="h-4 w-4" />
                <span className="text-sm font-medium">
                  {Math.abs(change).toFixed(1)}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    )
  }

  const SystemHealthCard = ({ metrics }) => (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Server className="h-5 w-5 text-blue-600" />
          System Health
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">CPU Usage</span>
            </div>
            <span className="text-sm font-medium">{metrics.cpu.toFixed(1)}%</span>
          </div>
          <Progress value={metrics.cpu} className="h-2" />
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Memory Usage</span>
            </div>
            <span className="text-sm font-medium">{metrics.memory.toFixed(1)}%</span>
          </div>
          <Progress value={metrics.memory} className="h-2" />
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-600">Disk Usage</span>
            </div>
            <span className="text-sm font-medium">{metrics.disk.toFixed(1)}%</span>
          </div>
          <Progress value={metrics.disk} className="h-2" />
        </div>
      </CardContent>
    </Card>
  )

  if (!performanceData || !systemMetrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-500">Loading performance data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Performance Monitor</h2>
          <p className="text-gray-600">
            System performance and analytics metrics • Last updated {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchPerformanceData}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <Activity className="h-4 w-4 mr-2" />
            Auto Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Response Time"
          value={systemMetrics.responseTime.current}
          unit="ms"
          change={systemMetrics.responseTime.change}
          status={systemMetrics.responseTime.status}
          icon={Clock}
        />
        
        <MetricCard
          title="Throughput"
          value={systemMetrics.throughput.current}
          unit="/min"
          change={systemMetrics.throughput.change}
          status={systemMetrics.throughput.status}
          icon={Zap}
        />
        
        <MetricCard
          title="Error Rate"
          value={systemMetrics.errorRate.current}
          unit="%"
          change={systemMetrics.errorRate.change}
          status={systemMetrics.errorRate.status}
          icon={AlertTriangle}
        />
        
        <MetricCard
          title="Cache Hit Rate"
          value={systemMetrics.cacheHitRate.current}
          unit="%"
          change={systemMetrics.cacheHitRate.change}
          status={systemMetrics.cacheHitRate.status}
          icon={Database}
        />
        
        <MetricCard
          title="Active Users"
          value={systemMetrics.activeUsers.current}
          unit=""
          change={systemMetrics.activeUsers.change}
          status={systemMetrics.activeUsers.status}
          icon={Users}
        />
        
        <SystemHealthCard metrics={systemMetrics.systemHealth} />
      </div>

      {/* Performance Charts */}
      <Tabs defaultValue="response-time" className="space-y-6">
        <TabsList>
          <TabsTrigger value="response-time">Response Time</TabsTrigger>
          <TabsTrigger value="throughput">Throughput</TabsTrigger>
          <TabsTrigger value="errors">Error Rate</TabsTrigger>
          <TabsTrigger value="cache">Cache Performance</TabsTrigger>
          <TabsTrigger value="users">User Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="response-time">
          <Card>
            <CardHeader>
              <CardTitle>Response Time Trends (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="hour" 
                    tickFormatter={(hour) => `${hour}:00`}
                  />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line
                    type="monotone"
                    dataKey="responseTime"
                    stroke="var(--color-responseTime)"
                    strokeWidth={2}
                    dot={{ fill: "var(--color-responseTime)", strokeWidth: 2, r: 3 }}
                  />
                </LineChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="throughput">
          <Card>
            <CardHeader>
              <CardTitle>Throughput Analysis (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <AreaChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="hour" 
                    tickFormatter={(hour) => `${hour}:00`}
                  />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Area
                    type="monotone"
                    dataKey="throughput"
                    stroke="var(--color-throughput)"
                    fill="var(--color-throughput)"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors">
          <Card>
            <CardHeader>
              <CardTitle>Error Rate Monitoring (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="hour" 
                    tickFormatter={(hour) => `${hour}:00`}
                  />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar
                    dataKey="errorRate"
                    fill="var(--color-errorRate)"
                  />
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cache">
          <Card>
            <CardHeader>
              <CardTitle>Cache Hit Rate (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="hour" 
                    tickFormatter={(hour) => `${hour}:00`}
                  />
                  <YAxis domain={[80, 100]} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line
                    type="monotone"
                    dataKey="cacheHitRate"
                    stroke="var(--color-cacheHitRate)"
                    strokeWidth={2}
                    dot={{ fill: "var(--color-cacheHitRate)", strokeWidth: 2, r: 3 }}
                  />
                </LineChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>Active Users (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-80">
                <AreaChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="hour" 
                    tickFormatter={(hour) => `${hour}:00`}
                  />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Area
                    type="monotone"
                    dataKey="activeUsers"
                    stroke="var(--color-activeUsers)"
                    fill="var(--color-activeUsers)"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default PerformanceMonitor
