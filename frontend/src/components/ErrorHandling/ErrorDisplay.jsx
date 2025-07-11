import React, { useState } from 'react'
import { 
  AlertTriangle, 
  RefreshCw, 
  Clock, 
  Wifi, 
  Shield, 
  Settings, 
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Copy,
  CheckCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { toast } from 'sonner'

const ErrorDisplay = ({ 
  error, 
  onRetry, 
  onDismiss, 
  showRetry = true, 
  showDismiss = true,
  className = "" 
}) => {
  const [showDetails, setShowDetails] = useState(false)
  const [copied, setCopied] = useState(false)

  if (!error) return null

  const getErrorIcon = (category) => {
    switch (category) {
      case 'network_error':
        return <Wifi className="w-5 h-5" />
      case 'authentication_error':
        return <Shield className="w-5 h-5" />
      case 'rate_limit_error':
        return <Clock className="w-5 h-5" />
      case 'validation_error':
        return <Settings className="w-5 h-5" />
      default:
        return <AlertTriangle className="w-5 h-5" />
    }
  }

  const getErrorColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'destructive'
      case 'high':
        return 'destructive'
      case 'medium':
        return 'default'
      case 'low':
        return 'secondary'
      default:
        return 'default'
    }
  }

  const copyErrorId = async () => {
    if (error.error_id) {
      try {
        await navigator.clipboard.writeText(error.error_id)
        setCopied(true)
        toast.success('Error ID copied to clipboard')
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        toast.error('Failed to copy error ID')
      }
    }
  }

  const formatUserActions = (actions) => {
    if (!actions || !Array.isArray(actions)) return []
    return actions.map((action, index) => (
      <li key={index} className="flex items-start">
        <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
          {index + 1}
        </span>
        <span className="text-sm text-gray-700">{action}</span>
      </li>
    ))
  }

  return (
    <Card className={`border-l-4 ${error.severity === 'critical' ? 'border-l-red-500' : 
                                   error.severity === 'high' ? 'border-l-orange-500' :
                                   error.severity === 'medium' ? 'border-l-yellow-500' : 
                                   'border-l-blue-500'} ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-3">
            <div className={`p-2 rounded-full ${
              error.severity === 'critical' ? 'bg-red-100 text-red-600' :
              error.severity === 'high' ? 'bg-orange-100 text-orange-600' :
              error.severity === 'medium' ? 'bg-yellow-100 text-yellow-600' :
              'bg-blue-100 text-blue-600'
            }`}>
              {getErrorIcon(error.category)}
            </div>
            <div className="flex-1">
              <CardTitle className="text-lg flex items-center gap-2">
                Something went wrong
                <Badge variant={getErrorColor(error.severity)} className="text-xs">
                  {error.severity}
                </Badge>
              </CardTitle>
              <CardDescription className="mt-1">
                {error.error || error.user_message || 'An unexpected error occurred'}
              </CardDescription>
            </div>
          </div>
          
          {error.error_id && (
            <Button
              variant="ghost"
              size="sm"
              onClick={copyErrorId}
              className="flex items-center gap-1 text-xs"
            >
              {copied ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copied' : 'Copy ID'}
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* User Actions */}
        {error.user_actions && error.user_actions.length > 0 && (
          <div>
            <h4 className="font-medium text-sm text-gray-900 mb-2 flex items-center">
              <HelpCircle className="w-4 h-4 mr-1" />
              What you can do:
            </h4>
            <ul className="space-y-2">
              {formatUserActions(error.user_actions)}
            </ul>
          </div>
        )}

        {/* Retry Information */}
        {error.can_retry_after_action && (
          <Alert>
            <Clock className="w-4 h-4" />
            <AlertDescription>
              You can try again after completing the suggested actions above.
            </AlertDescription>
          </Alert>
        )}

        {/* Fallback Information */}
        {error.fallback_available && (
          <Alert>
            <AlertTriangle className="w-4 h-4" />
            <AlertDescription>
              We're using alternative data sources to continue your analysis with limited functionality.
            </AlertDescription>
          </Alert>
        )}

        {/* Circuit Breaker Information */}
        {error.circuit_breaker_open && (
          <Alert>
            <Shield className="w-4 h-4" />
            <AlertDescription>
              Service is temporarily unavailable. 
              {error.retry_after && ` Please try again in ${error.retry_after} seconds.`}
            </AlertDescription>
          </Alert>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 pt-2">
          {showRetry && onRetry && !error.circuit_breaker_open && (
            <Button 
              onClick={onRetry}
              size="sm"
              disabled={error.requires_user_action && !error.can_retry_after_action}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          )}
          
          {showDismiss && onDismiss && (
            <Button 
              onClick={onDismiss}
              variant="outline"
              size="sm"
            >
              Dismiss
            </Button>
          )}
        </div>

        {/* Collapsible Technical Details */}
        {(error.error_id || error.category || error.technical_details) && (
          <Collapsible open={showDetails} onOpenChange={setShowDetails}>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm" className="w-full justify-between p-2">
                <span className="text-xs text-gray-500">Technical Details</span>
                {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-2">
              <div className="bg-gray-50 p-3 rounded-lg text-xs space-y-2">
                {error.error_id && (
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-700">Error ID:</span>
                    <code className="bg-white px-2 py-1 rounded border font-mono">
                      {error.error_id}
                    </code>
                  </div>
                )}
                
                {error.category && (
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-700">Category:</span>
                    <Badge variant="outline" className="text-xs">
                      {error.category.replace('_', ' ')}
                    </Badge>
                  </div>
                )}
                
                {error.timestamp && (
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-700">Time:</span>
                    <span className="text-gray-600">
                      {new Date(error.timestamp).toLocaleString()}
                    </span>
                  </div>
                )}
                
                {error.technical_details && (
                  <div>
                    <span className="font-medium text-gray-700 block mb-1">Technical Details:</span>
                    <pre className="text-gray-600 whitespace-pre-wrap text-xs bg-white p-2 rounded border">
                      {error.technical_details}
                    </pre>
                  </div>
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Support Information */}
        <div className="text-center text-xs text-gray-500 pt-2 border-t">
          If this problem persists, please contact support with the error ID above.
        </div>
      </CardContent>
    </Card>
  )
}

export default ErrorDisplay
