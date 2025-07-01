import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import HistoricalAnalysis from './components/HistoricalAnalysis'
import useAuthStore from './store/useAuthStore'
import useLoadingStore from './store/useLoadingStore'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Search, 
  Upload, 
  FileImage, 
  Palette, 
  Type, 
  BarChart3, 
  FileText, 
  Download,
  CheckCircle,
  Clock,
  AlertCircle,
  Sparkles
} from 'lucide-react'
import apiService from './services/api.js'
import { Toaster, toast } from 'sonner'
import './App.css'

function App() {
  const { isLoading, setLoading } = useLoadingStore()
  const [currentStep, setCurrentStep] = useState(1)
  const [brandQuery, setBrandQuery] = useState('')
  const [selectedFiles, setSelectedFiles] = useState([])
  const [analysisOptions, setAnalysisOptions] = useState({
    visualAnalysis: true,
    marketAnalysis: true,
    competitorAnalysis: false,
    sentimentAnalysis: true
  })
  const [analysisResults, setAnalysisResults] = useState(null)
  const [analysisId, setAnalysisId] = useState(null)

  const handleBrandSearch = async (e) => {
    e.preventDefault()
    if (!brandQuery.trim()) {
      toast.error('Please enter a brand name or website')
      return
    }

    setLoading(true)
    try {
      const response = await apiService.searchBrand(brandQuery)
      if (response.success) {
        toast.success('Brand found! Proceeding to next step.')
        setCurrentStep(2)
      } else {
        toast.error(response.message || 'Brand search failed')
      }
    } catch (error) {
      console.error('Brand search error:', error)
      toast.error('Failed to search brand. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (files) => {
    if (files.length === 0) {
      toast.error('Please select at least one file')
      return
    }

    setLoading(true)
    try {
      const response = await apiService.uploadFiles(files)
      if (response.success) {
        setSelectedFiles(files)
        toast.success('Files uploaded successfully!')
        setCurrentStep(3)
      } else {
        toast.error(response.message || 'File upload failed')
      }
    } catch (error) {
      console.error('File upload error:', error)
      toast.error('Failed to upload files. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleStartAnalysis = async () => {
    setLoading(true)
    try {
      const analysisData = {
        brand: brandQuery,
        files: selectedFiles.map(f => f.name),
        options: analysisOptions
      }

      const response = await apiService.startAnalysis(analysisData)
      if (response.success) {
        setAnalysisId(response.data.analysis_id)
        setCurrentStep(4)
        toast.success('Analysis started!')
        
        // Poll for results
        pollAnalysisStatus(response.data.analysis_id)
      } else {
        toast.error(response.message || 'Failed to start analysis')
      }
    } catch (error) {
      console.error('Analysis start error:', error)
      toast.error('Failed to start analysis. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const pollAnalysisStatus = async (id) => {
    const maxAttempts = 30
    let attempts = 0

    const checkStatus = async () => {
      try {
        const response = await apiService.getAnalysisStatus(id)
        
        if (response.data.status === 'completed') {
          const results = await apiService.getAnalysisResults(id)
          setAnalysisResults(results.data)
          setCurrentStep(5)
          toast.success('Analysis completed!')
        } else if (response.data.status === 'failed') {
          toast.error('Analysis failed. Please try again.')
          setCurrentStep(1)
        } else if (attempts < maxAttempts) {
          attempts++
          setTimeout(checkStatus, 3000) // Check every 3 seconds
        } else {
          toast.error('Analysis is taking longer than expected. Please check back later.')
        }
      } catch (error) {
        console.error('Status check error:', error)
        if (attempts < maxAttempts) {
          attempts++
          setTimeout(checkStatus, 3000)
        }
      }
    }

    checkStatus()
  }

  const renderStepIndicator = () => (
    <div className="flex justify-center mb-8">
      <div className="flex items-center space-x-4">
        {[1, 2, 3, 4, 5].map((step) => (
          <div key={step} className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
              ${currentStep >= step ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>
              {step}
            </div>
            {step < 5 && (
              <div className={`w-12 h-0.5 ${currentStep > step ? 'bg-primary' : 'bg-muted'}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  )

  const renderBrandInput = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Brand Information
        </CardTitle>
        <CardDescription>
          Enter the brand name or website you want to analyze
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleBrandSearch} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="brand-query">Brand Name or Website</Label>
            <Input
              id="brand-query"
              data-testid="brand-search"
              placeholder="e.g., Nike, apple.com, or starbucks.com"
              value={brandQuery}
              onChange={(e) => setBrandQuery(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Searching...' : 'Search Brand'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )

  const renderVisualAssets = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Visual Assets
        </CardTitle>
        <CardDescription>
          Upload brand assets for visual analysis (optional)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center">
            <FileImage className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Drag and drop files here, or click to select
              </p>
              <Input
                type="file"
                data-testid="upload"
                multiple
                accept=".png,.jpg,.jpeg,.gif,.svg,.webp,.pdf"
                onChange={(e) => handleFileUpload(Array.from(e.target.files))}
                className="cursor-pointer"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => setCurrentStep(3)} variant="outline">
              Skip Upload
            </Button>
            <Button onClick={() => setCurrentStep(3)} disabled={selectedFiles.length === 0}>
              Continue with {selectedFiles.length} file(s)
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderAnalysisOptions = () => (
    <Card data-testid="analysis-form">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Analysis Options
        </CardTitle>
        <CardDescription>
          Choose the types of analysis to perform
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries({
              visualAnalysis: 'Visual Brand Analysis',
              marketAnalysis: 'Market Presence Analysis',
              competitorAnalysis: 'Competitor Comparison',
              sentimentAnalysis: 'Sentiment Analysis'
            }).map(([key, label]) => (
              <div key={key} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id={key}
                  checked={analysisOptions[key]}
                  onChange={(e) => setAnalysisOptions(prev => ({
                    ...prev,
                    [key]: e.target.checked
                  }))}
                  className="rounded"
                />
                <Label htmlFor={key}>{label}</Label>
              </div>
            ))}
          </div>
          <Button onClick={handleStartAnalysis} disabled={isLoading}>
            {isLoading ? 'Starting Analysis...' : 'Start Analysis'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const renderProcessing = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Processing Analysis
        </CardTitle>
        <CardDescription>
          AI is analyzing your brand data...
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Progress value={75} className="w-full" />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span>This usually takes 2-3 minutes...</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderResults = () => (
    <Card data-testid="results" className="results">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-green-500" />
          Analysis Complete
        </CardTitle>
        <CardDescription>
          Your brand audit results are ready
        </CardDescription>
      </CardHeader>
      <CardContent>
        {analysisResults && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold">{analysisResults.overall_score || 'N/A'}</div>
                  <div className="text-sm text-muted-foreground">Overall Score</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold">{analysisResults.visual_score || 'N/A'}</div>
                  <div className="text-sm text-muted-foreground">Visual Consistency</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold">{analysisResults.market_score || 'N/A'}</div>
                  <div className="text-sm text-muted-foreground">Market Presence</div>
                </CardContent>
              </Card>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => setCurrentStep(1)}>
                Start New Analysis
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download Report
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b bg-card">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">AI Brand Audit Tool</h1>
              <p className="text-muted-foreground">
                Comprehensive brand analysis powered by AI
              </p>
            </div>
            <nav>
              <Link to="/historical-analysis" className="text-primary hover:underline" data-testid="history">
                Historical Analyses
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {isLoading && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="text-white text-xl">Loading...</div>
            </div>
          )}
          <Toaster position="top-right" />
          <Routes>
            <Route path="/" element={
              <>
                {renderStepIndicator()}
                {currentStep === 1 && renderBrandInput()}
                {currentStep === 2 && renderVisualAssets()}
                {currentStep === 3 && renderAnalysisOptions()}
                {currentStep === 4 && renderProcessing()}
                {currentStep === 5 && renderResults()}
              </>
            } />
            <Route path="/historical-analysis" element={<HistoricalAnalysis />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App