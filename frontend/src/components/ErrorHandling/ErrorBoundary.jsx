import React from 'react'
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: 0
    }
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      error: error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      errorInfo: errorInfo
    })

    // Log error to monitoring service
    this.logError(error, errorInfo)
  }

  logError = (error, errorInfo) => {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      errorId: this.state.errorId,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    }

    // Send to backend error logging
    fetch('/api/errors/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorData)
    }).catch(err => {
      console.error('Failed to log error:', err)
    })

    // Log to console for development
    console.error('Error Boundary caught an error:', error, errorInfo)
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
      retryCount: prevState.retryCount + 1
    }))
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  handleReportBug = () => {
    const subject = encodeURIComponent(`Bug Report - Error ID: ${this.state.errorId}`)
    const body = encodeURIComponent(`
Error ID: ${this.state.errorId}
Error Message: ${this.state.error?.message}
Timestamp: ${new Date().toISOString()}
URL: ${window.location.href}
User Agent: ${navigator.userAgent}

Please describe what you were doing when this error occurred:
[Your description here]
    `)
    
    window.open(`mailto:support@brandaudit.com?subject=${subject}&body=${body}`)
  }

  render() {
    if (this.state.hasError) {
      const isNetworkError = this.state.error?.message?.includes('fetch') || 
                            this.state.error?.message?.includes('network')
      
      const isDevelopment = process.env.NODE_ENV === 'development'

      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <CardTitle className="text-2xl text-gray-900">
                Something went wrong
              </CardTitle>
              <CardDescription className="text-lg">
                {isNetworkError 
                  ? "We're having trouble connecting to our servers"
                  : "An unexpected error occurred while loading the application"
                }
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Error ID for support */}
              <div className="bg-gray-100 p-3 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Error ID:</span>
                  <Badge variant="secondary" className="font-mono text-xs">
                    {this.state.errorId}
                  </Badge>
                </div>
              </div>

              {/* User-friendly error message */}
              <Alert>
                <AlertDescription>
                  {isNetworkError ? (
                    <>
                      Please check your internet connection and try again. If the problem persists, 
                      our servers might be temporarily unavailable.
                    </>
                  ) : (
                    <>
                      This error has been automatically reported to our team. You can try refreshing 
                      the page or return to the home page.
                    </>
                  )}
                </AlertDescription>
              </Alert>

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  onClick={this.handleRetry}
                  className="flex-1"
                  disabled={this.state.retryCount >= 3}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {this.state.retryCount >= 3 ? 'Max retries reached' : 'Try Again'}
                </Button>
                
                <Button 
                  onClick={this.handleGoHome}
                  variant="outline"
                  className="flex-1"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go Home
                </Button>
                
                <Button 
                  onClick={this.handleReportBug}
                  variant="outline"
                  className="flex-1"
                >
                  <Bug className="w-4 h-4 mr-2" />
                  Report Bug
                </Button>
              </div>

              {/* Retry count indicator */}
              {this.state.retryCount > 0 && (
                <div className="text-center text-sm text-gray-500">
                  Retry attempts: {this.state.retryCount}/3
                </div>
              )}

              {/* Development error details */}
              {isDevelopment && this.state.error && (
                <details className="mt-6">
                  <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                    Developer Details (Development Mode Only)
                  </summary>
                  <div className="mt-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="text-sm">
                      <div className="font-semibold text-red-800 mb-2">Error Message:</div>
                      <div className="text-red-700 mb-4 font-mono text-xs">
                        {this.state.error.message}
                      </div>
                      
                      {this.state.error.stack && (
                        <>
                          <div className="font-semibold text-red-800 mb-2">Stack Trace:</div>
                          <pre className="text-red-700 text-xs overflow-x-auto whitespace-pre-wrap">
                            {this.state.error.stack}
                          </pre>
                        </>
                      )}
                      
                      {this.state.errorInfo?.componentStack && (
                        <>
                          <div className="font-semibold text-red-800 mb-2 mt-4">Component Stack:</div>
                          <pre className="text-red-700 text-xs overflow-x-auto whitespace-pre-wrap">
                            {this.state.errorInfo.componentStack}
                          </pre>
                        </>
                      )}
                    </div>
                  </div>
                </details>
              )}

              {/* Help text */}
              <div className="text-center text-sm text-gray-500">
                If this problem continues, please contact our support team with the Error ID above.
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
