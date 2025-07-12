/**
 * React Hook for Real-time Analytics Integration
 * Provides easy-to-use hooks for real-time analytics data
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import realTimeAnalytics from '../services/realTimeAnalytics.js'

/**
 * Main hook for real-time analytics
 */
export const useRealTimeAnalytics = (brandId, options = {}) => {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [error, setError] = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)
  const subscriptionsRef = useRef(new Set())

  // Initialize connection
  useEffect(() => {
    if (!brandId) return

    const userId = localStorage.getItem('user_id') || 'anonymous'
    
    // Connect to real-time service
    realTimeAnalytics.connect(userId, options)

    // Subscribe to connection status
    const connectionId = realTimeAnalytics.subscribe('connection', (data) => {
      setIsConnected(data.status === 'connected')
      setConnectionStatus(data.status)
      if (data.error) {
        setError(data.error)
      }
    })

    subscriptionsRef.current.add(connectionId)

    // Cleanup on unmount
    return () => {
      subscriptionsRef.current.forEach(id => {
        realTimeAnalytics.unsubscribe('connection', id)
      })
      subscriptionsRef.current.clear()
    }
  }, [brandId, options])

  // Subscribe to specific events
  const subscribe = useCallback((eventType, callback, eventOptions = {}) => {
    const subscriptionId = realTimeAnalytics.subscribe(
      eventType, 
      (data) => {
        setLastUpdate({ eventType, data, timestamp: Date.now() })
        callback(data)
      },
      { ...eventOptions, brandId }
    )

    subscriptionsRef.current.add(subscriptionId)
    return subscriptionId
  }, [brandId])

  // Unsubscribe from events
  const unsubscribe = useCallback((eventType, subscriptionId) => {
    realTimeAnalytics.unsubscribe(eventType, subscriptionId)
    subscriptionsRef.current.delete(subscriptionId)
  }, [])

  // Request brand analytics
  const requestAnalytics = useCallback((metrics = []) => {
    realTimeAnalytics.requestBrandAnalytics(brandId, metrics)
  }, [brandId])

  return {
    isConnected,
    connectionStatus,
    error,
    lastUpdate,
    subscribe,
    unsubscribe,
    requestAnalytics,
    disconnect: () => realTimeAnalytics.disconnect()
  }
}

/**
 * Hook for brand health updates
 */
export const useBrandHealthUpdates = (brandId, callback) => {
  const [brandHealth, setBrandHealth] = useState(null)
  const [trend, setTrend] = useState(null)
  const { subscribe, unsubscribe } = useRealTimeAnalytics(brandId)

  useEffect(() => {
    if (!brandId) return

    const subscriptionId = subscribe('brand_health_change', (data) => {
      setBrandHealth(data.current)
      setTrend(data.trend)
      callback?.(data)
    })

    return () => unsubscribe('brand_health_change', subscriptionId)
  }, [brandId, callback, subscribe, unsubscribe])

  return { brandHealth, trend }
}

/**
 * Hook for sentiment updates
 */
export const useSentimentUpdates = (brandId, callback) => {
  const [sentiment, setSentiment] = useState(null)
  const [change, setChange] = useState(null)
  const { subscribe, unsubscribe } = useRealTimeAnalytics(brandId)

  useEffect(() => {
    if (!brandId) return

    const subscriptionId = subscribe('sentiment_update', (data) => {
      setSentiment(data.current)
      setChange(data.change)
      callback?.(data)
    })

    return () => unsubscribe('sentiment_update', subscriptionId)
  }, [brandId, callback, subscribe, unsubscribe])

  return { sentiment, change }
}

/**
 * Hook for competitor alerts
 */
export const useCompetitorAlerts = (brandId, callback) => {
  const [alerts, setAlerts] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const { subscribe, unsubscribe } = useRealTimeAnalytics(brandId)

  useEffect(() => {
    if (!brandId) return

    const subscriptionId = subscribe('competitor_alert', (data) => {
      setAlerts(prev => [data, ...prev.slice(0, 49)]) // Keep last 50 alerts
      setUnreadCount(prev => prev + 1)
      callback?.(data)
    })

    return () => unsubscribe('competitor_alert', subscriptionId)
  }, [brandId, callback, subscribe, unsubscribe])

  const markAsRead = useCallback(() => {
    setUnreadCount(0)
  }, [])

  const clearAlerts = useCallback(() => {
    setAlerts([])
    setUnreadCount(0)
  }, [])

  return { alerts, unreadCount, markAsRead, clearAlerts }
}

/**
 * Hook for analysis completion notifications
 */
