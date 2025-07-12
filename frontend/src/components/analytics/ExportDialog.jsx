import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import exportService from '../../services/exportService.js'
import { 
  Download, 
  FileText, 
  Image, 
  Table, 
  Presentation,
  Settings,
  CheckCircle,
  AlertTriangle,
  Loader2,
  X
} from 'lucide-react'

const ExportDialog = ({ 
  isOpen, 
  onClose, 
  data, 
  brandName = 'Brand',
  dashboardElementId = 'analytics-dashboard'
}) => {
  const [exportFormat, setExportFormat] = useState('pdf')
  const [template, setTemplate] = useState('detailed')
  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)
  const [exportStatus, setExportStatus] = useState(null)
  const [customOptions, setCustomOptions] = useState({
    includeCharts: true,
    includeData: true,
    includeInsights: true,
    customTitle: '',
    customDescription: '',
    dateRange: 'all',
    selectedMetrics: ['brandHealth', 'sentiment', 'marketShare']
  })

  const exportFormats = [
    { value: 'pdf', label: 'PDF Report', icon: FileText, description: 'Comprehensive PDF document' },
    { value: 'xlsx', label: 'Excel Spreadsheet', icon: Table, description: 'Data tables and charts' },
    { value: 'csv', label: 'CSV Data', icon: Table, description: 'Raw data export' },
    { value: 'png', label: 'PNG Image', icon: Image, description: 'Dashboard screenshot' },
    { value: 'pptx', label: 'PowerPoint', icon: Presentation, description: 'Presentation slides' }
  ]

  const templates = [
    { value: 'executive', label: 'Executive Summary', description: 'High-level overview for executives' },
    { value: 'detailed', label: 'Detailed Report', description: 'Comprehensive analysis report' },
    { value: 'competitive', label: 'Competitive Analysis', description: 'Focus on competitive insights' },
    { value: 'trends', label: 'Trend Analysis', description: 'Historical trends and forecasts' },
    { value: 'custom', label: 'Custom Report', description: 'Customizable template' }
  ]

  const availableMetrics = [
    { id: 'brandHealth', label: 'Brand Health' },
    { id: 'sentiment', label: 'Sentiment Analysis' },
    { id: 'marketShare', label: 'Market Share' },
    { id: 'awareness', label: 'Brand Awareness' },
    { id: 'engagement', label: 'Engagement Rate' },
    { id: 'competitive', label: 'Competitive Position' }
  ]

  const handleExport = async () => {
    setIsExporting(true)
    setExportProgress(0)
    setExportStatus(null)

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setExportProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      let blob
      let filename
      const timestamp = new Date().toISOString().split('T')[0]

      const exportOptions = {
        template,
        brandName,
        ...customOptions
      }

      switch (exportFormat) {
        case 'pdf':
          blob = await exportService.exportToPDF(data, exportOptions)
          filename = `${brandName}_analytics_report_${timestamp}.pdf`
          break

        case 'xlsx':
          const excelData = await exportService.exportToExcel(data, exportOptions)
          blob = new Blob([excelData], { 
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
          })
          filename = `${brandName}_analytics_data_${timestamp}.xlsx`
          break

        case 'csv':
          blob = await exportService.exportToCSV(data, exportOptions)
          filename = `${brandName}_analytics_data_${timestamp}.csv`
          break

        case 'png':
          blob = await exportService.exportToImage(dashboardElementId, {
            format: 'png',
            quality: 0.95
          })
          filename = `${brandName}_dashboard_${timestamp}.png`
          break

        case 'pptx':
          const pptData = await exportService.exportToPowerPoint(data, exportOptions)
          blob = new Blob([pptData], { type: 'application/json' })
          filename = `${brandName}_presentation_${timestamp}.json`
          break

        default:
          throw new Error('Unsupported export format')
      }

      clearInterval(progressInterval)
      setExportProgress(100)

      // Download the file
      exportService.downloadFile(blob, filename)

      setExportStatus({
        type: 'success',
        message: `Successfully exported ${exportFormat.toUpperCase()} report`,
        filename
      })

      // Auto-close after successful export
      setTimeout(() => {
        onClose()
        setExportStatus(null)
        setExportProgress(0)
      }, 2000)

    } catch (error) {
      console.error('Export error:', error)
      setExportStatus({
        type: 'error',
        message: error.message || 'Export failed'
      })
    } finally {
      setIsExporting(false)
    }
  }

  const handleMetricToggle = (metricId) => {
    setCustomOptions(prev => ({
      ...prev,
      selectedMetrics: prev.selectedMetrics.includes(metricId)
        ? prev.selectedMetrics.filter(id => id !== metricId)
        : [...prev.selectedMetrics, metricId]
    }))
  }

  const FormatCard = ({ format }) => {
    const Icon = format.icon
    const isSelected = exportFormat === format.value

    return (
      <Card 
        className={`cursor-pointer transition-all ${
          isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:shadow-md'
        }`}
        onClick={() => setExportFormat(format.value)}
      >
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <Icon className={`h-6 w-6 ${isSelected ? 'text-blue-600' : 'text-gray-600'}`} />
            <div>
              <h3 className="font-medium text-gray-900">{format.label}</h3>
              <p className="text-sm text-gray-600">{format.description}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-blue-600" />
            Export Analytics Report
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Export Status */}
          {exportStatus && (
            <div className={`p-4 rounded-lg flex items-center gap-3 ${
              exportStatus.type === 'success' 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              {exportStatus.type === 'success' ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-red-600" />
              )}
              <div>
                <p className={`font-medium ${
                  exportStatus.type === 'success' ? 'text-green-900' : 'text-red-900'
                }`}>
                  {exportStatus.message}
                </p>
                {exportStatus.filename && (
                  <p className="text-sm text-gray-600">File: {exportStatus.filename}</p>
                )}
              </div>
            </div>
          )}

          {/* Export Progress */}
          {isExporting && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Exporting...</span>
                <span className="text-sm text-gray-500">{exportProgress}%</span>
              </div>
              <Progress value={exportProgress} className="h-2" />
            </div>
          )}

          <Tabs defaultValue="format" className="space-y-6">
            <TabsList>
              <TabsTrigger value="format">Format</TabsTrigger>
              <TabsTrigger value="template">Template</TabsTrigger>
              <TabsTrigger value="options">Options</TabsTrigger>
            </TabsList>

            <TabsContent value="format" className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Select Export Format</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {exportFormats.map(format => (
                    <FormatCard key={format.value} format={format} />
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="template" className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Choose Template</h3>
                <Select value={template} onValueChange={setTemplate}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map(tmpl => (
                      <SelectItem key={tmpl.value} value={tmpl.value}>
                        <div>
                          <div className="font-medium">{tmpl.label}</div>
                          <div className="text-sm text-gray-600">{tmpl.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {template === 'custom' && (
                <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <Label htmlFor="custom-title">Custom Title</Label>
                    <Input
                      id="custom-title"
                      value={customOptions.customTitle}
                      onChange={(e) => setCustomOptions(prev => ({ 
                        ...prev, 
                        customTitle: e.target.value 
                      }))}
                      placeholder="Enter custom report title"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="custom-description">Description</Label>
                    <Textarea
                      id="custom-description"
                      value={customOptions.customDescription}
                      onChange={(e) => setCustomOptions(prev => ({ 
                        ...prev, 
                        customDescription: e.target.value 
                      }))}
                      placeholder="Enter report description"
                      rows={3}
                    />
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="options" className="space-y-6">
              {/* Content Options */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Content Options</h3>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      checked={customOptions.includeCharts}
                      onCheckedChange={(checked) => setCustomOptions(prev => ({ 
                        ...prev, 
                        includeCharts: checked 
                      }))}
                    />
                    <Label>Include Charts and Visualizations</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      checked={customOptions.includeData}
                      onCheckedChange={(checked) => setCustomOptions(prev => ({ 
                        ...prev, 
                        includeData: checked 
                      }))}
                    />
                    <Label>Include Raw Data Tables</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      checked={customOptions.includeInsights}
                      onCheckedChange={(checked) => setCustomOptions(prev => ({ 
                        ...prev, 
                        includeInsights: checked 
                      }))}
                    />
                    <Label>Include Insights and Recommendations</Label>
                  </div>
                </div>
              </div>

              {/* Metrics Selection */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Select Metrics</h3>
                <div className="grid grid-cols-2 gap-3">
                  {availableMetrics.map(metric => (
                    <div key={metric.id} className="flex items-center space-x-2">
                      <Checkbox
                        checked={customOptions.selectedMetrics.includes(metric.id)}
                        onCheckedChange={() => handleMetricToggle(metric.id)}
                      />
                      <Label className="text-sm">{metric.label}</Label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Date Range */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Date Range</h3>
                <Select 
                  value={customOptions.dateRange} 
                  onValueChange={(value) => setCustomOptions(prev => ({ 
                    ...prev, 
                    dateRange: value 
                  }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Available Data</SelectItem>
                    <SelectItem value="30d">Last 30 Days</SelectItem>
                    <SelectItem value="90d">Last 90 Days</SelectItem>
                    <SelectItem value="1y">Last Year</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </Tabs>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-gray-600">
              Export format: <Badge variant="outline">{exportFormat.toUpperCase()}</Badge>
              {template && <span> • Template: <Badge variant="outline">{template}</Badge></span>}
            </div>
            
            <div className="flex gap-3">
              <Button variant="outline" onClick={onClose} disabled={isExporting}>
                Cancel
              </Button>
              <Button onClick={handleExport} disabled={isExporting}>
                {isExporting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    Export Report
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default ExportDialog
