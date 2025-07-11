import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { 
  Megaphone, 
  ExternalLink, 
  Calendar, 
  Target, 
  Palette,
  TrendingUp,
  Users,
  Globe,
  Camera,
  FileText,
  Lightbulb,
  BarChart3
} from 'lucide-react'

const CampaignAnalysis = ({ campaignAnalysis, brandName }) => {
  const [selectedCampaign, setSelectedCampaign] = useState(null)

  // Extract campaign data
  const getCampaignData = () => {
    if (!campaignAnalysis) return null
    
    return {
      campaigns: campaignAnalysis.campaigns_discovered?.campaigns || [],
      campaignCount: campaignAnalysis.campaigns_discovered?.count || 0,
      creativeAssets: campaignAnalysis.creative_assets?.assets || [],
      tradePressCount: campaignAnalysis.trade_press_coverage?.count || 0,
      tradePressArticles: campaignAnalysis.trade_press_coverage?.articles || [],
      advertisingInsights: campaignAnalysis.advertising_insights || {},
      dataSources: campaignAnalysis.data_sources || {}
    }
  }

  const campaignData = getCampaignData()

  if (!campaignData || campaignData.campaignCount === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Megaphone className="h-5 w-5 text-gray-400" />
            Campaign Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Megaphone className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 mb-2">No campaign data available</p>
            <p className="text-sm text-gray-400">
              Campaign discovery requires API access for advertising research
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getCampaignTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'product_launch': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'brand_awareness': return 'bg-green-100 text-green-800 border-green-200'
      case 'seasonal': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'social_responsibility': return 'bg-purple-100 text-purple-800 border-purple-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getCampaignTypeIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'product_launch': return <TrendingUp className="h-4 w-4" />
      case 'brand_awareness': return <Target className="h-4 w-4" />
      case 'seasonal': return <Calendar className="h-4 w-4" />
      case 'social_responsibility': return <Users className="h-4 w-4" />
      default: return <Megaphone className="h-4 w-4" />
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Date unknown'
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch {
      return dateString
    }
  }

  const CampaignCard = ({ campaign, index }) => (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Campaign Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-semibold text-lg text-gray-900 mb-2">
                {campaign.title || campaign.name || `Campaign ${index + 1}`}
              </h4>
              <p className="text-sm text-gray-600 mb-3">
                {campaign.description || 'No description available'}
              </p>
            </div>
            <div className="text-right ml-4">
              {campaign.campaign_type && (
                <Badge className={`${getCampaignTypeColor(campaign.campaign_type)} border mb-2`}>
                  {getCampaignTypeIcon(campaign.campaign_type)}
                  <span className="ml-1 capitalize">{campaign.campaign_type.replace('_', ' ')}</span>
                </Badge>
              )}
              {campaign.confidence_score && (
                <p className="text-xs text-gray-500">
                  Confidence: {Math.round(campaign.confidence_score * 100)}%
                </p>
              )}
            </div>
          </div>

          {/* Campaign Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Launch Date */}
            {(campaign.launch_date || campaign.published_date) && (
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-700">
                  {formatDate(campaign.launch_date || campaign.published_date)}
                </span>
              </div>
            )}

            {/* Target Audience */}
            {campaign.target_audience && (
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-700">{campaign.target_audience}</span>
              </div>
            )}

            {/* Media Channels */}
            {campaign.media_channels && campaign.media_channels.length > 0 && (
              <div className="md:col-span-2">
                <p className="text-xs font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <Globe className="h-3 w-3" />
                  Media Channels
                </p>
                <div className="flex flex-wrap gap-1">
                  {campaign.media_channels.map((channel, i) => (
                    <Badge key={i} variant="outline" className="text-xs">
                      {channel}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Key Messaging */}
          {campaign.key_messaging && (
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm font-medium text-blue-900 mb-1">Key Messaging</p>
              <p className="text-sm text-blue-800">{campaign.key_messaging}</p>
            </div>
          )}

          {/* Campaign URL */}
          {campaign.url && (
            <div className="flex justify-between items-center pt-2 border-t">
              <span className="text-xs text-gray-500">
                Source: {campaign.source || 'Unknown'}
              </span>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => window.open(campaign.url, '_blank')}
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                View Article
              </Button>
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
          <Megaphone className="h-5 w-5 text-purple-600" />
          Campaign & Advertising Analysis
          {brandName && <span className="text-sm font-normal text-gray-500">for {brandName}</span>}
        </CardTitle>
        <div className="flex gap-2">
          {campaignData.dataSources.campaign_discovery && (
            <Badge variant="default" className="text-xs">
              <Megaphone className="h-3 w-3 mr-1" />
              {campaignData.campaignCount} Campaigns
            </Badge>
          )}
          {campaignData.dataSources.trade_press && (
            <Badge variant="secondary" className="text-xs">
              <FileText className="h-3 w-3 mr-1" />
              {campaignData.tradePressCount} Articles
            </Badge>
          )}
          {campaignData.dataSources.creative_analysis && (
            <Badge variant="outline" className="text-xs">
              <Camera className="h-3 w-3 mr-1" />
              Creative Analysis
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Campaigns Grid */}
          <div>
            <h4 className="font-medium text-gray-900 mb-4">Recent Campaigns</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {campaignData.campaigns.slice(0, 6).map((campaign, index) => (
                <CampaignCard 
                  key={index}
                  campaign={campaign}
                  index={index}
                />
              ))}
            </div>
          </div>

          {/* Advertising Insights */}
          {Object.keys(campaignData.advertisingInsights).length > 0 && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg border border-purple-200">
              <h5 className="font-medium text-purple-900 mb-4 flex items-center gap-2">
                <Lightbulb className="h-4 w-4" />
                Advertising Strategy Insights
              </h5>
              
              {campaignData.advertisingInsights.campaign_strategy_analysis && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  {/* Dominant Themes */}
                  {campaignData.advertisingInsights.campaign_strategy_analysis.dominant_themes && (
                    <div>
                      <p className="font-medium text-purple-800 mb-2">Dominant Themes</p>
                      <ul className="text-sm text-purple-700 space-y-1">
                        {campaignData.advertisingInsights.campaign_strategy_analysis.dominant_themes.map((theme, i) => (
                          <li key={i}>• {theme}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Preferred Channels */}
                  {campaignData.advertisingInsights.campaign_strategy_analysis.preferred_channels && (
                    <div>
                      <p className="font-medium text-purple-800 mb-2">Preferred Channels</p>
                      <div className="flex flex-wrap gap-1">
                        {campaignData.advertisingInsights.campaign_strategy_analysis.preferred_channels.map((channel, i) => (
                          <Badge key={i} variant="outline" className="text-xs text-purple-700 border-purple-300">
                            {channel}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Target Audience */}
                  {campaignData.advertisingInsights.campaign_strategy_analysis.target_audience_focus && (
                    <div>
                      <p className="font-medium text-purple-800 mb-2">Target Audience</p>
                      <p className="text-sm text-purple-700">
                        {campaignData.advertisingInsights.campaign_strategy_analysis.target_audience_focus}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Recommendations */}
              {campaignData.advertisingInsights.campaign_effectiveness?.recommendations && (
                <div>
                  <p className="font-medium text-purple-800 mb-2">Strategic Recommendations</p>
                  <ul className="text-sm text-purple-700 space-y-1">
                    {campaignData.advertisingInsights.campaign_effectiveness.recommendations.map((rec, i) => (
                      <li key={i}>• {rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Trade Press Coverage */}
          {campaignData.tradePressArticles.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Trade Press Coverage
              </h4>
              <div className="space-y-3">
                {campaignData.tradePressArticles.slice(0, 5).map((article, index) => (
                  <div key={index} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h5 className="font-medium text-gray-900 mb-1">{article.title}</h5>
                        <p className="text-sm text-gray-600 mb-2">{article.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          <span>{article.source}</span>
                          <span>{formatDate(article.published_date)}</span>
                        </div>
                      </div>
                      {article.url && (
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => window.open(article.url, '_blank')}
                        >
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analysis Summary */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h5 className="font-medium text-blue-900 mb-2">Campaign Analysis Summary</h5>
            <div className="text-sm text-blue-800 space-y-1">
              <p>✅ {campaignData.campaignCount} campaigns discovered through AI and news analysis</p>
              <p>📰 {campaignData.tradePressCount} trade press articles analyzed</p>
              <p>🎨 {campaignData.creativeAssets.length} creative assets processed</p>
              <p>🔄 Analysis based on real campaign data and industry coverage</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default CampaignAnalysis
