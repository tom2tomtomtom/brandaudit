import React, { useState, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Settings, 
  Layout, 
  Grid,
  Save,
  RotateCcw,
  Eye,
  EyeOff,
  Move,
  Trash2,
  Plus,
  Copy,
  Download,
  Upload,
  Palette,
  Monitor,
  Smartphone,
  Tablet
} from 'lucide-react'

const CustomizableDashboard = ({ data, layout, onLayoutChange }) => {
  const [editMode, setEditMode] = useState(false)
  const [selectedWidget, setSelectedWidget] = useState(null)
  const [dashboardConfig, setDashboardConfig] = useState({
    name: 'My Dashboard',
    theme: 'light',
    layout: 'grid',
    columns: 3,
    widgets: [
      { id: 'brand-health', type: 'metric', title: 'Brand Health', visible: true, position: { x: 0, y: 0, w: 1, h: 1 } },
      { id: 'sentiment-trend', type: 'chart', title: 'Sentiment Trend', visible: true, position: { x: 1, y: 0, w: 2, h: 1 } },
      { id: 'competitive-position', type: 'chart', title: 'Competitive Position', visible: true, position: { x: 0, y: 1, w: 1, h: 1 } },
      { id: 'key-metrics', type: 'metrics-grid', title: 'Key Metrics', visible: true, position: { x: 1, y: 1, w: 2, h: 1 } },
      { id: 'insights', type: 'list', title: 'Latest Insights', visible: true, position: { x: 0, y: 2, w: 3, h: 1 } }
    ]
  })

  // Available widget types
  const widgetTypes = [
    { id: 'metric', name: 'Single Metric', icon: '📊' },
    { id: 'chart', name: 'Chart', icon: '📈' },
    { id: 'metrics-grid', name: 'Metrics Grid', icon: '🔢' },
    { id: 'list', name: 'List', icon: '📋' },
    { id: 'gauge', name: 'Gauge', icon: '⏱️' },
    { id: 'table', name: 'Table', icon: '📄' },
    { id: 'map', name: 'Map', icon: '🗺️' },
    { id: 'calendar', name: 'Calendar', icon: '📅' }
  ]

  // Layout presets
  const layoutPresets = [
    { id: 'executive', name: 'Executive View', description: 'High-level metrics and KPIs' },
    { id: 'detailed', name: 'Detailed Analysis', description: 'Comprehensive data views' },
    { id: 'competitive', name: 'Competitive Focus', description: 'Competition-centered insights' },
    { id: 'trends', name: 'Trend Analysis', description: 'Time-series and trend data' }
  ]

  const handleWidgetToggle = (widgetId) => {
    setDashboardConfig(prev => ({
      ...prev,
      widgets: prev.widgets.map(widget =>
        widget.id === widgetId ? { ...widget, visible: !widget.visible } : widget
      )
    }))
  }

  const handleWidgetUpdate = (widgetId, updates) => {
    setDashboardConfig(prev => ({
      ...prev,
      widgets: prev.widgets.map(widget =>
        widget.id === widgetId ? { ...widget, ...updates } : widget
      )
    }))
  }

  const handleAddWidget = (type) => {
    const newWidget = {
      id: `widget-${Date.now()}`,
      type,
      title: `New ${widgetTypes.find(t => t.id === type)?.name}`,
      visible: true,
      position: { x: 0, y: 0, w: 1, h: 1 }
    }
    
    setDashboardConfig(prev => ({
      ...prev,
      widgets: [...prev.widgets, newWidget]
    }))
  }

  const handleRemoveWidget = (widgetId) => {
    setDashboardConfig(prev => ({
      ...prev,
      widgets: prev.widgets.filter(widget => widget.id !== widgetId)
    }))
  }

  const handleSaveLayout = () => {
    // Save to localStorage or API
    localStorage.setItem('dashboard-config', JSON.stringify(dashboardConfig))
    setEditMode(false)
  }

  const handleLoadPreset = (presetId) => {
    // Load preset configuration
    const presets = {
      executive: {
        ...dashboardConfig,
        widgets: dashboardConfig.widgets.filter(w => 
          ['brand-health', 'key-metrics', 'insights'].includes(w.id)
        )
      },
      detailed: {
        ...dashboardConfig,
        widgets: dashboardConfig.widgets
      },
      competitive: {
        ...dashboardConfig,
        widgets: dashboardConfig.widgets.filter(w => 
          ['competitive-position', 'sentiment-trend', 'key-metrics'].includes(w.id)
        )
      }
    }
    
    setDashboardConfig(presets[presetId] || dashboardConfig)
  }

  const WidgetCard = ({ widget }) => {
    const isSelected = selectedWidget === widget.id
    
    return (
      <Card 
        className={`relative transition-all ${
          editMode ? 'cursor-move border-dashed' : ''
        } ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
        onClick={() => editMode && setSelectedWidget(widget.id)}
      >
        {editMode && (
          <div className="absolute top-2 right-2 z-10 flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                handleWidgetToggle(widget.id)
              }}
            >
              {widget.visible ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                handleRemoveWidget(widget.id)
              }}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        )}
        
        <CardHeader className="pb-3">
          <CardTitle className="text-sm flex items-center gap-2">
            <span>{widgetTypes.find(t => t.id === widget.type)?.icon}</span>
            {editMode ? (
              <Input
                value={widget.title}
                onChange={(e) => handleWidgetUpdate(widget.id, { title: e.target.value })}
                className="text-sm h-6 border-none p-0 font-semibold"
              />
            ) : (
              widget.title
            )}
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          {/* Widget content based on type */}
          {widget.type === 'metric' && (
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">85</div>
              <div className="text-xs text-gray-500">Brand Health Score</div>
            </div>
          )}
          
          {widget.type === 'chart' && (
            <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
              <span className="text-gray-500 text-sm">Chart Placeholder</span>
            </div>
          )}
          
          {widget.type === 'metrics-grid' && (
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="font-semibold">78%</div>
                <div className="text-gray-500">Sentiment</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="font-semibold">15.2%</div>
                <div className="text-gray-500">Market Share</div>
              </div>
            </div>
          )}
          
          {widget.type === 'list' && (
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Positive sentiment trending up</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span>Competitor activity detected</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const WidgetLibrary = () => (
    <div className="space-y-4">
      <h3 className="font-semibold text-gray-900">Widget Library</h3>
      <div className="grid grid-cols-2 gap-2">
        {widgetTypes.map(type => (
          <Button
            key={type.id}
            variant="outline"
            size="sm"
            onClick={() => handleAddWidget(type.id)}
            className="justify-start text-xs"
          >
            <span className="mr-2">{type.icon}</span>
            {type.name}
          </Button>
        ))}
      </div>
    </div>
  )

  const LayoutSettings = () => (
    <div className="space-y-4">
      <h3 className="font-semibold text-gray-900">Layout Settings</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label htmlFor="dashboard-name" className="text-sm">Dashboard Name</Label>
          <Input
            id="dashboard-name"
            value={dashboardConfig.name}
            onChange={(e) => setDashboardConfig(prev => ({ ...prev, name: e.target.value }))}
            className="w-32 h-8 text-xs"
          />
        </div>
        
        <div className="flex items-center justify-between">
          <Label htmlFor="theme" className="text-sm">Theme</Label>
          <Select 
            value={dashboardConfig.theme} 
            onValueChange={(value) => setDashboardConfig(prev => ({ ...prev, theme: value }))}
          >
            <SelectTrigger className="w-32 h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
              <SelectItem value="auto">Auto</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex items-center justify-between">
          <Label htmlFor="columns" className="text-sm">Columns</Label>
          <Select 
            value={dashboardConfig.columns.toString()} 
            onValueChange={(value) => setDashboardConfig(prev => ({ ...prev, columns: parseInt(value) }))}
          >
            <SelectTrigger className="w-32 h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2">2 Columns</SelectItem>
              <SelectItem value="3">3 Columns</SelectItem>
              <SelectItem value="4">4 Columns</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  )

  const PresetLayouts = () => (
    <div className="space-y-4">
      <h3 className="font-semibold text-gray-900">Layout Presets</h3>
      <div className="space-y-2">
        {layoutPresets.map(preset => (
          <Button
            key={preset.id}
            variant="outline"
            size="sm"
            onClick={() => handleLoadPreset(preset.id)}
            className="w-full justify-start text-xs"
          >
            <div className="text-left">
              <div className="font-medium">{preset.name}</div>
              <div className="text-gray-500">{preset.description}</div>
            </div>
          </Button>
        ))}
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Dashboard Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-semibold text-gray-900">{dashboardConfig.name}</h2>
          <Badge variant="outline">{dashboardConfig.widgets.filter(w => w.visible).length} widgets</Badge>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <Label htmlFor="edit-mode" className="text-sm">Edit Mode</Label>
            <Switch
              id="edit-mode"
              checked={editMode}
              onCheckedChange={setEditMode}
            />
          </div>
          
          {editMode && (
            <>
              <Button variant="outline" size="sm" onClick={handleSaveLayout}>
                <Save className="h-4 w-4 mr-2" />
                Save
              </Button>
              <Button variant="outline" size="sm" onClick={() => setEditMode(false)}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Cancel
              </Button>
            </>
          )}
          
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar - Edit Controls */}
        {editMode && (
          <div className="lg:col-span-1 space-y-6">
            <Tabs defaultValue="widgets" className="space-y-4">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="widgets" className="text-xs">Widgets</TabsTrigger>
                <TabsTrigger value="layout" className="text-xs">Layout</TabsTrigger>
                <TabsTrigger value="presets" className="text-xs">Presets</TabsTrigger>
              </TabsList>
              
              <TabsContent value="widgets">
                <WidgetLibrary />
              </TabsContent>
              
              <TabsContent value="layout">
                <LayoutSettings />
              </TabsContent>
              
              <TabsContent value="presets">
                <PresetLayouts />
              </TabsContent>
            </Tabs>
          </div>
        )}

        {/* Main Dashboard Area */}
        <div className={editMode ? 'lg:col-span-3' : 'lg:col-span-4'}>
          <div 
            className={`grid gap-4 ${
              dashboardConfig.columns === 2 ? 'grid-cols-1 md:grid-cols-2' :
              dashboardConfig.columns === 3 ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' :
              'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
            }`}
          >
            {dashboardConfig.widgets
              .filter(widget => widget.visible)
              .map(widget => (
                <WidgetCard key={widget.id} widget={widget} />
              ))}
          </div>
          
          {editMode && dashboardConfig.widgets.filter(w => w.visible).length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Grid className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No widgets visible. Add widgets from the sidebar.</p>
            </div>
          )}
        </div>
      </div>

      {/* Responsive Preview */}
      {editMode && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Monitor className="h-5 w-5" />
              Responsive Preview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-4">
              <Button variant="outline" size="sm">
                <Monitor className="h-4 w-4 mr-2" />
                Desktop
              </Button>
              <Button variant="outline" size="sm">
                <Tablet className="h-4 w-4 mr-2" />
                Tablet
              </Button>
              <Button variant="outline" size="sm">
                <Smartphone className="h-4 w-4 mr-2" />
                Mobile
              </Button>
            </div>
            <div className="text-sm text-gray-500">
              Preview how your dashboard will look on different devices
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default CustomizableDashboard
