/**
 * Analytics API Service
 * Handles all analytics-related API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class AnalyticsApiService {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api/analytics`
  }

  /**
   * Get authentication headers
   */
  getAuthHeaders() {
    const token = localStorage.getItem('auth_token')
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    }
  }

  /**
   * Handle API response
   */
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Network error' }))
      throw new Error(error.error || `HTTP ${response.status}`)
    }
    return response.json()
  }

  /**
   * Get comprehensive dashboard data
   */
  async getDashboardData(brandId, timeframe = '30d') {
    try {
      const params = new URLSearchParams({
        brand_id: brandId,
        timeframe
      })

      const response = await fetch(`${this.baseURL}/dashboard?${params}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      const result = await this.handleResponse(response)
      return result.data
    } catch (error) {
      console.error('Dashboard data fetch error:', error)
      throw error
    }
  }

  /**
   * Get historical analytics data
   */
  async getHistoricalData(brandId, options = {}) {
    try {
      const params = new URLSearchParams({
        brand_id: brandId,
        timeframe: options.timeframe || '30d',
        metrics: options.metrics ? options.metrics.join(',') : 'brandHealth,sentiment,marketShare'
      })

      if (options.dateFrom) params.append('date_from', options.dateFrom)
      if (options.dateTo) params.append('date_to', options.dateTo)

      const response = await fetch(`${this.baseURL}/historical?${params}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      const result = await this.handleResponse(response)
      return result.data
    } catch (error) {
      console.error('Historical data fetch error:', error)
      throw error
    }
  }

  /**
   * Get brand comparison data
   */
  async getComparisonData(primaryBrandId, comparisonBrandIds, metrics = []) {
    try {
      const requestBody = {
        primary_brand_id: primaryBrandId,
        comparison_brand_ids: comparisonBrandIds,
        metrics: metrics.length > 0 ? metrics : ['brandHealth', 'sentiment', 'marketShare']
      }

      const response = await fetch(`${this.baseURL}/comparison`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(requestBody)
      })

      const result = await this.handleResponse(response)
      return result.data
    } catch (error) {
      console.error('Comparison data fetch error:', error)
      throw error
    }
  }

  /**
   * Get trend analysis data
   */
  async getTrendAnalysis(brandId, metrics, options = {}) {
    try {
      const params = new URLSearchParams({
        brand_id: brandId,
        metrics: metrics.join(','),
        period: options.period || '30d',
        granularity: options.granularity || 'daily'
      })

      const response = await fetch(`${this.baseURL}/trends?${params}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      const result = await this.handleResponse(response)
      return result.data
    } catch (error) {
      console.error('Trend analysis fetch error:', error)
      throw error
    }
  }

  /**
   * Get predictive insights
   */
  async getPredictiveInsights(brandId, options = {}) {
    try {
      const params = new URLSearchParams({
        brand_id: brandId,
        forecast_period: options.forecastPeriod || '30d',
        confidence_threshold: options.confidenceThreshold || 0.7
      })

      const response = await fetch(`${this.baseURL}/predictions?${params}`, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })

      const result = await this.handleResponse(response)
      return result.data
    } catch (error) {
      console.error('Predictive insights fetch error:', error)
      throw error
    }
  }

  /**
   * Export analytics data
   */
  async exportData(data, format = 'json', type = 'dashboard') {
    try {
      const requestBody = {
        data,
        format,
        type
      }

      const response = await fetch(`${this.baseURL}/export`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(requestBody)
      })

      const result = await this.handleResponse(response)
      return result.data
    } catch (error) {
      console.error('Export data error:', error)
      throw error
    }
  }

  /**
   * Get available brands for comparison
   */
  async getAvailableBrands() {
    try {
      // This would typically come from a brands endpoint
      // For now, return mock data
      return [
        { id: 'comp-1', name: 'Competitor A', industry: 'Technology' },
        { id: 'comp-2', name: 'Competitor B', industry: 'Technology' },
        { id: 'comp-3', name: 'Competitor C', industry: 'Technology' },
        { id: 'comp-4', name: 'Competitor D', industry: 'Technology' },
        { id: 'comp-5', name: 'Competitor E', industry: 'Technology' }
      ]
    } catch (error) {
      console.error('Available brands fetch error:', error)
      throw error
    }
  }

  /**
   * Get analytics metrics definitions
   */
  getMetricsDefinitions() {
    return {
      brandHealth: {
        label: 'Brand Health',
        description: 'Overall brand performance score',
        unit: 'score',
        range: [0, 100]
      },
      sentiment: {
        label: 'Brand Sentiment',
        description: 'Public sentiment towards the brand',
        unit: 'percentage',
        range: [0, 100]
      },
      marketShare: {
        label: 'Market Share',
        description: 'Brand\'s share of the total market',
        unit: 'percentage',
        range: [0, 100]
      },
      awareness: {
        label: 'Brand Awareness',
        description: 'Level of brand recognition',
        unit: 'percentage',
        range: [0, 100]
      },
      engagement: {
        label: 'Engagement Rate',
        description: 'Customer engagement with brand content',
        unit: 'rate',
        range: [0, 10]
      },
      visualConsistency: {
        label: 'Visual Consistency',
        description: 'Consistency of brand visual elements',
        unit: 'score',
        range: [0, 100]
      },
      customerLoyalty: {
        label: 'Customer Loyalty',
        description: 'Customer retention and loyalty metrics',
        unit: 'score',
        range: [0, 100]
      },
      innovation: {
        label: 'Innovation Score',
        description: 'Brand\'s innovation perception',
        unit: 'score',
        range: [0, 100]
      },
      trustworthiness: {
        label: 'Trustworthiness',
        description: 'Brand trust and reliability perception',
        unit: 'score',
        range: [0, 100]
      }
    }
  }

  /**
   * Get chart color palette
   */
  getChartColors() {
    return [
      '#3B82F6', // Blue
      '#10B981', // Green
      '#F59E0B', // Yellow
      '#EF4444', // Red
      '#8B5CF6', // Purple
      '#06B6D4', // Cyan
      '#F97316', // Orange
      '#84CC16', // Lime
      '#EC4899', // Pink
      '#6B7280'  // Gray
    ]
  }

  /**
   * Format metric value for display
   */
  formatMetricValue(value, metric) {
    const definition = this.getMetricsDefinitions()[metric]
    if (!definition) return value

    switch (definition.unit) {
      case 'percentage':
        return `${Math.round(value)}%`
      case 'rate':
        return value.toFixed(1)
      case 'score':
        return Math.round(value)
      default:
        return value
    }
  }

  /**
   * Get metric performance level
   */
  getMetricPerformanceLevel(value, metric) {
    const thresholds = {
      brandHealth: { excellent: 80, good: 60, fair: 40 },
      sentiment: { excellent: 75, good: 55, fair: 35 },
      marketShare: { excellent: 20, good: 10, fair: 5 },
      awareness: { excellent: 80, good: 60, fair: 40 },
      engagement: { excellent: 4, good: 2.5, fair: 1 }
    }

    const threshold = thresholds[metric] || { excellent: 80, good: 60, fair: 40 }

    if (value >= threshold.excellent) return 'excellent'
    if (value >= threshold.good) return 'good'
    if (value >= threshold.fair) return 'fair'
    return 'poor'
  }

  /**
   * Calculate trend direction
   */
  calculateTrend(current, previous) {
    if (!previous || previous === 0) return 0
    return ((current - previous) / previous) * 100
  }

  /**
   * Get trend indicator
   */
  getTrendIndicator(trend) {
    if (trend > 5) return { direction: 'up', color: 'green', icon: '↗' }
    if (trend < -5) return { direction: 'down', color: 'red', icon: '↘' }
    return { direction: 'stable', color: 'gray', icon: '→' }
  }
}

// Create and export singleton instance
const analyticsApi = new AnalyticsApiService()
export default analyticsApi
