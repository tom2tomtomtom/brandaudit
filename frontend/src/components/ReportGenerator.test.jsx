import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ReportGenerator from './ReportGenerator';

// Mock fetch
global.fetch = vi.fn();

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(() => 'mock-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Sample test data
const mockAnalysisResults = {
  key_metrics: {
    overall_score: 78,
    visual_score: 82,
    market_score: 75,
    sentiment_score: 80
  },
  competitor_analysis: {
    competitors_identified: {
      competitors: [
        { name: 'Apple', market_position: 'Premium leader' },
        { name: 'Samsung', market_position: 'Technology innovator' }
      ]
    }
  },
  actionable_insights: [
    {
      finding: 'Enhance visual brand consistency',
      priority: 'High',
      timeline: '60 days',
      impact: 'High'
    },
    {
      finding: 'Strengthen competitive positioning',
      priority: 'Medium',
      timeline: '90 days',
      impact: 'Medium'
    }
  ]
};

describe('ReportGenerator', () => {
  const mockOnReportGenerated = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
    fetch.mockClear();
  });

  it('renders report generator interface', () => {
    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Check main elements
    expect(screen.getByText('Professional Report Generator')).toBeInTheDocument();
    expect(screen.getByText('Tesla')).toBeInTheDocument();
    expect(screen.getByText('Report Template')).toBeInTheDocument();
    expect(screen.getByText('Visual Theme')).toBeInTheDocument();
    expect(screen.getByText('Export Formats')).toBeInTheDocument();
  });

  it('displays all template options', () => {
    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Click template dropdown
    const templateSelect = screen.getByRole('combobox');
    fireEvent.click(templateSelect);

    // Check template options
    expect(screen.getByText('Executive Summary')).toBeInTheDocument();
    expect(screen.getByText('Detailed Analysis')).toBeInTheDocument();
    expect(screen.getByText('Presentation Deck')).toBeInTheDocument();
    expect(screen.getByText('Consulting Report')).toBeInTheDocument();
    expect(screen.getByText('Strategic Brief')).toBeInTheDocument();
  });

  it('displays all export format options', () => {
    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Check export format checkboxes
    expect(screen.getByLabelText('PDF Report')).toBeInTheDocument();
    expect(screen.getByLabelText('PowerPoint')).toBeInTheDocument();
    expect(screen.getByLabelText('Interactive HTML')).toBeInTheDocument();
  });

  it('shows error when no formats selected', async () => {
    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Uncheck all formats
    const pdfCheckbox = screen.getByLabelText('PDF Report');
    fireEvent.click(pdfCheckbox);

    // Try to generate
    const generateButton = screen.getByText('Generate Reports');
    fireEvent.click(generateButton);

    // Check for error
    await waitFor(() => {
      expect(screen.getByText('Please select at least one export format')).toBeInTheDocument();
    });
  });

  it('handles successful report generation', async () => {
    const mockResponse = {
      success: true,
      reports_generated: {
        pdf: {
          filename: 'tesla_detailed_analysis_report.pdf',
          download_url: '/static/presentations/tesla_detailed_analysis_report.pdf',
          file_size: 1024000
        },
        html: {
          filename: 'tesla_detailed_analysis_interactive.html',
          download_url: '/static/presentations/tesla_detailed_analysis_interactive.html',
          file_size: 512000
        }
      },
      charts_generated: [
        { type: 'brand_health', title: 'Brand Health Dashboard' },
        { type: 'competitive_positioning', title: 'Competitive Positioning Matrix' }
      ]
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Generate reports
    const generateButton = screen.getByText('Generate Reports');
    fireEvent.click(generateButton);

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText('Generated Reports')).toBeInTheDocument();
    });

    // Check generated reports
    expect(screen.getByText('tesla_detailed_analysis_report.pdf')).toBeInTheDocument();
    expect(screen.getByText('tesla_detailed_analysis_interactive.html')).toBeInTheDocument();
    expect(screen.getAllByText('Download')).toHaveLength(2);

    // Check callback was called
    expect(mockOnReportGenerated).toHaveBeenCalledWith(mockResponse);
  });

  it('handles API errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('API Error'));

    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Generate reports
    const generateButton = screen.getByText('Generate Reports');
    fireEvent.click(generateButton);

    // Wait for error
    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });

  it('updates template selection and shows preview', () => {
    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Initially shows detailed analysis preview
    expect(screen.getByText('Detailed Analysis')).toBeInTheDocument();
    expect(screen.getByText('15-20 pages')).toBeInTheDocument();
    expect(screen.getByText('Marketing Teams')).toBeInTheDocument();
  });

  it('updates theme selection and shows color preview', () => {
    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Initially shows corporate blue theme
    expect(screen.getByText('Corporate Blue')).toBeInTheDocument();
    expect(screen.getByText('Professional blue theme')).toBeInTheDocument();
  });

  it('shows progress during generation', async () => {
    // Mock a slow response
    fetch.mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({ success: true, reports_generated: {} })
        }), 100)
      )
    );

    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Start generation
    const generateButton = screen.getByText('Generate Reports');
    fireEvent.click(generateButton);

    // Check progress appears
    await waitFor(() => {
      expect(screen.getByText('Generating reports...')).toBeInTheDocument();
    });

    // Check button is disabled
    expect(generateButton).toBeDisabled();
  });

  it('allows format selection changes', () => {
    render(
      <ReportGenerator
        analysisResults={mockAnalysisResults}
        brandName="Tesla"
        onReportGenerated={mockOnReportGenerated}
      />
    );

    // Initially PDF is selected
    const pdfCheckbox = screen.getByLabelText('PDF Report');
    expect(pdfCheckbox).toBeChecked();

    // Select PowerPoint
    const pptxCheckbox = screen.getByLabelText('PowerPoint');
    fireEvent.click(pptxCheckbox);
    expect(pptxCheckbox).toBeChecked();

    // Check format count updates
    expect(screen.getByText('2 formats selected')).toBeInTheDocument();
  });
});
