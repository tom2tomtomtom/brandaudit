/**
 * Advanced Export Service
 * Handles comprehensive data export functionality for analytics dashboards
 */

import jsPDF from 'jspdf'
import 'jspdf-autotable'
import * as XLSX from 'xlsx'
import html2canvas from 'html2canvas'

class ExportService {
  constructor() {
    this.exportFormats = {
      PDF: 'pdf',
      EXCEL: 'xlsx',
      CSV: 'csv',
      JSON: 'json',
      PNG: 'png',
      SVG: 'svg'
    }
    
    this.templates = {
      EXECUTIVE_SUMMARY: 'executive',
      DETAILED_REPORT: 'detailed',
      COMPETITIVE_ANALYSIS: 'competitive',
      TREND_ANALYSIS: 'trends',
      CUSTOM: 'custom'
    }
  }

  /**
   * Export analytics dashboard as PDF
   */
  async exportToPDF(data, options = {}) {
    const {
      template = this.templates.DETAILED_REPORT,
      brandName = 'Brand',
      includeCharts = true,
      includeData = true,
      customization = {}
    } = options

    try {
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      let yPosition = 20

      // Header
      pdf.setFontSize(24)
      pdf.setFont('helvetica', 'bold')
      pdf.text(`${brandName} Analytics Report`, 20, yPosition)
      yPosition += 15

      // Date and metadata
      pdf.setFontSize(10)
      pdf.setFont('helvetica', 'normal')
      pdf.text(`Generated: ${new Date().toLocaleDateString()}`, 20, yPosition)
      pdf.text(`Template: ${template}`, pageWidth - 60, yPosition)
      yPosition += 20

      // Executive Summary
      if (template === this.templates.EXECUTIVE_SUMMARY || template === this.templates.DETAILED_REPORT) {
        yPosition = await this.addExecutiveSummary(pdf, data, yPosition, pageWidth)
      }

      // Brand Health Overview
      if (data.brandHealth) {
        yPosition = await this.addBrandHealthSection(pdf, data.brandHealth, yPosition, pageWidth)
      }

      // Key Metrics Table
      if (data.keyMetrics && includeData) {
        yPosition = await this.addKeyMetricsTable(pdf, data.keyMetrics, yPosition, pageWidth)
      }

      // Competitive Analysis
      if (data.competitivePosition && (template === this.templates.COMPETITIVE_ANALYSIS || template === this.templates.DETAILED_REPORT)) {
        yPosition = await this.addCompetitiveSection(pdf, data.competitivePosition, yPosition, pageWidth)
      }

      // Charts (if requested and available)
      if (includeCharts) {
        yPosition = await this.addChartsSection(pdf, data, yPosition, pageWidth, pageHeight)
      }

      // Insights and Recommendations
      if (data.insights) {
        yPosition = await this.addInsightsSection(pdf, data.insights, yPosition, pageWidth, pageHeight)
      }

      // Footer
      this.addFooter(pdf, pageWidth, pageHeight)

      return pdf.output('blob')
    } catch (error) {
      console.error('PDF export error:', error)
      throw new Error('Failed to generate PDF report')
    }
  }

