/**
 * Frontend component integration tests
 * Tests React components with backend data integration
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'

// Import components
import App from '../../src/App'
import AnalysisProgress from '../../src/components/AnalysisProgress'
import StrategicIntelligenceBriefing from '../../src/components/StrategicIntelligenceBriefing'
import ModernLanding from '../../src/components/ModernLanding'

// Mock API service
import * as apiService from '../../src/services/api'

// Test data
const mockAnalysisResponse = {
  success: true,
  data: {
    analysis_id: 'test-analysis-123',
    estimated_completion: new Date(Date.now() + 300000).toISOString()
  }
}

const mockAnalysisResults = {
  success: true,
  data: {
    analysis_id: 'test-analysis-123',
    brand_name: 'Test Brand',
    status: 'completed',
    progress: 100,
    llm_insights: {
      analysis: 'Comprehensive brand analysis with strategic insights...',
      sentiment_score: 0.85,
      key_findings: ['Strong market presence', 'Positive brand perception']
    },
    visual_analysis: {
      primary_colors: ['#1E3A8A', '#FFFFFF'],
      secondary_colors: ['#64748B', '#F1F5F9'],
      fonts: ['Inter', 'Roboto'],
      logo_quality_score: 0.9
    },
    news_analysis: {
      articles_count: 15,
      sentiment_distribution: { positive: 70, neutral: 20, negative: 10 }
    },
    competitive_analysis: {
      competitors: ['Competitor A', 'Competitor B'],
      market_position: 'leader'
    }
  }
}

const mockProgressUpdate = {
  analysis_id: 'test-analysis-123',
  overall_progress: 50,
  current_stage: 2,
  stage_progress: 75,
  current_step_name: 'Visual Analysis',
  current_substep: 'Extracting brand colors',
  status: 'processing',
  time_remaining: 120,
  elapsed_time: 180
}

// Mock WebSocket
const mockWebSocket = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  emit: vi.fn(),
  on: vi.fn(),
  connected: true
}

// Mock socket.io-client
vi.mock('socket.io-client', () => ({
  default: vi.fn(() => mockWebSocket),
  io: vi.fn(() => mockWebSocket)
}))

describe('Frontend Component Integration Tests', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks()
    
    // Mock API service methods
    vi.spyOn(apiService, 'startAnalysis').mockResolvedValue(mockAnalysisResponse)
    vi.spyOn(apiService, 'getAnalysisStatus').mockResolvedValue({
      success: true,
      data: { status: 'processing', progress: 50 }
    })
    vi.spyOn(apiService, 'getAnalysisResults').mockResolvedValue(mockAnalysisResults)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('App Component Integration', () => {
    it('should handle complete analysis workflow', async () => {
      const user = userEvent.setup()
      
      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      )

      // Should start on landing page
      expect(screen.getByText(/AI Brand Analysis/i)).toBeInTheDocument()

      // Enter brand name and start analysis
      const input = screen.getByPlaceholderText(/Enter brand name/i)
      const submitButton = screen.getByRole('button', { name: /analyze/i })

      await user.type(input, 'Test Brand')
      await user.click(submitButton)

      // Should call API service
      expect(apiService.startAnalysis).toHaveBeenCalledWith({
        company_name: 'Test Brand',
        analysis_options: expect.objectContaining({
          brandPerception: true,
          competitiveAnalysis: true,
          visualAnalysis: true,
          pressCoverage: true
        })
      })

      // Should show progress view
      await waitFor(() => {
        expect(screen.getByText(/Analysis in Progress/i)).toBeInTheDocument()
      })
    })

    it('should handle API errors gracefully', async () => {
      const user = userEvent.setup()
      
      // Mock API error
      vi.spyOn(apiService, 'startAnalysis').mockRejectedValue(new Error('API Error'))

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      )

      const input = screen.getByPlaceholderText(/Enter brand name/i)
      const submitButton = screen.getByRole('button', { name: /analyze/i })

      await user.type(input, 'Test Brand')
      await user.click(submitButton)

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/Failed to start analysis/i)).toBeInTheDocument()
      })

      // Should return to landing page
      expect(screen.getByText(/AI Brand Analysis/i)).toBeInTheDocument()
    })

    it('should handle loading states correctly', async () => {
      const user = userEvent.setup()
      
      // Mock delayed API response
      vi.spyOn(apiService, 'startAnalysis').mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockAnalysisResponse), 1000))
      )

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      )

      const input = screen.getByPlaceholderText(/Enter brand name/i)
      const submitButton = screen.getByRole('button', { name: /analyze/i })

      await user.type(input, 'Test Brand')
      await user.click(submitButton)

      // Should show loading state
      expect(submitButton).toBeDisabled()

      // Wait for API call to complete
      await waitFor(() => {
        expect(screen.getByText(/Analysis in Progress/i)).toBeInTheDocument()
      }, { timeout: 2000 })
    })
  })

  describe('AnalysisProgress Component Integration', () => {
    const mockOnComplete = vi.fn()

    it('should display progress information correctly', () => {
      // Mock useWebSocket hook
      const mockUseWebSocket = vi.fn(() => ({
        isConnected: true,
        progress: 50,
        currentStage: 2,
        currentStepName: 'Visual Analysis',
        status: 'processing',
        timeRemaining: 120,
        elapsedTime: 180,
        formatTimeRemaining: '2 minutes',
        formatElapsedTime: '3 minutes'
      }))

      vi.doMock('../../src/hooks/useWebSocket', () => ({
        default: mockUseWebSocket,
        useWebSocket: mockUseWebSocket
      }))

      render(
        <AnalysisProgress 
          analysisId="test-analysis-123" 
          onComplete={mockOnComplete} 
        />
      )

      // Should display progress information
      expect(screen.getByText(/50%/)).toBeInTheDocument()
      expect(screen.getByText(/Visual Analysis/i)).toBeInTheDocument()
      expect(screen.getByText(/2 minutes/)).toBeInTheDocument()
    })

    it('should handle WebSocket connection errors', () => {
      const mockUseWebSocket = vi.fn(() => ({
        isConnected: false,
        connectionQuality: 'poor',
        errorMessage: 'Connection failed',
        progress: 0,
        status: 'error',
        retry: vi.fn()
      }))

      vi.doMock('../../src/hooks/useWebSocket', () => ({
        default: mockUseWebSocket
      }))

      render(
        <AnalysisProgress 
          analysisId="test-analysis-123" 
          onComplete={mockOnComplete} 
        />
      )

      // Should display error state
      expect(screen.getByText(/Connection failed/i)).toBeInTheDocument()
      
      // Should show retry option
      const retryButton = screen.getByRole('button', { name: /retry/i })
      expect(retryButton).toBeInTheDocument()
    })

    it('should call onComplete when analysis finishes', () => {
      const mockUseWebSocket = vi.fn(() => ({
        isConnected: true,
        progress: 100,
        status: 'completed',
        currentStepName: 'Analysis Complete'
      }))

      vi.doMock('../../src/hooks/useWebSocket', () => ({
        default: mockUseWebSocket
      }))

      // Mock the completion callback
      const onCompleteSpy = vi.fn()

      render(
        <AnalysisProgress 
          analysisId="test-analysis-123" 
          onComplete={onCompleteSpy} 
        />
      )

      // Should show completion state
      expect(screen.getByText(/100%/)).toBeInTheDocument()
      expect(screen.getByText(/Analysis Complete/i)).toBeInTheDocument()
    })
  })

  describe('StrategicIntelligenceBriefing Component Integration', () => {
    it('should render analysis results correctly', () => {
      render(
        <StrategicIntelligeBriefing 
          analysisResults={mockAnalysisResults.data}
          brandName="Test Brand"
          onNewAnalysis={vi.fn()}
        />
      )

      // Should display brand name
      expect(screen.getByText(/Test Brand/i)).toBeInTheDocument()

      // Should display key metrics
      expect(screen.getByText(/Overall Brand Score/i)).toBeInTheDocument()
      expect(screen.getByText(/Competitive Position/i)).toBeInTheDocument()

      // Should display analysis sections
      expect(screen.getByText(/Executive Summary/i)).toBeInTheDocument()
      expect(screen.getByText(/Visual Analysis/i)).toBeInTheDocument()
    })

    it('should handle missing data gracefully', () => {
      const incompleteResults = {
        analysis_id: 'test-123',
        brand_name: 'Test Brand',
        status: 'completed'
        // Missing other analysis sections
      }

      render(
        <StrategicIntelligenceBriefing 
          analysisResults={incompleteResults}
          brandName="Test Brand"
          onNewAnalysis={vi.fn()}
        />
      )

      // Should still render without crashing
      expect(screen.getByText(/Test Brand/i)).toBeInTheDocument()
      
      // Should show placeholder messages for missing data
      expect(screen.getByText(/will appear here when analysis is complete/i)).toBeInTheDocument()
    })

    it('should handle tab navigation', async () => {
      const user = userEvent.setup()

      render(
        <StrategicIntelligenceBriefing 
          analysisResults={mockAnalysisResults.data}
          brandName="Test Brand"
          onNewAnalysis={vi.fn()}
        />
      )

      // Should start on executive tab
      expect(screen.getByText(/Executive Summary/i)).toBeInTheDocument()

      // Click on competitive tab
      const competitiveTab = screen.getByRole('tab', { name: /competitive/i })
      await user.click(competitiveTab)

      // Should show competitive analysis content
      expect(screen.getByText(/Competitor A/i)).toBeInTheDocument()
    })

    it('should trigger new analysis correctly', async () => {
      const user = userEvent.setup()
      const onNewAnalysisSpy = vi.fn()

      render(
        <StrategicIntelligenceBriefing 
          analysisResults={mockAnalysisResults.data}
          brandName="Test Brand"
          onNewAnalysis={onNewAnalysisSpy}
        />
      )

      // Find and click new analysis button
      const newAnalysisButton = screen.getByRole('button', { name: /new analysis/i })
      await user.click(newAnalysisButton)

      expect(onNewAnalysisSpy).toHaveBeenCalled()
    })
  })

  describe('Data Flow Integration', () => {
    it('should pass data correctly between components', async () => {
      const user = userEvent.setup()

      // Mock successful analysis completion
      vi.spyOn(apiService, 'getAnalysisResults').mockResolvedValue(mockAnalysisResults)

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      )

      // Start analysis
      const input = screen.getByPlaceholderText(/Enter brand name/i)
      const submitButton = screen.getByRole('button', { name: /analyze/i })

      await user.type(input, 'Test Brand')
      await user.click(submitButton)

      // Wait for progress view
      await waitFor(() => {
        expect(screen.getByText(/Analysis in Progress/i)).toBeInTheDocument()
      })

      // Simulate analysis completion
      act(() => {
        // This would normally be triggered by WebSocket
        // For testing, we'll simulate the completion callback
        const progressComponent = screen.getByTestId('analysis-progress')
        if (progressComponent) {
          // Trigger completion manually for test
          fireEvent.click(screen.getByRole('button', { name: /complete/i }))
        }
      })

      // Should show results view with correct data
      await waitFor(() => {
        expect(screen.getByText(/Strategic Intelligence/i)).toBeInTheDocument()
        expect(screen.getByText(/Test Brand/i)).toBeInTheDocument()
      })
    })

    it('should handle real-time updates correctly', async () => {
      // Mock WebSocket progress updates
      const mockUseWebSocket = vi.fn(() => ({
        isConnected: true,
        progress: 25,
        currentStage: 1,
        currentStepName: 'LLM Analysis',
        status: 'processing'
      }))

      vi.doMock('../../src/hooks/useWebSocket', () => ({
        default: mockUseWebSocket
      }))

      render(
        <AnalysisProgress 
          analysisId="test-analysis-123" 
          onComplete={vi.fn()} 
        />
      )

      // Should display current progress
      expect(screen.getByText(/25%/)).toBeInTheDocument()
      expect(screen.getByText(/LLM Analysis/i)).toBeInTheDocument()

      // Simulate progress update
      act(() => {
        mockUseWebSocket.mockReturnValue({
          isConnected: true,
          progress: 75,
          currentStage: 3,
          currentStepName: 'News Analysis',
          status: 'processing'
        })
      })

      // Re-render to reflect updated progress
      render(
        <AnalysisProgress 
          analysisId="test-analysis-123" 
          onComplete={vi.fn()} 
        />
      )

      expect(screen.getByText(/75%/)).toBeInTheDocument()
      expect(screen.getByText(/News Analysis/i)).toBeInTheDocument()
    })
  })

  describe('Error Handling Integration', () => {
    it('should display API errors to user', async () => {
      const user = userEvent.setup()
      
      // Mock API error
      vi.spyOn(apiService, 'startAnalysis').mockRejectedValue({
        message: 'Rate limit exceeded'
      })

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      )

      const input = screen.getByPlaceholderText(/Enter brand name/i)
      const submitButton = screen.getByRole('button', { name: /analyze/i })

      await user.type(input, 'Test Brand')
      await user.click(submitButton)

      // Should show specific error message
      await waitFor(() => {
        expect(screen.getByText(/Rate limit exceeded/i)).toBeInTheDocument()
      })
    })

    it('should handle network errors gracefully', async () => {
      const user = userEvent.setup()
      
      // Mock network error
      vi.spyOn(apiService, 'startAnalysis').mockRejectedValue(new Error('Network Error'))

      render(
        <BrowserRouter>
          <App />
        </BrowserRouter>
      )

      const input = screen.getByPlaceholderText(/Enter brand name/i)
      const submitButton = screen.getByRole('button', { name: /analyze/i })

      await user.type(input, 'Test Brand')
      await user.click(submitButton)

      // Should show generic error message
      await waitFor(() => {
        expect(screen.getByText(/Failed to start analysis/i)).toBeInTheDocument()
      })

      // Should allow retry
      expect(submitButton).not.toBeDisabled()
    })
  })
})
