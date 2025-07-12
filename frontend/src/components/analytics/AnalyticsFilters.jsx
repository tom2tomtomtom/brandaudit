import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover.jsx'
import { Calendar } from '@/components/ui/calendar.jsx'
import { 
  Filter, 
  Calendar as CalendarIcon, 
  X, 
  Save, 
  RotateCcw,
  Search,
  TrendingUp,
  Target,
  BarChart3,
  Eye,
  MessageSquare,
  Globe
} from 'lucide-react'
import { format } from 'date-fns'

const AnalyticsFilters = ({ 
  filters, 
  onFiltersChange, 
  dateRange, 
  onDateRangeChange,
  savedFilters = [],
  onSaveFilter,
  onLoadFilter 
}) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [tempFilters, setTempFilters] = useState(filters)

  // Available filter options
  const analysisTypes = [
    { id: 'brandPerception', label: 'Brand Perception', icon: Eye },
    { id: 'newsAnalysis', label: 'News Analysis', icon: MessageSquare },
    { id: 'visualAnalysis', label: 'Visual Analysis', icon: BarChart3 },
    { id: 'competitiveAnalysis', label: 'Competitive Analysis', icon: Target },
    { id: 'campaignAnalysis', label: 'Campaign Analysis', icon: TrendingUp },
    { id: 'socialMedia', label: 'Social Media', icon: Globe }
  ]

  const timeframeOptions = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 3 months' },
    { value: '6m', label: 'Last 6 months' },
    { value: '1y', label: 'Last year' },
    { value: 'custom', label: 'Custom range' }
  ]

  const competitorFilterOptions = [
    { value: 'all', label: 'All Competitors' },
    { value: 'direct', label: 'Direct Competitors' },
    { value: 'indirect', label: 'Indirect Competitors' },
    { value: 'top5', label: 'Top 5 Competitors' }
  ]

  const handleFilterChange = (key, value) => {
    const newFilters = { ...tempFilters, [key]: value }
    setTempFilters(newFilters)
    onFiltersChange(newFilters)
  }

  const handleAnalysisTypeToggle = (typeId) => {
    const currentTypes = tempFilters.analysisTypes || []
    const newTypes = currentTypes.includes(typeId)
      ? currentTypes.filter(id => id !== typeId)
      : [...currentTypes, typeId]
    
    handleFilterChange('analysisTypes', newTypes)
  }

  const handleSentimentRangeChange = (value) => {
    handleFilterChange('sentimentRange', value)
  }

  const handleDateRangeChange = (range) => {
    onDateRangeChange(range)
    if (range?.from && range?.to) {
      handleFilterChange('timeframe', 'custom')
    }
  }

  const resetFilters = () => {
    const defaultFilters = {
      analysisTypes: [],
      sentimentRange: [0, 100],
      competitorFilter: 'all',
      timeframe: '30d'
    }
    setTempFilters(defaultFilters)
    onFiltersChange(defaultFilters)
    onDateRangeChange({ from: null, to: null })
    setSearchTerm('')
  }

  const saveCurrentFilter = () => {
    const filterName = prompt('Enter a name for this filter preset:')
    if (filterName && onSaveFilter) {
      onSaveFilter({
        name: filterName,
        filters: tempFilters,
        dateRange,
        createdAt: new Date().toISOString()
      })
    }
  }

  const getActiveFilterCount = () => {
    let count = 0
    if (tempFilters.analysisTypes?.length > 0) count++
    if (tempFilters.sentimentRange[0] > 0 || tempFilters.sentimentRange[1] < 100) count++
    if (tempFilters.competitorFilter !== 'all') count++
    if (tempFilters.timeframe !== '30d') count++
    if (searchTerm) count++
    return count
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">Analytics Filters</CardTitle>
            {getActiveFilterCount() > 0 && (
              <Badge variant="secondary" className="ml-2">
                {getActiveFilterCount()} active
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={resetFilters}
              disabled={getActiveFilterCount() === 0}
            >
              <RotateCcw className="h-4 w-4 mr-1" />
              Reset
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={saveCurrentFilter}
              disabled={getActiveFilterCount() === 0}
            >
              <Save className="h-4 w-4 mr-1" />
              Save
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Quick Filters Row */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Search */}
          <div className="relative flex-1 min-w-64">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search brands, competitors, or keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Timeframe */}
          <Select value={tempFilters.timeframe} onValueChange={(value) => handleFilterChange('timeframe', value)}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {timeframeOptions.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Date Range Picker (for custom timeframe) */}
          {tempFilters.timeframe === 'custom' && (
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="outline" className="w-60 justify-start text-left font-normal">
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateRange?.from ? (
                    dateRange.to ? (
                      <>
                        {format(dateRange.from, "LLL dd, y")} -{" "}
                        {format(dateRange.to, "LLL dd, y")}
                      </>
                    ) : (
                      format(dateRange.from, "LLL dd, y")
                    )
                  ) : (
                    <span>Pick a date range</span>
                  )}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  initialFocus
                  mode="range"
                  defaultMonth={dateRange?.from}
                  selected={dateRange}
                  onSelect={handleDateRangeChange}
                  numberOfMonths={2}
                />
              </PopoverContent>
            </Popover>
          )}

          {/* Competitor Filter */}
          <Select 
            value={tempFilters.competitorFilter} 
            onValueChange={(value) => handleFilterChange('competitorFilter', value)}
          >
            <SelectTrigger className="w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {competitorFilterOptions.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Expanded Filters */}
        {isExpanded && (
          <div className="space-y-6 pt-4 border-t">
            {/* Analysis Types */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">Analysis Types</Label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {analysisTypes.map(type => {
                  const Icon = type.icon
                  const isSelected = tempFilters.analysisTypes?.includes(type.id)
                  
                  return (
                    <div
                      key={type.id}
                      className={`flex items-center space-x-2 p-3 rounded-lg border cursor-pointer transition-colors ${
                        isSelected 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleAnalysisTypeToggle(type.id)}
                    >
                      <Checkbox
                        checked={isSelected}
                        onChange={() => handleAnalysisTypeToggle(type.id)}
                      />
                      <Icon className="h-4 w-4 text-gray-600" />
                      <span className="text-sm font-medium">{type.label}</span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Sentiment Range */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">
                Sentiment Score Range: {tempFilters.sentimentRange[0]}% - {tempFilters.sentimentRange[1]}%
              </Label>
              <Slider
                value={tempFilters.sentimentRange}
                onValueChange={handleSentimentRangeChange}
                max={100}
                min={0}
                step={5}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Negative</span>
                <span>Neutral</span>
                <span>Positive</span>
              </div>
            </div>

            {/* Saved Filter Presets */}
            {savedFilters.length > 0 && (
              <div className="space-y-3">
                <Label className="text-sm font-medium">Saved Filter Presets</Label>
                <div className="flex flex-wrap gap-2">
                  {savedFilters.map((preset, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => onLoadFilter?.(preset)}
                      className="text-xs"
                    >
                      {preset.name}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Active Filters Summary */}
        {getActiveFilterCount() > 0 && (
          <div className="flex flex-wrap gap-2 pt-3 border-t">
            {tempFilters.analysisTypes?.map(typeId => {
              const type = analysisTypes.find(t => t.id === typeId)
              return (
                <Badge key={typeId} variant="secondary" className="flex items-center gap-1">
                  {type?.label}
                  <X 
                    className="h-3 w-3 cursor-pointer" 
                    onClick={() => handleAnalysisTypeToggle(typeId)}
                  />
                </Badge>
              )
            })}
            
            {(tempFilters.sentimentRange[0] > 0 || tempFilters.sentimentRange[1] < 100) && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Sentiment: {tempFilters.sentimentRange[0]}%-{tempFilters.sentimentRange[1]}%
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => handleSentimentRangeChange([0, 100])}
                />
              </Badge>
            )}
            
            {tempFilters.competitorFilter !== 'all' && (
              <Badge variant="secondary" className="flex items-center gap-1">
                {competitorFilterOptions.find(opt => opt.value === tempFilters.competitorFilter)?.label}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => handleFilterChange('competitorFilter', 'all')}
                />
              </Badge>
            )}
            
            {searchTerm && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Search: "{searchTerm}"
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => setSearchTerm('')}
                />
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default AnalyticsFilters