export const useAnalysisNotifications = (callback) => {
  const [notifications, setNotifications] = useState([])
  const { subscribe, unsubscribe } = useRealTimeAnalytics()

  useEffect(() => {
    const subscriptionId = subscribe('analysis_complete', (data) => {
      const notification = {
        id: Date.now(),
        ...data,
        timestamp: new Date().toISOString()
      }
      
      setNotifications(prev => [notification, ...prev.slice(0, 9)]) // Keep last 10
      callback?.(notification)
    })

    return () => unsubscribe('analysis_complete', subscriptionId)
  }, [callback, subscribe, unsubscribe])

  const dismissNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
  }, [])

  return { notifications, dismissNotification, clearAll }
}

/**
 * Hook for system status monitoring
 */
export const useSystemStatus = () => {
  const [systemStatus, setSystemStatus] = useState({
    status: 'unknown',
    uptime: 0,
    activeUsers: 0,
    apiResponseTime: 0
  })
  const { subscribe, unsubscribe } = useRealTimeAnalytics()

  useEffect(() => {
    const subscriptionId = subscribe('system_status', (data) => {
      setSystemStatus(data)
    })

    return () => unsubscribe('system_status', subscriptionId)
  }, [subscribe, unsubscribe])

  return systemStatus
}

/**
 * Hook for real-time analytics data streaming
 */
export const useAnalyticsStream = (brandId, metrics = [], options = {}) => {
  const [streamData, setStreamData] = useState({})
  const [isStreaming, setIsStreaming] = useState(false)
  const { subscribe, unsubscribe, requestAnalytics, isConnected } = useRealTimeAnalytics(brandId)

  useEffect(() => {
    if (!brandId || !isConnected) return

    setIsStreaming(true)

    const subscriptionId = subscribe('analytics_update', (data) => {
      setStreamData(prev => ({
        ...prev,
        [data.metric]: {
          value: data.value,
          timestamp: data.timestamp,
          change: data.change
        }
      }))
    }, { 
      filter: (data) => metrics.length === 0 || metrics.includes(data.metric)
    })

    // Request initial data
    requestAnalytics(metrics)

    return () => {
      unsubscribe('analytics_update', subscriptionId)
      setIsStreaming(false)
    }
  }, [brandId, metrics, isConnected, subscribe, unsubscribe, requestAnalytics])

  return { streamData, isStreaming }
}

/**
 * Hook for connection quality monitoring
 */
export const useConnectionQuality = () => {
  const [quality, setQuality] = useState({
    latency: 0,
    stability: 'good',
    reconnectCount: 0
  })
  const { subscribe, unsubscribe } = useRealTimeAnalytics()
  const pingStartRef = useRef(null)

  useEffect(() => {
    const connectionId = subscribe('connection', (data) => {
      if (data.status === 'disconnected') {
        setQuality(prev => ({
          ...prev,
          stability: 'poor',
          reconnectCount: prev.reconnectCount + 1
        }))
      } else if (data.status === 'connected') {
        setQuality(prev => ({
          ...prev,
          stability: 'good'
        }))
      }
    })

    // Measure latency with periodic pings
    const pingInterval = setInterval(() => {
      pingStartRef.current = Date.now()
      realTimeAnalytics.emit('ping', { timestamp: pingStartRef.current })
    }, 10000) // Every 10 seconds

    const pongId = subscribe('pong', (data) => {
      if (pingStartRef.current) {
        const latency = Date.now() - pingStartRef.current
        setQuality(prev => ({
          ...prev,
          latency,
          stability: latency < 100 ? 'excellent' : latency < 300 ? 'good' : 'poor'
        }))
      }
    })

    return () => {
      unsubscribe('connection', connectionId)
      unsubscribe('pong', pongId)
      clearInterval(pingInterval)
    }
  }, [subscribe, unsubscribe])

  return quality
}

/**
 * Hook for batch analytics updates
 */
export const useBatchAnalytics = (brandId, updateInterval = 5000) => {
  const [batchData, setBatchData] = useState({})
  const [lastBatchUpdate, setLastBatchUpdate] = useState(null)
  const batchRef = useRef({})
  const { subscribe, unsubscribe } = useRealTimeAnalytics(brandId)

  useEffect(() => {
    if (!brandId) return

    // Collect updates in batch
    const subscriptionId = subscribe('analytics_update', (data) => {
      batchRef.current[data.metric] = data
    })

    // Process batch updates at intervals
    const batchInterval = setInterval(() => {
      if (Object.keys(batchRef.current).length > 0) {
        setBatchData({ ...batchRef.current })
        setLastBatchUpdate(Date.now())
        batchRef.current = {}
      }
    }, updateInterval)

    return () => {
      unsubscribe('analytics_update', subscriptionId)
      clearInterval(batchInterval)
    }
  }, [brandId, updateInterval, subscribe, unsubscribe])

  return { batchData, lastBatchUpdate }
}
