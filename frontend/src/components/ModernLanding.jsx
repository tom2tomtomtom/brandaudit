import React, { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import {
  Search,
  Sparkles,
  Brain,
  TrendingUp,
  Target,
  Zap,
  CheckCircle,
  ArrowRight,
  Building2,
  BarChart3,
  Globe,
  Star,
  Rocket,
  Clock,
  Loader2
} from 'lucide-react'

const ModernLanding = ({ onStartAnalysis, isLoading }) => {
  const [brandQuery, setBrandQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (brandQuery.trim()) {
      onStartAnalysis(brandQuery.trim())
    }
  }

  const features = [
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Claude AI provides strategic insights typically found in $10K+ consulting reports'
    },
    {
      icon: TrendingUp,
      title: 'Market Intelligence',
      description: 'Real-time market trends, competitive positioning, and industry benchmarks'
    },
    {
      icon: Target,
      title: 'Actionable Insights',
      description: 'Prioritized recommendations with timelines and expected business impact'
    },
    {
      icon: BarChart3,
      title: 'Brand Health Scoring',
      description: 'Comprehensive scoring across visual identity, market presence, and perception'
    }
  ]

  const exampleBrands = [
    'Apple', 'Tesla', 'Nike', 'Starbucks', 'Microsoft', 'Netflix'
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 py-20">
          <div className="text-center space-y-8">
            {/* Header */}
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-2 mb-4">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl">
                  <Sparkles className="h-8 w-8 text-white" />
                </div>
              </div>
              
              <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent leading-tight">
                AI Brand Audit Tool
              </h1>
              
              <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                Get professional-grade brand analysis in minutes, not months. 
                <span className="font-semibold text-blue-600"> Powered by Claude AI</span> and real market data.
              </p>
            </div>

            {/* Value Proposition */}
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              <Badge variant="secondary" className="px-4 py-2 text-sm">
                <CheckCircle className="h-4 w-4 mr-2" />
                $10,000+ Value
              </Badge>
              <Badge variant="secondary" className="px-4 py-2 text-sm">
                <Clock className="h-4 w-4 mr-2" />
                2-3 Minutes
              </Badge>
              <Badge variant="secondary" className="px-4 py-2 text-sm">
                <Zap className="h-4 w-4 mr-2" />
                Real Data Only
              </Badge>
            </div>

            {/* Search Form */}
            <div className="max-w-2xl mx-auto">
              <Card className="p-8 shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-3">
                    <label className="text-lg font-semibold text-gray-700 block">
                      Enter your brand name to get started
                    </label>
                    <div className="relative">
                      <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <Input
                        type="text"
                        placeholder="e.g., Apple, Tesla, Nike, or your company name"
                        value={brandQuery}
                        onChange={(e) => setBrandQuery(e.target.value)}
                        className="pl-12 pr-4 py-4 text-lg border-2 border-gray-200 focus:border-blue-500 rounded-xl"
                        required
                      />
                    </div>
                  </div>
                  
                  <Button 
                    type="submit" 
                    disabled={isLoading || !brandQuery.trim()}
                    className="w-full py-4 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                        Starting Analysis...
                      </>
                    ) : (
                      <>
                        <Rocket className="h-5 w-5 mr-2" />
                        Start AI Brand Audit
                        <ArrowRight className="h-5 w-5 ml-2" />
                      </>
                    )}
                  </Button>
                </form>
              </Card>
            </div>

            {/* Example Brands */}
            <div className="space-y-4">
              <p className="text-gray-500">Try these popular brands:</p>
              <div className="flex flex-wrap justify-center gap-3">
                {exampleBrands.map((brand) => (
                  <button
                    key={brand}
                    onClick={() => setBrandQuery(brand)}
                    className="px-4 py-2 bg-white border border-gray-200 rounded-full hover:border-blue-300 hover:bg-blue-50 transition-colors duration-200 text-sm font-medium"
                  >
                    {brand}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Professional Brand Analysis, Powered by AI
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get the same insights that Fortune 500 companies pay consulting firms $10,000+ for, 
              delivered in minutes with real data and AI intelligence.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="p-6 border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <CardContent className="p-0 space-y-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="py-16 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="text-white space-y-6">
            <h3 className="text-2xl md:text-3xl font-bold">
              Trusted by Marketing Professionals
            </h3>
            <p className="text-xl text-blue-100">
              "This tool provides the same strategic insights we used to pay $15,000 for from McKinsey. 
              The AI analysis is incredibly detailed and actionable."
            </p>
            <div className="flex items-center justify-center gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star key={star} className="h-6 w-6 text-yellow-400 fill-current" />
              ))}
              <span className="ml-2 text-blue-100 font-medium">5.0 from marketing teams</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ModernLanding
