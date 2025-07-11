import { useState, useEffect, useCallback, useRef, useMemo } from 'react'

/**
 * Custom hook for performance optimization utilities
 */
export const usePerformanceOptimization = () => {
  const [performanceMetrics, setPerformanceMetrics] = useState({
    renderTime: 0,
    memoryUsage: 0,
    componentCount: 0
  })

  const renderStartTime = useRef(null)

  // Track render performance
  const startRenderTracking = useCallback(() => {
    renderStartTime.current = performance.now()
  }, [])

  const endRenderTracking = useCallback((componentName = 'Unknown') => {
    if (renderStartTime.current) {
      const renderTime = performance.now() - renderStartTime.current
      setPerformanceMetrics(prev => ({
        ...prev,
        renderTime,
        componentCount: prev.componentCount + 1
      }))
      
      if (renderTime > 100) {
        console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`)
      }
    }
  }, [])

  // Memory usage tracking
  useEffect(() => {
    const updateMemoryUsage = () => {
      if (performance.memory) {
        setPerformanceMetrics(prev => ({
          ...prev,
          memoryUsage: performance.memory.usedJSHeapSize / 1024 / 1024 // MB
        }))
      }
    }

    const interval = setInterval(updateMemoryUsage, 5000)
    updateMemoryUsage()

    return () => clearInterval(interval)
  }, [])

  return {
    performanceMetrics,
    startRenderTracking,
    endRenderTracking
  }
}

/**
 * Hook for debouncing values to improve performance
 */
export const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * Hook for throttling function calls
 */
export const useThrottle = (callback, delay) => {
  const lastRun = useRef(Date.now())

  return useCallback((...args) => {
    if (Date.now() - lastRun.current >= delay) {
      callback(...args)
      lastRun.current = Date.now()
    }
  }, [callback, delay])
}

/**
 * Hook for intersection observer (lazy loading)
 */
export const useIntersectionObserver = (options = {}) => {
  const [isIntersecting, setIsIntersecting] = useState(false)
  const [hasIntersected, setHasIntersected] = useState(false)
  const elementRef = useRef(null)

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const observer = new IntersectionObserver(([entry]) => {
      const isElementIntersecting = entry.isIntersecting
      setIsIntersecting(isElementIntersecting)
      
      if (isElementIntersecting && !hasIntersected) {
        setHasIntersected(true)
      }
    }, {
      rootMargin: '50px',
      threshold: 0.1,
      ...options
    })

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [hasIntersected, options])

  return { elementRef, isIntersecting, hasIntersected }
}

/**
 * Hook for virtual scrolling large lists
 */
export const useVirtualScroll = ({ 
  items, 
  itemHeight, 
  containerHeight, 
  overscan = 5 
}) => {
  const [scrollTop, setScrollTop] = useState(0)
  const scrollElementRef = useRef(null)

  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight)
    const visibleCount = Math.ceil(containerHeight / itemHeight)
    const end = Math.min(items.length, start + visibleCount + overscan)
    
    return {
      start: Math.max(0, start - overscan),
      end
    }
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan])

  const visibleItems = useMemo(() => {
    return items.slice(visibleRange.start, visibleRange.end).map((item, index) => ({
      ...item,
      index: visibleRange.start + index
    }))
  }, [items, visibleRange])

  const totalHeight = items.length * itemHeight
  const offsetY = visibleRange.start * itemHeight

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop)
  }, [])

  return {
    scrollElementRef,
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  }
}

/**
 * Hook for memoizing expensive calculations
 */
export const useExpensiveCalculation = (calculate, dependencies) => {
  return useMemo(() => {
    const start = performance.now()
    const result = calculate()
    const end = performance.now()
    
    if (end - start > 50) {
      console.warn(`Expensive calculation took ${(end - start).toFixed(2)}ms`)
    }
    
    return result
  }, dependencies)
}

/**
 * Hook for managing component state with performance optimizations
 */
export const useOptimizedState = (initialState) => {
  const [state, setState] = useState(initialState)
  const stateRef = useRef(state)

  // Update ref when state changes
  useEffect(() => {
    stateRef.current = state
  }, [state])

  // Optimized setter that prevents unnecessary re-renders
  const setOptimizedState = useCallback((newState) => {
    if (typeof newState === 'function') {
      setState(prevState => {
        const nextState = newState(prevState)
        // Only update if state actually changed
        if (JSON.stringify(nextState) !== JSON.stringify(prevState)) {
          return nextState
        }
        return prevState
      })
    } else {
      // Only update if state actually changed
      if (JSON.stringify(newState) !== JSON.stringify(stateRef.current)) {
        setState(newState)
      }
    }
  }, [])

  return [state, setOptimizedState]
}

/**
 * Hook for batch updates to prevent multiple re-renders
 */
export const useBatchUpdates = () => {
  const [updates, setUpdates] = useState([])
  const timeoutRef = useRef(null)

  const batchUpdate = useCallback((updateFn) => {
    setUpdates(prev => [...prev, updateFn])

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Batch updates together
    timeoutRef.current = setTimeout(() => {
      setUpdates(currentUpdates => {
        // Apply all updates
        currentUpdates.forEach(fn => fn())
        return []
      })
    }, 0)
  }, [])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return batchUpdate
}

/**
 * Hook for preloading data
 */
export const useDataPreloader = () => {
  const preloadedData = useRef(new Map())

  const preload = useCallback(async (key, fetchFn) => {
    if (!preloadedData.current.has(key)) {
      try {
        const data = await fetchFn()
        preloadedData.current.set(key, { data, timestamp: Date.now() })
      } catch (error) {
        console.error(`Preload failed for ${key}:`, error)
      }
    }
  }, [])

  const getPreloaded = useCallback((key, maxAge = 300000) => { // 5 minutes default
    const cached = preloadedData.current.get(key)
    if (cached && Date.now() - cached.timestamp < maxAge) {
      return cached.data
    }
    return null
  }, [])

  const clearPreloaded = useCallback((key) => {
    if (key) {
      preloadedData.current.delete(key)
    } else {
      preloadedData.current.clear()
    }
  }, [])

  return { preload, getPreloaded, clearPreloaded }
}

/**
 * Hook for managing loading states efficiently
 */
export const useLoadingState = () => {
  const [loadingStates, setLoadingStates] = useState({})

  const setLoading = useCallback((key, isLoading) => {
    setLoadingStates(prev => ({
      ...prev,
      [key]: isLoading
    }))
  }, [])

  const isLoading = useCallback((key) => {
    return Boolean(loadingStates[key])
  }, [loadingStates])

  const isAnyLoading = useMemo(() => {
    return Object.values(loadingStates).some(Boolean)
  }, [loadingStates])

  return { setLoading, isLoading, isAnyLoading }
}
