import React from 'react'
import { toast } from 'sonner'
import { 
  AlertTriangle, 
  Wifi, 
  Shield, 
  Clock, 
  Settings,
  RefreshCw,
  X
} from 'lucide-react'

const ErrorToast = {
  // Show different types of error toasts based on error category
  show: (error, options = {}) => {
    const {
      duration = 6000,
      action,
      onDismiss,
      position = 'top-right'
    } = options

    const getIcon = (category) => {
      switch (category) {
        case 'network_error':
          return <Wifi className="w-4 h-4" />
        case 'authentication_error':
          return <Shield className="w-4 h-4" />
        case 'rate_limit_error':
          return <Clock className="w-4 h-4" />
        case 'validation_error':
          return <Settings className="w-4 h-4" />
        default:
          return <AlertTriangle className="w-4 h-4" />
      }
    }

    const getToastType = (severity) => {
      switch (severity) {
        case 'critical':
        case 'high':
          return 'error'
        case 'medium':
          return 'warning'
        case 'low':
        default:
          return 'info'
      }
    }

    const message = error.error || error.user_message || 'An unexpected error occurred'
    const toastType = getToastType(error.severity)

    const toastOptions = {
      duration,
      position,
      icon: getIcon(error.category),
      description: error.user_actions && error.user_actions.length > 0 
        ? error.user_actions[0] 
        : undefined,
      action: action || (error.can_retry_after_action && {
        label: 'Retry',
        onClick: () => {
          if (options.onRetry) {
            options.onRetry()
          }
        }
      }),
      onDismiss,
      className: `error-toast error-toast--${error.category} error-toast--${error.severity}`,
      id: error.error_id || `error-${Date.now()}`
    }

    // Show appropriate toast type
    switch (toastType) {
      case 'error':
        return toast.error(message, toastOptions)
      case 'warning':
        return toast.warning(message, toastOptions)
      default:
        return toast.info(message, toastOptions)
    }
  },

  // Specific toast types for common error scenarios
  networkError: (message = 'Network connection failed', options = {}) => {
    return ErrorToast.show({
      category: 'network_error',
      severity: 'medium',
      error: message,
      user_actions: ['Check your internet connection', 'Try again in a moment']
    }, {
      duration: 8000,
      ...options
    })
  },

  authError: (message = 'Authentication failed', options = {}) => {
    return ErrorToast.show({
      category: 'authentication_error',
      severity: 'high',
      error: message,
      user_actions: ['Please log in again', 'Check your credentials']
    }, {
      duration: 10000,
      ...options
    })
  },

  rateLimitError: (message = 'Too many requests', retryAfter = null, options = {}) => {
    const retryMessage = retryAfter 
      ? `Please wait ${retryAfter} seconds before trying again`
      : 'Please wait a moment before trying again'

    return ErrorToast.show({
      category: 'rate_limit_error',
      severity: 'medium',
      error: message,
      user_actions: [retryMessage]
    }, {
      duration: retryAfter ? retryAfter * 1000 : 8000,
      ...options
    })
  },

  validationError: (message = 'Please check your input', options = {}) => {
    return ErrorToast.show({
      category: 'validation_error',
      severity: 'low',
      error: message,
      user_actions: ['Review the form fields', 'Correct any highlighted errors']
    }, {
      duration: 6000,
      ...options
    })
  },

  apiError: (apiName, message = 'Service temporarily unavailable', options = {}) => {
    const friendlyNames = {
      'brandfetch': 'Brand information service',
      'newsapi': 'News service',
      'openrouter': 'AI analysis service',
      'opencorporates': 'Company data service'
    }

    const serviceName = friendlyNames[apiName] || apiName
    const fullMessage = `${serviceName} is ${message.toLowerCase()}`

    return ErrorToast.show({
      category: 'api_error',
      severity: 'medium',
      error: fullMessage,
      user_actions: ['We\'ll try alternative sources', 'Some features may be limited']
    }, {
      duration: 8000,
      ...options
    })
  },

  // Success toast for error recovery
  recovery: (message = 'Service restored', options = {}) => {
    return toast.success(message, {
      icon: <RefreshCw className="w-4 h-4" />,
      duration: 4000,
      ...options
    })
  },

  // Dismiss all error toasts
  dismissAll: () => {
    toast.dismiss()
  },

  // Dismiss specific toast by ID
  dismiss: (toastId) => {
    toast.dismiss(toastId)
  }
}

// Custom toast styles (to be added to global CSS)
export const errorToastStyles = `
.error-toast {
  border-left: 4px solid;
}

.error-toast--critical,
.error-toast--high {
  border-left-color: #ef4444;
}

.error-toast--medium {
  border-left-color: #f59e0b;
}

.error-toast--low {
  border-left-color: #3b82f6;
}

.error-toast--network_error {
  background-color: #fef3c7;
}

.error-toast--authentication_error {
  background-color: #fee2e2;
}

.error-toast--rate_limit_error {
  background-color: #fef3c7;
}

.error-toast--validation_error {
  background-color: #dbeafe;
}
`

export default ErrorToast
