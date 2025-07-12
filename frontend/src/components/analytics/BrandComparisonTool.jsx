import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent
} from '@/components/ui/chart.jsx'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Legend
} from 'recharts'
import { 
  Target, 
  TrendingUp, 
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Plus,
  X,
  Filter,
  Download,
  RefreshCw,
  Eye,
  BarChart3,
  Award,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'

const BrandComparisonTool = ({ 
  primaryBrand, 
  availableBrands = [], 
  onBrandSelect,
  onExport 
}) => {
  const [selectedBrands, setSelectedBrands] = useState([])
  const [comparisonMetrics, setComparisonMetrics] = useState([
    'brandHealth', 'sentiment', 'marketShare', 'awareness', 'engagement'
  ])
  const [viewType, setViewType] = useState('side-by-side')
  const [sortBy, setSortBy] = useState('brandHealth')
  const [filterCriteria, setFilterCriteria] = useState({
    minBrandHealth: 0,
    maxBrandHealth: 100,
    industries: [],
    regions: []
  })

  // Chart configuration
  const chartConfig = {
    brandHealth: { label: "Brand Health", color: "hsl(var(--chart-1))" },
    sentiment: { label: "Sentiment", color: "hsl(var(--chart-2))" },
    marketShare: { label: "Market Share", color: "hsl(var(--chart-3))" },
    awareness: { label: "Awareness", color: "hsl(var(--chart-4))" },
    engagement: { label: "Engagement", color: "hsl(var(--chart-5))" }
  }

  // Generate comparison data
  const comparisonData = useMemo(() => {
    const brands = [
      {
        name: primaryBrand || 'Your Brand',
        brandHealth: 85,
        sentiment: 78,
        marketShare: 15.2,
        awareness: 82,
        engagement: 4.2,
        visualConsistency: 88,
        customerLoyalty: 76,
        innovation: 91,
        trustworthiness: 89,
        isPrimary: true,
        industry: 'Technology',
        region: 'North America'
      },
      ...selectedBrands.map((brand, index) => ({
        name: brand.name || `Competitor ${index + 1}`,
        brandHealth: 60 + Math.random() * 30,
        sentiment: 50 + Math.random() * 40,
        marketShare: 5 + Math.random() * 20,
        awareness: 40 + Math.random() * 50,
        engagement: 2 + Math.random() * 4,
        visualConsistency: 60 + Math.random() * 30,
        customerLoyalty: 50 + Math.random() * 40,
        innovation: 40 + Math.random() * 50,
        trustworthiness: 55 + Math.random() * 35,
        isPrimary: false,
        industry: brand.industry || 'Technology',
        region: brand.region || 'North America'
      }))
    ]

    return brands.sort((a, b) => b[sortBy] - a[sortBy])
  }, [primaryBrand, selectedBrands, sortBy])

  // Radar chart data
  const radarData = useMemo(() => {
    const dimensions = [
      'Brand Health',
      'Sentiment',
      'Market Share',
      'Awareness',
      'Engagement',
      'Visual Consistency',
      'Customer Loyalty',
      'Innovation',
      'Trustworthiness'
    ]

    return dimensions.map(dimension => {
      const key = dimension.toLowerCase().replace(/\s+/g, '')
      const dataPoint = { dimension }
      
      comparisonData.forEach(brand => {
        dataPoint[brand.name] = brand[key] || 0
      })
      
      return dataPoint
    })
  }, [comparisonData])

  // Bar chart data for metrics comparison
  const barChartData = useMemo(() => {
    return comparisonMetrics.map(metric => {
      const dataPoint = { metric: chartConfig[metric]?.label || metric }
      
      comparisonData.forEach(brand => {
        dataPoint[brand.name] = brand[metric] || 0
      })
      
      return dataPoint
    })
  }, [comparisonData, comparisonMetrics])

  const handleBrandAdd = (brand) => {
    if (selectedBrands.length < 5 && !selectedBrands.find(b => b.name === brand.name)) {
      setSelectedBrands([...selectedBrands, brand])
    }
  }

  const handleBrandRemove = (brandName) => {
    setSelectedBrands(selectedBrands.filter(b => b.name !== brandName))
  }

  const handleMetricToggle = (metric) => {
    if (comparisonMetrics.includes(metric)) {
      setComparisonMetrics(comparisonMetrics.filter(m => m !== metric))
    } else {
      setComparisonMetrics([...comparisonMetrics, metric])
    }
  }

  const getTrendIcon = (value, benchmark = 70) => {
    if (value > benchmark + 10) return { icon: TrendingUp, color: 'text-green-500' }
    if (value < benchmark - 10) return { icon: TrendingDown, color: 'text-red-500' }
    return { icon: Minus, color: 'text-gray-500' }
  }

  const getPerformanceColor = (value, metric) => {
    const thresholds = {
      brandHealth: { excellent: 80, good: 60 },
      sentiment: { excellent: 75, good: 55 },
      marketShare: { excellent: 20, good: 10 },
      awareness: { excellent: 80, good: 60 },
      engagement: { excellent: 4, good: 2.5 }
    }
    
    const threshold = thresholds[metric] || { excellent: 80, good: 60 }
    
    if (value >= threshold.excellent) return 'text-green-600'
    if (value >= threshold.good) return 'text-yellow-600'
    return 'text-red-600'
  }

  const BrandCard = ({ brand, rank }) => {
    const trendIndicator = getTrendIcon(brand.brandHealth)
    const TrendIcon = trendIndicator.icon
    
    return (
      <Card className={`${brand.isPrimary ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                rank === 1 ? 'bg-yellow-100 text-yellow-800' :
                rank === 2 ? 'bg-gray-100 text-gray-800' :
                rank === 3 ? 'bg-orange-100 text-orange-800' :
                'bg-gray-50 text-gray-600'
              }`}>
                #{rank}
              </div>
              <div>
                <CardTitle className="text-lg">{brand.name}</CardTitle>
                {brand.isPrimary && (
                  <Badge variant="default" className="text-xs mt-1">Your Brand</Badge>
                )}
              </div>
            </div>
            
            {!brand.isPrimary && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleBrandRemove(brand.name)}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Primary Metrics */}
          <div className="grid grid-cols-2 gap-4">
            {comparisonMetrics.slice(0, 4).map(metric => (
              <div key={metric} className="text-center">
                <div className={`text-lg font-bold ${getPerformanceColor(brand[metric], metric)}`}>
                  {metric === 'engagement' ? brand[metric]?.toFixed(1) : Math.round(brand[metric] || 0)}
                  {metric === 'marketShare' ? '%' : metric === 'engagement' ? '' : ''}
                </div>
                <div className="text-xs text-gray-500 capitalize">
                  {metric.replace(/([A-Z])/g, ' $1').trim()}
                </div>
              </div>
            ))}
          </div>
          
          {/* Performance Bars */}
          <div className="space-y-2">
            {comparisonMetrics.slice(0, 3).map(metric => (
              <div key={metric}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="capitalize">{metric.replace(/([A-Z])/g, ' $1').trim()}</span>
                  <span>{Math.round(brand[metric] || 0)}</span>
                </div>
                <Progress value={brand[metric] || 0} className="h-2" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const BrandSelector = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="h-5 w-5 text-blue-600" />
          Add Brands to Compare
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {availableBrands.slice(0, 10).map(brand => (
            <Button
              key={brand.name}
              variant="outline"
              size="sm"
              onClick={() => handleBrandAdd(brand)}
              disabled={selectedBrands.length >= 5 || selectedBrands.find(b => b.name === brand.name)}
              className="text-xs"
            >
              {brand.name}
            </Button>
          ))}
        </div>
        
        <div className="text-xs text-gray-500">
          Selected: {selectedBrands.length}/5 brands
        </div>
      </CardContent>
    </Card>
  )

  const MetricSelector = () => (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Comparison Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(chartConfig).map(([key, config]) => (
            <div key={key} className="flex items-center space-x-2">
              <Checkbox
                checked={comparisonMetrics.includes(key)}
                onCheckedChange={() => handleMetricToggle(key)}
              />
              <Label className="text-sm">{config.label}</Label>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Select value={viewType} onValueChange={setViewType}>
            <SelectTrigger className="w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="side-by-side">Side by Side</SelectItem>
              <SelectItem value="radar">Radar Chart</SelectItem>
              <SelectItem value="bar-chart">Bar Chart</SelectItem>
              <SelectItem value="detailed">Detailed View</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="brandHealth">Brand Health</SelectItem>
              <SelectItem value="sentiment">Sentiment</SelectItem>
              <SelectItem value="marketShare">Market Share</SelectItem>
              <SelectItem value="awareness">Awareness</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button variant="outline" size="sm" onClick={() => onExport?.('comparison')}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Controls */}
        <div className="lg:col-span-1 space-y-4">
          <BrandSelector />
          <MetricSelector />
        </div>

        {/* Main Comparison Area */}
        <div className="lg:col-span-3">
          <Tabs value={viewType} onValueChange={setViewType} className="space-y-6">
            <TabsContent value="side-by-side" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {comparisonData.map((brand, index) => (
                  <BrandCard key={brand.name} brand={brand} rank={index + 1} />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="radar" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Multi-Dimensional Brand Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <ChartContainer config={chartConfig} className="h-96">
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="dimension" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} />
                      
                      {comparisonData.map((brand, index) => (
                        <Radar
                          key={brand.name}
                          name={brand.name}
                          dataKey={brand.name}
                          stroke={brand.isPrimary ? '#3B82F6' : `hsl(${index * 60}, 70%, 50%)`}
                          fill={brand.isPrimary ? '#3B82F6' : `hsl(${index * 60}, 70%, 50%)`}
                          fillOpacity={brand.isPrimary ? 0.3 : 0.1}
                          strokeWidth={brand.isPrimary ? 3 : 2}
                        />
                      ))}
                      
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Legend />
                    </RadarChart>
                  </ChartContainer>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="bar-chart" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Metric Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <ChartContainer config={chartConfig} className="h-80">
                    <BarChart data={barChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="metric" />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Legend />
                      
                      {comparisonData.map((brand, index) => (
                        <Bar
                          key={brand.name}
                          dataKey={brand.name}
                          fill={brand.isPrimary ? '#3B82F6' : `hsl(${index * 60}, 70%, 50%)`}
                        />
                      ))}
                    </BarChart>
                  </ChartContainer>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="detailed" className="space-y-6">
              <div className="space-y-4">
                {comparisonData.map((brand, index) => (
                  <Card key={brand.name}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                            index === 0 ? 'bg-yellow-100 text-yellow-800' :
                            index === 1 ? 'bg-gray-100 text-gray-800' :
                            'bg-gray-50 text-gray-600'
                          }`}>
                            #{index + 1}
                          </div>
                          {brand.name}
                          {brand.isPrimary && <Badge variant="default">Your Brand</Badge>}
                        </CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                        {Object.entries(chartConfig).map(([key, config]) => (
                          <div key={key} className="text-center">
                            <div className={`text-xl font-bold ${getPerformanceColor(brand[key], key)}`}>
                              {key === 'engagement' ? brand[key]?.toFixed(1) : Math.round(brand[key] || 0)}
                              {key === 'marketShare' ? '%' : ''}
                            </div>
                            <div className="text-xs text-gray-500">{config.label}</div>
                            <Progress value={brand[key] || 0} className="h-1 mt-1" />
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

export default BrandComparisonTool
