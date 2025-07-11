// Enhanced API service for brand audit tool with comprehensive error handling
import ErrorToast from '../components/ErrorHandling/ErrorToast.jsx'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
    this.retryAttempts = new Map() // Track retry attempts per request
    this.circuitBreakers = new Map() // Track circuit breaker states
    this.requestQueue = new Map() // Queue for rate-limited requests
  }

  async request(endpoint, options = {}) {
    const requestId = `${endpoint}_${Date.now()}`
    const url = `${this.baseURL}${endpoint}`

    // Check circuit breaker
    if (this.isCircuitOpen(endpoint)) {
      const error = {
        category: 'api_error',
        severity: 'high',
        error: 'Service temporarily unavailable',
        circuit_breaker_open: true,
        retry_after: this.getCircuitRetryTime(endpoint)
      }

      if (options.showToast !== false) {
        ErrorToast.show(error)
      }

      throw new Error('Circuit breaker is open')
    }

    const config = {
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
        'X-Request-ID': requestId,
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await this.executeWithRetry(url, config, endpoint, options)

      // Reset circuit breaker on success
      this.resetCircuitBreaker(endpoint)

      return response
    } catch (error) {
      // Update circuit breaker on failure
      this.updateCircuitBreaker(endpoint, error)

      // Handle error with user-friendly messages
      const enhancedError = this.enhanceError(error, endpoint, options)

      if (options.showToast !== false) {
        this.showErrorToast(enhancedError, options)
      }

      throw enhancedError
    }
  }

  async executeWithRetry(url, config, endpoint, options) {
    const maxRetries = options.maxRetries || 3
    const retryKey = `${endpoint}_${JSON.stringify(config.body || {})}`

    let lastError

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        const response = await fetch(url, config)

        // Handle different response statuses
        if (response.status === 429) {
          // Rate limited
          const retryAfter = response.headers.get('Retry-After') || 60
          throw new RateLimitError(`Rate limited. Retry after ${retryAfter} seconds`, retryAfter)
        }

        if (response.status === 401 || response.status === 403) {
          // Authentication error - don't retry
          throw new AuthenticationError('Authentication failed')
        }

        if (response.status >= 400 && response.status < 500) {
          // Client error - don't retry
          const errorData = await response.json().catch(() => ({}))
          throw new ClientError(errorData.message || `Client error: ${response.status}`, response.status)
        }

        if (!response.ok) {
          // Server error - retry
          throw new ServerError(`Server error: ${response.status}`, response.status)
        }

        const data = await response.json()

        // Reset retry count on success
        this.retryAttempts.delete(retryKey)

        return data

      } catch (error) {
        lastError = error

        // Don't retry certain error types
        if (error instanceof AuthenticationError ||
            error instanceof ClientError ||
            error instanceof RateLimitError) {
          break
        }

        // Don't retry on last attempt
        if (attempt === maxRetries - 1) {
          break
        }

        // Calculate delay with exponential backoff and jitter
        const baseDelay = Math.pow(2, attempt) * 1000 // 1s, 2s, 4s
        const jitter = Math.random() * 1000 // 0-1s jitter
        const delay = Math.min(baseDelay + jitter, 10000) // Max 10s

        console.log(`Retrying ${endpoint} in ${delay}ms (attempt ${attempt + 1}/${maxRetries})`)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }

    // Track retry attempts
    this.retryAttempts.set(retryKey, (this.retryAttempts.get(retryKey) || 0) + 1)

    throw lastError
  }

  enhanceError(error, endpoint, options) {
    // Create enhanced error object with user-friendly information
    const enhancedError = {
      original: error,
      endpoint,
      timestamp: new Date().toISOString(),
      error_id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }

    if (error instanceof RateLimitError) {
      enhancedError.category = 'rate_limit_error'
      enhancedError.severity = 'medium'
      enhancedError.error = 'Too many requests. Please wait before trying again.'
      enhancedError.user_actions = [`Wait ${error.retryAfter} seconds before retrying`]
      enhancedError.retry_after = error.retryAfter
      enhancedError.can_retry_after_action = true
    } else if (error instanceof AuthenticationError) {
      enhancedError.category = 'authentication_error'
      enhancedError.severity = 'high'
      enhancedError.error = 'Authentication failed. Please log in again.'
      enhancedError.user_actions = ['Check your login credentials', 'Try logging out and back in']
      enhancedError.requires_user_action = true
    } else if (error instanceof ClientError) {
      enhancedError.category = 'validation_error'
      enhancedError.severity = 'low'
      enhancedError.error = error.message || 'Please check your input and try again.'
      enhancedError.user_actions = ['Review your input', 'Correct any errors and try again']
      enhancedError.requires_user_action = true
    } else if (error instanceof ServerError) {
      enhancedError.category = 'api_error'
      enhancedError.severity = 'medium'
      enhancedError.error = 'Server is experiencing issues. Please try again.'
      enhancedError.user_actions = ['Try again in a few moments', 'Contact support if the issue persists']
      enhancedError.can_retry_after_action = true
    } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
      enhancedError.category = 'network_error'
      enhancedError.severity = 'medium'
      enhancedError.error = 'Network connection failed. Please check your internet connection.'
      enhancedError.user_actions = ['Check your internet connection', 'Try again in a moment']
      enhancedError.can_retry_after_action = true
    } else {
      enhancedError.category = 'system_error'
      enhancedError.severity = 'medium'
      enhancedError.error = 'An unexpected error occurred. Please try again.'
      enhancedError.user_actions = ['Try again', 'Contact support if the issue persists']
      enhancedError.can_retry_after_action = true
    }

    return enhancedError
  }

  showErrorToast(error, options) {
    const toastOptions = {
      onRetry: options.onRetry,
      duration: this.getToastDuration(error.severity)
    }

    switch (error.category) {
      case 'network_error':
        ErrorToast.networkError(error.error, toastOptions)
        break
      case 'authentication_error':
        ErrorToast.authError(error.error, toastOptions)
        break
      case 'rate_limit_error':
        ErrorToast.rateLimitError(error.error, error.retry_after, toastOptions)
        break
      case 'validation_error':
        ErrorToast.validationError(error.error, toastOptions)
        break
      case 'api_error':
        const apiName = this.getApiNameFromEndpoint(error.endpoint)
        ErrorToast.apiError(apiName, error.error, toastOptions)
        break
      default:
        ErrorToast.show(error, toastOptions)
    }
  }

  getToastDuration(severity) {
    switch (severity) {
      case 'critical': return 12000
      case 'high': return 10000
      case 'medium': return 8000
      case 'low': return 6000
      default: return 8000
    }
  }

  getApiNameFromEndpoint(endpoint) {
    if (endpoint.includes('brand')) return 'brandfetch'
    if (endpoint.includes('news')) return 'newsapi'
    if (endpoint.includes('analyze')) return 'openrouter'
    return 'api'
  }

  // Circuit breaker methods
  isCircuitOpen(endpoint) {
    const breaker = this.circuitBreakers.get(endpoint)
    if (!breaker) return false

    if (breaker.state === 'open') {
      // Check if enough time has passed to try again
      if (Date.now() > breaker.nextAttempt) {
        breaker.state = 'half-open'
        return false
      }
      return true
    }

    return false
  }

  updateCircuitBreaker(endpoint, error) {
    const breaker = this.circuitBreakers.get(endpoint) || {
      failures: 0,
      state: 'closed',
      nextAttempt: 0
    }

    if (error instanceof ServerError || error.name === 'TypeError') {
      breaker.failures++

      // Open circuit after 3 failures
      if (breaker.failures >= 3) {
        breaker.state = 'open'
        breaker.nextAttempt = Date.now() + (60 * 1000) // 1 minute
        console.log(`Circuit breaker opened for ${endpoint}`)
      }
    }

    this.circuitBreakers.set(endpoint, breaker)
  }

  resetCircuitBreaker(endpoint) {
    const breaker = this.circuitBreakers.get(endpoint)
    if (breaker) {
      breaker.failures = 0
      breaker.state = 'closed'
      breaker.nextAttempt = 0
    }
  }

  getCircuitRetryTime(endpoint) {
    const breaker = this.circuitBreakers.get(endpoint)
    if (breaker && breaker.nextAttempt > Date.now()) {
      return Math.ceil((breaker.nextAttempt - Date.now()) / 1000)
    }
    return 0
  }

  // Health check method
  async healthCheck() {
    try {
      const response = await this.request('/health', {
        showToast: false,
        maxRetries: 1
      })
      return response
    } catch (error) {
      console.warn('Health check failed:', error)
      return { status: 'unhealthy', error: error.message }
    }
  }

  // Get system status
  async getSystemStatus() {
    try {
      const response = await this.request('/health/detailed', {
        showToast: false,
        maxRetries: 1
      })
      return response
    } catch (error) {
      return { status: 'unknown', error: error.message }
    }
  }

  // Brand search and information
  async searchBrand(query) {
    return this.request('/brand/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    })
  }

  async getBrandAssets(website) {
    return this.request('/brand/assets', {
      method: 'POST',
      body: JSON.stringify({ website }),
    })
  }

  // File upload
  async uploadFiles(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    return this.request('/upload', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    })
  }

  // Analysis
  async startAnalysis(analysisData) {
    return this.request('/analyze', {
      method: 'POST',
      body: JSON.stringify(analysisData),
    })
  }

  async getAnalysisStatus(analysisId) {
    return this.request(`/analyze/${analysisId}/status`)
  }

  async getAnalysisResults(analysisId) {
    return this.request(`/analyze/${analysisId}/results`)
  }

  // Report generation
  async generateReport(reportData) {
    return this.request('/report/generate', {
      method: 'POST',
      body: JSON.stringify(reportData),
    })
  }

  // Health check
  async healthCheck() {
    return this.request('/health')
  }

  // Historical analyses
  async getUserAnalyses() {
    return this.request('/analyses')
  }
}

}

// Custom Error Classes
class RateLimitError extends Error {
  constructor(message, retryAfter) {
    super(message)
    this.name = 'RateLimitError'
    this.retryAfter = retryAfter
  }
}

class AuthenticationError extends Error {
  constructor(message) {
    super(message)
    this.name = 'AuthenticationError'
  }
}

class ClientError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ClientError'
    this.status = status
  }
}

class ServerError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ServerError'
    this.status = status
  }
}

export const apiService = new ApiService()
export default apiService

