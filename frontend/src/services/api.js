// API service for brand audit tool
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Brand search and information
  async searchBrand(query) {
    return this.request('/brand/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    })
  }

  async getBrandAssets(website) {
    return this.request('/brand/assets', {
      method: 'POST',
      body: JSON.stringify({ website }),
    })
  }

  // File upload
  async uploadFiles(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    return this.request('/upload', {
      method: 'POST',
      headers: {}, // Let browser set Content-Type for FormData
      body: formData,
    })
  }

  // Analysis
  async startAnalysis(analysisData) {
    return this.request('/analyze', {
      method: 'POST',
      body: JSON.stringify(analysisData),
    })
  }

  async getAnalysisStatus(analysisId) {
    return this.request(`/analyze/${analysisId}/status`)
  }

  async getAnalysisResults(analysisId) {
    return this.request(`/analyze/${analysisId}/results`)
  }

  // Report generation
  async generateReport(reportData) {
    return this.request('/report/generate', {
      method: 'POST',
      body: JSON.stringify(reportData),
    })
  }

  // Health check
  async healthCheck() {
    return this.request('/health')
  }

  // Historical analyses
  async getUserAnalyses() {
    return this.request('/analyses')
  }
}

export const apiService = new ApiService()
export default apiService

