import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  Clock, 
  Zap, 
  Database, 
  Image, 
  TrendingUp,
  RefreshCw,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'

/**
 * Performance Monitoring Component
 * Tracks and displays real-time performance metrics
 */
const PerformanceMonitor = ({ analysisId, showDetailed = false }) => {
  const [metrics, setMetrics] = useState({
    loading: true,
    totalDuration: 0,
    concurrentTasks: 0,
    cacheHitRate: 0,
    imageOptimization: {
      processed: 0,
      compressionRatio: 0,
      totalSizeSaved: 0
    },
    apiPerformance: {
      totalCalls: 0,
      averageResponseTime: 0,
      successRate: 100
    },
    databasePerformance: {
      queryCount: 0,
      averageQueryTime: 0
    }
  })

  const [realTimeStats, setRealTimeStats] = useState({
    currentStep: '',
    progress: 0,
    estimatedTimeRemaining: 0
  })

  const intervalRef = useRef(null)

  useEffect(() => {
    if (analysisId) {
      fetchPerformanceMetrics()
      
      // Set up real-time monitoring
      intervalRef.current = setInterval(fetchPerformanceMetrics, 2000)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [analysisId])

  const fetchPerformanceMetrics = async () => {
    try {
      const response = await fetch(`/api/analyze/${analysisId}/performance`)
      if (response.ok) {
        const data = await response.json()
        setMetrics(prev => ({ ...prev, ...data.metrics, loading: false }))
        setRealTimeStats(data.realTimeStats || {})
      }
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error)
      setMetrics(prev => ({ ...prev, loading: false }))
    }
  }

  const getPerformanceScore = () => {
    if (metrics.loading) return 0
    
    let score = 100
    
    // Deduct points for slow performance
    if (metrics.totalDuration > 180) score -= 20 // Over 3 minutes
    else if (metrics.totalDuration > 120) score -= 10 // Over 2 minutes
    
    // Add points for cache efficiency
    if (metrics.cacheHitRate > 80) score += 10
    else if (metrics.cacheHitRate < 30) score -= 10
    
    // Add points for concurrent processing
    if (metrics.concurrentTasks > 3) score += 5
    
    return Math.max(0, Math.min(100, score))
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`
  }

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (metrics.loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 animate-pulse" />
            Performance Monitor
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
            <span className="ml-2 text-gray-500">Loading performance data...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  const performanceScore = getPerformanceScore()

  return (
    <div className="space-y-4">
      {/* Performance Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Performance Overview
            </div>
            <Badge 
              variant={performanceScore >= 80 ? 'default' : performanceScore >= 60 ? 'secondary' : 'destructive'}
              className="text-lg px-3 py-1"
            >
              {performanceScore}/100
            </Badge>
          </CardTitle>
          <CardDescription>
            Real-time analysis performance metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Clock className="h-5 w-5 text-blue-500" />
              </div>
              <div className="text-2xl font-bold">{formatDuration(metrics.totalDuration)}</div>
              <div className="text-sm text-gray-500">Total Time</div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Zap className="h-5 w-5 text-yellow-500" />
              </div>
              <div className="text-2xl font-bold">{metrics.concurrentTasks}</div>
              <div className="text-sm text-gray-500">Concurrent Tasks</div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Database className="h-5 w-5 text-green-500" />
              </div>
              <div className="text-2xl font-bold">{metrics.cacheHitRate.toFixed(1)}%</div>
              <div className="text-sm text-gray-500">Cache Hit Rate</div>
            </div>
            
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Image className="h-5 w-5 text-purple-500" />
              </div>
              <div className="text-2xl font-bold">{metrics.imageOptimization.processed}</div>
              <div className="text-sm text-gray-500">Images Optimized</div>
            </div>
          </div>

          {realTimeStats.currentStep && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">
                  {realTimeStats.currentStep}
                </span>
                <span className="text-sm text-blue-700">
                  {realTimeStats.progress}%
                </span>
              </div>
              <Progress value={realTimeStats.progress} className="h-2" />
              {realTimeStats.estimatedTimeRemaining > 0 && (
                <div className="text-xs text-blue-600 mt-1">
                  Est. {formatDuration(realTimeStats.estimatedTimeRemaining)} remaining
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detailed Metrics */}
      {showDetailed && (
        <div className="grid md:grid-cols-2 gap-4">
          {/* Image Optimization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Image className="h-5 w-5" />
                Image Optimization
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Compression Ratio</span>
                  <span className="font-medium">
                    {metrics.imageOptimization.compressionRatio.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Size Saved</span>
                  <span className="font-medium">
                    {formatBytes(metrics.imageOptimization.totalSizeSaved)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Images Processed</span>
                  <span className="font-medium">
                    {metrics.imageOptimization.processed}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* API Performance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                API Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total API Calls</span>
                  <span className="font-medium">{metrics.apiPerformance.totalCalls}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Avg Response Time</span>
                  <span className="font-medium">
                    {metrics.apiPerformance.averageResponseTime.toFixed(0)}ms
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Success Rate</span>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">
                      {metrics.apiPerformance.successRate.toFixed(1)}%
                    </span>
                    {metrics.apiPerformance.successRate >= 95 ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Performance Tips */}
      {performanceScore < 80 && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-800">
              <AlertTriangle className="h-5 w-5" />
              Performance Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="text-sm text-yellow-700 space-y-1">
              {metrics.totalDuration > 180 && (
                <li>• Consider enabling concurrent processing for faster analysis</li>
              )}
              {metrics.cacheHitRate < 50 && (
                <li>• Low cache hit rate detected - results may be slower on repeated analyses</li>
              )}
              {metrics.imageOptimization.processed === 0 && (
                <li>• Enable image optimization to reduce bandwidth and improve loading times</li>
              )}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default PerformanceMonitor
