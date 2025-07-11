import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Server, 
  Wifi, 
  Database,
  Zap,
  TrendingUp,
  TrendingDown,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import apiService from '../../services/api.js'

const SystemHealthDashboard = ({ className = "" }) => {
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    fetchHealthData()
    
    if (autoRefresh) {
      const interval = setInterval(fetchHealthData, 30000) // Update every 30 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const fetchHealthData = async () => {
    try {
      const data = await apiService.getSystemStatus()
      setHealthData(data)
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Failed to fetch health data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return 'text-green-600 bg-green-100'
      case 'degraded':
      case 'warning':
        return 'text-yellow-600 bg-yellow-100'
      case 'unhealthy':
      case 'error':
      case 'critical':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'operational':
        return <CheckCircle className="w-4 h-4" />
      case 'degraded':
      case 'warning':
        return <AlertTriangle className="w-4 h-4" />
      case 'unhealthy':
      case 'error':
      case 'critical':
        return <AlertTriangle className="w-4 h-4" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  const formatResponseTime = (time) => {
    if (time < 1000) return `${Math.round(time)}ms`
    return `${(time / 1000).toFixed(2)}s`
  }

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) return `${days}d ${hours}h`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            System Health
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="w-6 h-6 animate-spin" />
            <span className="ml-2">Loading system status...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!healthData) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            System Health
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertTriangle className="w-4 h-4" />
            <AlertDescription>
              Unable to fetch system health data. Please try again later.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    )
  }

  const overallStatus = healthData.status || 'unknown'
  const services = healthData.services || {}
  const metrics = healthData.metrics || {}
  const alerts = healthData.alerts || []

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Overall Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              System Health
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge className={getStatusColor(overallStatus)}>
                {getStatusIcon(overallStatus)}
                <span className="ml-1 capitalize">{overallStatus}</span>
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchHealthData}
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>
          <CardDescription>
            Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {healthData.uptime && (
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>System Uptime</span>
                <span>{formatUptime(healthData.uptime)}</span>
              </div>
              <Progress value={Math.min((healthData.uptime / 86400) * 100, 100)} />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Services Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(services).map(([serviceName, serviceData]) => (
          <Card key={serviceName}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {serviceName.includes('api') ? <Server className="w-4 h-4" /> :
                   serviceName.includes('database') ? <Database className="w-4 h-4" /> :
                   <Wifi className="w-4 h-4" />}
                  <span className="capitalize">{serviceName.replace('_', ' ')}</span>
                </div>
                <Badge size="sm" className={getStatusColor(serviceData.status)}>
                  {getStatusIcon(serviceData.status)}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2 text-sm">
                {serviceData.response_time && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Response Time:</span>
                    <span className={serviceData.response_time > 5000 ? 'text-red-600' : 'text-green-600'}>
                      {formatResponseTime(serviceData.response_time)}
                    </span>
                  </div>
                )}
                
                {serviceData.success_rate !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Success Rate:</span>
                    <span className={serviceData.success_rate < 0.95 ? 'text-red-600' : 'text-green-600'}>
                      {(serviceData.success_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                
                {serviceData.last_check && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last Check:</span>
                    <span className="text-gray-800">
                      {new Date(serviceData.last_check).toLocaleTimeString()}
                    </span>
                  </div>
                )}
                
                {serviceData.error_message && (
                  <div className="text-red-600 text-xs mt-2 p-2 bg-red-50 rounded">
                    {serviceData.error_message}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Performance Metrics */}
      {metrics && Object.keys(metrics).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Performance Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(metrics).map(([metricName, metricData]) => (
                <div key={metricName} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {typeof metricData === 'number' ? 
                      metricData.toFixed(2) : 
                      metricData.value || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-600 capitalize">
                    {metricName.replace('_', ' ')}
                  </div>
                  {metricData.trend && (
                    <div className={`flex items-center justify-center mt-1 ${
                      metricData.trend === 'up' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {metricData.trend === 'up' ? 
                        <TrendingUp className="w-3 h-3" /> : 
                        <TrendingDown className="w-3 h-3" />}
                      <span className="text-xs ml-1">{metricData.change || ''}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Active Alerts */}
      {alerts && alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Active Alerts ({alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert, index) => (
                <Alert key={index}>
                  <AlertTriangle className="w-4 h-4" />
                  <AlertDescription>
                    <div className="flex items-center justify-between">
                      <span>{alert.message || alert.title}</span>
                      <Badge variant="outline" className="text-xs">
                        {alert.level || 'warning'}
                      </Badge>
                    </div>
                    {alert.timestamp && (
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    )}
                  </AlertDescription>
                </Alert>
              ))}
              
              {alerts.length > 5 && (
                <div className="text-center text-sm text-gray-500">
                  ... and {alerts.length - 5} more alerts
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default SystemHealthDashboard
