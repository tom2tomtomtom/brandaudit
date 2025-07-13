import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import App from '../../App.jsx'
import ModernLanding from '../../components/ModernLanding.jsx'
import AnalysisProgress from '../../components/AnalysisProgress.jsx'
import ModernResultsDisplay from '../../components/ModernResultsDisplay.jsx'
import apiService from '../../services/api.js'
import { io } from 'socket.io-client'

// Mock the API service
vi.mock('../../services/api.js', () => ({
  default: {
    startAnalysis: vi.fn(),
    getAnalysisResults: vi.fn(),
    healthCheck: vi.fn(),
    searchBrand: vi.fn(),
    getBrandAssets: vi.fn()
  }
}))

// Mock Socket.IO
vi.mock('socket.io-client', () => ({
  io: vi.fn(() => ({
    on: vi.fn(),
    emit: vi.fn(),
    disconnect: vi.fn(),
    connected: false
  }))
}))

// Mock Zustand stores
vi.mock('../../store/useAuthStore', () => ({
  default: () => ({
    user: null,
    isAuthenticated: false,
    login: vi.fn(),
    logout: vi.fn()
  })
}))

vi.mock('../../store/useLoadingStore', () => ({
  default: () => ({
    isLoading: false,
    setLoading: vi.fn()
  })
}))

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
)

