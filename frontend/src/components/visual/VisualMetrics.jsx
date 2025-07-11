import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  BarChart3, 
  Palette, 
  Eye, 
  Camera, 
  CheckCircle,
  AlertTriangle,
  Info,
  TrendingUp
} from 'lucide-react'

const VisualMetrics = ({ visualAnalysis, brandName }) => {
  // Extract visual scores and metrics
  const getVisualMetrics = () => {
    if (!visualAnalysis) return null

    const visualScores = visualAnalysis.visual_scores || {}
    const capabilities = visualAnalysis.processing_capabilities || {}
    const dataSources = visualAnalysis.data_sources || {}

    return {
      visualScores,
      capabilities,
      dataSources,
      hasVisualData: Object.keys(visualScores).length > 0
    }
  }

  const metrics = getVisualMetrics()

  if (!metrics || !metrics.hasVisualData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-gray-400" />
            Visual Analysis Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No visual metrics available</p>
            <p className="text-sm text-gray-400">
              Visual processing required for detailed metrics
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getScoreColor = (score) => {
    if (score >= 70) return "text-green-600"
    if (score >= 40) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBackground = (score) => {
    if (score >= 70) return "bg-green-50 border-green-200"
    if (score >= 40) return "bg-yellow-50 border-yellow-200"
    return "bg-red-50 border-red-200"
  }

  const getScoreIcon = (score) => {
    if (score >= 70) return <CheckCircle className="h-5 w-5 text-green-600" />
    if (score >= 40) return <AlertTriangle className="h-5 w-5 text-yellow-600" />
    return <Info className="h-5 w-5 text-red-600" />
  }

  const getScoreDescription = (scoreType, score) => {
    const descriptions = {
      color_consistency: {
        high: "Excellent color palette consistency across brand materials",
        medium: "Good color usage with some inconsistencies",
        low: "Color palette needs improvement for better brand consistency"
      },
      logo_quality: {
        high: "High-quality logo assets with good visibility",
        medium: "Logo assets present but could be optimized",
        low: "Logo quality or visibility needs improvement"
      },
      content_quality: {
        high: "Well-structured content with clear messaging",
        medium: "Good content structure with room for improvement",
        low: "Content structure and messaging need enhancement"
      },
      overall_visual_score: {
        high: "Excellent overall visual brand presentation",
        medium: "Good visual presentation with optimization opportunities",
        low: "Visual brand presentation needs significant improvement"
      }
    }

    const level = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'
    return descriptions[scoreType]?.[level] || "Visual analysis completed"
  }

  const formatScoreTitle = (scoreType) => {
    return scoreType
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
  }

  const ScoreCard = ({ title, score, icon: Icon, description }) => (
    <Card className={`${getScoreBackground(score)} border-2`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Icon className={getScoreColor(score)} />
            <div>
              <h4 className="font-semibold text-gray-900">{title}</h4>
              <p className={`text-2xl font-bold ${getScoreColor(score)}`}>
                {score}/100
              </p>
            </div>
          </div>
          {getScoreIcon(score)}
        </div>
        <Progress value={score} className="mb-3" />
        <p className="text-sm text-gray-600">{description}</p>
      </CardContent>
    </Card>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          Visual Analysis Metrics
          {brandName && <span className="text-sm font-normal text-gray-500">for {brandName}</span>}
        </CardTitle>
        <div className="flex gap-2">
          {metrics.dataSources.visual_processing && (
            <Badge variant="default" className="text-xs">
              <Eye className="h-3 w-3 mr-1" />
              Visual Processing
            </Badge>
          )}
          {metrics.dataSources.brandfetch && (
            <Badge variant="secondary" className="text-xs">
              <Palette className="h-3 w-3 mr-1" />
              Brandfetch
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Visual Scores Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(metrics.visualScores).map(([scoreType, score]) => {
              const icons = {
                color_consistency: Palette,
                logo_quality: Camera,
                content_quality: Eye,
                overall_visual_score: TrendingUp
              }
              
              const Icon = icons[scoreType] || BarChart3
              
              return (
                <ScoreCard
                  key={scoreType}
                  title={formatScoreTitle(scoreType)}
                  score={score}
                  icon={Icon}
                  description={getScoreDescription(scoreType, score)}
                />
              )
            })}
          </div>

          {/* Capabilities Overview */}
          {Object.keys(metrics.capabilities).length > 0 && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-3 flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Processing Capabilities
              </h5>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(metrics.capabilities).map(([capability, available]) => (
                  <div key={capability} className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${available ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className="text-sm text-blue-800 capitalize">
                      {capability.replace(/_/g, ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Sources Status */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h5 className="font-medium text-gray-900 mb-3">Data Sources</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(metrics.dataSources).map(([source, active]) => (
                <div key={source} className="flex items-center justify-between p-2 bg-white rounded border">
                  <span className="font-medium capitalize text-gray-700">
                    {source.replace(/_/g, ' ')}
                  </span>
                  <Badge variant={active ? "default" : "secondary"}>
                    {active ? "Active" : "Inactive"}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Visual Analysis Summary */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
            <h5 className="font-medium text-blue-900 mb-2">Analysis Summary</h5>
            <div className="text-sm text-blue-800 space-y-1">
              <p>✅ Visual metrics calculated from real data sources</p>
              <p>🎨 Color analysis and brand consistency evaluated</p>
              <p>📊 Scores based on industry best practices</p>
              <p>🔄 Metrics update automatically with new visual data</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default VisualMetrics