  /**
   * Export data to Excel
   */
  async exportToExcel(data, options = {}) {
    const {
      brandName = 'Brand',
      includeCharts = false,
      multipleSheets = true
    } = options

    try {
      const workbook = XLSX.utils.book_new()

      // Summary Sheet
      const summaryData = this.prepareSummaryData(data, brandName)
      const summarySheet = XLSX.utils.json_to_sheet(summaryData)
      XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary')

      // Brand Health Sheet
      if (data.brandHealth && multipleSheets) {
        const healthData = this.prepareBrandHealthData(data.brandHealth)
        const healthSheet = XLSX.utils.json_to_sheet(healthData)
        XLSX.utils.book_append_sheet(workbook, healthSheet, 'Brand Health')
      }

      // Competitive Analysis Sheet
      if (data.competitivePosition && multipleSheets) {
        const competitiveData = this.prepareCompetitiveData(data.competitivePosition)
        const competitiveSheet = XLSX.utils.json_to_sheet(competitiveData)
        XLSX.utils.book_append_sheet(workbook, competitiveSheet, 'Competitive Analysis')
      }

      // Historical Data Sheet
      if (data.historicalData && multipleSheets) {
        const historicalSheet = XLSX.utils.json_to_sheet(data.historicalData)
        XLSX.utils.book_append_sheet(workbook, historicalSheet, 'Historical Data')
      }

      // Insights Sheet
      if (data.insights && multipleSheets) {
        const insightsData = data.insights.map(insight => ({
          Category: insight.category,
          Title: insight.title,
          Description: insight.description,
          Confidence: `${Math.round(insight.confidence * 100)}%`,
          Type: insight.type
        }))
        const insightsSheet = XLSX.utils.json_to_sheet(insightsData)
        XLSX.utils.book_append_sheet(workbook, insightsSheet, 'Insights')
      }

      return XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    } catch (error) {
      console.error('Excel export error:', error)
      throw new Error('Failed to generate Excel report')
    }
  }

  /**
   * Export data to CSV
   */
  async exportToCSV(data, options = {}) {
    const { dataType = 'summary' } = options

    try {
      let csvData = []

      switch (dataType) {
        case 'summary':
          csvData = this.prepareSummaryData(data)
          break
        case 'brandHealth':
          csvData = this.prepareBrandHealthData(data.brandHealth)
          break
        case 'competitive':
          csvData = this.prepareCompetitiveData(data.competitivePosition)
          break
        case 'insights':
          csvData = data.insights || []
          break
        default:
          csvData = this.prepareSummaryData(data)
      }

      const csv = this.convertToCSV(csvData)
      return new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    } catch (error) {
      console.error('CSV export error:', error)
      throw new Error('Failed to generate CSV report')
    }
  }

  /**
   * Export dashboard as image
   */
  async exportToImage(elementId, options = {}) {
    const {
      format = 'png',
      quality = 0.95,
      backgroundColor = '#ffffff'
    } = options

    try {
      const element = document.getElementById(elementId)
      if (!element) {
        throw new Error('Element not found')
      }

      const canvas = await html2canvas(element, {
        backgroundColor,
        scale: 2,
        useCORS: true,
        allowTaint: true
      })

      return new Promise((resolve) => {
        canvas.toBlob(resolve, `image/${format}`, quality)
      })
    } catch (error) {
      console.error('Image export error:', error)
      throw new Error('Failed to generate image')
    }
  }

  /**
   * Create PowerPoint presentation
   */
  async exportToPowerPoint(data, options = {}) {
    const {
      brandName = 'Brand',
      template = this.templates.EXECUTIVE_SUMMARY,
      includeCharts = true
    } = options

    try {
      // This would require a PowerPoint library like PptxGenJS
      // For now, we'll create a structured data format that can be used
      // to generate PowerPoint slides
      
      const presentation = {
        title: `${brandName} Analytics Presentation`,
        slides: []
      }

      // Title slide
      presentation.slides.push({
        type: 'title',
        title: `${brandName} Brand Analytics`,
        subtitle: `Generated ${new Date().toLocaleDateString()}`,
        layout: 'title'
      })

      // Executive Summary slide
      if (data.brandHealth) {
        presentation.slides.push({
          type: 'content',
          title: 'Executive Summary',
          content: [
            `Overall Brand Health: ${data.brandHealth.overall}/100`,
            `Visual Consistency: ${data.brandHealth.visual}%`,
            `Sentiment Score: ${data.brandHealth.sentiment}%`,
            `News Coverage: ${data.brandHealth.news}%`
          ],
          layout: 'content'
        })
      }

      // Key Metrics slide
      if (data.keyMetrics) {
        presentation.slides.push({
          type: 'metrics',
          title: 'Key Performance Metrics',
          metrics: data.keyMetrics,
          layout: 'two-column'
        })
      }

      // Competitive Position slide
      if (data.competitivePosition) {
        presentation.slides.push({
          type: 'competitive',
          title: 'Competitive Position',
          data: data.competitivePosition,
          layout: 'chart'
        })
      }

      // Insights slide
      if (data.insights && data.insights.length > 0) {
        presentation.slides.push({
          type: 'insights',
          title: 'Key Insights & Recommendations',
          insights: data.insights.slice(0, 5), // Top 5 insights
          layout: 'bullet-points'
        })
      }

      return JSON.stringify(presentation, null, 2)
    } catch (error) {
      console.error('PowerPoint export error:', error)
      throw new Error('Failed to generate PowerPoint presentation')
    }
  }

