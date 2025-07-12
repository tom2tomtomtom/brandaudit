import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import HistoricalAnalysis from './components/HistoricalAnalysis'
import FullConsultingReport from './components/FullConsultingReport'
import ModernLanding from './components/ModernLanding'
import AnalysisProgress from './components/AnalysisProgress'
import StrategicIntelligenceBriefing from './components/StrategicIntelligenceBriefing'
import AdvancedAnalyticsDashboard from './components/analytics/AdvancedAnalyticsDashboard'
import AnalyticsTest from './components/analytics/AnalyticsTest'
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
  Sparkles,
  TrendingUp,
  Target,
  Zap,
  Brain,
  Rocket,
  Star,
  ArrowRight,
  Building2,
  Globe
} from 'lucide-react'
import apiService from './services/api.js'
import { Toaster, toast } from 'sonner'
import './App.css'

function App() {
  const { isLoading, setLoading } = useLoadingStore()
  const [currentView, setCurrentView] = useState('landing') // 'landing', 'analyzing', 'results'
  const [brandQuery, setBrandQuery] = useState('')
  const [analysisResults, setAnalysisResults] = useState(null)
  const [analysisId, setAnalysisId] = useState(null)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisStatus, setAnalysisStatus] = useState('')

  const handleStartAnalysis = async (brandName) => {
    setBrandQuery(brandName)
    setLoading(true)
    setCurrentView('analyzing')

    try {
      const response = await apiService.startAnalysis({
        company_name: brandName,
        analysis_options: {
          brandPerception: true,
          competitiveAnalysis: true,
          visualAnalysis: true,  // NEW: Enable enhanced visual analysis with color extraction
          pressCoverage: true,
          socialSentiment: false
        }
      })
      if (response.success) {
        setAnalysisId(response.data.analysis_id)
        toast.success('Analysis started! This will take 2-3 minutes.')
      } else {
        toast.error(response.message || 'Failed to start analysis')
        setCurrentView('landing')
      }
    } catch (error) {
      console.error('Analysis start error:', error)
      toast.error('Failed to start analysis. Please try again.')
      setCurrentView('landing')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalysisComplete = async () => {
    try {
      const response = await apiService.getAnalysisResults(analysisId)
      if (response.success) {
        setAnalysisResults(response.data)
        setCurrentView('results')
        toast.success('Analysis completed!')
      } else {
        toast.error('Failed to get analysis results')
        setCurrentView('landing')
      }
    } catch (error) {
      console.error('Error getting results:', error)
      toast.error('Failed to get analysis results')
      setCurrentView('landing')
    }
  }

  const handleNewAnalysis = () => {
    setCurrentView('landing')
    setAnalysisResults(null)
    setAnalysisId(null)
    setBrandQuery('')
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'landing':
        return <ModernLanding onStartAnalysis={handleStartAnalysis} isLoading={isLoading} />

      case 'analyzing':
        return (
          <div className="min-h-screen bg-gray-50 py-8">
            <AnalysisProgress
              analysisId={analysisId}
              onComplete={handleAnalysisComplete}
            />
          </div>
        )

      case 'results':
        return (
          <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4">
              <StrategicIntelligenceBriefing
                analysisResults={analysisResults}
                brandName={brandQuery}
                onNewAnalysis={handleNewAnalysis}
              />
            </div>
          </div>
        )

      default:
        return <ModernLanding onStartAnalysis={handleStartAnalysis} isLoading={isLoading} />
    }
  }







  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={renderCurrentView()} />
          <Route path="/historical-analysis" element={<HistoricalAnalysis />} />
          <Route path="/analytics" element={
            <div className="min-h-screen bg-gray-50 py-8">
              <div className="max-w-7xl mx-auto px-4">
                <AdvancedAnalyticsDashboard
                  analysisResults={analysisResults}
                  brandName={brandQuery}
                  historicalData={[]}
                  competitorData={[]}
                  onExport={(format, data) => console.log('Export:', format, data)}
                  onRefresh={() => console.log('Refresh analytics')}
                />
              </div>
            </div>
          } />
          <Route path="/analytics-test" element={
            <div className="min-h-screen bg-gray-50">
              <AnalyticsTest />
            </div>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App