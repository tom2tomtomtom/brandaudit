import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  Building2, 
  ExternalLink, 
  Eye, 
  Palette, 
  BarChart3,
  Users,
  TrendingUp,
  Target,
  Globe,
  Camera
} from 'lucide-react'

const CompetitorComparison = ({ competitorAnalysis, brandName }) => {
  const [selectedCompetitor, setSelectedCompetitor] = useState(null)

  // Extract competitor data
  const getCompetitorData = () => {
    if (!competitorAnalysis) return null
    
    return {
      competitors: competitorAnalysis.competitors_identified?.competitors || [],
      competitorCount: competitorAnalysis.competitors_identified?.count || 0,
      visualComparisons: competitorAnalysis.visual_comparisons || [],
      competitivePositioning: competitorAnalysis.competitive_positioning || {},
      dataSources: competitorAnalysis.data_sources || {}
    }
  }

  const competitorData = getCompetitorData()

  if (!competitorData || competitorData.competitorCount === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-gray-400" />
            Competitor Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Building2 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No competitor data available</p>
            <p className="text-sm text-gray-400">
              AI competitor identification required for competitive analysis
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getMarketPositionColor = (position) => {
    switch (position?.toLowerCase()) {
      case 'leader': return 'bg-green-100 text-green-800 border-green-200'
      case 'challenger': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'follower': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'niche': return 'bg-purple-100 text-purple-800 border-purple-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getMarketPositionIcon = (position) => {
    switch (position?.toLowerCase()) {
      case 'leader': return <TrendingUp className="h-4 w-4" />
      case 'challenger': return <Target className="h-4 w-4" />
      case 'follower': return <Users className="h-4 w-4" />
      case 'niche': return <Globe className="h-4 w-4" />
      default: return <Building2 className="h-4 w-4" />
    }
  }

  const CompetitorCard = ({ competitor, visualComparison }) => (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Competitor Header */}
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-lg text-gray-900 mb-1">
                {competitor.name}
              </h4>
              <p className="text-sm text-gray-600 mb-2">
                {competitor.description}
              </p>
              {competitor.website && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => window.open(competitor.website, '_blank')}
                >
                  <ExternalLink className="h-3 w-3 mr-1" />
                  Visit Website
                </Button>
              )}
            </div>
            <div className="text-right">
              <Badge className={`${getMarketPositionColor(competitor.market_position)} border mb-2`}>
                {getMarketPositionIcon(competitor.market_position)}
                <span className="ml-1 capitalize">{competitor.market_position}</span>
              </Badge>
              {competitor.confidence_score && (
                <p className="text-xs text-gray-500">
                  Confidence: {Math.round(competitor.confidence_score * 100)}%
                </p>
              )}
            </div>
          </div>

          {/* Key Differentiator */}
          {competitor.key_differentiator && (
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm font-medium text-blue-900 mb-1">Key Differentiator</p>
              <p className="text-sm text-blue-800">{competitor.key_differentiator}</p>
            </div>
          )}

          {/* Visual Analysis */}
          {visualComparison && (
            <div className="space-y-3">
              <h5 className="font-medium text-gray-900 flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Visual Analysis
              </h5>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Screenshots */}
                {Object.keys(visualComparison.screenshots).length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <Camera className="h-3 w-3" />
                      Screenshots ({Object.keys(visualComparison.screenshots).length})
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(visualComparison.screenshots).slice(0, 2).map(([page, url]) => (
                        <img 
                          key={page}
                          src={url}
                          alt={`${competitor.name} ${page}`}
                          className="w-full h-16 object-cover rounded border"
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Color Palette */}
                {visualComparison.color_palette?.primary_colors?.length > 0 && (
                  <div>
                    <p className="text-xs font-medium text-gray-700 mb-2 flex items-center gap-1">
                      <Palette className="h-3 w-3" />
                      Brand Colors
                    </p>
                    <div className="flex gap-1">
                      {visualComparison.color_palette.primary_colors.slice(0, 4).map((color, index) => (
                        <div 
                          key={index}
                          className="w-6 h-6 rounded border"
                          style={{ backgroundColor: color.hex || `rgb(${color.rgb?.join(',')})` }}
                          title={color.hex || color.name}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Visual Scores */}
              {Object.keys(visualComparison.visual_scores).length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-700 mb-2 flex items-center gap-1">
                    <BarChart3 className="h-3 w-3" />
                    Visual Scores
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(visualComparison.visual_scores).map(([metric, score]) => (
                      <div key={metric} className="text-xs">
                        <span className="text-gray-600 capitalize">
                          {metric.replace('_', ' ')}: 
                        </span>
                        <span className="font-medium ml-1">{score}/100</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-orange-600" />
          Competitor Analysis
          {brandName && <span className="text-sm font-normal text-gray-500">vs {brandName}</span>}
        </CardTitle>
        <div className="flex gap-2">
          {competitorData.dataSources.competitor_identification && (
            <Badge variant="default" className="text-xs">
              <Building2 className="h-3 w-3 mr-1" />
              {competitorData.competitorCount} Competitors
            </Badge>
          )}
          {competitorData.dataSources.visual_analysis && (
            <Badge variant="secondary" className="text-xs">
              <Eye className="h-3 w-3 mr-1" />
              Visual Analysis
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Competitors Grid */}
          <div>
            <h4 className="font-medium text-gray-900 mb-4">Direct Competitors</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {competitorData.competitors.map((competitor, index) => {
                const visualComparison = competitorData.visualComparisons.find(
                  vc => vc.competitor_name === competitor.name
                )
                return (
                  <CompetitorCard 
                    key={index}
                    competitor={competitor}
                    visualComparison={visualComparison}
                  />
                )
              })}
            </div>
          </div>

          {/* Competitive Positioning Matrix */}
          {competitorData.competitivePositioning.positioning_matrix && (
            <div className="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-lg border border-orange-200">
              <h5 className="font-medium text-orange-900 mb-4 flex items-center gap-2">
                <Target className="h-4 w-4" />
                Competitive Positioning Matrix
              </h5>
              <div className="space-y-3">
                {competitorData.competitivePositioning.competitive_analysis && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    {competitorData.competitivePositioning.competitive_analysis.market_leaders && (
                      <div>
                        <p className="font-medium text-orange-800 mb-1">Market Leaders</p>
                        <ul className="text-orange-700 space-y-1">
                          {competitorData.competitivePositioning.competitive_analysis.market_leaders.map((leader, i) => (
                            <li key={i}>• {leader}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {competitorData.competitivePositioning.competitive_analysis.threats && (
                      <div>
                        <p className="font-medium text-orange-800 mb-1">Key Threats</p>
                        <ul className="text-orange-700 space-y-1">
                          {competitorData.competitivePositioning.competitive_analysis.threats.map((threat, i) => (
                            <li key={i}>• {threat}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {competitorData.competitivePositioning.competitive_analysis.opportunities && (
                      <div>
                        <p className="font-medium text-orange-800 mb-1">Opportunities</p>
                        <ul className="text-orange-700 space-y-1">
                          {competitorData.competitivePositioning.competitive_analysis.opportunities.map((opp, i) => (
                            <li key={i}>• {opp}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Analysis Summary */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h5 className="font-medium text-blue-900 mb-2">Competitive Analysis Summary</h5>
            <div className="text-sm text-blue-800 space-y-1">
              <p>✅ {competitorData.competitorCount} direct competitors identified using AI analysis</p>
              <p>🎨 {competitorData.visualComparisons.length} competitors analyzed visually</p>
              <p>📊 Competitive positioning and strategic insights generated</p>
              <p>🔄 Analysis based on real-time data and market intelligence</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default CompetitorComparison