  // Helper methods for data preparation
  prepareSummaryData(data, brandName = 'Brand') {
    return [
      { Metric: 'Brand Name', Value: brandName },
      { Metric: 'Report Date', Value: new Date().toLocaleDateString() },
      { Metric: 'Overall Brand Health', Value: data.brandHealth?.overall || 'N/A' },
      { Metric: 'Sentiment Score', Value: `${data.brandHealth?.sentiment || 'N/A'}%` },
      { Metric: 'Market Position', Value: `#${data.competitivePosition?.ranking || 'N/A'}` },
      { Metric: 'Market Share', Value: `${data.competitivePosition?.marketShare?.toFixed(1) || 'N/A'}%` },
      { Metric: 'Total Mentions', Value: data.keyMetrics?.totalMentions || 'N/A' },
      { Metric: 'Visual Assets', Value: data.keyMetrics?.visualAssets || 'N/A' }
    ]
  }

  prepareBrandHealthData(brandHealth) {
    return [
      { Dimension: 'Overall Health', Score: brandHealth.overall, Trend: brandHealth.trend },
      { Dimension: 'Visual Identity', Score: brandHealth.visual, Trend: 'N/A' },
      { Dimension: 'Brand Sentiment', Score: brandHealth.sentiment, Trend: 'N/A' },
      { Dimension: 'News Coverage', Score: brandHealth.news, Trend: 'N/A' }
    ]
  }

  prepareCompetitiveData(competitive) {
    return [
      { Metric: 'Brand Score', Value: competitive.brandScore },
      { Metric: 'Average Competitor Score', Value: competitive.avgCompetitorScore },
      { Metric: 'Market Ranking', Value: competitive.ranking },
      { Metric: 'Market Share', Value: `${competitive.marketShare?.toFixed(1)}%` }
    ]
  }