describe('Frontend Integration Tests', () => {
  let mockSocket

  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks()
    
    // Setup mock socket
    mockSocket = {
      on: vi.fn(),
      emit: vi.fn(),
      disconnect: vi.fn(),
      connected: false
    }
    io.mockReturnValue(mockSocket)
    
    // Setup default API responses
    apiService.healthCheck.mockResolvedValue({ status: 'healthy' })
    apiService.startAnalysis.mockResolvedValue({
      success: true,
      data: { analysis_id: 'test-analysis-123' }
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('App Component Integration', () => {
    it('should render landing page by default', async () => {
      render(
        <TestWrapper>
          <App />
        </TestWrapper>
      )

      // Check for landing page elements
      expect(screen.getByText(/AI-Powered Brand Analysis/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/Enter brand or company name/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Start Analysis/i })).toBeInTheDocument()
    })

    it('should handle brand analysis workflow', async () => {
      render(
        <TestWrapper>
          <App />
        </TestWrapper>
      )

      // Enter brand name
      const brandInput = screen.getByPlaceholderText(/Enter brand or company name/i)
      const startButton = screen.getByRole('button', { name: /Start Analysis/i })

      fireEvent.change(brandInput, { target: { value: 'Apple' } })
      expect(brandInput.value).toBe('Apple')

      // Start analysis
      fireEvent.click(startButton)

      await waitFor(() => {
        expect(apiService.startAnalysis).toHaveBeenCalledWith({
          company_name: 'Apple',
          analysis_options: {
            brandPerception: true,
            competitiveAnalysis: true,
            visualAnalysis: true,
            pressCoverage: true,
            socialSentiment: false
          }
        })
      })
    })
  })

  describe('API Service Integration', () => {
    it('should handle API errors gracefully', async () => {
      // Mock API failure
      apiService.startAnalysis.mockRejectedValue(new Error('Network error'))

      render(
        <TestWrapper>
          <App />
        </TestWrapper>
      )

      const brandInput = screen.getByPlaceholderText(/Enter brand or company name/i)
      const startButton = screen.getByRole('button', { name: /Start Analysis/i })

      fireEvent.change(brandInput, { target: { value: 'TestBrand' } })
      fireEvent.click(startButton)

      // Should handle error and stay on landing page
      await waitFor(() => {
        expect(screen.getByText(/AI-Powered Brand Analysis/i)).toBeInTheDocument()
      })
    })

    it('should validate API service methods exist', () => {
      expect(apiService.startAnalysis).toBeDefined()
      expect(apiService.getAnalysisResults).toBeDefined()
      expect(apiService.healthCheck).toBeDefined()
      expect(apiService.searchBrand).toBeDefined()
      expect(apiService.getBrandAssets).toBeDefined()
    })
  })

  describe('ModernLanding Component', () => {
    it('should render all key sections', () => {
      render(
        <TestWrapper>
          <ModernLanding onStartAnalysis={vi.fn()} />
        </TestWrapper>
      )

      // Check for main sections
      expect(screen.getByText(/AI-Powered Brand Analysis/i)).toBeInTheDocument()
      expect(screen.getByText(/Professional insights in minutes/i)).toBeInTheDocument()
      
      // Check for feature highlights
      expect(screen.getByText(/Real-time Analysis/i)).toBeInTheDocument()
      expect(screen.getByText(/Visual Intelligence/i)).toBeInTheDocument()
      expect(screen.getByText(/Competitive Insights/i)).toBeInTheDocument()
    })

    it('should handle brand search input', () => {
      const mockOnStartAnalysis = vi.fn()
      
      render(
        <TestWrapper>
          <ModernLanding onStartAnalysis={mockOnStartAnalysis} />
        </TestWrapper>
      )

      const input = screen.getByPlaceholderText(/Enter brand or company name/i)
      const button = screen.getByRole('button', { name: /Start Analysis/i })

      fireEvent.change(input, { target: { value: 'Nike' } })
      fireEvent.click(button)

      expect(mockOnStartAnalysis).toHaveBeenCalledWith('Nike')
    })
  })

  describe('AnalysisProgress Component', () => {
    const mockAnalysisId = 'test-analysis-123'
    const mockOnComplete = vi.fn()

    it('should render progress indicators', () => {
      render(
        <TestWrapper>
          <AnalysisProgress
            analysisId={mockAnalysisId}
            onComplete={mockOnComplete}
          />
        </TestWrapper>
      )

      // Check for progress elements
      expect(screen.getByText(/AI Brand Analysis in Progress/i)).toBeInTheDocument()
      expect(screen.getByText(/Analysis Progress/i)).toBeInTheDocument()
      expect(screen.getByText(/Analysis Steps/i)).toBeInTheDocument()
    })

    it('should display connection status', () => {
      render(
        <TestWrapper>
          <AnalysisProgress
            analysisId={mockAnalysisId}
            onComplete={mockOnComplete}
          />
        </TestWrapper>
      )

      // Should show connection status (initially disconnected in test)
      expect(screen.getByText(/Disconnected/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument()
    })

    it('should display analysis steps', () => {
      render(
        <TestWrapper>
          <AnalysisProgress
            analysisId={mockAnalysisId}
            onComplete={mockOnComplete}
          />
        </TestWrapper>
      )

      // Check for default analysis steps
      expect(screen.getByText(/Multi-Pass Strategic Analysis/i)).toBeInTheDocument()
      expect(screen.getByText(/Brand Asset Discovery/i)).toBeInTheDocument()
      expect(screen.getByText(/Visual Brand Analysis/i)).toBeInTheDocument()
      expect(screen.getByText(/Competitive Intelligence/i)).toBeInTheDocument()
    })
  })

  describe('ModernResultsDisplay Component', () => {
    const mockAnalysisResults = {
      key_metrics: {
        overall_score: 85,
        visual_consistency: 78,
        market_position: 92
      },
      actionable_insights: [
        {
          finding: 'Strong brand recognition',
          priority: 'high',
          impact: 'Significant market advantage',
          recommendation: 'Leverage brand strength in new markets'
        }
      ],
      llm_sections: {
        executive_summary: 'Comprehensive brand analysis shows strong performance',
        competitive_analysis: 'Leading position in key markets'
      },
      api_responses: {
        brand_data: {
          domain: 'apple.com'
        }
      }
    }

    it('should render analysis results', () => {
      render(
        <TestWrapper>
          <ModernResultsDisplay
            analysisResults={mockAnalysisResults}
            brandName="Apple"
            onNewAnalysis={vi.fn()}
          />
        </TestWrapper>
      )

      // Check for results header
      expect(screen.getByText(/Brand Analysis Complete/i)).toBeInTheDocument()
      expect(screen.getByText(/Apple/i)).toBeInTheDocument()
      expect(screen.getByText(/Analysis Complete/i)).toBeInTheDocument()
    })

    it('should display key metrics', () => {
      render(
        <TestWrapper>
          <ModernResultsDisplay
            analysisResults={mockAnalysisResults}
            brandName="Apple"
            onNewAnalysis={vi.fn()}
          />
        </TestWrapper>
      )

      // Check for metric scores
      expect(screen.getByText('85/100')).toBeInTheDocument()
      expect(screen.getByText('78/100')).toBeInTheDocument()
      expect(screen.getByText('92/100')).toBeInTheDocument()
    })

    it('should display actionable insights', () => {
      render(
        <TestWrapper>
          <ModernResultsDisplay
            analysisResults={mockAnalysisResults}
            brandName="Apple"
            onNewAnalysis={vi.fn()}
          />
        </TestWrapper>
      )

      // Navigate to insights tab
      const insightsTab = screen.getByRole('tab', { name: /Insights/i })
      fireEvent.click(insightsTab)

      // Check for insight content
      expect(screen.getByText(/Strong brand recognition/i)).toBeInTheDocument()
      expect(screen.getByText(/high Priority/i)).toBeInTheDocument()
      expect(screen.getByText(/Leverage brand strength/i)).toBeInTheDocument()
    })

    it('should have functional tab navigation', () => {
      render(
        <TestWrapper>
          <ModernResultsDisplay
            analysisResults={mockAnalysisResults}
            brandName="Apple"
            onNewAnalysis={vi.fn()}
          />
        </TestWrapper>
      )

      // Check all tabs are present
      expect(screen.getByRole('tab', { name: /Overview/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /Visual/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /Dashboard/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /Insights/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /AI Analysis/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /Competitive/i })).toBeInTheDocument()

      // Test tab switching
      const visualTab = screen.getByRole('tab', { name: /Visual/i })
      fireEvent.click(visualTab)

      // Tab should be active (this would need more specific testing based on implementation)
      expect(visualTab).toHaveAttribute('data-state', 'active')
    })
  })
})
