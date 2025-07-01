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
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Sparkles className="h-5 w-5" />
                      Welcome to AI Brand Audit Tool
                    </CardTitle>
                    <CardDescription>
                      Get comprehensive insights into your brand's visual identity and market positioning
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card>
                        <CardContent className="p-6 text-center">
                          <Search className="h-8 w-8 mx-auto mb-2 text-primary" />
                          <h3 className="font-semibold mb-2">Brand Search</h3>
                          <p className="text-sm text-muted-foreground">
                            Search and analyze any brand's digital presence
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-6 text-center">
                          <Upload className="h-8 w-8 mx-auto mb-2 text-primary" />
                          <h3 className="font-semibold mb-2">Asset Analysis</h3>
                          <p className="text-sm text-muted-foreground">
                            Upload and analyze brand assets and logos
                          </p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-6 text-center">
                          <BarChart3 className="h-8 w-8 mx-auto mb-2 text-primary" />
                          <h3 className="font-semibold mb-2">AI Insights</h3>
                          <p className="text-sm text-muted-foreground">
                            Get AI-powered recommendations and insights
                          </p>
                        </CardContent>
                      </Card>
                    </div>
                    <div className="mt-6 text-center">
                      <Button className="mr-2">Start Brand Analysis</Button>
                      <Button variant="outline">
                        <Link to="/historical-analysis">View Past Analyses</Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            } />
            <Route path="/historical-analysis" element={<HistoricalAnalysis />} />
            {/* role === 'admin' && (
              <Route path="/admin-dashboard" element={<div>Admin Dashboard Content (Coming Soon!)</div>} />
            ) */}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App