  convertToCSV(data) {
    if (!data || data.length === 0) return ''
    
    const headers = Object.keys(data[0])
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header]
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value
        }).join(',')
      )
    ].join('\n')
    
    return csvContent
  }

  // PDF helper methods
  async addExecutiveSummary(pdf, data, yPosition, pageWidth) {
    pdf.setFontSize(16)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Executive Summary', 20, yPosition)
    yPosition += 10

    pdf.setFontSize(10)
    pdf.setFont('helvetica', 'normal')
    
    const summary = [
      `Overall brand health score of ${data.brandHealth?.overall || 'N/A'}/100`,
      `Market ranking: #${data.competitivePosition?.ranking || 'N/A'}`,
      `${data.keyMetrics?.totalMentions || 'N/A'} total brand mentions analyzed`,
      `${data.insights?.length || 0} actionable insights identified`
    ]

    summary.forEach(line => {
      pdf.text(line, 25, yPosition)
      yPosition += 5
    })

    return yPosition + 10
  }

  async addBrandHealthSection(pdf, brandHealth, yPosition, pageWidth) {
    pdf.setFontSize(14)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Brand Health Overview', 20, yPosition)
    yPosition += 10

    const healthData = [
      ['Metric', 'Score', 'Status'],
      ['Overall Health', `${brandHealth.overall}/100`, this.getHealthStatus(brandHealth.overall)],
      ['Visual Identity', `${brandHealth.visual}%`, this.getHealthStatus(brandHealth.visual)],
      ['Brand Sentiment', `${brandHealth.sentiment}%`, this.getHealthStatus(brandHealth.sentiment)],
      ['News Coverage', `${brandHealth.news}%`, this.getHealthStatus(brandHealth.news)]
    ]

    pdf.autoTable({
      head: [healthData[0]],
      body: healthData.slice(1),
      startY: yPosition,
      theme: 'grid',
      styles: { fontSize: 9 }
    })

    return pdf.lastAutoTable.finalY + 15
  }

  async addKeyMetricsTable(pdf, keyMetrics, yPosition, pageWidth) {
    pdf.setFontSize(14)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Key Performance Metrics', 20, yPosition)
    yPosition += 10

    const metricsData = [
      ['Metric', 'Value'],
      ['Total Mentions', keyMetrics.totalMentions?.toString() || 'N/A'],
      ['Sentiment Score', `${Math.round((keyMetrics.sentimentScore || 0) * 100)}%`],
      ['Visual Assets', keyMetrics.visualAssets?.toString() || 'N/A'],
      ['Competitor Count', keyMetrics.competitorCount?.toString() || 'N/A'],
      ['Campaign Count', keyMetrics.campaignCount?.toString() || 'N/A']
    ]

    pdf.autoTable({
      head: [metricsData[0]],
      body: metricsData.slice(1),
      startY: yPosition,
      theme: 'striped',
      styles: { fontSize: 9 }
    })

    return pdf.lastAutoTable.finalY + 15
  }

  async addCompetitiveSection(pdf, competitive, yPosition, pageWidth) {
    pdf.setFontSize(14)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Competitive Analysis', 20, yPosition)
    yPosition += 10

    const competitiveData = [
      ['Metric', 'Your Brand', 'Industry Average'],
      ['Brand Score', competitive.brandScore?.toString() || 'N/A', competitive.avgCompetitorScore?.toString() || 'N/A'],
      ['Market Ranking', `#${competitive.ranking || 'N/A'}`, 'N/A'],
      ['Market Share', `${competitive.marketShare?.toFixed(1) || 'N/A'}%`, 'N/A']
    ]

    pdf.autoTable({
      head: [competitiveData[0]],
      body: competitiveData.slice(1),
      startY: yPosition,
      theme: 'grid',
      styles: { fontSize: 9 }
    })

    return pdf.lastAutoTable.finalY + 15
  }

  async addInsightsSection(pdf, insights, yPosition, pageWidth, pageHeight) {
    pdf.setFontSize(14)
    pdf.setFont('helvetica', 'bold')
    pdf.text('Key Insights & Recommendations', 20, yPosition)
    yPosition += 10

    insights.slice(0, 5).forEach((insight, index) => {
      if (yPosition > pageHeight - 40) {
        pdf.addPage()
        yPosition = 20
      }

      pdf.setFontSize(11)
      pdf.setFont('helvetica', 'bold')
      pdf.text(`${index + 1}. ${insight.title}`, 25, yPosition)
      yPosition += 7

      pdf.setFontSize(9)
      pdf.setFont('helvetica', 'normal')
      const lines = pdf.splitTextToSize(insight.description, pageWidth - 50)
      pdf.text(lines, 30, yPosition)
      yPosition += lines.length * 4 + 5

      pdf.setFontSize(8)
      pdf.setFont('helvetica', 'italic')
      pdf.text(`Confidence: ${Math.round(insight.confidence * 100)}%`, 30, yPosition)
      yPosition += 10
    })

    return yPosition
  }

  addFooter(pdf, pageWidth, pageHeight) {
    pdf.setFontSize(8)
    pdf.setFont('helvetica', 'normal')
    pdf.text('Generated by Brand Audit Analytics Platform', pageWidth / 2, pageHeight - 10, { align: 'center' })
  }

  getHealthStatus(score) {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Poor'
  }

  /**
   * Download file with given blob and filename
   */
  downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * Get available export formats
   */
  getAvailableFormats() {
    return Object.values(this.exportFormats)
  }

  /**
   * Get available templates
   */
  getAvailableTemplates() {
    return Object.values(this.templates)
  }
}

// Create singleton instance
const exportService = new ExportService()
export default exportService
