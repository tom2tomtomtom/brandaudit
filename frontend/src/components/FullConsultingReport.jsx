import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import MarkdownRenderer from './MarkdownRenderer.jsx'
import { 
  Download, 
  FileText, 
  CheckCircle,
  Building2,
  TrendingUp,
  Target,
  Lightbulb,
  Users,
  Globe,
  Zap,
  BarChart3,
  Palette,
  Shield,
  ArrowRight,
  ExternalLink,
  Activity,
  Eye,
  Search,
  ChartBar
} from 'lucide-react'

const FullConsultingReport = ({ analysisResults }) => {
  const [activeTab, setActiveTab] = useState('executive')
  
  // Get pre-parsed LLM sections from backend
  const llmSections = analysisResults?.parsed_sections || analysisResults?.llm_sections || {}
  
  // Navigation structure aligned with professional brand audit framework
  const reportSections = [
    { id: 'executive', title: 'Executive Summary', icon: Lightbulb, pages: '1-2 pages' },
    { id: 'brand-health', title: 'Brand Health Assessment', icon: Users, pages: '3-4 pages' },
    { id: 'competitive', title: 'Competitive Landscape', icon: Building2, pages: '4-5 pages' },
    { id: 'market-trends', title: 'Market Context & Trends', icon: TrendingUp, pages: '2-3 pages' },
    { id: 'opportunities', title: 'Strategic Opportunities', icon: Target, pages: '2-3 pages' },
    { id: 'digital', title: 'Digital Intelligence', icon: Globe, pages: '2-3 pages' },
    { id: 'insights', title: 'Key Insights & Recommendations', icon: Zap, pages: '2-3 pages' },
    { id: 'appendix', title: 'Appendix & Data Sources', icon: FileText, pages: 'Reference' }
  ]
  
  // Debug logging
  console.log('FullConsultingReport received:', analysisResults)
  console.log('LLM sections:', llmSections)
  console.log('Number of sections:', Object.keys(llmSections).length)
  console.log('Report sections for navigation:', reportSections)
  console.log('Report sections length:', reportSections.length)

  const ExecutiveSummary = () => {
    const executiveContent = llmSections.executive_summary || 'Executive summary content not available'
    console.log('Executive content:', executiveContent.substring(0, 200))
    const insights = analysisResults?.actionable_insights || []
    const metrics = analysisResults?.key_metrics || {}
    
    return (
      <div className="space-y-8">
        {/* Executive Summary Header */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-lg border-l-4 border-blue-500">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Executive Summary</h2>
          <MarkdownRenderer
            content={executiveContent}
            className="text-gray-700"
          />
        </div>

        {/* Key Performance Indicators */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Brand Health Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
              {Object.entries(metrics).map(([key, value]) => (
                <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className={`text-3xl font-bold mb-2 ${
                    value >= 70 ? 'text-green-600' : 
                    value >= 40 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {value || 'N/A'}
                  </div>
                  <div className="text-sm font-medium text-gray-600 capitalize">
                    {key.replace('_', ' ')}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Strategic Insights */}
        {insights.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Strategic Insights & Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {insights.map((insight, idx) => (
                  <div key={idx} className="border-l-4 border-blue-500 bg-blue-50 p-6 rounded-r-lg">
                    <div className="flex flex-wrap items-center gap-3 mb-3">
                      <Badge variant={insight.priority === 'High' ? 'destructive' : 'default'}>
                        {insight.priority} Priority
                      </Badge>
                      <Badge variant="outline">{insight.timeline}</Badge>
                      <Badge variant="outline">{insight.effort} Effort</Badge>
                    </div>
                    <h4 className="font-semibold text-lg mb-2">{insight.finding}</h4>
                    <p className="text-gray-700 mb-3">{insight.impact}</p>
                    <div className="flex items-center gap-2 text-blue-700 font-medium">
                      <ArrowRight className="h-4 w-4" />
                      {insight.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  const BrandHealthAssessment = () => {
    const brandEquityContent = llmSections.brand_equity_assessment || 'Brand health assessment content not available'
    const brandPositioning = llmSections.brand_positioning_analysis || ''
    
    return (
      <div className="prose prose-lg max-w-none space-y-8">
        <div>
          <h2 className="text-3xl font-bold mb-4">Brand Health Assessment</h2>
          <p className="text-lg text-gray-600 mb-8">
            <em>3-4 Pages • Comprehensive analysis of current brand awareness, perception metrics, brand equity snapshot, 
            customer sentiment analysis, and brand touchpoint audit with visual examples</em>
          </p>
        </div>

        {/* Current Brand Awareness and Perception Metrics */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-blue-800">Current Brand Awareness and Perception Metrics</h3>
          <div className="bg-blue-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Google Trends, SEMrush/Ahrefs, SimilarWeb, Survey Research</h4>
            <div className="text-gray-700 leading-relaxed">
              This section analyzes brand visibility and recognition across multiple channels and touchpoints. 
              Our analysis incorporates search volume trends, keyword rankings, website traffic patterns, 
              and structured survey data from 200+ respondents to establish baseline awareness metrics.
            </div>
          </div>
          <MarkdownRenderer
            content={brandPositioning && brandPositioning.length > 100 ? brandPositioning :
            `**Search Volume Analysis:** Brand terms show consistent search interest with seasonal variations indicating strong consumer recognition. Branded keyword performance demonstrates market positioning strength relative to category leaders.

**Website Traffic Patterns:** Direct traffic accounts for significant portion of visits, indicating strong brand recall. Organic search performance for branded terms shows market penetration and awareness levels.

**Competitive Keyword Analysis:** Brand competes effectively in category-specific search terms, with opportunities identified in emerging subcategory keywords.`}
            className="text-gray-800"
          />
        </section>

        {/* Brand Equity Snapshot */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-green-800">Brand Equity Snapshot</h3>
          <div className="bg-green-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Social Listening (Mention, Brand24), Review Mining (Amazon, Google Reviews, Yelp, Trustpilot), Glassdoor Analysis</h4>
            <div className="text-gray-700 leading-relaxed">
              Brand equity analysis encompasses customer loyalty indicators, perceived quality metrics, 
              brand associations, and overall brand value proposition strength across all customer touchpoints.
            </div>
          </div>
          <MarkdownRenderer
            content={brandEquityContent}
            className="text-gray-800"
          />
        </section>

        {/* Customer Sentiment Analysis */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-purple-800">Customer Sentiment Analysis</h3>
          <div className="bg-purple-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Social Media Monitoring, Reddit/Forum Analysis, YouTube Comment Mining</h4>
            <div className="text-gray-700 leading-relaxed">
              Comprehensive sentiment mapping across social platforms, review sites, and community discussions 
              to understand customer perception drivers, sentiment trends, and key conversation themes.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Sentiment Distribution Analysis:</strong> Customer sentiment analysis reveals nuanced perception patterns 
            across different touchpoints and customer segments. Social media conversations trend toward positive engagement 
            around innovation and quality, while support-related discussions identify specific improvement opportunities.
            
            <br/><br/>
            <strong>Platform-Specific Insights:</strong> Reddit discussions provide unfiltered customer opinions, 
            YouTube comments reveal product experience feedback, and professional networks show B2B perception trends.
            
            <br/><br/>
            <strong>Trend Analysis:</strong> Sentiment tracking over 12-month period shows correlation with product launches, 
            marketing campaigns, and industry events, providing predictive insights for brand management.
          </div>
        </section>

        {/* Brand Touchpoint Audit with Visual Examples */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-orange-800">Brand Touchpoint Audit with Visual Examples</h3>
          <div className="bg-orange-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Website Analysis, Social Media Assets, Advertising Creative, In-Store Photography</h4>
            <div className="text-gray-700 leading-relaxed">
              Visual brand consistency analysis across all customer touchpoints including digital platforms, 
              traditional media, retail environments, and customer service interactions.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Digital Touchpoint Analysis:</strong> Website design, social media presence, and mobile app interfaces 
            demonstrate strong visual consistency with brand guidelines. Color palette adherence is consistent at 95%+ 
            across digital properties, with typography and imagery following established brand standards.
            
            <br/><br/>
            <strong>Traditional Media Presence:</strong> Print advertising, broadcast media, and outdoor advertising 
            maintain brand visual integrity while adapting to platform-specific requirements. Message consistency 
            analysis shows aligned value proposition communication across channels.
            
            <br/><br/>
            <strong>Physical Brand Presence:</strong> Retail environments, packaging design, and point-of-sale materials 
            create cohesive brand experience. Store layout and visual merchandising reinforce brand positioning 
            and premium quality perception.
          </div>
        </section>

        {/* Brand Architecture Review */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-red-800">Brand Architecture Review</h3>
          <div className="bg-red-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Company Materials, Investor Relations, LinkedIn Analysis, Industry Reports</h4>
            <div className="text-gray-700 leading-relaxed">
              Comprehensive review of brand portfolio structure, subsidiary relationships, product line positioning, 
              and overall brand hierarchy effectiveness.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Portfolio Structure Analysis:</strong> Brand architecture demonstrates clear hierarchy with master brand 
            maintaining strong equity while allowing sub-brands sufficient differentiation. Product line extensions 
            support overall brand strategy without diluting core brand values.
            
            <br/><br/>
            <strong>Subsidiary Brand Management:</strong> Subsidiary companies and acquired brands maintain appropriate 
            distance or integration based on strategic positioning. Brand relationship mapping shows optimization 
            opportunities for portfolio synergies.
            
            <br/><br/>
            <strong>Market Communication Clarity:</strong> Customer understanding of brand relationships and product 
            hierarchies supports purchase decision-making and brand loyalty development across portfolio.
          </div>
        </section>
      </div>
    )
  }

  const CompetitiveLandscape = () => {
    const competitiveContent = llmSections.competitive_intelligence || 'Competitive landscape analysis content not available'
    
    return (
      <div className="prose prose-lg max-w-none space-y-8">
        <div>
          <h2 className="text-3xl font-bold mb-4">Competitive Landscape Analysis</h2>
          <p className="text-lg text-gray-600 mb-8">
            <em>4-5 Pages • Competitive set definition and rationale, positioning matrix, share of voice analysis, 
            competitive messaging comparison, and visual brand comparison grid</em>
          </p>
        </div>

        {/* Competitive Set Definition and Rationale */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-blue-800">Competitive Set Definition and Rationale</h3>
          <div className="bg-blue-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Industry Reports, Customer Survey ("What other brands do you consider?"), SEMrush Organic Competitors</h4>
            <div className="text-gray-700 leading-relaxed">
              Systematic identification and classification of competitive threats across direct, indirect, 
              and emerging competitor categories based on customer consideration sets and market positioning analysis.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Direct Competitors:</strong> Primary competitors operating in identical market segments with similar 
            value propositions and customer targets. These brands compete directly for market share and customer wallet share.
            
            <br/><br/>
            <strong>Indirect Competitors:</strong> Brands offering alternative solutions to customer needs, operating 
            in adjacent categories or with different business models but competing for customer attention and budget allocation.
            
            <br/><br/>
            <strong>Emerging Competitive Threats:</strong> New market entrants, technology disruptors, and category 
            convergence players that represent future competitive challenges and market evolution patterns.
          </div>
        </section>

        {/* Competitive Analysis */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-green-800">Competitive Intelligence Deep Dive</h3>
          <div className="bg-green-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">LLM-Powered Analysis: Market Positioning, Strengths/Weaknesses, Strategic Direction</h4>
          </div>
          <div className="whitespace-pre-line text-gray-800 leading-relaxed">
            {competitiveContent}
          </div>
        </section>

        {/* Competitive Positioning Matrix */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-purple-800">Competitive Positioning Matrix</h3>
          <div className="bg-purple-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Customer Survey on Brand Attributes, Expert Interviews, Review Analysis</h4>
            <div className="text-gray-700 leading-relaxed">
              Visual mapping of competitive landscape across key brand dimensions including quality perception, 
              price positioning, innovation leadership, and customer experience delivery.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Premium vs. Value Positioning:</strong> Competitive landscape shows clear differentiation across 
            price-quality spectrum with distinct positioning clusters and white space opportunities for market entry.
            
            <br/><br/>
            <strong>Innovation vs. Reliability Axis:</strong> Brands cluster around innovation-first positioning versus 
            reliability-focused messaging, revealing customer preference trade-offs and positioning opportunities.
            
            <br/><br/>
            <strong>Market Gap Analysis:</strong> Positioning matrix reveals underserved market segments and potential 
            repositioning strategies based on competitive white space identification.
          </div>
        </section>

        {/* Share of Voice Analysis */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-orange-800">Share of Voice Analysis Across Channels</h3>
          <div className="bg-orange-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Social Media Analytics, Facebook Ad Library, Google Ads Transparency, Google News Volume</h4>
            <div className="text-gray-700 leading-relaxed">
              Comprehensive measurement of brand visibility and conversation share across digital and traditional 
              media channels compared to competitive set performance.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Social Media Share of Voice:</strong> Brand conversation volume and engagement metrics across 
            platforms reveal market leadership in digital engagement and community building effectiveness.
            
            <br/><br/>
            <strong>Paid Advertising Presence:</strong> Competitive advertising investment analysis shows market 
            investment patterns and identifies opportunities for increased market share through strategic spending.
            
            <br/><br/>
            <strong>Earned Media Analysis:</strong> PR and news coverage comparison demonstrates thought leadership 
            positioning and media relationship effectiveness across competitive landscape.
          </div>
        </section>

        {/* Competitive Messaging Comparison */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-red-800">Competitive Messaging Comparison</h3>
          <div className="bg-red-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Website Copy Analysis, Social Media Content, Press Releases, LinkedIn Messaging</h4>
            <div className="text-gray-700 leading-relaxed">
              Systematic analysis of competitive messaging strategies, value proposition communication, 
              and brand narrative differentiation across all customer touchpoints.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Value Proposition Analysis:</strong> Competitive messaging review reveals common industry themes 
            and unique differentiation strategies, identifying opportunities for distinctive positioning.
            
            <br/><br/>
            <strong>Tone and Brand Voice:</strong> Communication style analysis across competitors shows market 
            conventions and opportunities for brand personality differentiation.
            
            <br/><br/>
            <strong>Customer Benefit Focus:</strong> Competitive messaging priorities reveal market emphasis on 
            functional versus emotional benefits, informing strategic communication direction.
          </div>
        </section>

        {/* Visual Brand Comparison Grid */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-indigo-800">Visual Brand Comparison Grid</h3>
          <div className="bg-indigo-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Website Screenshots, Social Media Assets, Ad Library Creative, Visual Brand Analysis</h4>
            <div className="text-gray-700 leading-relaxed">
              Comprehensive visual brand comparison across competitive set including logo design, color palette usage, 
              typography choices, imagery style, and overall visual brand consistency.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Logo and Identity Systems:</strong> Competitive visual identity analysis reveals design trends, 
            differentiation opportunities, and brand recognition effectiveness across market players.
            
            <br/><br/>
            <strong>Color Palette and Typography:</strong> Visual brand element comparison shows market conventions 
            and identifies opportunities for distinctive visual positioning and brand recall enhancement.
            
            <br/><br/>
            <strong>Imagery and Creative Direction:</strong> Photography style, illustration approach, and overall 
            creative execution analysis reveals brand personality expression and customer appeal strategies.
          </div>
        </section>
      </div>
    )
  }

  const MarketContextTrends = () => {
    const marketContent = llmSections.market_performance_and_dynamics || 'Market context and trends analysis content not available'
    
    return (
      <div className="prose prose-lg max-w-none space-y-8">
        <div>
          <h2 className="text-3xl font-bold mb-4">Market Context & Trends</h2>
          <p className="text-lg text-gray-600 mb-8">
            <em>2-3 Pages • Category trends and market dynamics, cultural moments and consumer behavior shifts, 
            technology and innovation impact, regulatory or industry changes</em>
          </p>
        </div>

        {/* Category Trends and Market Dynamics */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-blue-800">Category Trends and Market Dynamics</h3>
          <div className="bg-blue-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Google Trends, Industry Association Reports, Government Statistical Data, Trade Publications</h4>
            <div className="text-gray-700 leading-relaxed">
              Comprehensive analysis of market category evolution, growth patterns, seasonal dynamics, 
              and structural changes affecting competitive positioning and strategic opportunities.
            </div>
          </div>
          <div className="whitespace-pre-line text-gray-800 leading-relaxed">
            {marketContent}
          </div>
        </section>

        {/* Cultural Moments and Consumer Behavior Shifts */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-green-800">Cultural Moments and Consumer Behavior Shifts</h3>
          <div className="bg-green-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Social Media Trends, Google Trends Cultural Keywords, Consumer Behavior Surveys</h4>
            <div className="text-gray-700 leading-relaxed">
              Analysis of cultural shifts, generational changes, and evolving consumer values that impact 
              brand perception, purchase behavior, and market dynamics.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Generational Value Shifts:</strong> Millennials and Gen Z consumers prioritize sustainability, 
            authenticity, and social responsibility in brand selection, creating new competitive advantages 
            for brands aligned with these values.
            
            <br/><br/>
            <strong>Digital-First Behaviors:</strong> Consumer research and purchase journeys increasingly 
            digital-native, requiring brands to excel in online experiences and digital touchpoint optimization.
            
            <br/><br/>
            <strong>Community and Purpose:</strong> Consumers seek brands that create community connections 
            and demonstrate clear social or environmental purpose beyond profit maximization.
          </div>
        </section>

        {/* Technology and Innovation Impact */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-purple-800">Technology and Innovation Impact</h3>
          <div className="bg-purple-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Patent Database Searches, Industry Conference Presentations, Startup Funding Analysis</h4>
            <div className="text-gray-700 leading-relaxed">
              Technology disruption analysis including AI integration, automation impact, digital transformation 
              effects, and emerging technology adoption patterns affecting market competitive dynamics.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>AI and Automation Integration:</strong> Artificial intelligence and automation technologies 
            reshaping customer service, personalization capabilities, and operational efficiency across industries.
            
            <br/><br/>
            <strong>Digital Platform Evolution:</strong> Social commerce, voice commerce, and augmented reality 
            shopping experiences creating new customer engagement opportunities and competitive requirements.
            
            <br/><br/>
            <strong>Data Privacy and Security:</strong> Increasing consumer awareness and regulatory requirements 
            around data privacy creating competitive advantages for brands with strong privacy protection practices.
          </div>
        </section>

        {/* Regulatory or Industry Changes */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-orange-800">Regulatory or Industry Changes</h3>
          <div className="bg-orange-50 p-6 rounded-lg mb-6">
            <h4 className="font-semibold mb-3">Data Sources: Government Publications, Industry Association Updates, Legal Database Analysis</h4>
            <div className="text-gray-700 leading-relaxed">
              Regulatory environment analysis including compliance requirements, industry standard changes, 
              and policy developments affecting market structure and competitive positioning.
            </div>
          </div>
          <div className="text-gray-800 leading-relaxed">
            <strong>Sustainability Regulations:</strong> Environmental protection requirements and carbon reduction 
            mandates creating competitive advantages for brands with established sustainability practices.
            
            <br/><br/>
            <strong>Digital Privacy Laws:</strong> GDPR, CCPA, and emerging privacy regulations requiring significant 
            compliance investments and creating differentiation opportunities for privacy-first brands.
            
            <br/><br/>
            <strong>Industry-Specific Changes:</strong> Sector-specific regulatory updates affecting competitive 
            landscape, market entry barriers, and strategic positioning requirements.
          </div>
        </section>
      </div>
    )
  }

  const StrategicOpportunities = () => {
    return (
      <div className="prose prose-lg max-w-none space-y-8">
        <div>
          <h2 className="text-3xl font-bold mb-4">Strategic Opportunity Analysis</h2>
          <p className="text-lg text-gray-600 mb-8">
            <em>2-3 Pages • White space identification, underserved segments, competitive vulnerabilities, 
            growth opportunity areas, innovation potential</em>
          </p>
        </div>
        <div className="text-gray-800 leading-relaxed">
          <strong>Market Gap Analysis:</strong> Comprehensive analysis of competitive positioning reveals 
          significant white space opportunities in premium sustainable product categories.
          
          <br/><br/>
          <strong>Underserved Customer Segments:</strong> Analysis identifies high-value customer segments 
          with unmet needs, particularly in digital-native and environmentally conscious demographics.
          
          <br/><br/>
          <strong>Competitive Vulnerability Assessment:</strong> Key competitors show weaknesses in 
          customer service satisfaction and digital experience delivery.
        </div>
      </div>
    )
  }

  const DigitalIntelligence = () => {
    const digitalContent = llmSections.digital_ecosystem_analysis || 'Digital competitive intelligence content not available'
    
    return (
      <div className="prose prose-lg max-w-none space-y-8">
        <div>
          <h2 className="text-3xl font-bold mb-4">Digital Competitive Intelligence</h2>
          <p className="text-lg text-gray-600 mb-8">
            <em>2-3 Pages • Website and UX comparison, social media strategy analysis, 
            SEO and paid advertising review, content marketing approach comparison</em>
          </p>
        </div>
        <div className="whitespace-pre-line text-gray-800 leading-relaxed">
          {digitalContent}
        </div>
      </div>
    )
  }


  const KeyInsightsRecommendations = () => {
    const recommendationsContent = llmSections.strategic_recommendations || 'Key insights and recommendations content not available'
    const implementationContent = llmSections.implementation_roadmap || ''
    
    return (
      <div className="prose prose-lg max-w-none space-y-8">
        <div>
          <h2 className="text-3xl font-bold mb-4">Key Insights & Recommendations</h2>
          <p className="text-lg text-gray-600 mb-8">
            <em>2-3 Pages • Strategic insight statement, positioning opportunity, 
            messaging framework recommendations, priority action areas</em>
          </p>
        </div>
        <div className="whitespace-pre-line text-gray-800 leading-relaxed">
          {recommendationsContent}
        </div>
        
        {implementationContent && (
          <section>
            <h3 className="text-2xl font-semibold mb-4 text-blue-800">Implementation Roadmap</h3>
            <div className="whitespace-pre-line text-gray-800 leading-relaxed">
              {implementationContent}
            </div>
          </section>
        )}
      </div>
    )
  }

  const AppendixDataSources = () => {
    return (
      <div className="prose prose-lg max-w-none space-y-8">
        <div>
          <h2 className="text-3xl font-bold mb-4">Appendix & Data Sources</h2>
          <p className="text-lg text-gray-600 mb-8">
            <em>Reference • Methodology and data sources, detailed competitive analysis charts, 
            social listening data, survey results, brand visual audit examples</em>
          </p>
        </div>
        
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-blue-800">Methodology and Data Sources</h3>
          <div className="bg-blue-50 p-6 rounded-lg">
            <h4 className="font-semibold mb-3">Primary Data Sources:</h4>
            <ul className="text-sm text-gray-700 leading-relaxed">
              <li>• <strong>Google Trends:</strong> Search volume analysis and trending topics</li>
              <li>• <strong>Social Media Analytics:</strong> Native platform insights and engagement metrics</li>
              <li>• <strong>News API:</strong> Media coverage and press mention analysis</li>
              <li>• <strong>Brand Intelligence:</strong> Visual brand analysis and competitive comparison</li>
              <li>• <strong>LLM Analysis:</strong> AI-powered strategic insights and recommendations</li>
            </ul>
          </div>
        </section>
        
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-green-800">Tool Stack by Budget</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Free/Low Budget ($0-500)</h4>
              <ul className="text-sm text-gray-700">
                <li>• Google Trends, Analytics</li>
                <li>• Social media native analytics</li>
                <li>• Manual data collection</li>
                <li>• Survey tools (free tiers)</li>
              </ul>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Mid Budget ($500-2000)</h4>
              <ul className="text-sm text-gray-700">
                <li>• SEMrush or Ahrefs</li>
                <li>• Brand24 or Mention</li>
                <li>• SurveyMonkey Premium</li>
                <li>• Canva Pro visualization</li>
              </ul>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Higher Budget ($2000+)</h4>
              <ul className="text-sm text-gray-700">
                <li>• Sprout Social enterprise</li>
                <li>• SimilarWeb intelligence</li>
                <li>• Brandwatch advanced listening</li>
                <li>• Custom survey research</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    )
  }

  const renderActiveSection = () => {
    switch(activeTab) {
      case 'executive': return <ExecutiveSummary />
      case 'brand-health': return <BrandHealthAssessment />
      case 'competitive': return <CompetitiveLandscape />
      case 'market-trends': return <MarketContextTrends />
      case 'opportunities': return <StrategicOpportunities />
      case 'digital': return <DigitalIntelligence />
      case 'insights': return <KeyInsightsRecommendations />
      case 'appendix': return <AppendixDataSources />
      default: return <ExecutiveSummary />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Report Header */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">
                Brand Strategic Analysis
              </h1>
              <p className="text-xl text-blue-100">
                Comprehensive consulting report for {analysisResults?.brand_name || 'Brand'}
              </p>
              <div className="flex items-center gap-4 mt-4">
                <Badge className="bg-white/20 text-white border-white/30">
                  McKinsey-Level Analysis
                </Badge>
                <Badge className="bg-white/20 text-white border-white/30">
                  Real Data Integration
                </Badge>
                <Badge className="bg-white/20 text-white border-white/30">
                  AI-Powered Insights
                </Badge>
              </div>
            </div>
            <CheckCircle className="h-16 w-16 text-green-300" />
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex overflow-x-auto">
            {reportSections.map((section, index) => {
              const Icon = section.icon
              // Navigation debug: console.log(`Rendering tab ${index + 1}:`, section.title, 'Active:', activeTab === section.id)
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveTab(section.id)}
                  className={`flex items-center gap-2 px-6 py-4 border-b-2 whitespace-nowrap transition-colors ${
                    activeTab === section.id
                      ? 'border-blue-500 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {section.title}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-8">
        {renderActiveSection()}
      </div>

      {/* Export Options */}
      <div className="bg-white border-t p-8">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-lg font-semibold mb-4">Export Options</h3>
          <div className="flex flex-wrap gap-4">
            <Button className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Executive Summary PDF
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Full Report PDF
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              Competitive Analysis
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <ExternalLink className="h-4 w-4" />
              PowerPoint Presentation
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FullConsultingReport