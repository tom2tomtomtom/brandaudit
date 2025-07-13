import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'

// Import visual components
import VisualAnalysisDashboard from '../../components/visual/VisualAnalysisDashboard.jsx'
import EnhancedVisualGallery from '../../components/visual/EnhancedVisualGallery.jsx'
import InteractiveColorPalette from '../../components/visual/InteractiveColorPalette.jsx'
import BrandAssetShowcase from '../../components/visual/BrandAssetShowcase.jsx'
import VisualMetrics from '../../components/visual/VisualMetrics.jsx'

// Test wrapper
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
)

describe('Visual Components Integration Tests', () => {
  const mockVisualData = {
    screenshots: [
      {
        url: 'https://example.com/screenshot1.png',
        page_type: 'homepage',
        timestamp: '2024-01-01T00:00:00Z',
        metadata: {
          title: 'Homepage Screenshot',
          viewport: '1920x1080'
        }
      }
    ],
    color_palette: {
      primary_colors: [
        { hex: '#FF0000', name: 'Primary Red', usage: 'primary' },
        { hex: '#0000FF', name: 'Primary Blue', usage: 'secondary' }
      ],
      secondary_colors: [
        { hex: '#00FF00', name: 'Accent Green', usage: 'accent' }
      ]
    },
    brand_assets: {
      logos: [
        {
          url: 'https://example.com/logo.png',
          type: 'primary',
          format: 'png',
          size: '512x512'
        }
      ],
      icons: [
        {
          url: 'https://example.com/icon.png',
          type: 'favicon',
          format: 'png'
        }
      ]
    },
    visual_metrics: {
      color_consistency: 85,
      logo_usage: 92,
      visual_hierarchy: 78,
      brand_alignment: 88
    },
    typography: {
      primary_font: 'Arial',
      secondary_font: 'Helvetica',
      font_consistency: 82
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('VisualAnalysisDashboard', () => {
    it('should render visual analysis dashboard', () => {
      render(
        <TestWrapper>
          <VisualAnalysisDashboard visualData={mockVisualData} />
        </TestWrapper>
      )

      // Check for dashboard elements
      expect(screen.getByText(/Visual Analysis Dashboard/i)).toBeInTheDocument()
    })

    it('should display visual metrics', () => {
      render(
        <TestWrapper>
          <VisualAnalysisDashboard visualData={mockVisualData} />
        </TestWrapper>
      )

      // Check for metric values
      expect(screen.getByText('85')).toBeInTheDocument() // color_consistency
      expect(screen.getByText('92')).toBeInTheDocument() // logo_usage
      expect(screen.getByText('78')).toBeInTheDocument() // visual_hierarchy
    })
  })

  describe('EnhancedVisualGallery', () => {
    it('should render visual gallery with screenshots', () => {
      render(
        <TestWrapper>
          <EnhancedVisualGallery 
            screenshots={mockVisualData.screenshots}
            brandAssets={mockVisualData.brand_assets}
          />
        </TestWrapper>
      )

      // Check for gallery elements
      expect(screen.getByText(/Visual Gallery/i)).toBeInTheDocument()
    })

    it('should handle screenshot display', () => {
      render(
        <TestWrapper>
          <EnhancedVisualGallery 
            screenshots={mockVisualData.screenshots}
            brandAssets={mockVisualData.brand_assets}
          />
        </TestWrapper>
      )

      // Check for screenshot elements
      const screenshot = screen.getByAltText(/Homepage Screenshot/i)
      expect(screenshot).toBeInTheDocument()
      expect(screenshot).toHaveAttribute('src', 'https://example.com/screenshot1.png')
    })

    it('should display brand assets', () => {
      render(
        <TestWrapper>
          <EnhancedVisualGallery 
            screenshots={mockVisualData.screenshots}
            brandAssets={mockVisualData.brand_assets}
          />
        </TestWrapper>
      )

      // Check for logo display
      const logo = screen.getByAltText(/Logo/i)
      expect(logo).toBeInTheDocument()
      expect(logo).toHaveAttribute('src', 'https://example.com/logo.png')
    })
  })

  describe('InteractiveColorPalette', () => {
    it('should render color palette', () => {
      render(
        <TestWrapper>
          <InteractiveColorPalette colorPalette={mockVisualData.color_palette} />
        </TestWrapper>
      )

      // Check for color palette elements
      expect(screen.getByText(/Color Palette/i)).toBeInTheDocument()
    })

    it('should display primary colors', () => {
      render(
        <TestWrapper>
          <InteractiveColorPalette colorPalette={mockVisualData.color_palette} />
        </TestWrapper>
      )

      // Check for color names
      expect(screen.getByText(/Primary Red/i)).toBeInTheDocument()
      expect(screen.getByText(/Primary Blue/i)).toBeInTheDocument()
    })

    it('should display color hex values', () => {
      render(
        <TestWrapper>
          <InteractiveColorPalette colorPalette={mockVisualData.color_palette} />
        </TestWrapper>
      )

      // Check for hex values
      expect(screen.getByText('#FF0000')).toBeInTheDocument()
      expect(screen.getByText('#0000FF')).toBeInTheDocument()
    })

    it('should handle color interaction', async () => {
      render(
        <TestWrapper>
          <InteractiveColorPalette colorPalette={mockVisualData.color_palette} />
        </TestWrapper>
      )

      // Find and click on a color swatch
      const colorSwatch = screen.getByText('#FF0000').closest('div')
      if (colorSwatch) {
        fireEvent.click(colorSwatch)
        
        // Should show color details or copy functionality
        await waitFor(() => {
          // This would depend on the actual implementation
          expect(colorSwatch).toHaveClass('selected') // or similar
        })
      }
    })
  })

  describe('BrandAssetShowcase', () => {
    it('should render brand asset showcase', () => {
      render(
        <TestWrapper>
          <BrandAssetShowcase brandAssets={mockVisualData.brand_assets} />
        </TestWrapper>
      )

      // Check for showcase elements
      expect(screen.getByText(/Brand Assets/i)).toBeInTheDocument()
    })

    it('should display logos section', () => {
      render(
        <TestWrapper>
          <BrandAssetShowcase brandAssets={mockVisualData.brand_assets} />
        </TestWrapper>
      )

      // Check for logos section
      expect(screen.getByText(/Logos/i)).toBeInTheDocument()
      
      // Check for logo image
      const logo = screen.getByAltText(/Logo/i)
      expect(logo).toBeInTheDocument()
    })

    it('should display asset metadata', () => {
      render(
        <TestWrapper>
          <BrandAssetShowcase brandAssets={mockVisualData.brand_assets} />
        </TestWrapper>
      )

      // Check for asset details
      expect(screen.getByText(/512x512/i)).toBeInTheDocument()
      expect(screen.getByText(/png/i)).toBeInTheDocument()
    })
  })

  describe('VisualMetrics', () => {
    it('should render visual metrics', () => {
      render(
        <TestWrapper>
          <VisualMetrics metrics={mockVisualData.visual_metrics} />
        </TestWrapper>
      )

      // Check for metrics display
      expect(screen.getByText(/Visual Metrics/i)).toBeInTheDocument()
    })

    it('should display metric scores', () => {
      render(
        <TestWrapper>
          <VisualMetrics metrics={mockVisualData.visual_metrics} />
        </TestWrapper>
      )

      // Check for metric values
      expect(screen.getByText('85')).toBeInTheDocument() // color_consistency
      expect(screen.getByText('92')).toBeInTheDocument() // logo_usage
      expect(screen.getByText('78')).toBeInTheDocument() // visual_hierarchy
      expect(screen.getByText('88')).toBeInTheDocument() // brand_alignment
    })

    it('should show metric labels', () => {
      render(
        <TestWrapper>
          <VisualMetrics metrics={mockVisualData.visual_metrics} />
        </TestWrapper>
      )

      // Check for metric labels
      expect(screen.getByText(/Color Consistency/i)).toBeInTheDocument()
      expect(screen.getByText(/Logo Usage/i)).toBeInTheDocument()
      expect(screen.getByText(/Visual Hierarchy/i)).toBeInTheDocument()
      expect(screen.getByText(/Brand Alignment/i)).toBeInTheDocument()
    })
  })

  describe('Visual Components Error Handling', () => {
    it('should handle missing visual data gracefully', () => {
      render(
        <TestWrapper>
          <VisualAnalysisDashboard visualData={null} />
        </TestWrapper>
      )

      // Should not crash and show appropriate message
      expect(screen.getByText(/No visual data available/i) || screen.getByText(/Loading/i)).toBeInTheDocument()
    })

    it('should handle empty color palette', () => {
      render(
        <TestWrapper>
          <InteractiveColorPalette colorPalette={{ primary_colors: [], secondary_colors: [] }} />
        </TestWrapper>
      )

      // Should handle empty data gracefully
      expect(screen.getByText(/No colors available/i) || screen.getByText(/Color Palette/i)).toBeInTheDocument()
    })

    it('should handle missing brand assets', () => {
      render(
        <TestWrapper>
          <BrandAssetShowcase brandAssets={{ logos: [], icons: [] }} />
        </TestWrapper>
      )

      // Should handle empty assets gracefully
      expect(screen.getByText(/No assets available/i) || screen.getByText(/Brand Assets/i)).toBeInTheDocument()
    })
  })
})
