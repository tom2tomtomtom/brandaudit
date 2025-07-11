import { useState, useEffect, useRef, useCallback } from 'react'
import { io } from 'socket.io-client'

const WEBSOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useWebSocket = (analysisId, onComplete) => {
  const [isConnected, setIsConnected] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStage, setCurrentStage] = useState(0)
  const [stageProgress, setStageProgress] = useState(0)
  const [currentStepName, setCurrentStepName] = useState('')
  const [currentSubstep, setCurrentSubstep] = useState('')
  const [status, setStatus] = useState('starting')
  const [timeRemaining, setTimeRemaining] = useState(null)
  const [estimatedCompletion, setEstimatedCompletion] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)
  const [stages, setStages] = useState([])
  const [completedSteps, setCompletedSteps] = useState(new Set())
  const [elapsedTime, setElapsedTime] = useState(0)
  const [connectionQuality, setConnectionQuality] = useState('good') // good, poor, disconnected
  const [lastUpdateTime, setLastUpdateTime] = useState(null)

  const socketRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const heartbeatIntervalRef = useRef(null)
  const connectionQualityTimeoutRef = useRef(null)

  const startHeartbeat = useCallback(() => {
    // Clear existing heartbeat
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
    }

    // Monitor connection quality based on update frequency
    heartbeatIntervalRef.current = setInterval(() => {
      const now = Date.now()
      if (lastUpdateTime) {
        const timeSinceLastUpdate = now - lastUpdateTime

        if (timeSinceLastUpdate > 30000) { // 30 seconds without update
          setConnectionQuality('poor')
        } else if (timeSinceLastUpdate > 60000) { // 1 minute without update
          setConnectionQuality('disconnected')
        }
      }
    }, 10000) // Check every 10 seconds
  }, [lastUpdateTime])

  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = null
    }
    if (connectionQualityTimeoutRef.current) {
      clearTimeout(connectionQualityTimeoutRef.current)
      connectionQualityTimeoutRef.current = null
    }
  }, [])

  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      return
    }

    console.log('🔌 Connecting to WebSocket server:', WEBSOCKET_URL)
    
    socketRef.current = io(WEBSOCKET_URL, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true
    })

    socketRef.current.on('connect', () => {
      console.log('✅ WebSocket connected')
      setIsConnected(true)
      setErrorMessage(null)
      setConnectionQuality('good')
      reconnectAttempts.current = 0

      // Join the analysis room
      if (analysisId) {
        socketRef.current.emit('join_analysis', { analysis_id: analysisId })
        console.log('🏠 Joined analysis room:', analysisId)
      }

      // Start heartbeat monitoring
      startHeartbeat()
    })

    socketRef.current.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason)
      setIsConnected(false)
      
      // Attempt to reconnect unless it was a manual disconnect
      if (reason !== 'io client disconnect' && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000)
        console.log(`🔄 Attempting to reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`)
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttempts.current++
          connect()
        }, delay)
      }
    })

    socketRef.current.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error)
      setErrorMessage('Connection failed. Retrying...')
    })

    socketRef.current.on('progress_update', (data) => {
      console.log('📊 Progress update received:', data)

      // Update last update time for connection quality monitoring
      setLastUpdateTime(Date.now())
      setConnectionQuality('good')

      setProgress(data.overall_progress || 0)
      setCurrentStage(data.current_stage || 0)
      setStageProgress(data.stage_progress || 0)
      setCurrentStepName(data.current_step_name || '')
      setCurrentSubstep(data.current_substep || '')
      setStatus(data.status || 'processing')
      setTimeRemaining(data.time_remaining)
      setEstimatedCompletion(data.estimated_completion)
      setElapsedTime(data.elapsed_time || 0)

      if (data.stages) {
        setStages(data.stages)
      }

      if (data.error_message) {
        setErrorMessage(data.error_message)
        setStatus('error')
      } else {
        setErrorMessage(null)
      }

      // Update completed steps
      const completed = new Set()
      for (let i = 0; i < data.current_stage; i++) {
        completed.add(i)
      }
      if (data.status === 'completed') {
        for (let i = 0; i < (data.stages?.length || 8); i++) {
          completed.add(i)
        }
      }
      setCompletedSteps(completed)

      // Call completion callback
      if (data.status === 'completed' && onComplete) {
        console.log('✅ Analysis completed, calling onComplete callback')
        onComplete()
      }
    })

    socketRef.current.on('connected', (data) => {
      console.log('🎉 Server connection confirmed:', data)
    })

  }, [analysisId, onComplete])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    // Stop heartbeat monitoring
    stopHeartbeat()

    if (socketRef.current) {
      if (analysisId) {
        socketRef.current.emit('leave_analysis', { analysis_id: analysisId })
      }
      socketRef.current.disconnect()
      socketRef.current = null
    }

    setIsConnected(false)
    setConnectionQuality('disconnected')
    reconnectAttempts.current = 0
  }, [analysisId, stopHeartbeat])

  const retry = useCallback(() => {
    disconnect()
    setTimeout(() => {
      reconnectAttempts.current = 0
      connect()
    }, 1000)
  }, [connect, disconnect])

  // Connect when analysisId is provided
  useEffect(() => {
    if (analysisId) {
      connect()
    }
    
    return () => {
      disconnect()
    }
  }, [analysisId, connect, disconnect])

  // Format time remaining
  const formatTimeRemaining = useCallback((seconds) => {
    if (!seconds || seconds <= 0) return null
    
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    }
    return `${remainingSeconds}s`
  }, [])

  // Format elapsed time
  const formatElapsedTime = useCallback((seconds) => {
    if (!seconds) return '0s'
    
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    }
    return `${remainingSeconds}s`
  }, [])

  return {
    // Connection state
    isConnected,
    connectionQuality,
    errorMessage,

    // Progress data
    progress,
    currentStage,
    stageProgress,
    currentStepName,
    currentSubstep,
    status,
    timeRemaining,
    estimatedCompletion,
    elapsedTime,
    stages,
    completedSteps,

    // Utility functions
    formatTimeRemaining: formatTimeRemaining(timeRemaining),
    formatElapsedTime: formatElapsedTime(elapsedTime),

    // Control functions
    retry,
    disconnect
  }
}

export default useWebSocket
