import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  useRealTimeAnalytics,
  useBrandHealthUpdates,
  useSentimentUpdates,
  useCompetitorAlerts,
  useAnalysisNotifications,
  useSystemStatus,
  useConnectionQuality
} from '../../hooks/useRealTimeAnalytics.js'
import { 
  Activity, 
  Wifi, 
  WifiOff,
  Bell,
  BellRing,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Signal,
  Users,
  Server,
  X
} from 'lucide-react'

const RealTimeAnalyticsPanel = ({ brandId, onDataUpdate }) => {
  const [isRealTimeEnabled, setIsRealTimeEnabled] = useState(true)
  const [selectedMetrics, setSelectedMetrics] = useState(['brandHealth', 'sentiment'])
  
  // Real-time hooks
  const { isConnected, connectionStatus, error, lastUpdate } = useRealTimeAnalytics(brandId)
  const { brandHealth, trend } = useBrandHealthUpdates(brandId, onDataUpdate)
  const { sentiment, change } = useSentimentUpdates(brandId, onDataUpdate)
  const { alerts, unreadCount, markAsRead, clearAlerts } = useCompetitorAlerts(brandId)
  const { notifications, dismissNotification, clearAll } = useAnalysisNotifications()
  const systemStatus = useSystemStatus()
  const connectionQuality = useConnectionQuality()

  // Connection status indicator
  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-500'
      case 'connecting': return 'text-yellow-500'
      case 'disconnected': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getConnectionStatusIcon = () => {
    return isConnected ? Wifi : WifiOff
  }

  // Real-time metrics display
  const MetricCard = ({ title, value, change, trend, icon: Icon, unit = '' }) => {
    const getTrendColor = () => {
      if (trend > 0) return 'text-green-500'
      if (trend < 0) return 'text-red-500'
      return 'text-gray-500'
    }

    const TrendIcon = trend > 0 ? TrendingUp : trend < 0 ? TrendingDown : Activity

    return (
      <Card className="relative overflow-hidden">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {Icon && <Icon className="h-4 w-4 text-blue-600" />}
              <span className="text-sm font-medium text-gray-600">{title}</span>
            </div>
            <Badge variant="outline" className="text-xs">
              Live
            </Badge>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="text-2xl font-bold text-gray-900">
              {value !== null ? `${Math.round(value)}${unit}` : '--'}
            </div>
            
            {trend !== null && (
              <div className={`flex items-center gap-1 ${getTrendColor()}`}>
                <TrendIcon className="h-4 w-4" />
                <span className="text-sm font-medium">
                  {Math.abs(trend).toFixed(1)}%
                </span>
              </div>
            )}
          </div>
          
          {change !== null && (
            <div className="text-xs text-gray-500 mt-1">
              Change: {change > 0 ? '+' : ''}{change.toFixed(2)}
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  // Notification item
  const NotificationItem = ({ notification, onDismiss }) => {
    const getNotificationIcon = () => {
      switch (notification.type) {
        case 'success': return CheckCircle
        case 'warning': return AlertTriangle
        case 'error': return AlertTriangle
        default: return Bell
      }
    }

    const getNotificationColor = () => {
      switch (notification.type) {
        case 'success': return 'text-green-600'
        case 'warning': return 'text-yellow-600'
        case 'error': return 'text-red-600'
        default: return 'text-blue-600'
      }
    }

    const Icon = getNotificationIcon()

    return (
      <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
        <Icon className={`h-4 w-4 mt-0.5 ${getNotificationColor()}`} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">{notification.title}</p>
          <p className="text-xs text-gray-600">{notification.message}</p>
          <p className="text-xs text-gray-400 mt-1">
            {new Date(notification.timestamp).toLocaleTimeString()}
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDismiss(notification.id)}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>
    )
  }

  // Alert item
  const AlertItem = ({ alert }) => (
    <div className="flex items-start gap-3 p-3 border-l-4 border-orange-400 bg-orange-50 rounded-r-lg">
      <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm font-medium text-orange-900">{alert.title}</p>
        <p className="text-xs text-orange-700">{alert.message}</p>
        <p className="text-xs text-orange-600 mt-1">
          Competitor: {alert.competitor} • {new Date(alert.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Real-time Controls */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-600" />
              Real-time Analytics
            </CardTitle>
            
            <div className="flex items-center gap-4">
              {/* Connection Status */}
              <div className="flex items-center gap-2">
                {React.createElement(getConnectionStatusIcon(), {
                  className: `h-4 w-4 ${getConnectionStatusColor()}`
                })}
                <span className={`text-sm font-medium ${getConnectionStatusColor()}`}>
                  {connectionStatus}
                </span>
              </div>
              
              {/* Real-time Toggle */}
              <div className="flex items-center gap-2">
                <Label htmlFor="realtime-toggle" className="text-sm">
                  Live Updates
                </Label>
                <Switch
                  id="realtime-toggle"
                  checked={isRealTimeEnabled}
                  onCheckedChange={setIsRealTimeEnabled}
                />
              </div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <span className="text-sm text-red-800">Connection Error: {error}</span>
              </div>
            </div>
          )}
          
          {/* Connection Quality */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Signal className="h-4 w-4 text-gray-500" />
              <span>Latency: {connectionQuality.latency}ms</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-gray-500" />
              <span>Quality: {connectionQuality.stability}</span>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-gray-500" />
              <span>Users: {systemStatus.activeUsers}</span>
            </div>
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4 text-gray-500" />
              <span>API: {systemStatus.apiResponseTime}ms</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Metrics */}
      {isRealTimeEnabled && isConnected && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricCard
            title="Brand Health"
            value={brandHealth}
            trend={trend}
            icon={Activity}
          />
          
          <MetricCard
            title="Sentiment Score"
            value={sentiment ? sentiment * 100 : null}
            change={change}
            icon={TrendingUp}
            unit="%"
          />
          
          <MetricCard
            title="System Status"
            value={systemStatus.uptime}
            icon={Server}
            unit="h"
          />
        </div>
      )}

      {/* Notifications and Alerts */}
      <Tabs defaultValue="notifications" className="space-y-4">
        <TabsList>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
            {notifications.length > 0 && (
              <Badge variant="destructive" className="ml-1 text-xs">
                {notifications.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="alerts" className="flex items-center gap-2">
            <BellRing className="h-4 w-4" />
            Competitor Alerts
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-1 text-xs">
                {unreadCount}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="notifications" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Recent Notifications</h3>
            {notifications.length > 0 && (
              <Button variant="outline" size="sm" onClick={clearAll}>
                Clear All
              </Button>
            )}
          </div>
          
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {notifications.length > 0 ? (
              notifications.map(notification => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onDismiss={dismissNotification}
                />
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p>No new notifications</p>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Competitor Alerts</h3>
            <div className="flex gap-2">
              {unreadCount > 0 && (
                <Button variant="outline" size="sm" onClick={markAsRead}>
                  Mark as Read
                </Button>
              )}
              {alerts.length > 0 && (
                <Button variant="outline" size="sm" onClick={clearAlerts}>
                  Clear All
                </Button>
              )}
            </div>
          </div>
          
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {alerts.length > 0 ? (
              alerts.map((alert, index) => (
                <AlertItem key={index} alert={alert} />
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertTriangle className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p>No competitor alerts</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Last Update Info */}
      {lastUpdate && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>Last update: {new Date(lastUpdate.timestamp).toLocaleTimeString()}</span>
              </div>
              <span>Event: {lastUpdate.eventType}</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default RealTimeAnalyticsPanel
