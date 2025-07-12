/**
 * Real-time Analytics Service
 * Handles WebSocket connections for live analytics updates
 */

import { io } from 'socket.io-client'

class RealTimeAnalyticsService {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.subscribers = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.heartbeatInterval = null
    
    // Event types
    this.events = {
      ANALYTICS_UPDATE: 'analytics_update',
      BRAND_HEALTH_CHANGE: 'brand_health_change',
      SENTIMENT_UPDATE: 'sentiment_update',
      COMPETITOR_ALERT: 'competitor_alert',
      ANALYSIS_COMPLETE: 'analysis_complete',
      SYSTEM_STATUS: 'system_status',
      ERROR: 'error'
    }
  }

  /**
   * Initialize WebSocket connection
   */
  connect(userId, options = {}) {
    const socketUrl = options.url || (import.meta.env.VITE_WS_URL || 'ws://localhost:8000')
    
    try {
      this.socket = io(socketUrl, {
        auth: {
          userId,
          token: localStorage.getItem('auth_token')
        },
        transports: ['websocket', 'polling'],
        timeout: 20000,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay
      })

      this.setupEventHandlers()
      this.startHeartbeat()
      
      console.log('🔌 Real-time analytics service connecting...')
      
    } catch (error) {
      console.error('❌ Failed to initialize WebSocket connection:', error)
      this.handleConnectionError(error)
    }
  }

  /**
   * Setup WebSocket event handlers
   */
  setupEventHandlers() {
    if (!this.socket) return

    // Connection events
    this.socket.on('connect', () => {
      console.log('✅ Real-time analytics connected')
      this.isConnected = true
      this.reconnectAttempts = 0
      this.notifySubscribers('connection', { status: 'connected' })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('🔌 Real-time analytics disconnected:', reason)
      this.isConnected = false
      this.notifySubscribers('connection', { status: 'disconnected', reason })
    })

    this.socket.on('connect_error', (error) => {
      console.error('❌ Connection error:', error)
      this.handleConnectionError(error)
    })

    // Analytics events
    this.socket.on(this.events.ANALYTICS_UPDATE, (data) => {
      console.log('📊 Analytics update received:', data)
      this.notifySubscribers(this.events.ANALYTICS_UPDATE, data)
    })

    this.socket.on(this.events.BRAND_HEALTH_CHANGE, (data) => {
      console.log('💗 Brand health change:', data)
      this.notifySubscribers(this.events.BRAND_HEALTH_CHANGE, data)
    })

    this.socket.on(this.events.SENTIMENT_UPDATE, (data) => {
      console.log('😊 Sentiment update:', data)
      this.notifySubscribers(this.events.SENTIMENT_UPDATE, data)
    })

    this.socket.on(this.events.COMPETITOR_ALERT, (data) => {
      console.log('🎯 Competitor alert:', data)
      this.notifySubscribers(this.events.COMPETITOR_ALERT, data)
    })

    this.socket.on(this.events.ANALYSIS_COMPLETE, (data) => {
      console.log('✅ Analysis complete:', data)
      this.notifySubscribers(this.events.ANALYSIS_COMPLETE, data)
    })

    this.socket.on(this.events.SYSTEM_STATUS, (data) => {
      console.log('🔧 System status:', data)
      this.notifySubscribers(this.events.SYSTEM_STATUS, data)
    })

    this.socket.on(this.events.ERROR, (error) => {
      console.error('❌ Real-time error:', error)
      this.notifySubscribers(this.events.ERROR, error)
    })

    // Heartbeat response
    this.socket.on('pong', (data) => {
      console.log('💓 Heartbeat response:', data)
    })
  }

  /**
   * Subscribe to real-time events
   */
  subscribe(eventType, callback, options = {}) {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, new Set())
    }
    
    const subscription = {
      callback,
      options,
      id: Math.random().toString(36).substr(2, 9)
    }
    
    this.subscribers.get(eventType).add(subscription)
    
    // If requesting specific brand data, join room
    if (options.brandId) {
      this.joinBrandRoom(options.brandId)
    }
    
    return subscription.id
  }

  /**
   * Unsubscribe from events
   */
  unsubscribe(eventType, subscriptionId) {
    if (!this.subscribers.has(eventType)) return
    
    const subscribers = this.subscribers.get(eventType)
    for (const subscription of subscribers) {
      if (subscription.id === subscriptionId) {
        subscribers.delete(subscription)
        break
      }
    }
    
    if (subscribers.size === 0) {
      this.subscribers.delete(eventType)
    }
  }

  /**
   * Notify all subscribers of an event
   */
  notifySubscribers(eventType, data) {
    if (!this.subscribers.has(eventType)) return
    
    const subscribers = this.subscribers.get(eventType)
    subscribers.forEach(subscription => {
      try {
        // Apply filters if specified
        if (subscription.options.filter && !subscription.options.filter(data)) {
          return
        }
        
        subscription.callback(data)
      } catch (error) {
        console.error('❌ Error in subscriber callback:', error)
      }
    })
  }

  /**
   * Join a brand-specific room for targeted updates
   */
  joinBrandRoom(brandId) {
    if (!this.socket || !this.isConnected) return
    
    this.socket.emit('join_brand_room', { brandId })
    console.log(`🏠 Joined brand room: ${brandId}`)
  }

  /**
   * Leave a brand-specific room
   */
  leaveBrandRoom(brandId) {
    if (!this.socket || !this.isConnected) return
    
    this.socket.emit('leave_brand_room', { brandId })
    console.log(`🚪 Left brand room: ${brandId}`)
  }

  /**
   * Request real-time analytics for a specific brand
   */
  requestBrandAnalytics(brandId, metrics = []) {
    if (!this.socket || !this.isConnected) return
    
    this.socket.emit('request_brand_analytics', {
      brandId,
      metrics,
      timestamp: Date.now()
    })
  }

  /**
   * Send heartbeat to maintain connection
   */
  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.socket && this.isConnected) {
        this.socket.emit('ping', { timestamp: Date.now() })
      }
    }, 30000) // Every 30 seconds
  }

  /**
   * Stop heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * Handle connection errors
   */
  handleConnectionError(error) {
    this.isConnected = false
    this.reconnectAttempts++
    
    if (this.reconnectAttempts <= this.maxReconnectAttempts) {
      console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => {
        if (this.socket) {
          this.socket.connect()
        }
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('❌ Max reconnection attempts reached')
      this.notifySubscribers('connection', { 
        status: 'failed', 
        error: 'Max reconnection attempts reached' 
      })
    }
  }

  /**
   * Get connection status
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      subscriberCount: Array.from(this.subscribers.values())
        .reduce((total, set) => total + set.size, 0)
    }
  }

  /**
   * Disconnect and cleanup
   */
  disconnect() {
    console.log('🔌 Disconnecting real-time analytics service...')
    
    this.stopHeartbeat()
    
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    
    this.isConnected = false
    this.subscribers.clear()
    this.reconnectAttempts = 0
  }

  /**
   * Send custom event
   */
  emit(eventName, data) {
    if (!this.socket || !this.isConnected) {
      console.warn('⚠️ Cannot emit event - not connected')
      return false
    }
    
    this.socket.emit(eventName, data)
    return true
  }

  /**
   * Get available event types
   */
  getEventTypes() {
    return { ...this.events }
  }
}

// Create singleton instance
const realTimeAnalytics = new RealTimeAnalyticsService()

// React hook for easy integration
export const useRealTimeAnalytics = (eventType, callback, options = {}) => {
  const [isConnected, setIsConnected] = React.useState(realTimeAnalytics.isConnected)
  const [lastUpdate, setLastUpdate] = React.useState(null)
  
  React.useEffect(() => {
    // Subscribe to connection status
    const connectionId = realTimeAnalytics.subscribe('connection', (data) => {
      setIsConnected(data.status === 'connected')
    })
    
    // Subscribe to the requested event
    const subscriptionId = realTimeAnalytics.subscribe(eventType, (data) => {
      setLastUpdate(data)
      callback?.(data)
    }, options)
    
    return () => {
      realTimeAnalytics.unsubscribe('connection', connectionId)
      realTimeAnalytics.unsubscribe(eventType, subscriptionId)
    }
  }, [eventType, callback, options])
  
  return {
    isConnected,
    lastUpdate,
    connectionStatus: realTimeAnalytics.getConnectionStatus()
  }
}

export default realTimeAnalytics
