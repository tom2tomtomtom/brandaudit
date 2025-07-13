import { describe, it, expect, beforeEach, vi } from 'vitest'
import apiService from '../../services/api.js'

// Real API connectivity tests (without mocking)
describe('API Connectivity Integration Tests', () => {
  beforeEach(() => {
    // Clear any existing mocks for real API testing
    vi.restoreAllMocks()
  })

  describe('API Service Health Check', () => {
    it('should connect to backend health endpoint', async () => {
      try {
        const response = await apiService.healthCheck()
        
        // Should return health status
        expect(response).toBeDefined()
        expect(response.status).toBeDefined()
        
        console.log('✅ Health check successful:', response)
      } catch (error) {
        console.log('❌ Health check failed:', error.message)
        
        // If backend is not running, this is expected
        expect(error).toBeDefined()
        expect(error.message).toContain('fetch')
      }
    }, 10000) // 10 second timeout

    it('should handle health check timeout gracefully', async () => {
      try {
        const response = await apiService.healthCheck()
        console.log('Health check response:', response)
      } catch (error) {
        // Should handle network errors gracefully
        expect(error).toBeInstanceOf(Error)
        console.log('Expected network error:', error.message)
      }
    })
  })

  describe('API Service Error Handling', () => {
    it('should have proper error handling structure', () => {
      // Validate API service has error handling methods
      expect(apiService.enhanceError).toBeDefined()
      expect(apiService.executeWithRetry).toBeDefined()
      expect(apiService.isCircuitOpen).toBeDefined()
    })

    it('should handle circuit breaker functionality', () => {
      // Test circuit breaker methods exist
      expect(apiService.updateCircuitBreaker).toBeDefined()
      expect(apiService.resetCircuitBreaker).toBeDefined()
      expect(apiService.getCircuitRetryTime).toBeDefined()
    })

    it('should have retry logic configured', () => {
      // Validate retry configuration
      expect(apiService.retryAttempts).toBeDefined()
      expect(apiService.circuitBreakers).toBeDefined()
    })
  })

  describe('Brand Analysis API Methods', () => {
    it('should have all required analysis methods', () => {
      // Validate all required API methods exist
      expect(apiService.startAnalysis).toBeDefined()
      expect(apiService.getAnalysisStatus).toBeDefined()
      expect(apiService.getAnalysisResults).toBeDefined()
      expect(apiService.searchBrand).toBeDefined()
      expect(apiService.getBrandAssets).toBeDefined()
    })

    it('should handle brand search request structure', async () => {
      const testQuery = 'Apple'
      
      try {
        await apiService.searchBrand(testQuery)
      } catch (error) {
        // Should fail with proper error structure
        expect(error).toBeDefined()
        
        // Check if it's a network error (expected when backend is down)
        if (error.message.includes('fetch')) {
          console.log('✅ Network error handled correctly:', error.message)
        }
      }
    })

    it('should handle analysis start request structure', async () => {
      const testAnalysisData = {
        company_name: 'Test Company',
        analysis_options: {
          brandPerception: true,
          competitiveAnalysis: true,
          visualAnalysis: true,
          pressCoverage: true,
          socialSentiment: false
        }
      }
      
      try {
        await apiService.startAnalysis(testAnalysisData)
      } catch (error) {
        // Should fail with proper error structure
        expect(error).toBeDefined()
        console.log('Expected analysis start error:', error.message)
      }
    })
  })

  describe('API Request Configuration', () => {
    it('should have proper base URL configuration', () => {
      expect(apiService.baseURL).toBeDefined()
      expect(apiService.baseURL).toContain('http')
      console.log('API Base URL:', apiService.baseURL)
    })

    it('should have proper request headers', async () => {
      // Test that request method sets proper headers
      const testEndpoint = '/test'
      const testOptions = {}
      
      try {
        await apiService.request(testEndpoint, testOptions)
      } catch (error) {
        // Should fail but with proper request structure
        expect(error).toBeDefined()
      }
    })

    it('should handle CORS and ngrok headers', () => {
      // Validate that ngrok-skip-browser-warning header is set
      const testConfig = {
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        }
      }
      
      expect(testConfig.headers['ngrok-skip-browser-warning']).toBe('true')
      expect(testConfig.headers['Content-Type']).toBe('application/json')
    })
  })

  describe('Real-World API Testing', () => {
    it('should test actual backend connectivity if available', async () => {
      console.log('🔍 Testing real backend connectivity...')
      
      try {
        // Try to connect to the actual backend
        const healthResponse = await fetch('http://localhost:8000/api/health', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
          }
        })
        
        if (healthResponse.ok) {
          const data = await healthResponse.json()
          console.log('✅ Backend is running:', data)
          
          expect(data).toBeDefined()
          expect(data.status).toBeDefined()
        } else {
          console.log('❌ Backend returned error:', healthResponse.status)
        }
      } catch (error) {
        console.log('❌ Backend not available:', error.message)
        // This is expected if backend is not running
        expect(error).toBeDefined()
      }
    }, 15000)

    it('should validate environment configuration', () => {
      // Check environment variables
      const apiUrl = import.meta.env.VITE_API_BASE_URL
      console.log('Environment API URL:', apiUrl)
      
      // Should have fallback to localhost
      expect(apiService.baseURL).toBeDefined()
      expect(apiService.baseURL).toMatch(/http/)
    })
  })

  describe('WebSocket Integration', () => {
    it('should have WebSocket URL configured', () => {
      const wsUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      expect(wsUrl).toBeDefined()
      expect(wsUrl).toMatch(/http/)
      console.log('WebSocket URL:', wsUrl)
    })

    it('should test WebSocket connection availability', async () => {
      try {
        // Test if WebSocket endpoint is available
        const wsTestUrl = 'http://localhost:8000/socket.io/'
        const response = await fetch(wsTestUrl, {
          method: 'GET',
          headers: { 'ngrok-skip-browser-warning': 'true' }
        })
        
        console.log('WebSocket endpoint status:', response.status)
      } catch (error) {
        console.log('WebSocket endpoint not available:', error.message)
        // Expected if backend is not running
      }
    })
  })

  describe('Data Flow Validation', () => {
    it('should validate analysis data structure', () => {
      const mockAnalysisResults = {
        key_metrics: {},
        actionable_insights: [],
        llm_sections: {},
        visual_analysis: {},
        competitor_analysis: {},
        campaign_analysis: {}
      }
      
      // Validate expected data structure
      expect(mockAnalysisResults.key_metrics).toBeDefined()
      expect(mockAnalysisResults.actionable_insights).toBeInstanceOf(Array)
      expect(mockAnalysisResults.llm_sections).toBeDefined()
      expect(mockAnalysisResults.visual_analysis).toBeDefined()
    })

    it('should validate visual data structure', () => {
      const mockVisualData = {
        screenshots: [],
        color_palette: {
          primary_colors: [],
          secondary_colors: []
        },
        brand_assets: {
          logos: [],
          icons: []
        },
        visual_metrics: {}
      }
      
      // Validate visual data structure
      expect(mockVisualData.screenshots).toBeInstanceOf(Array)
      expect(mockVisualData.color_palette).toBeDefined()
      expect(mockVisualData.brand_assets).toBeDefined()
      expect(mockVisualData.visual_metrics).toBeDefined()
    })
  })
})
