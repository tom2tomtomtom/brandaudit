import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import useWebSocket from '@/hooks/useWebSocket.js'
import {
  Brain,
  Search,
  Building2,
  TrendingUp,
  Palette,
  CheckCircle,
  Clock,
  Loader2,
  Sparkles,
  BarChart3,
  Globe,
  Target,
  Wifi,
  WifiOff,
  RefreshCw,
  AlertTriangle
} from 'lucide-react'

const AnalysisProgress = ({ analysisId, onComplete }) => {
  // Use WebSocket hook for real-time updates
  const {
    isConnected,
    connectionQuality,
    errorMessage,
    progress,
    currentStage,
    stageProgress,
    currentStepName,
    currentSubstep,
    status,
    timeRemaining,
    estimatedCompletion,
    elapsedTime,
    stages: wsStages,
    completedSteps,
    formatTimeRemaining,
    formatElapsedTime,
    retry,
    disconnect
  } = useWebSocket(analysisId, onComplete)

  // Default analysis steps (fallback if WebSocket doesn't provide stages)
  const defaultAnalysisSteps = [
    {
      id: 'llm_analysis',
      name: 'Multi-Pass Strategic Analysis',
      description: 'GPT-4 generating comprehensive brand intelligence (7 sections)',
      icon: Brain,
      estimated_duration: 180,
      color: 'purple',
      substeps: [
        'Executive Summary & Market Position',
        'Competitive Intelligence Deep-Dive',
        'Strategic Challenges & Growth Opportunities',
        'Cultural Position & Social Impact',
        'Thought Starters & Strategic Provocations',
        'Agency Partnership Opportunities',
        'Strategic Recommendations'
      ]
    },
    {
      id: 'news_analysis',
      name: 'News & Market Intelligence',
      description: 'Gathering recent news and market sentiment',
      icon: TrendingUp,
      estimated_duration: 20,
      color: 'green'
    },
    {
      id: 'brand_data',
      name: 'Brand Asset Discovery',
      description: 'Retrieving logos, colors, and brand assets via Brandfetch',
      icon: Search,
      estimated_duration: 15,
      color: 'blue'
    },
    {
      id: 'visual_analysis',
      name: 'Visual Brand Analysis',
      description: 'Capturing screenshots and analyzing visual identity',
      icon: Palette,
      estimated_duration: 45,
      color: 'pink'
    },
    {
      id: 'competitor_analysis',
      name: 'Competitive Intelligence',
      description: 'Identifying and analyzing key competitors',
      icon: Building2,
      estimated_duration: 60,
      color: 'orange'
    },
    {
      id: 'campaign_analysis',
      name: 'Campaign Discovery',
      description: 'Finding recent marketing campaigns and messaging',
      icon: Target,
      estimated_duration: 30,
      color: 'cyan'
    },
    {
      id: 'strategic_synthesis',
      name: 'Strategic Synthesis',
      description: 'Generating actionable recommendations',
      icon: Sparkles,
      estimated_duration: 30,
      color: 'indigo'
    },
    {
      id: 'presentation',
      name: 'Report Generation',
      description: 'Creating professional presentation slides',
      icon: BarChart3,
      estimated_duration: 20,
      color: 'emerald'
    }
  ]

  // Use WebSocket stages if available, otherwise use default
  const analysisSteps = wsStages && wsStages.length > 0 ? wsStages.map((stage, index) => ({
    ...stage,
    icon: defaultAnalysisSteps[index]?.icon || Brain,
    color: defaultAnalysisSteps[index]?.color || 'blue'
  })) : defaultAnalysisSteps

  // No longer needed - WebSocket hook handles all real-time updates

  const getStepStatus = (stepIndex) => {
    if (completedSteps.has(stepIndex)) return 'completed'
    if (stepIndex === currentStage) return 'active'
    return 'pending'
  }

  const getStepIcon = (step, stepIndex) => {
    const status = getStepStatus(stepIndex)
    const IconComponent = step.icon
    
    if (status === 'completed') {
      return <CheckCircle className="h-6 w-6 text-green-500" />
    } else if (status === 'active') {
      return <Loader2 className="h-6 w-6 text-blue-500 animate-spin" />
    } else {
      return <IconComponent className="h-6 w-6 text-gray-400" />
    }
  }

  const getProgressColor = () => {
    if (progress >= 90) return 'bg-green-500'
    if (progress >= 70) return 'bg-blue-500'
    if (progress >= 50) return 'bg-purple-500'
    if (progress >= 20) return 'bg-orange-500'
    return 'bg-blue-500'
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Sparkles className="h-8 w-8 text-blue-500" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI Brand Analysis in Progress
          </h1>
        </div>
        <p className="text-lg text-gray-600">
          Our AI is conducting a comprehensive analysis of your brand using real-time updates.
        </p>

        {/* Connection Status */}
        <div className="flex items-center justify-center gap-2">
          {isConnected ? (
            <div className={`flex items-center gap-2 ${
              connectionQuality === 'good' ? 'text-green-600' :
              connectionQuality === 'poor' ? 'text-yellow-600' : 'text-red-600'
            }`}>
              <Wifi className="h-4 w-4" />
              <span className="text-sm">
                Connected {connectionQuality === 'poor' ? '(Poor Quality)' : ''}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-red-600">
              <WifiOff className="h-4 w-4" />
              <span className="text-sm">Disconnected</span>
              <Button
                variant="outline"
                size="sm"
                onClick={retry}
                className="ml-2"
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                Retry
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <div>
                <h3 className="font-semibold text-red-800">Analysis Error</h3>
                <p className="text-sm text-red-700">{errorMessage}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={retry}
                className="ml-auto"
              >
                <RefreshCw className="h-3 w-3 mr-1" />
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overall Progress */}
      <Card className="border-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Analysis Progress
            </CardTitle>
            <Badge variant="outline" className="text-lg px-3 py-1">
              {Math.round(progress)}%
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Progress value={progress} className="h-3" />
            <div className="flex justify-between text-sm text-gray-600">
              <span>Started</span>
              <span className="font-medium">
                {status === 'completed' ? 'Analysis Complete!' :
                 status === 'error' ? 'Error occurred' :
                 currentStepName ? currentStepName : 'Processing...'}
              </span>
              <span>Complete</span>
            </div>

            {/* Current Step and Substep */}
            {currentStepName && status !== 'completed' && status !== 'error' && (
              <div className="text-center space-y-1">
                <p className="text-sm text-blue-600 font-medium">
                  Currently: {currentStepName}
                </p>
                {currentSubstep && (
                  <p className="text-xs text-gray-500">
                    {currentSubstep}
                  </p>
                )}
              </div>
            )}

            {/* Time Information */}
            <div className="flex justify-between text-xs text-gray-500">
              <span>
                Elapsed: {formatElapsedTime || '0s'}
              </span>
              {formatTimeRemaining && status !== 'completed' && status !== 'error' && (
                <span>
                  Remaining: ~{formatTimeRemaining}
                </span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step-by-Step Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Steps</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {analysisSteps.map((step, index) => {
              const stepStatus = getStepStatus(index)
              const isActive = stepStatus === 'active'
              const isCompleted = stepStatus === 'completed'
              
              return (
                <div
                  key={step.id}
                  className={`flex items-start gap-4 p-4 rounded-lg transition-all duration-300 ${
                    isActive 
                      ? 'bg-blue-50 border-2 border-blue-200 shadow-md' 
                      : isCompleted 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-gray-50 border border-gray-200'
                  }`}
                >
                  {/* Step Icon */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center ${
                    isCompleted 
                      ? 'bg-green-100' 
                      : isActive 
                        ? 'bg-blue-100' 
                        : 'bg-gray-100'
                  }`}>
                    {getStepIcon(step, index)}
                  </div>
                  
                  {/* Step Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className={`font-semibold ${
                        isActive ? 'text-blue-700' : isCompleted ? 'text-green-700' : 'text-gray-600'
                      }`}>
                        {step.title}
                      </h3>
                      {isActive && (
                        <Badge variant="secondary" className="animate-pulse">
                          Processing
                        </Badge>
                      )}
                      {isCompleted && (
                        <Badge variant="default" className="bg-green-500">
                          Complete
                        </Badge>
                      )}
                    </div>
                    <p className={`text-sm ${
                      isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {step.description}
                    </p>
                    
                    {/* Step Progress Bar */}
                    {isActive && (
                      <div className="mt-3">
                        <div className="w-full bg-blue-200 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${stageProgress}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>Stage Progress</span>
                          <span>{stageProgress}%</span>
                        </div>
                      </div>
                    )}

                    {/* Substeps for active stage */}
                    {isActive && step.substeps && (
                      <div className="mt-3 space-y-1">
                        {step.substeps.map((substep, substepIndex) => (
                          <div key={substepIndex} className="flex items-center gap-2 text-xs">
                            <div className={`w-2 h-2 rounded-full ${
                              currentSubstep === substep ? 'bg-blue-500' : 'bg-gray-300'
                            }`} />
                            <span className={currentSubstep === substep ? 'text-blue-600 font-medium' : 'text-gray-500'}>
                              {substep}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Step Number */}
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    isCompleted 
                      ? 'bg-green-500 text-white' 
                      : isActive 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-300 text-gray-600'
                  }`}>
                    {index + 1}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Fun Facts */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200">
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Globe className="h-6 w-6 text-purple-600" />
            <h3 className="font-semibold text-purple-800">Did you know?</h3>
          </div>
          <p className="text-purple-700">
            Our AI analyzes over 50 different brand factors including market positioning, 
            competitive landscape, visual identity, and strategic opportunities to provide 
            you with actionable insights that typically cost $10,000+ from consulting firms.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default AnalysisProgress
