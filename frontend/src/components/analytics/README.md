# Advanced Analytics Dashboard

A comprehensive analytics dashboard for brand audit insights with interactive visualizations, comparative analysis, and predictive capabilities.

## Features

### 🎯 Core Analytics
- **Brand Health Overview**: Real-time brand performance metrics
- **Interactive Charts**: Drill-down capable visualizations with Recharts
- **Competitive Intelligence**: Multi-brand comparison and positioning analysis
- **Trend Analysis**: Historical tracking with time-series analysis
- **Predictive Insights**: AI-powered forecasting and recommendations

### 📊 Visualization Components
- **Interactive Chart Grid**: Multiple chart types with drill-down capabilities
- **Brand Health Overview**: Key performance indicators and health scores
- **Competitive Intelligence**: Market positioning and competitor analysis
- **Trend Analysis Panel**: Time-series data with seasonal patterns
- **Predictive Insights**: Forecasting with confidence intervals

### 🔧 Advanced Features
- **Customizable Dashboards**: Drag-and-drop widget management
- **Advanced Filtering**: Multi-dimensional data filtering with saved presets
- **Real-time Updates**: WebSocket integration for live data streaming
- **Export Capabilities**: PDF, Excel, and PowerPoint export options
- **Responsive Design**: Mobile-first approach with adaptive layouts

## Components

### AdvancedAnalyticsDashboard
Main dashboard component with tabbed interface and comprehensive analytics.

```jsx
<AdvancedAnalyticsDashboard
  analysisResults={analysisResults}
  brandName="Apple"
  historicalData={historicalData}
  competitorData={competitorData}
  onExport={handleExport}
  onRefresh={handleRefresh}
/>
```

### BrandHealthOverview
Displays key brand health metrics with trend indicators.

```jsx
<BrandHealthOverview 
  data={analyticsData}
  layout="standard" // 'standard' | 'executive'
/>
```

### InteractiveChartGrid
Grid of interactive charts with drill-down capabilities.

```jsx
<InteractiveChartGrid 
  data={analyticsData}
  filters={filters}
  onDrillDown={handleDrillDown}
/>
```

### CompetitiveIntelligence
Comprehensive competitive analysis with positioning maps.

```jsx
<CompetitiveIntelligence 
  data={analyticsData}
  competitorData={competitorData}
  brandName="Apple"
/>
```

### TrendAnalysisPanel
Time-series analysis with multiple visualization options.

```jsx
<TrendAnalysisPanel 
  data={analyticsData}
  historicalData={historicalData}
  dateRange={dateRange}
/>
```

### PredictiveInsights
AI-powered predictions and strategic recommendations.

```jsx
<PredictiveInsights 
  data={analyticsData}
  predictions={predictions}
/>
```

### CustomizableDashboard
Drag-and-drop dashboard customization interface.

```jsx
<CustomizableDashboard 
  data={analyticsData}
  layout={dashboardLayout}
  onLayoutChange={setDashboardLayout}
/>
```

### BrandComparisonTool
Side-by-side brand comparison with multiple visualization modes.

```jsx
<BrandComparisonTool
  primaryBrand="Apple"
  availableBrands={availableBrands}
  onBrandSelect={handleBrandSelect}
  onExport={handleExport}
/>
```

### AnalyticsFilters
Advanced filtering system with saved presets.

```jsx
<AnalyticsFilters
  filters={filters}
  onFiltersChange={setFilters}
  dateRange={dateRange}
  onDateRangeChange={setDateRange}
/>
```

## API Integration

### Analytics API Service
Centralized service for all analytics API calls.

```javascript
import analyticsApi from '../../services/analyticsApi.js'

// Get dashboard data
const dashboardData = await analyticsApi.getDashboardData(brandId, timeframe)

// Get historical data
const historicalData = await analyticsApi.getHistoricalData(brandId, options)

// Get comparison data
const comparisonData = await analyticsApi.getComparisonData(
  primaryBrandId, 
  comparisonBrandIds, 
  metrics
)

// Export data
const exportResult = await analyticsApi.exportData(data, format, type)
```

### Backend Endpoints
- `GET /api/analytics/dashboard` - Dashboard data
- `GET /api/analytics/historical` - Historical trends
- `POST /api/analytics/comparison` - Brand comparison
- `GET /api/analytics/trends` - Trend analysis
- `GET /api/analytics/predictions` - Predictive insights
- `POST /api/analytics/export` - Data export

## Data Structure

### Analytics Data Format
```javascript
{
  brandHealth: {
    overall: 85,
    visual: 78,
    sentiment: 82,
    news: 76,
    trend: 5.2
  },
  keyMetrics: {
    totalMentions: 150,
    sentimentScore: 0.78,
    visualAssets: 25,
    competitorCount: 5
  },
  sentimentTrends: {
    current: 0.78,
    historical: [...],
    change: 0.05
  },
  competitivePosition: {
    brandScore: 85,
    avgCompetitorScore: 72,
    ranking: 1,
    marketShare: 15.2
  },
  insights: [...],
  predictions: [...]
}
```

## Usage Examples

### Basic Dashboard
```jsx
import { AdvancedAnalyticsDashboard } from './components/analytics'

function App() {
  return (
    <AdvancedAnalyticsDashboard
      analysisResults={analysisResults}
      brandName="Apple"
      onExport={handleExport}
      onRefresh={handleRefresh}
    />
  )
}
```

### Custom Dashboard Layout
```jsx
import { CustomizableDashboard } from './components/analytics'

function CustomDashboard() {
  const [layout, setLayout] = useState('executive')
  
  return (
    <CustomizableDashboard
      data={analyticsData}
      layout={layout}
      onLayoutChange={setLayout}
    />
  )
}
```

### Brand Comparison
```jsx
import { BrandComparisonTool } from './components/analytics'

function ComparisonPage() {
  return (
    <BrandComparisonTool
      primaryBrand="Apple"
      availableBrands={competitors}
      onBrandSelect={handleBrandSelect}
    />
  )
}
```

## Testing

### Analytics Test Suite
Run the comprehensive test suite to verify all components:

```bash
# Navigate to analytics test page
http://localhost:3000/analytics-test
```

### Component Tests
- Dashboard rendering and data loading
- Chart interactivity and drill-down
- Filter functionality and persistence
- Export capabilities
- Real-time updates
- Responsive design

## Performance Optimization

### Caching Strategy
- API responses cached for 30 minutes
- Chart data memoized with useMemo
- Component rendering optimized with React.memo

### Data Loading
- Lazy loading for large datasets
- Progressive data fetching
- Error boundaries for graceful failures

### Bundle Optimization
- Code splitting by route
- Dynamic imports for heavy components
- Tree shaking for unused code

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

### Core Dependencies
- React 19+
- Recharts 2.15+
- Lucide React 0.510+
- Date-fns 4.1+

### UI Components
- Radix UI primitives
- Tailwind CSS 4.1+
- Custom UI component library

## Contributing

1. Follow the existing component structure
2. Add comprehensive PropTypes/TypeScript definitions
3. Include unit tests for new components
4. Update documentation for new features
5. Ensure responsive design compatibility

## License

MIT License - see LICENSE file for details
