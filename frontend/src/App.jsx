import { useState } from 'react'
import HistoricalAnalysis from './components/HistoricalAnalysis'
import useAuthStore from './store/useAuthStore'
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
              <Link to="/historical-analysis" className="text-primary hover:underline">
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
            {role === 'admin' && (
              <Route path="/admin-dashboard" element={<div>Admin Dashboard Content (Coming Soon!)</div>} />
            )}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App

